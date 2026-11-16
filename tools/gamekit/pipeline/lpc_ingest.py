#!/usr/bin/env python3
"""Ingest LPC character exports into the Godot project.

Usage:  gamekit sprites <game>
        python3 lpc_ingest.py --game <game-dir>

Input (one file per character, in <game>/assets/source/lpc/; the file
stem becomes the character name, so rename the download first):

  <name>.zip   The generator's "split animations" ZIP export:
               standard/<anim>.png, custom/<anim>.png, credits/credits.csv,
               character.json.  (Recommended - it carries the credits.)
  <name>.png   A full "character-spritesheet.png". Needs a sidecar
               <name>.credits.csv (the generator's "credits.csv" download),
               and optionally <name>.json (its "export to JSON").

Output, per character, in <game>/assets/sprites/characters/<name>/:
  standard/<anim>.png   one PNG per animation, rows = directions
  custom/<anim>.png     oversize animations, copied as-is (not converted yet)
  credits.csv           attribution for exactly the layers used
  character.json        the generator selection, to reopen and edit later

Then rebuilds the merged attribution in assets/credits/ (lpc_credits.csv and
CREDITS.md). LPC art is CC-BY-SA / GPL / OGA-BY: a character without credits
is refused, because shipping it would break the licence.

Converting the PNGs into Godot SpriteFrames is a separate step
(addons/gamekit/lpc/build_sprite_frames.gd, also run by `gamekit sprites`).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
LAYOUT_PATH = KIT / "addon/gamekit/lpc/lpc_layout.json"
CREDIT_FIELDS = ["filename", "notes", "authors", "licenses", "urls"]


def sanitize(stem: str) -> str:
    """Character folder name: lowercase snake_case."""
    name = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    if not name:
        raise ValueError(f"cannot derive a character name from {stem!r}")
    return name


def read_credits(text: str) -> list[dict[str, str]]:
    """Parse a generator credits.csv (its rows have a stray space after quotes)."""
    rows = []
    for row in csv.DictReader(io.StringIO(text)):
        clean = {k.strip(): (v or "").strip() for k, v in row.items() if k}
        if clean.get("filename"):
            rows.append({f: clean.get(f, "") for f in CREDIT_FIELDS})
    return rows


def write_credits(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CREDIT_FIELDS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    keep_as_is(path)


def keep_as_is(path: Path) -> None:
    """Godot imports every .csv as a translation table; mark it "Keep File"
    so it stays a plain file, and drop any translations already generated."""
    imp = path.with_name(path.name + ".import")
    if not imp.exists() or 'importer="keep"' not in imp.read_text("utf-8"):
        imp.write_text('[remap]\n\nimporter="keep"\n', encoding="utf-8")
    for stale in path.parent.glob(path.stem + ".*.translation"):
        stale.unlink()


def sync_pngs(target: Path, files: dict[str, bytes]) -> None:
    """Write PNGs into target, removing stale ones (and their .import/.uid)."""
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("*.png"):
        if old.name not in files:
            for p in (old, old.with_name(old.name + ".import")):
                p.unlink(missing_ok=True)
    for name, data in files.items():
        dest = target / name
        if not dest.exists() or dest.read_bytes() != data:
            dest.write_bytes(data)


def ingest_zip(src: Path, out: Path) -> list[dict[str, str]]:
    standard: dict[str, bytes] = {}
    custom: dict[str, bytes] = {}
    credits: list[dict[str, str]] = []
    with zipfile.ZipFile(src) as z:
        for info in z.infolist():
            parts = Path(info.filename).parts
            if info.is_dir() or not parts:
                continue
            base = Path(parts[-1]).name  # never trust paths inside the zip
            if len(parts) == 2 and parts[0] == "standard" and base.endswith(".png"):
                standard[base] = z.read(info)
            elif len(parts) == 2 and parts[0] == "custom" and base.endswith(".png"):
                custom[base] = z.read(info)
            elif parts[-2:] == ("credits", "credits.csv"):
                credits = read_credits(z.read(info).decode("utf-8"))
            elif len(parts) == 1 and base == "character.json":
                (out / "character.json").write_bytes(z.read(info))
    if not standard:
        raise ValueError(f"{src.name}: no standard/*.png - is this the 'split animations' ZIP?")
    sync_pngs(out / "standard", standard)
    if custom:
        sync_pngs(out / "custom", custom)
    return credits


def ingest_sheet(src: Path, out: Path, layout: dict) -> list[dict[str, str]]:
    from PIL import Image  # only needed for full sheets

    sidecar = src.with_suffix(".credits.csv")
    credits = read_credits(sidecar.read_text("utf-8")) if sidecar.exists() else []
    meta = src.with_suffix(".json")
    if meta.exists():
        shutil.copyfile(meta, out / "character.json")
    size = int(layout["frame_size"])
    sheet = Image.open(src).convert("RGBA")
    files: dict[str, bytes] = {}
    for anim in layout["animations"]:
        top = int(anim["row"]) * size
        height = int(anim["directions"]) * size
        if top + height > sheet.height:
            continue
        crop = sheet.crop((0, top, sheet.width, top + height))
        if crop.getbbox() is None:  # fully transparent: animation not drawn
            continue
        buf = io.BytesIO()
        crop.save(buf, "PNG")
        files[anim["file"] + ".png"] = buf.getvalue()
    sync_pngs(out / "standard", files)
    return credits


def build_credit_docs(chars_dir: Path, credits_dir: Path) -> int:
    """Merge every character's credits.csv into assets/credits/."""
    merged: dict[str, dict[str, str]] = {}
    used_by: dict[str, set[str]] = {}
    for f in sorted(chars_dir.glob("*/credits.csv")):
        for row in read_credits(f.read_text("utf-8")):
            merged.setdefault(row["filename"], row)
            used_by.setdefault(row["filename"], set()).add(f.parent.name)
    credits_dir.mkdir(parents=True, exist_ok=True)
    rows = [merged[k] for k in sorted(merged)]
    write_credits(credits_dir / "lpc_credits.csv", rows)

    authors = sorted({a.strip() for r in rows for a in r["authors"].split(",") if a.strip()})
    licenses = sorted({l.strip() for r in rows for l in r["licenses"].split(",") if l.strip()})
    lines = [
        "# Credits",
        "",
        "<!-- Generated by gamekit (tools/gamekit/pipeline/lpc_ingest.py) - do not edit by hand. -->",
        "",
        "Character sprites by the Liberated Pixel Cup (LPC) contributors, composed with the",
        "Universal LPC Spritesheet Character Generator",
        "(https://github.com/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator).",
        "",
        f"**Licenses:** {', '.join(licenses) if licenses else '-'}",
        "",
        f"**Artists:** {', '.join(authors) if authors else '-'}",
        "",
        "Per-file details (authors, licence, source links) are in `lpc_credits.csv`.",
        "",
        "## Files",
        "",
    ]
    for r in rows:
        who = ", ".join(sorted(used_by[r["filename"]]))
        lines.append(f"- `{r['filename']}` ({who}) - {r['licenses']} - {r['authors']}")
        if r["urls"]:
            lines.append(f"  - {r['urls']}")
    (credits_dir / "CREDITS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", required=True, type=Path, help="game folder (holds project.godot)")
    args = ap.parse_args()
    root = args.game.resolve()
    if not (root / "project.godot").exists():
        print(f"{root} has no project.godot", file=sys.stderr)
        return 2
    args.source = root / "assets/source/lpc"
    args.dest = root / "assets/sprites/characters"
    args.credits_out = root / "assets/credits"

    layout = json.loads(LAYOUT_PATH.read_text("utf-8"))
    sources = sorted(p for p in args.source.glob("*") if p.suffix.lower() in (".zip", ".png"))
    if not sources:
        print(f"No .zip or .png in {args.source} - nothing to ingest.")
    failed = 0
    for src in sources:
        name = sanitize(src.stem)
        out = args.dest / name
        out.mkdir(parents=True, exist_ok=True)
        try:
            if src.suffix.lower() == ".zip":
                credits = ingest_zip(src, out)
            else:
                credits = ingest_sheet(src, out, layout)
        except (ValueError, zipfile.BadZipFile, OSError) as exc:
            print(f"FAIL  {src.name}: {exc}", file=sys.stderr)
            failed += 1
            continue
        if not credits:
            print(f"FAIL  {src.name}: no credits found. LPC art cannot ship without attribution - "
                  f"use the ZIP export, or add {src.with_suffix('.credits.csv').name}.", file=sys.stderr)
            failed += 1
            continue
        write_credits(out / "credits.csv", credits)
        anims = sorted(p.stem for p in (out / "standard").glob("*.png"))
        print(f"OK    {src.name} -> {out.relative_to(root)}  ({len(anims)} animations, {len(credits)} credit rows)")

    n = build_credit_docs(args.dest, args.credits_out)
    print(f"Credits: {n} files listed in {args.credits_out.relative_to(root)}/")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
