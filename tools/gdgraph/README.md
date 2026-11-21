# gdgraph: index GDScript for graphify

`graphify` 0.9.104 ships tree-sitter extractors for Python, TypeScript, Go, Rust and more — **not GDScript**.
Pointing it at a game indexes only the Markdown in `.claude/` (measured on `games/bach-ai`: 5.979 nodes,
**0** `.gd`). `gdgraph` fills that gap: it parses every `.gd` with tree-sitter-gdscript and writes the same
`graph.json` shape, so the normal graphify lookups work on game code unchanged.

Measured on `games/bach-ai` (2026-11-21): 158 `.gd` files → 1.765 nodes / 4.565 links in **0,5 s**.
`graphify explain "_step_meteors"` answers in **793 bytes** (caller `_tick`, 9 callees with file:line)
instead of reading `src/run/run.gd` (**139 KB**, 3.269 lines).

## Install (once per machine)

```bash
python3 -m venv tools/gdgraph/.venv
tools/gdgraph/.venv/bin/pip install -r tools/gdgraph/requirements.txt
```

The venv is local and gitignored; only `requirements.txt` is committed.

## Use

```bash
limited tools/gdgraph/gdgraph games/bach-ai    # writes games/bach-ai/graphify-out/graph.json
graphify explain "_step_meteors" --graph games/bach-ai/graphify-out/graph.json
graphify explain "run.gd::_ready" --graph games/bach-ai/graphify-out/graph.json
graphify path "run.gd::_step_meteors" "meteor_shower.gd::start" --graph games/bach-ai/graphify-out/graph.json
graphify query "where is a meteor landing applied" --graph games/bach-ai/graphify-out/graph.json
```

Rebuild after a batch of code changes (it is cheap); `graphify-out/` is generated and never committed.
`-o <path>` writes elsewhere, `--quiet` prints nothing.

## What is indexed

| Node | Label | Example |
|---|---|---|
| file | `run.gd` | every `.gd` outside `.godot/`, `builds/`, `graphify-out/` |
| class | `MeteorShower` | `class_name` statement |
| function | `_step_meteors()` | every `func`, `L<line>` points at the definition |
| constant | `SOURCE` | top-level `const` |
| signal, enum | `died`, `Kind` | top-level `signal` / `enum` |
| external | `RefCounted` | an `extends` target with no `class_name` in the project |

Links: `contains` (file → class → members), `extends`, and `calls` with the **call site** in
`source_file` / `source_location`, so `explain` prints where the call happens.

Call targets resolve through, in order:

1. the same file;
2. the type of the receiver, when known from `var x: Type`, `var x := Type.new()` or a typed parameter;
3. a project `class_name` used directly (`MeteorShower.start(...)`);
4. an autoload from `project.godot` (`Audio.play(...)`);
5. a project-wide **unique** function name.

Everything else — Godot built-ins, `array.append()`, unknown receivers — is dropped rather than guessed, so a
missing edge means "not resolved", not "no call". Lambdas are walked like any other body. There is no
inheritance-aware method lookup yet: a call through a base class only resolves when the receiver's own type
declares the method.

## Test

```bash
tools/gdgraph/.venv/bin/python -m unittest discover -s tools/gdgraph -p 'test_gdgraph.py'
```

Ruff-clean under the workspace rule (`tools/free-tools/venv/bin/ruff check tools/gdgraph --select
F401,F841,F821,F541`).
