#!/usr/bin/env python3
"""Index a Godot game's GDScript into a graphify-compatible `graph.json`.

`graphify` (0.9.104) has no GDScript extractor, so `graphify update` on a game
picks up only its Markdown and never the `.gd` code. This tool fills that gap:
it parses every `.gd` with tree-sitter, writes the same `graph.json` shape, and
the usual lookups work unchanged on it:

    graphify explain "_step_meteors" --graph games/bach-ai/graphify-out/graph.json
    graphify path "run.gd::_ready" "meteor_shower.gd::start" --graph ...

What it records: file, `class_name`, functions, constants, signals and enums as
nodes; `contains` (file -> class -> member), `extends` and `calls` as links, with
each call link carrying the call site so `explain` prints file:line.

Call targets resolve through, in order: the same file, the class named in the
caller's variable type (`var s: Type` / `var s := Type.new()` / typed parameter),
a project `class_name`, an autoload from `project.godot`, then a project-wide
unique function name. Anything else (Godot built-ins, `array.append`, ...) is
left out rather than guessed.

Usage:
    tools/gdgraph/gdgraph games/bach-ai              # writes <game>/graphify-out/graph.json
    tools/gdgraph/gdgraph games/bach-ai -o /tmp/g.json --quiet

Requires the venv next to this file (`tools/gdgraph/.venv`, see README.md).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from tree_sitter import Language, Parser
import tree_sitter_gdscript

SKIP_DIRS = {".godot", ".git", "builds", "graphify-out", ".import", "export"}
LANGUAGE = Language(tree_sitter_gdscript.language())


def slug(path: str) -> str:
    """`src/run/run.gd` -> `src_run_run` (graphify-style id stem)."""
    return re.sub(r"[^a-z0-9]+", "_", path.lower()).strip("_").removesuffix("_gd")


def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)


def text(node, src: bytes) -> str:
    return src[node.start_byte : node.end_byte].decode("utf-8", "replace")


def line(node) -> int:
    return node.start_point[0] + 1


def _child_of_type(node, wanted: tuple[str, ...]):
    for child in node.children:
        if child.type in wanted:
            return child
    return None


def _declared_type(stmt, src: bytes) -> str:
    """Type of a `var` / `const`: `: Type`, `:= Type.new()`, or ""."""
    explicit = _child_of_type(stmt, ("type",))
    if explicit is not None:
        return text(explicit, src)
    init = stmt.child_by_field_name("value")
    if init is None:
        return ""
    # `var s := MeteorShower.new()` parses as attribute_call `new` on `MeteorShower`.
    for node in walk(init):
        if node.type == "attribute_call" and text(node.child_by_field_name("name") or node, src) == "new":
            base = node.parent
            if base is not None and base.type == "attribute":
                ident = _child_of_type(base, ("identifier",))
                if ident is not None:
                    return text(ident, src)
    for node in walk(init):
        if node.type in ("identifier", "type"):
            return text(node, src)
    return ""


def _params(stmt, src: bytes) -> dict[str, str]:
    out: dict[str, str] = {}
    params = stmt.child_by_field_name("parameters")
    if params is None:
        return out
    for param in params.children:
        if param.type not in ("typed_parameter", "identifier"):
            continue
        name = param.child_by_field_name("name") or _child_of_type(param, ("identifier",))
        if name is None:
            continue
        ty = _child_of_type(param, ("type",))
        out[text(name, src)] = text(ty, src) if ty is not None else ""
    return out


def parse_file(root: Path, path: Path) -> dict:
    src = path.read_bytes()
    tree = Parser(LANGUAGE).parse(src).root_node
    rel = path.relative_to(root).as_posix()
    stem = slug(rel)
    info = {
        "path": rel,
        "id": stem,
        "label": path.name,
        "class": None,          # (name, id)
        "extends": "",          # stripped `extends` target
        "funcs": {},            # name -> id
        "consts": {},
        "signals": {},
        "enums": {},
        "vars": {},             # file-level var name -> type name
        "nodes": [],
        "raw_calls": [],        # (caller id, base|"", attr|"", line, type map)
    }

    def add(nid: str, label: str, at: int, callable_: bool = False) -> None:
        info["nodes"].append(
            {
                "id": nid,
                "label": label,
                "_callable": callable_,
                "_origin": "ast",
                "file_type": "code",
                "norm_label": label.lower(),
                "source_file": info["path"],
                "source_location": f"L{at}",
                "community_name": rel.rsplit("/", 1)[0] if "/" in rel else ".",
            }
        )

    add(stem, info["label"], 1)
    for node in tree.children:
        kind = node.type
        name_node = node.child_by_field_name("name")
        if kind == "class_name_statement" and name_node is not None:
            name = text(name_node, src)
            info["class"] = (name, f"{stem}_{name}")
            add(info["class"][1], name, line(node), True)
        elif kind == "extends_statement":
            target = _child_of_type(node, ("type", "identifier", "attribute"))
            info["extends"] = text(target, src).strip() if target is not None else ""
        elif kind == "function_definition" and name_node is not None:
            name = text(name_node, src)
            info["funcs"][name] = f"{stem}_{name}"
            add(info["funcs"][name], f"{name}()", line(node), True)
            types = {**info["vars"], **_params(node, src)}
            body = node.child_by_field_name("body")
            if body is None:
                continue
            for sub in walk(body):
                if sub.type == "variable_statement":
                    vname = sub.child_by_field_name("name")
                    vtype = _declared_type(sub, src)
                    if vname is not None and vtype:
                        types[text(vname, src)] = vtype
                elif sub.type == "call":
                    callee = _child_of_type(sub, ("identifier", "attribute"))
                    if callee is not None and callee.type == "identifier":
                        info["raw_calls"].append(
                            (info["funcs"][name], "", text(callee, src), line(sub), dict(types))
                        )
                elif sub.type == "attribute_call":
                    base = sub.parent
                    ident = _child_of_type(base, ("identifier",)) if base is not None else None
                    if ident is None:
                        continue
                    info["raw_calls"].append(
                        (
                            info["funcs"][name],
                            text(ident, src),
                            text(sub.child_by_field_name("name") or _child_of_type(sub, ("identifier",)), src),
                            line(sub),
                            dict(types),
                        )
                    )
        elif kind == "const_statement" and name_node is not None:
            name = text(name_node, src)
            info["consts"][name] = f"{stem}_const_{name}"
            add(info["consts"][name], name, line(node))
        elif kind == "signal_statement" and name_node is not None:
            name = text(name_node, src)
            info["signals"][name] = f"{stem}_sig_{name}"
            add(info["signals"][name], name, line(node))
        elif kind == "enum_definition":
            enum_name = name_node or _child_of_type(node, ("identifier",))
            if enum_name is not None:
                name = text(enum_name, src)
                info["enums"][name] = f"{stem}_enum_{name}"
                add(info["enums"][name], name, line(node))
        elif kind == "variable_statement" and name_node is not None:
            vtype = _declared_type(node, src)
            if vtype:
                info["vars"][text(name_node, src)] = vtype
    return info


def autoloads(root: Path) -> dict[str, str]:
    """`project.godot` [autoload] name -> script path (when it points at a .gd)."""
    project = root / "project.godot"
    if not project.exists():
        return {}
    out: dict[str, str] = {}
    section = ""
    for raw in project.read_text(encoding="utf-8", errors="replace").splitlines():
        line_ = raw.strip()
        if line_.startswith("[") and line_.endswith("]"):
            section = line_[1:-1]
        elif section == "autoload" and "=" in line_:
            name, value = line_.split("=", 1)
            found = re.search(r"res://([^\"]+\.gd)", value)
            if found:
                out[name.strip()] = found.group(1)
    return out


def build(root: Path) -> dict:
    files = [
        parse_file(root, path)
        for path in sorted(root.rglob("*.gd"))
        if not (set(path.relative_to(root).parts[:-1]) & SKIP_DIRS)
    ]
    nodes = [n for info in files for n in info["nodes"]]
    links: dict[tuple[str, str, str], dict] = {}

    def link(src: str, tgt: str, relation: str, file: str, at: int) -> None:
        key = (src, tgt, relation)
        if key in links:
            return
        links[key] = {
            "source": src,
            "target": tgt,
            "relation": relation,
            "_origin": "ast",
            "confidence": "EXTRACTED",
            "confidence_score": 1.0,
            "context": relation,
            "source_file": file,
            "source_location": f"L{at}",
            "weight": 1.0,
        }

    by_name = {name: info for info in files if info["class"] for name, _ in [info["class"]]}
    by_autoload = {
        name: path for name, path in autoloads(root).items()
    }
    by_path = {info["path"]: info for info in files}
    functions: dict[str, list[str]] = {}
    for info in files:
        for name, fid in info["funcs"].items():
            functions.setdefault(name, []).append(fid)
        for name, cid in info["consts"].items():
            functions.setdefault(name, []).append(cid)

    # contains + extends
    at_of = {n["id"]: int(str(n["source_location"]).removeprefix("L") or 1) for n in nodes}
    for info in files:
        members = [*info["funcs"].values(), *info["consts"].values(), *info["signals"].values(), *info["enums"].values()]
        owner = info["id"]
        if info["class"]:
            owner = info["class"][1]
            link(info["id"], owner, "contains", info["path"], at_of.get(owner, 1))
        for member_id in members:
            link(owner, member_id, "contains", info["path"], at_of.get(member_id, 1))
        if info["extends"]:
            target = by_name.get(info["extends"])
            tgt_id = target["class"][1] if target else f"ext_{slug(info['extends'])}"
            if target is None and tgt_id not in {n["id"] for n in nodes}:
                nodes.append(
                    {
                        "id": tgt_id,
                        "label": info["extends"],
                        "_origin": "external",
                        "file_type": "code",
                        "norm_label": info["extends"].lower(),
                        "source_file": "",
                        "source_location": "",
                        "community_name": "Godot",
                    }
                )
            link(owner, tgt_id, "extends", info["path"], 1)

    # calls
    for info in files:
        for caller, base, name, at, types in info["raw_calls"]:
            target = ""
            if not base:
                target = info["funcs"].get(name, "")
                if not target:
                    hits = functions.get(name) or []
                    target = hits[0] if len(hits) == 1 else ""
            elif base == "self":
                target = info["funcs"].get(name, "")
            else:
                owner = by_name.get(types.get(base, "")) or by_name.get(base)
                if owner is None:
                    owner = by_path.get(by_autoload.get(base, ""))
                if owner is not None:
                    target = owner["funcs"].get(name, "")
            if target:
                link(caller, target, "calls", info["path"], at)

    commit = ""
    try:
        commit = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True, timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return {
        "directed": True,
        "multigraph": True,
        "graph": {"schema_version": 1, "graphify_version": "gdgraph"},
        "nodes": nodes,
        "links": list(links.values()),
        "built_at_commit": commit,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("game", help="game directory (contains project.godot)")
    ap.add_argument("-o", "--out", help="output path (default <game>/graphify-out/graph.json)")
    ap.add_argument("-q", "--quiet", action="store_true")
    args = ap.parse_args(argv)

    root = Path(args.game).resolve()
    if not root.is_dir():
        print(f"error: no such directory: {root}", file=sys.stderr)
        return 1
    data = build(root)
    out = Path(args.out) if args.out else root / "graphify-out" / "graph.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    if not args.quiet:
        gd = sum(1 for n in data["nodes"] if n["source_file"].endswith(".gd"))
        print(f"{out}: {len(data['nodes'])} nodes ({gd} in {len({n['source_file'] for n in data['nodes'] if n['source_file'].endswith('.gd')})} .gd files), {len(data['links'])} links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
