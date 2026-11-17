#!/usr/bin/env python3
"""sword-wave: Sóng kiếm bay (Bách Ải). The crescent of cleave-wave held still at the
anchor (cleave-wave moves inside its own frame, made for a strike on the spot: as a
flying wave its hitbox, measured over all frames, was a big box off the blade).
fly_right: the crescent with a glint running along the blade (6 frames); 16 flight
directions (lib/dirs16.py); impact: the crescent breaking into specks.
Run: gamekit art run sword-wave
"""
import json
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from PIL import Image
from spritekit import Canvas
from sheet import export
import dirs16

SRC = HERE.parent / "cleave-wave"
S = 40
meta = json.loads((SRC / "cleave-wave.json").read_text())
strip = Image.open(SRC / "cleave-wave_strip.png").convert("RGBA")
fw, fh = meta["frame_size"]
sweep = [a for a in meta["animations"] if a["name"] == "sweep_right"][0]
# the fullest frame of the sweep: the crescent at its biggest
best = max(range(sweep["frames"]), key=lambda k: sum(1 for p in strip.crop(((sweep["start"] + k) * fw, 0, (sweep["start"] + k + 1) * fw, fh)).getdata() if p[3] >= 96))
src = strip.crop(((sweep["start"] + best) * fw, 0, (sweep["start"] + best + 1) * fw, fh))
blade = src.crop(src.getbbox())
bw, bh = blade.size


def frame(k):
    c = Canvas(S, S)
    ox, oy = S // 2 - bw // 2, S // 2 - bh // 2
    c.img.alpha_composite(blade, (ox, oy))
    px = c.img.load()
    # a glint running along the blade: the solid pixels of one band of rows turn white
    band = int(k / 6 * bh)
    for y in range(oy + band, min(oy + band + 3, S)):
        for x in range(ox, ox + bw):
            if px[x, y][3] >= 200:
                px[x, y] = (255, 255, 255, px[x, y][3])
    return c


def impact(k):
    c = Canvas(S, S)
    ox, oy = S // 2 - bw // 2, S // 2 - bh // 2
    bp = blade.load()
    px = c.img.load()
    for y in range(bh):
        for x in range(bw):
            if bp[x, y][3] >= 96 and (x * 7 + y * 3 + k) % (2 + k) == 0:
                nx, ny = ox + x + (k * (x - bw // 2)) // 4, oy + y + (k * (y - bh // 2)) // 6
                if 0 <= nx < S and 0 <= ny < S:
                    px[nx, ny] = bp[x, y]
    return c


fly = [frame(k) for k in range(6)]
hb = {"shape": "rect", "center": [S / 2, S / 2], "active": [0, 5]}
ANIMATIONS = [
    ("fly_right", fly, 14, True, {"hitbox": hb}),
    ("impact", [impact(k) for k in range(5)], 14, False, {}),
]
ANIMATIONS, ANCHOR = dirs16.with_directions(ANIMATIONS, (S / 2, S / 2), 48)

if __name__ == "__main__":
    export(HERE, HERE.name, ANIMATIONS, anchor=ANCHOR)
    print("OK", HERE.name)
