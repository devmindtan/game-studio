#!/usr/bin/env python3
"""Don dap manh cua búa chien (4 huong, song chan + moc nhon, hitbox rect)."""

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

NAME = "war-hammer-strike"
SIZE = 40
PIVOT = (18.0, 20.0)
ANCHOR = PIVOT
CORE = "#ffffff"
EDGE = "#f0f4f8"
STEEL = "#b8c7d9"
DEEP = "#5f7187"
FADE = "#9fb3c890"
WOOD = "#6b4423"
GLOW = "#e8f0ff50"
A_START, A_END = -50.0, 50.0
R_OUT = 15.0


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
    cx, cy = int(PIVOT[0]), int(PIVOT[1])
    if i == 0:
        # bua chien giu cao: can noi tu tay, dau vuong + moc nhon
        c.line(cx + 1, cy - 1, cx + 7, cy - 7, WOOD)
        c.rect(cx + 4, cy - 11, cx + 10, cy - 5, DEEP)
        c.line(cx + 4, cy - 11, cx + 10, cy - 11, EDGE)
        c.line(cx + 2, cy - 9, cx + 5, cy - 8, STEEL)
        c.pixel(cx + 1, cy - 9, CORE)
    elif i == 1:
        # dap manh: dau vuong + moc + tia va
        crescent(c, A_START, A_END, R_OUT + 2, 7.0, GLOW)
        crescent(c, A_START, A_END, R_OUT, 5.0, DEEP)
        c.rect(cx + R_OUT - 6, cy - 5, cx + R_OUT, cy + 4, STEEL)
        c.line(cx + R_OUT - 6, cy - 5, cx + R_OUT, cy - 5, EDGE)
        c.line(cx + R_OUT - 6, cy + 4, cx + R_OUT, cy + 4, DEEP)
        c.line(cx + R_OUT - 1, cy, cx + R_OUT + 3, cy, CORE)
        c.pixel(cx + R_OUT + 4, cy, EDGE)
        for a in (-40, -15, 15, 40):
            x, y = polar(a, R_OUT + 1)
            p(c, x, y, EDGE)
    elif i == 2:
        # hai vong song chan + manh vu
        crescent(c, A_START - 8, A_END + 8, R_OUT + 3, 3.5, FADE)
        crescent(c, A_START, A_END, R_OUT + 1, 2.0, STEEL)
        x, y = polar(0, R_OUT + 2)
        for dx, dy in ((0, -3), (0, 3), (-3, 0), (3, 0), (-2, -2), (2, 2)):
            p(c, x + dx, y + dy, CORE)
        for a in (-50, 50):
            ax, ay = polar(a, R_OUT + 2)
            p(c, ax, ay, DEEP)
    else:
        for a in (-35, -10, 15, 40):
            x, y = polar(a, R_OUT + 1)
            p(c, x, y, FADE)
        x, y = polar(0, R_OUT + 4)
        p(c, x, y, DEEP)
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


RIGHT = [frame(i) for i in range(4)]
DUR = [75.0, 65.0, 60.0, 50.0]
HIT = {"shape": "rect", "center": list(PIVOT), "active": [1, 2]}
ANIMATIONS = [
    ("strike_right", RIGHT, 13, False, {"durations_ms": DUR, "hitbox": dict(HIT)}),
    ("strike_left", turned(RIGHT, Image.Transpose.FLIP_LEFT_RIGHT), 13, False,
     {"durations_ms": DUR, "hitbox": dict(HIT)}),
    ("strike_up", turned(RIGHT, Image.Transpose.ROTATE_90), 13, False,
     {"durations_ms": DUR, "hitbox": dict(HIT)}),
    ("strike_down", turned(RIGHT, Image.Transpose.ROTATE_270), 13, False,
     {"durations_ms": DUR, "hitbox": dict(HIT)}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print(f"OK {NAME}")
