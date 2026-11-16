#!/usr/bin/env python3
"""Vung chém nang cua rìu (don danh co ban, 4 huong). Vung cung quet rong, hitbox arc."""

import math
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

from PIL import Image  # noqa: E402
from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = "axe-chop"
SIZE = 48
PIVOT = (20.0, 26.0)
ANCHOR = PIVOT
CORE = "#ffffff"
EDGE = "#e8f4ff"
STEEL = "#b8c7d9"
DEEP = "#5f7187"
WOOD = "#8a5a2e"
FADE = "#8fa4bb90"
GLOW = "#cfe6ff50"
A_START, A_END = -75.0, 80.0
R_OUT = 20.0


def p(c, x, y, col):
    c.pixel(x, y, col)


def crescent(c, a0, a1, r_out, thick_max, col, taper=True):
    cx, cy = PIVOT
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            a = math.degrees(math.atan2(dy, dx))
            if not (a0 <= a <= a1):
                continue
            u = (a - a0) / max(1e-6, a1 - a0)
            th = thick_max * (math.sin(math.pi * u) if taper else 1.0)
            if r_out - max(1.0, th) <= d <= r_out:
                c.pixel(x, y, col)



def frame(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        crescent(c, A_START, A_START + 28, R_OUT, 2.0, STEEL)
        for a in (A_START + 10, A_START + 22):
            x, y = polar(a, R_OUT - 2)
            p(c, x, y, WOOD)
    elif i == 1:
        crescent(c, A_START, 12, R_OUT + 1, 7.0, GLOW)
        crescent(c, A_START, 12, R_OUT, 5.0, DEEP)
        crescent(c, A_START, 12, R_OUT, 3.0, STEEL)
        crescent(c, A_START + 6, 4, R_OUT, 1.4, EDGE)
    elif i == 2:
        crescent(c, A_START, A_END, R_OUT + 1, 8.0, GLOW)
        crescent(c, A_START, A_END, R_OUT, 6.0, DEEP)
        crescent(c, A_START, A_END, R_OUT, 4.0, STEEL)
        crescent(c, A_START + 12, A_END - 12, R_OUT, 2.0, EDGE)
        crescent(c, A_START + 18, A_END - 18, R_OUT - 3, 1.2, CORE)
        x, y = polar(A_END - 8, R_OUT - 3)
        p(c, x, y, EDGE)
    elif i == 3:
        crescent(c, -10, A_END, R_OUT, 3.5, FADE)
        crescent(c, 12, A_END, R_OUT, 1.6, STEEL)
    else:
        for a in (18, 40, 62):
            x, y = polar(a, R_OUT - 2)
            p(c, x, y, FADE)
        x, y = polar(A_END, R_OUT)
        p(c, x, y, EDGE)
    return c


def turned(frames, op):
    out = []
    for f in frames:
        c = Canvas(SIZE, SIZE)
        c.img = f.img.transpose(op) if op is not None else f.img.copy()
        out.append(c)
    return out


def polar(a, r):
    cx, cy = PIVOT
    return (round(cx + math.cos(math.radians(a)) * r - 0.5),
            round(cy + math.sin(math.radians(a)) * r - 0.5))


RIGHT = [frame(i) for i in range(5)]
DUR = [60.0, 50.0, 70.0, 70.0, 60.0]
HIT = {"shape": "arc", "center": list(PIVOT), "active": [1, 2]}
ANIMATIONS = [
    ("chop_right", RIGHT, 14, False, {"durations_ms": DUR, "hitbox": dict(HIT)}),
    ("chop_left", turned(RIGHT, Image.Transpose.FLIP_LEFT_RIGHT), 14, False,
     {"durations_ms": DUR, "hitbox": dict(HIT)}),
    ("chop_up", turned(RIGHT, Image.Transpose.ROTATE_90), 14, False,
     {"durations_ms": DUR, "hitbox": dict(HIT)}),
    ("chop_down", turned(RIGHT, Image.Transpose.ROTATE_270), 14, False,
     {"durations_ms": DUR, "hitbox": dict(HIT)}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print(f"OK {NAME}")
