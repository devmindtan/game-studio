#!/usr/bin/env python3
"""Family generator for Dao hồi (boomerang-i .. boomerang-v, design/rogue-kits.md, 2026-11-26): the user's own dagger
(sprite-lab/sources/user/assassin-2026-11-25.png) spinning end over end, with a crescent of light around it that
grows and warms each tier (I steel .. V violet-gold). A spin reads the same in every direction, so every fly_ anim is
the same spin. Each tier folder's gen.py runs this file. Chạy: gamekit art run boomerang-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
# tier: [crescent radius, crescent colours (outer, core), arc length in degrees]
TIERS = {"boomerang-i": [12, ("#8a94a6", "#d8e0ea"), 90], "boomerang-ii": [14, ("#6fb7e0", "#bfeaff"), 120],
         "boomerang-iii": [16, ("#7a3ab8", "#c38df5"), 150], "boomerang-iv": [18, ("#7a3ab8", "#e0b8ff"), 180],
         "boomerang-v": [20, ("#c0801a", "#fff4b0"), 220]}
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
WS = _ws()
sys.path.insert(0, str(WS / "tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(TIER_FILE).resolve().parents[2] / "lib"))
from PIL import Image  # noqa: E402
from spritekit import Canvas  # noqa: E402
from icefx import _p  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = 64
C = SIZE // 2
FPS = 16.0
SRC = WS / "sprite-lab/sources/user/assassin-2026-11-25.png"
PIECE = (28, 23, 42, 32)
HB = {"shape": "rect", "center": [float(C), float(C)], "active": [0, 3]}


def spin():
    piece = Image.open(SRC).convert("RGBA").crop(PIECE)
    piece = piece.resize((piece.width * 2, piece.height * 2), Image.NEAREST)
    radius, (outer, core), arc = _V
    out = []
    for f in range(4):
        c = Canvas(SIZE, SIZE)
        a0 = -f * 90.0                                    # the crescent trails the spin
        for k in range(int(arc)):
            a = math.radians(a0 - k)
            for dr, col in ((0, core), (1, outer), (-1, outer)):
                if k > arc * 0.6 and dr != 0:
                    continue
                _p(c, C + math.cos(a) * (radius + dr), C + math.sin(a) * (radius + dr), col if k < arc * 0.6 else outer)
        big = Image.new("RGBA", (SIZE, SIZE))
        big.alpha_composite(piece, (C - piece.width // 2, C - piece.height // 2))
        big = big.rotate(-f * 90, resample=Image.NEAREST, center=(C, C))
        c.img.alpha_composite(big)
        out.append(c)
    return out


FRAMES = spin()
DIRS = [("fly", 0), ("fly_right", 0), ("fly_left", 180), ("fly_up", 270), ("fly_down", 90)] + \
    [("fly_%03d" % round(k * 22.5), k * 22.5) for k in range(16)]
ANIM = [(n, [f.copy() for f in FRAMES], FPS, True, {"hitbox": dict(HB)}) for n, _ in DIRS]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(float(C), float(C)), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
