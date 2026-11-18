#!/usr/bin/env python3
"""aura-shield — Khiên từ (magnetic shield), the pickup-item buff.

User 2026-11-18: it read as an ice bubble sitting behind the hero. Reworked as
a magnetic field that wraps him: two poles, curved field lines and iron filings
in violet/gold (not cyan ice), a brighter near-side arc and faint glass streaks
in front of the body. Same 48x48 frame, feet anchor (24,44), bubble zone and
the "loop" animation the game draws. 4 form + 8 loop frames.
"""
import math
import sys
from pathlib import Path


def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from heroaura import canvas, px, ellipse_points, BUBBLE, ANCHOR  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name

OUT = "#3a1a5a"        # dark violet edge: keeps it off the green grass
RIM = "#e6b8ff"        # pale violet light
RIM2 = "#a86fe0"       # magnetic violet
FILL = "#b06cff16"     # almost clear violet interior
FIELD = "#c9a6ff70"    # field lines
FILING = "#ffe1a0"     # iron filings caught in the field
POLE_N = "#ff6a6a"     # north pole, warm red
POLE_S = "#ffd36a"     # south pole, gold
HOT = "#ffffff"

TAU = math.tau


def _h01(x, y, salt):
    h = (int(x) * 374761393 + int(y) * 668265263 + int(salt) * 1103515245) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _fill(c, cx, cy, rx, ry):
    for y in range(int(cy - ry) + 1, int(cy + ry)):
        dy = (y - cy) / ry
        half = rx * math.sqrt(max(0.0, 1 - dy * dy)) - 1.5
        for x in range(int(round(cx - half)), int(round(cx + half)) + 1):
            px(c, x, y, FILL)


def _field(c, cx, cy, rx, ry, i):
    """Curved force lines from pole to pole, above and below the hero."""
    xa, xb = cx - rx * 0.78, cx + rx * 0.78
    for k in range(3):
        for side in (-1, 1):          # far side / near side of the field
            h = ry * (0.32 + 0.20 * k)
            for s in range(25):
                t = s / 24.0
                x = xa + (xb - xa) * t
                y = cy + side * math.sin(math.pi * t) * h + (k - 1) * side
                if _h01(x, y, 5 + k + i % 3) < 0.32:
                    continue
                col = FILING if (s + i + k) % 7 == 0 else FIELD
                px(c, x, y, col)
    # a few filings drift poleward each frame
    for j in range(5):
        t = 0.18 + ((i * 2 + j * 5) % 15) / 20.0
        x = xa + (xb - xa) * t
        y = cy + (j - 2) * 5 + int(2 * math.sin(i + j))
        px(c, x, y, FILING if j % 2 else HOT)


def _poles(c, cx, cy, rx, i):
    for x, col in ((cx - rx * 0.78, POLE_N), (cx + rx * 0.78, POLE_S)):
        x, y = int(x), int(cy)
        px(c, x - 1, y, OUT)
        px(c, x + 1, y, OUT)
        px(c, x, y - 1, col)
        px(c, x, y + 1, col)
        px(c, x, y, HOT if i % 2 == 0 else col)


def _front_glass(c, cx, cy):
    """Faint streaks in front of the body: the field encloses, not sits behind."""
    for dx in (-9, -3, 4, 10):
        for y in range(int(cy - 13), int(cy + 9)):
            if _h01(dx, y, 29) < 0.55:
                continue
            px(c, cx + dx, y, FILL if dx % 2 else FIELD)


def frame(i, form=1.0):
    c = canvas()
    cx, cy, rx, ry = BUBBLE
    rx, ry = rx * form, ry * form

    if form >= 1.0:
        _fill(c, cx, cy, rx, ry)
        _field(c, cx, cy, rx, ry, i)
        _poles(c, cx, cy, rx, i)
    else:
        # the poles snap on first, then the field opens around them
        for k in range(6):
            a = k * TAU / 6 + 0.2
            for s in range(2, 5):
                px(c, cx + math.cos(a) * s, cy + math.sin(a) * s,
                   RIM2 if s > 2 else HOT)
        _poles(c, cx, cy, rx * form, i)

    # outer edge, then a second inner ring with gaps gives the shell thickness
    for (x, y), _ in ellipse_points(cx, cy, rx + 1, ry + 1, 240):
        px(c, x, y, OUT)
    for (x, y), a in ellipse_points(cx, cy, rx, ry, 240):
        px(c, x, y, RIM2)
    if form >= 1.0:
        for (x, y), _ in ellipse_points(cx, cy, rx - 2, ry - 2, 220):
            if _h01(x, y, 11 + i % 4) < 0.62:
                continue
            px(c, x, y, RIM)
        # the near (lower) arc is brighter: the bubble passes in front of the hero
        for (x, y), a in ellipse_points(cx, cy, rx + 1, ry + 1, 240):
            if 0.15 < a < math.pi - 0.15:
                px(c, x, y, RIM)
        for k in range(3):
            g = (i / 8.0 + k / 3.0) * TAU
            px(c, cx + math.cos(g) * rx, cy + math.sin(g) * ry, HOT)
        _front_glass(c, cx, cy)
    else:
        px(c, cx, cy, HOT)
        px(c, cx + 1, cy, RIM)
        px(c, cx - 1, cy, RIM)
        px(c, cx, cy + 1, RIM)
    return c


ANIM = [("form", [frame(0, f) for f in (0.40, 0.68, 0.88, 1.08)], 16, False, {}),
        ("loop", [frame(i) for i in range(8)], 10, True, {})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print("OK", NAME)
