#!/usr/bin/env python3
"""aura-heal — Hoa hồi phục: dấu cộng xanh bay lên ở hai bên thân (vùng: x 11 và 37, y 38..18,
nằm trong bong bóng khiên). Khung 48 px, neo chân (24,44) như nhân vật. Chạy: gamekit art run aura-heal
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

LIGHT = "#eaffdc"; GREEN = "#6fd66a"; DARK = "#2f8f3a"


def plus(c, x, y, big):
    cols = (LIGHT, GREEN) if big else (GREEN, DARK)
    px(c, x, y, cols[0])
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        px(c, x + dx, y + dy, cols[1])


def frame(i):
    c = canvas()
    # three plus signs per side at staggered heights, rising 2.5 px a frame
    for side, x in ((0, 11), (1, 37)):
        for k in range(3):
            phase = (i + k * 8 / 3 + side * 4) % 8
            y = 38 - phase * 2.6
            plus(c, x + (1 if (k + side) % 2 else 0), y, phase < 5)
    return c


ANIM = [("loop", [frame(i) for i in range(8)], 10, True, {})]
if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print("OK", NAME)
