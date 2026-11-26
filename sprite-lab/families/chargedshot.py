#!/usr/bin/env python3
"""Family generator for Tên tích lực (charged-shot-i .. charged-shot-v, design/rogue-kits.md, 2026-11-26): a steel
arrow wrapped in gathered light, a pulsing halo round its head and a glowing shaft. Each tier: a bigger halo, white to
gold. Chạy: gamekit art run charged-shot-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
# tier: [halo radius, glow colours (outer, core), shaft glow length]
TIERS = {"charged-shot-i": [4, ("#8ab8e0", "#e8f4ff"), 10], "charged-shot-ii": [5, ("#6fb7e0", "#ffffff"), 12],
         "charged-shot-iii": [6, ("#c38df5", "#ffffff"), 14], "charged-shot-iv": [7, ("#f2b64a", "#fff4b0"), 16],
         "charged-shot-v": [8, ("#f2c14e", "#ffffff"), 18]}
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
SIZE = 72
C = SIZE / 2
HB = {"shape": "rect", "center": [C, C], "active": [0, 3]}
HALO, (OUTER, CORE), GLOW = _V


def frames(deg):
    out = arrowfx.arrow("b", SIZE, deg)
    ux, uy = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    for f, c in enumerate(out):
        r = HALO + (1 if f % 2 else 0)                    # the halo pulses
        for k in range(int(r * 8)):
            a = k * math.tau / (r * 8)
            _p(c, C - ux * 2 + math.cos(a) * r, C - uy * 2 + math.sin(a) * r, OUTER)
        for d in range(4, 4 + GLOW):                      # light running down the shaft
            for side in (-2, 2):
                x, y = C - ux * d - uy * side, C - uy * d + ux * side
                if (d + f) % 3:
                    _p(c, x, y, CORE if d < 4 + GLOW // 2 else OUTER)
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
