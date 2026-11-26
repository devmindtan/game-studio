#!/usr/bin/env python3
"""Family generator for Lốc dao (blade-orbit-i .. blade-orbit-v, design/rogue-kits.md, 2026-11-26): daggers circling
the hero (looping "spin", drawn round the hero's centre). Each tier: more daggers, a wider ring, a violet then gold
trail. Chạy: gamekit art run blade-orbit-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
# tier: [daggers, ring radius (px at double density), trail colour or None]
TIERS = {"blade-orbit-i": [3, 34, None], "blade-orbit-ii": [4, 36, "#7a3ab8"], "blade-orbit-iii": [4, 38, "#c38df5"],
         "blade-orbit-iv": [5, 40, "#e0b8ff"], "blade-orbit-v": [6, 42, "#fff4b0"]}
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
import roguefx  # noqa: E402
from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
N, R, TRAIL = _V
S = 2 * R + 24
C = S // 2


def spin():
    out = []
    for f in range(8):
        c = Canvas(S, S)
        turn = f * math.tau / 8 / N * 2
        for k in range(N):
            a = turn + k * math.tau / N
            if TRAIL:
                for t in range(1, 8):
                    b = a - t * 0.06
                    c.pixel(int(C + math.cos(b) * R), int(C + math.sin(b) * R), TRAIL)
            roguefx._dagger(c, C + math.cos(a) * R, C + math.sin(a) * R, a + math.pi / 2, L=14)
        c.outline(roguefx.OUT)
        out.append(c)
    return out


ANIM = [("spin", spin(), 14.0, True,
         {"hitbox": {"shape": "circle", "center": [float(C), float(C)], "active": [0, 7], "radius": float(R + 8), "inner": float(R - 10)}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(float(C), float(C)), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
