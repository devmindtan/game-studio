#!/usr/bin/env python3
"""aura-haste — Rune tốc độ: vòng vàng dẹt xoay dưới chân + vệt gió hai bên (vùng: chân, y 45..47).
Khung 48 px, neo chân (24,44) như nhân vật. Chạy: gamekit art run aura-haste
"""
import math, sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from heroaura import canvas, px, ellipse_points, BUBBLE, ANCHOR
from sheet import export

NAME = HERE.name

GOLD = "#ffd04a"; LIGHT = "#fff2a8"; DARK = "#b06d16"


def frame(i):
    c = canvas()
    cx, cy, rx, ry = 24.0, 45.5, 14.0, 2.0
    for (x, y), a in ellipse_points(cx, cy, rx, ry, 120):
        # dashed ring turning: 4 lit dashes
        k = (a / math.tau * 16 + i) % 4
        px(c, x, y, LIGHT if k < 1 else (GOLD if k < 2.2 else DARK))
    # wind streaks at both sides of the feet, sliding outward
    for side in (-1, 1):
        for j in range(2):
            off = 15 + ((i * 2 + j * 5) % 8)
            y = 43 - j * 2
            for t in range(3 - j):
                px(c, cx + side * (off + t), y, LIGHT if t == 0 else GOLD)
    return c


ANIM = [("loop", [frame(i) for i in range(8)], 12, True, {})]
if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print("OK", NAME)
