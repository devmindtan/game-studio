#!/usr/bin/env python3
"""aura-shield — Khiên từ: bong bóng elip bao trọn nhân vật (vùng: quanh cả người).
Viền sáng 1 px + viền trong, lõi gần trong suốt để vẫn thấy nhân vật, vệt sáng trên-trái,
ba điểm sáng chạy quanh viền; lục giác mờ trên mặt bong bóng. Khung 48 px, neo chân (24,44)
như nhân vật. Chạy: gamekit art run aura-shield
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

RIM = "#c8f4ff"; RIM2 = "#4fb0f0"; FILL = "#6fc3ff22"; HEX = "#9fdcff40"; WHITE = "#ffffff"


def frame(i, form=1.0):
    c = canvas()
    cx, cy, rx, ry = BUBBLE
    rx, ry = rx * form, ry * form
    if form >= 1.0:
        for (x, y), a in ellipse_points(cx, cy, rx - 1, ry - 1, 220):
            pass
        # faint fill: scanlines inside the ellipse
        for y in range(int(cy - ry) + 1, int(cy + ry)):
            dy = (y - cy) / ry
            half = rx * math.sqrt(max(0.0, 1 - dy * dy)) - 1.5
            for x in range(int(round(cx - half)), int(round(cx + half)) + 1):
                px(c, x, y, FILL)
        # hex facets: a few short lines on the surface, slowly turning
        for k in range(6):
            a = k * math.pi / 3 + i * 0.08
            x0, y0 = cx + math.cos(a) * rx * 0.62, cy + math.sin(a) * ry * 0.62
            x1, y1 = cx + math.cos(a + math.pi / 3) * rx * 0.62, cy + math.sin(a + math.pi / 3) * ry * 0.62
            for t in range(0, 9):
                if (t + i) % 3 == 0:
                    px(c, x0 + (x1 - x0) * t / 8, y0 + (y1 - y0) * t / 8, HEX)
    pts = ellipse_points(cx, cy, rx, ry, 240)
    for (x, y), a in ellipse_points(cx, cy, rx - 1, ry - 1, 220):
        px(c, x, y, RIM2)
    for (x, y), a in pts:
        px(c, x, y, RIM)
    if form >= 1.0:
        # highlight arc top-left
        for (x, y), a in pts:
            if 3.6 < a < 4.3:
                px(c, x + 2, y + 1, WHITE)
        # three glints running round the rim
        for k in range(3):
            g = (i / 8.0 + k / 3.0) * math.tau
            px(c, cx + math.cos(g) * rx, cy + math.sin(g) * ry, WHITE)
    return c


ANIM = [("form", [frame(0, f) for f in (0.55, 0.75, 0.9, 1.05)], 16, False, {}),
        ("loop", [frame(i) for i in range(8)], 10, True, {})]
if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print("OK", NAME)
