#!/usr/bin/env python3
"""Generator cho sprite "staff-strike": đòn đánh thường cận chiến bằng gậy phép (pháp sư/cận chiến phép).

Khung 32x32, neo (16, 16) = điểm xoay (tay cầm gậy). Cú đập/quét ngắn với tia năng lượng ở đầu gậy,
tầm ~11 px phía trước.

Animation (mỗi hướng 4 frame, một lần): giơ → đập/đánh → dư chấn năng lượng → tan.
  strike_right / strike_left / strike_up / strike_down.
Hitbox: rect theo vùng tác động thực tế (frame 1..2).
Chạy: gamekit art run staff-strike
"""

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

NAME = "staff-strike"
SIZE = 32
PIVOT = (16.0, 16.0)
ANCHOR = PIVOT

CORE = "#e8f7ff"
GLOW = "#7fd4ff"
MAGIC = "#45a8ff"
DEEP = "#2a5fb8"
SPARK = "#ffffff"
FADE = "#5a8ab080"

A_START, A_END = -35.0, 35.0
R_OUT = 11.0


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
    if i == 0:  # wind-up: small orb forming
        c.ellipse(cx + 4, cy - 2, cx + 7, cy + 1, DEEP)
        c.pixel(cx + 5, cy - 1, GLOW)
    elif i == 1:  # strike: arc burst forward
        crescent(c, A_START, A_END, R_OUT + 1, 5.5, FADE, taper=True)
        crescent(c, A_START, A_END, R_OUT, 3.8, DEEP)
        crescent(c, A_START + 5, A_END - 5, R_OUT, 2.2, MAGIC)
        crescent(c, -10, 10, R_OUT, 1.2, GLOW)
        c.pixel(cx + R_OUT - 1, cy, SPARK)
    elif i == 2:  # aftershock
        crescent(c, -15, A_END, R_OUT, 2.5, MAGIC)
        crescent(c, 0, A_END - 5, R_OUT, 1.2, GLOW)
        for a in (-20, 0, 20):
            r = R_OUT - 2
            c.pixel(round(cx + math.cos(math.radians(a)) * r - 0.5),
                    round(cy + math.sin(math.radians(a)) * r - 0.5), CORE)
    else:  # fade
        for a in (-10, 10, 25):
            r = R_OUT - 1
            c.pixel(round(cx + math.cos(math.radians(a)) * r - 0.5),
                    round(cy + math.sin(math.radians(a)) * r - 0.5), FADE)
    return c


def turned(frames, op):
    out = []
    for f in frames:
        c = Canvas(SIZE, SIZE)
        c.img = f.img.transpose(op) if op is not None else f.img.copy()
        out.append(c)
    return out


RIGHT = [frame(i) for i in range(4)]
DURATIONS = [60.0, 60.0, 60.0, 50.0]
HIT = {"shape": "rect", "center": list(PIVOT), "active": [1, 2]}
ANIMATIONS = [
    ("strike_right", RIGHT, 14, False, {"durations_ms": DURATIONS, "hitbox": dict(HIT)}),
    ("strike_left", turned(RIGHT, Image.Transpose.FLIP_LEFT_RIGHT), 14, False,
     {"durations_ms": DURATIONS, "hitbox": dict(HIT)}),
    ("strike_up", turned(RIGHT, Image.Transpose.ROTATE_90), 14, False,
     {"durations_ms": DURATIONS, "hitbox": dict(HIT)}),
    ("strike_down", turned(RIGHT, Image.Transpose.ROTATE_270), 14, False,
     {"durations_ms": DURATIONS, "hitbox": dict(HIT)}),
]


if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print(f"OK {NAME}")
