#!/usr/bin/env python3
"""Family generator for Tên nảy (ricochet-i .. ricochet-v, design/rogue-kits.md, 2026-11-26): a steel arrow trailing a
zig-zag of light that bounces off; each tier the trail is longer, brighter and gains sparks (I teal .. V gold).
Each tier folder's gen.py runs this file. Chạy: gamekit art run ricochet-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
# tier: [trail length, zig amplitude, colours (outer, core), sparks]
TIERS = {"ricochet-i": [18, 2, ("#3fb8c8", "#bff4ff"), 0], "ricochet-ii": [22, 3, ("#3fb8c8", "#e8ffff"), 1],
         "ricochet-iii": [26, 3, ("#4fd0a0", "#f0fff0"), 2], "ricochet-iv": [30, 4, ("#e0b040", "#fff4c0"), 3],
         "ricochet-v": [34, 5, ("#f2c14e", "#ffffff"), 4]}
import json
import math
import sys
from pathlib import Path


def _ws():
    for p in Path(TIER_FILE).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(TIER_FILE).resolve().parent
_V = TIERS[HERE.name]
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(TIER_FILE).resolve().parents[2] / "lib"))
import arrowfx  # noqa: E402
from icefx import _p  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = 112
C = SIZE / 2
FPS = 12.0
HB = {"shape": "rect", "center": [C, C], "active": [0, 3]}


def frames(deg):
    out = arrowfx.arrow("b", SIZE, deg)
    ux, uy = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    length, amp, (outer, core), sparks = _V
    for f, c in enumerate(out):
        for d in range(20, 20 + length):                 # a zig-zag trail behind the arrow, wobbling each frame
            off = amp * math.sin((d + f * 3) * 0.6)
            x, y = C - ux * d - uy * off, C - uy * d + ux * off
            if 1 <= x < SIZE - 1 and 1 <= y < SIZE - 1 and c.img.getpixel((int(x), int(y)))[3] == 0:
                _p(c, x, y, core if d < 20 + length * 0.6 else outer)
                _p(c, x - uy, y + ux, outer)
        for k in range(sparks):                          # sparks flicking off the trail
            d = 22 + (k * 7 + f * 5) % max(1, length)
            s = (-1) ** (k + f) * (amp + 3)
            sx, sy = C - ux * d - uy * s, C - uy * d + ux * s
            if 1 <= sx < SIZE - 1 and 1 <= sy < SIZE - 1:
                _p(c, sx, sy, core)
        out[f] = c
    return out


DIRS = [("fly", 0), ("fly_right", 0), ("fly_left", 180), ("fly_up", 270), ("fly_down", 90)] + \
    [("fly_%03d" % round(k * 22.5), k * 22.5) for k in range(16)]
ANIM = [(n, frames(d), FPS, True, {"hitbox": dict(HB)}) for n, d in DIRS]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
