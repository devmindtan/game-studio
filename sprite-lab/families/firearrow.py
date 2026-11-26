#!/usr/bin/env python3
"""Family generator for Tên lửa (fire-arrow-i .. fire-arrow-v, design/rogue-kits.md, 2026-11-26): a steel
arrow trailing fire. Each tier: a longer, hotter flame, red-orange to white-blue at
the core. Chạy: gamekit art run fire-arrow-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
# tier: [halo radius, glow colours (outer, core), shaft glow length]
# tier: [flame length, colours (outer, mid, core)]
TIERS = {"fire-arrow-i": [10, ("#7a1410", "#d9361e", "#ff9a2a")], "fire-arrow-ii": [13, ("#d9361e", "#ff9a2a", "#fff2a0")],
         "fire-arrow-iii": [16, ("#d9361e", "#ff9a2a", "#ffffff")], "fire-arrow-iv": [19, ("#ff6a2a", "#fff2a0", "#ffffff")],
         "fire-arrow-v": [22, ("#3f8fe0", "#9ee0ff", "#ffffff")]}
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
HB = {"shape": "rect", "center": [C, C], "active": [0, 3]}
LENGTH, (OUTER, MID, CORE) = _V


def frames(deg):
    out = arrowfx.arrow("a", SIZE, deg)
    ux, uy = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    for f, c in enumerate(out):
        for d in range(16, 16 + LENGTH):                  # the flame streaming behind, flickering each frame
            w = max(1, 3 - (d - 16) * 3 // LENGTH)
            wob = math.sin((d + f * 2) * 0.9)
            for side in range(-w, w + 1):
                x, y = C - ux * d - uy * (side + wob), C - uy * d + ux * (side + wob)
                if 1 <= x < SIZE - 1 and 1 <= y < SIZE - 1 and c.img.getpixel((int(x), int(y)))[3] == 0:
                    col = CORE if abs(side) == 0 and d < 16 + LENGTH // 2 else (MID if abs(side) <= 1 else OUTER)
                    _p(c, x, y, col)
        for k in range(3):                                # embers round the head
            a = k * 2.1 + f
            _p(c, C - ux * 2 + math.cos(a) * 4, C - uy * 2 + math.sin(a) * 4, MID)
        out[f] = c
    return out


DIRS = [("fly", 0), ("fly_right", 0), ("fly_left", 180), ("fly_up", 270), ("fly_down", 90)] + \
    [("fly_%03d" % round(k * 22.5), k * 22.5) for k in range(16)]
ANIM = [(n, frames(d), 12.0, True, {"hitbox": dict(HB)}) for n, d in DIRS]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
