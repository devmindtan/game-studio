#!/usr/bin/env python3
"""Family generator for Đánh dấu (hunter-mark-i .. hunter-mark-v, design/rogue-kits.md, 2026-11-26): a hunter's
reticle over the marked monster, turning slowly (looping "mark"). Each tier: a bigger ring, more brackets, red to
gold. Chạy: gamekit art run hunter-mark-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
# tier: [radius, brackets, (dark, light)]
TIERS = {"hunter-mark-i": [16, 2, ("#8a1a18", "#e0402e")], "hunter-mark-ii": [18, 3, ("#8a1a18", "#ff7a5a")],
         "hunter-mark-iii": [20, 3, ("#a8661f", "#f2b64a")], "hunter-mark-iv": [22, 4, ("#a8661f", "#fff27a")],
         "hunter-mark-v": [24, 4, ("#c0801a", "#ffffff")]}
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
from sheet import export  # noqa: E402

NAME = HERE.name
R, B, (DK, LT) = _V
S = 2 * R + 16
C = S // 2


def mark():
    out = []
    for f in range(4):
        c = Canvas(S, S)
        turn = f * math.pi / (2 * B * 2)
        for k in range(B):                                   # bracket arcs round the target
            a0 = turn + k * math.tau / B
            for t in range(14):
                a = a0 + t * 0.045
                for dr, col in ((0, LT), (1, DK)):
                    c.pixel(int(C + math.cos(a) * (R + dr)), int(C + math.sin(a) * (R + dr)), col)
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):  # four ticks pointing in
            for d in range(R - 6, R - 1):
                c.pixel(C + dx * d, C + dy * d, LT)
        c.outline("#14111c")
        out.append(c)
    return out


ANIM = [("mark", mark(), 6.0, True, {"hitbox": {"shape": "circle", "center": [float(C), float(C)], "active": [0, 3], "radius": float(R + 2), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(float(C), float(C)), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
