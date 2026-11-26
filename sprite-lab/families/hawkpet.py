#!/usr/bin/env python3
"""Family generator for the Cung thủ's companion hawk (hawk-pet-i .. hawk-pet-v, design/rogue-kits.md, 2026-11-26).
fly: a 4-frame wing beat seen from the side, facing right (the run flips it); strike: the claw rake where it dives
(12 frames, hit mask on the hit frames). Each tier: bigger wingspan, plumage from brown to gold, tier V trails light.
Chạy: gamekit art run hawk-pet-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
# tier: [wing span, body (dark, mid, light), beak / claw, glow or None]
TIERS = {"hawk-pet-i": [8, ("#3a2414", "#6a4020", "#a8703a"), "#f2c14e", None],
         "hawk-pet-ii": [9, ("#3a2414", "#7a4a26", "#c08a4a"), "#f2c14e", None],
         "hawk-pet-iii": [10, ("#2a2a3a", "#5a5a70", "#a0a8c0"), "#fff4b0", None],
         "hawk-pet-iv": [11, ("#3a2a10", "#a87020", "#e8c060"), "#ffffff", "#fff4b0"],
         "hawk-pet-v": [12, ("#7a4a10", "#e0a030", "#fff0a0"), "#ffffff", "#ffffff"]}
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
from spritekit import Canvas  # noqa: E402
from fxkit import FxFrames, mask_disk  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
S = 64
C = S // 2
OUT = "#14111c"
SPAN, (D, M, L), BEAK, GLOW = _V


def bird(c, x, y, beat):
    """The hawk side-on facing right, centre (x, y); beat 0..3 = wings up, mid, down, mid."""
    lift = (-SPAN, -SPAN // 2, SPAN // 2, -SPAN // 2)[beat]
    if GLOW:
        c.line(x - 14, y + 1, x - 7, y, GLOW, 1)
    c.polygon([(x - 7, y - 1), (x + 5, y - 2), (x + 8, y + 1), (x + 2, y + 3), (x - 8, y + 2)], M)     # body
    c.polygon([(x - 8, y), (x - 13, y - 2), (x - 13, y + 3)], D)                                       # tail
    c.polygon([(x - 2, y - 1), (x - 6, y + lift), (x + 3, y + lift // 2), (x + 3, y - 1)], L)           # wing
    c.ellipse(x + 3, y - 5, x + 8, y, M)                                                               # head
    c.polygon([(x + 8, y - 3), (x + 11, y - 1), (x + 8, y)], BEAK)                                     # beak
    c.pixel(x + 6, y - 3, OUT)


def fly():
    out = []
    for f in range(4):
        c = Canvas(S, S)
        bird(c, C, C + (1 if f % 2 else 0), f)
        c.outline(OUT)
        out.append(c)
    return out


def strike(R):
    """Three claw rakes slash down across the target, sparks fly, fade."""
    out = []
    for f in range(12):
        c = Canvas(S, S)
        if f >= 1 and f <= 7:
            L_ = int(R * min(1.0, f / 2.0))
            for d in (-6, 0, 6):
                c.line(C - L_ // 2 + d, C - L_, C + L_ // 2 + d, C + L_ // 2, D, 3)
                c.line(C - L_ // 2 + d, C - L_, C + L_ // 2 + d, C + L_ // 2, BEAK if f < 4 else L, 1)
        if f >= 3:
            for k in range(6 + (SPAN - 8) * 2):
                a = k * math.tau / (6 + (SPAN - 8) * 2)
                d = 6 + (f - 3) * 3
                if d < C - 2:
                    c.pixel(int(C + math.cos(a) * d), int(C + math.sin(a) * d), BEAK if f < 9 else D)
        c.outline(OUT)
        out.append(c)
    return out


R = 18 + (SPAN - 8) * 2
_ST = strike(R)
ANIM = [("fly", fly(), 10.0, True, {"hitbox": {"shape": "circle", "center": [C, C], "active": [0, 3], "radius": 8.0, "inner": 0.0}}),
        ("strike", FxFrames(_ST, [mask_disk(S, S, C, C, R if 1 <= k <= 6 else 0) for k in range(12)]), 12.0, False,
         {"hitbox": {"shape": "circle", "center": [C, C], "active": [1, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(float(C), float(C)), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
