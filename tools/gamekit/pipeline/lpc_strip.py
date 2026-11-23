#!/usr/bin/env python3
"""Turn an ingested LPC character into a side-view SpriteSheet strip the game's run already draws.

Usage:  python3 lpc_strip.py --game <game-dir>        (run by `gamekit sprites` after lpc_ingest.py)

For each <game>/assets/sprites/characters/<name>/standard/*.png, writes
<game>/assets/sprites/custom/lpc-<name>/lpc-<name>_strip.png + lpc-<name>.json (SpriteSheet format: one row of 64x64
frames, animations, anchor at the feet, body circle, px_scale 0.5 so it draws at its own pixel size where the run
scales world sprites x2). Only the right-facing row is used: the run flips for left.

Game animation <- LPC:  idle <- idle,  run <- walk 1-8,  dash <- run,  hurt <- idle (the run tints it),
death <- hurt (LPC's fall),  shoot / slash / spellcast / thrust <- same name.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

F = 64
RIGHT = 3          # row of the right-facing frames in a 4-direction LPC sheet

# (game name, LPC file, columns, fps, loop)
MAP = [
    ("idle", "idle", [0, 1], 3, True),
    ("run", "walk", [1, 2, 3, 4, 5, 6, 7, 8], 10, True),
    ("hurt", "idle", [0], 10, False),
    ("dash", "run", [0, 2, 4, 6], 14, False),
    ("death", "hurt", [0, 1, 2, 3, 4, 5], 8, False),
    ("shoot", "shoot", list(range(13)), 16, False),
    ("slash", "slash", list(range(6)), 12, False),
    ("spellcast", "spellcast", list(range(7)), 12, False),
    ("thrust", "thrust", list(range(8)), 12, False),
]


def frame(sheet: Image.Image, col: int) -> Image.Image:
    row = RIGHT if sheet.height >= 4 * F else 0          # one-direction sheets (hurt) have a single row
    return sheet.crop((col * F, row * F, col * F + F, row * F + F))


def build(char_dir: Path, out_root: Path) -> Path | None:
    std = char_dir / "standard"
    if not std.is_dir():
        return None
    name = "lpc-" + char_dir.name
    frames: list[Image.Image] = []
    anims = []
    for game_name, src, cols, fps, loop in MAP:
        png = std / f"{src}.png"
        if not png.exists():
            continue
        sheet = Image.open(png).convert("RGBA")
        cols = [c for c in cols if (c + 1) * F <= sheet.width]
        if not cols:
            continue
        anims.append({"name": game_name, "start": len(frames), "frames": len(cols), "fps": float(fps), "loop": loop})
        frames += [frame(sheet, c) for c in cols]
    if not frames:
        return None
    idle = frames[0]
    bbox = idle.getbbox() or (16, 8, 48, 62)
    anchor = [float(F // 2), float(bbox[3])]                     # feet: the lowest opaque row of the idle frame
    cx, cy = (bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0
    radius = min(bbox[2] - bbox[0], bbox[3] - bbox[1]) * 0.4
    out = out_root / name
    out.mkdir(parents=True, exist_ok=True)
    strip = Image.new("RGBA", (F * len(frames), F))
    for i, im in enumerate(frames):
        strip.alpha_composite(im, (i * F, 0))
    strip.save(out / f"{name}_strip.png")
    meta = {"frames": len(frames), "frame_size": [F, F], "fps": anims[0]["fps"], "loop": True, "anchor": anchor,
            "anchor_source": "lpc_strip: lowest opaque row of idle", "ground": True, "px_scale": 0.5,
            "body": {"anim": "idle", "center": [cx, cy], "radius": radius}, "animations": anims,
            "source": f"assets/sprites/characters/{char_dir.name} (LPC; credits in assets/credits)"}
    (out / f"{name}.json").write_text(json.dumps(meta, indent=2) + "\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--game", required=True, type=Path)
    a = ap.parse_args()
    chars = a.game / "assets" / "sprites" / "characters"
    out_root = a.game / "assets" / "sprites" / "custom"
    n = 0
    for d in sorted(p for p in chars.glob("*") if p.is_dir()):
        o = build(d, out_root)
        if o:
            n += 1
            print(f"OK    {d.name} -> {o.relative_to(a.game)}")
    if n == 0:
        print("No LPC characters to strip.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
