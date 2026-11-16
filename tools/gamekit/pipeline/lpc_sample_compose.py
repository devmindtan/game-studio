#!/usr/bin/env python3
"""Compose a sample LPC character offline, straight from a generator checkout.

Writes a ZIP in the same shape as the generator's "split animations" export
(standard/<anim>.png, credits/credits.csv, character.json), so the rest of the
pipeline can be exercised without opening the browser app. For real
characters, use the generator UI - it handles z-order, palettes and every
item; this script only stacks a few hard-coded layers.

  gamekit sample-sprite <game>
  python3 lpc_sample_compose.py --generator tools/lpc-generator \
      --name sample_hero --out <game>/assets/source/lpc/sample_hero.zip
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import zipfile
from pathlib import Path

from PIL import Image

LAYOUT_PATH = Path(__file__).resolve().parents[1] / "addon/gamekit/lpc/lpc_layout.json"
CREDIT_FIELDS = ["filename", "notes", "authors", "licenses", "urls"]

# Bottom-to-top. Each is a folder holding <anim>.png files (generator naming).
SAMPLE_LAYERS = [
    "body/bodies/male",
    "feet/shoes/revised/male",
    "legs/pants/male",
    "torso/clothes/longsleeve/longsleeves/male",
    "head/heads/human/male",
    "hair/bob/adult",
]
# Generator file stem per layout file stem, where they differ.
LAYER_FILE = {"combat": "combat_idle", "1h_backslash": "backslash", "1h_halfslash": "halfslash"}


def load_credit_index(generator: Path) -> dict[str, dict[str, str]]:
    index = {}
    with (generator / "CREDITS.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            clean = {k.strip(): (v or "").strip() for k, v in row.items() if k}
            index[clean["filename"]] = {f: clean.get(f, "") for f in CREDIT_FIELDS}
    return index


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--generator", required=True, type=Path)
    ap.add_argument("--name", default="sample_hero")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    sheets = args.generator / "spritesheets"
    layout = json.loads(LAYOUT_PATH.read_text("utf-8"))
    size, cols = int(layout["frame_size"]), int(layout["sheet_columns"])
    credit_index = load_credit_index(args.generator)
    used_credits: dict[str, dict[str, str]] = {}
    missing = 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as z:
        for anim in layout["animations"]:
            stem = LAYER_FILE.get(anim["file"], anim["file"])
            canvas = Image.new("RGBA", (cols * size, int(anim["directions"]) * size))
            drawn = False
            for layer in SAMPLE_LAYERS:
                path = sheets / layer / f"{stem}.png"
                if not path.exists():
                    continue
                img = Image.open(path).convert("RGBA")
                canvas.alpha_composite(img.crop((0, 0, min(img.width, canvas.width),
                                                 min(img.height, canvas.height))))
                drawn = True
                # CREDITS.csv names rows by the export name (combat, 1h_backslash),
                # not by the layer file (combat_idle, backslash).
                keys = [f"{layer}/{anim['file']}.png", f"{layer}/{stem}.png"]
                rel = next((k for k in keys if k in credit_index), None)
                if rel:
                    used_credits[rel] = credit_index[rel]
                else:
                    missing += 1
                    print(f"error: no CREDITS.csv row for {keys[0]}", file=sys.stderr)
            if not drawn:
                continue
            buf = io.BytesIO()
            canvas.save(buf, "PNG")
            z.writestr(f"standard/{anim['file']}.png", buf.getvalue())

        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=CREDIT_FIELDS, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(used_credits[k] for k in sorted(used_credits))
        z.writestr("credits/credits.csv", out.getvalue())
        z.writestr("character.json", json.dumps(
            {"_note": "sample composed by lpc_sample_compose.py, not by the generator UI",
             "bodyType": "male", "layers": SAMPLE_LAYERS}, indent=2))
    print(f"Wrote {args.out} ({len(used_credits)} credited layer files)")
    return 1 if missing else 0  # uncredited art must not reach the game


if __name__ == "__main__":
    sys.exit(main())
