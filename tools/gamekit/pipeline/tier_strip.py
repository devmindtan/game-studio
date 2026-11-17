#!/usr/bin/env python3
"""Upgrade tiers side by side: the largest frame of <skill>-i .. <skill>-v in one row,
x3 nearest, on a dark background, with the tier label under each.

Used by `gamekit art tiers <skill>` so the inheritance check of the pixel-sprite
skill (tier N keeps the motif of tier N-1) is one look, not a script to write.

Usage: tier_strip.py <sprites_dir> <skill> <out.png>
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TIERS = ["i", "ii", "iii", "iv", "v"]
SCALE = 3


def biggest_frame(d: Path, name: str) -> Image.Image:
    meta = json.loads((d / f"{name}.json").read_text())
    strip = Image.open(d / f"{name}_strip.png").convert("RGBA")
    fw, fh = (int(v) for v in meta["frame_size"])
    best, area = None, -1
    for i in range(strip.width // fw):
        f = strip.crop((i * fw, 0, i * fw + fw, fh))
        bb = f.getbbox()
        a = 0 if bb is None else (bb[2] - bb[0]) * (bb[3] - bb[1])
        if a >= area:
            best, area = f, a
    return best


def main() -> int:
    root, skill, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    frames = []
    for t in TIERS:
        name = f"{skill}-{t}"
        d = root / name
        if (d / f"{name}.json").exists():
            frames.append((t.upper(), biggest_frame(d, name)))
    if len(frames) < 2:
        print(f"ERROR: fewer than two tiers found for {skill} ({skill}-i .. {skill}-v)", file=sys.stderr)
        return 1
    cell = max(max(f.width, f.height) for _, f in frames) * SCALE + 24
    img = Image.new("RGBA", (cell * len(frames), cell + 28), (30, 32, 44, 255))
    draw = ImageDraw.Draw(img)
    for k, (label, f) in enumerate(frames):
        big = f.resize((f.width * SCALE, f.height * SCALE), Image.NEAREST)
        img.alpha_composite(big, (k * cell + (cell - big.width) // 2, (cell - big.height) // 2))
        draw.text((k * cell + cell // 2 - 6, cell + 6), label, fill=(220, 220, 230, 255))
    img.save(out)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
