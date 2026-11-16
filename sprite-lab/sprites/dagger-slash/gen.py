#!/usr/bin/env python3
"""Generator cho sprite "dagger-slash": đòn đánh thường của sát thủ (dao găm), chém/thọc nhanh tầm ngắn.

Khung 32x32, neo (16, 16) = điểm xoay (tay cầm dao). Vệt ngắn, bán kính ngoài ~11 px (ngắn hơn kiếm),
quét nhanh phía trước (~90 độ). Đòn cơ bản nhanh gọn, không phải sóng bay xa.

Animation (mỗi hướng 4 frame, một lần): lấy đà mảnh → chém nhanh → vệt mờ → tan.
  slash_right / slash_left / slash_up / slash_down.
Hitbox: hình chữ nhật theo vùng vệt thực tế (đo từ pixel frame gây sát thương 1..2).
Chạy: gamekit art run dagger-slash
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

NAME = "dagger-slash"
SIZE = 32
PIVOT = (16.0, 16.0)
ANCHOR = PIVOT
CORE = "#ffffff"
EDGE = "#d8e4f0"
STEEL = "#9fb3c8"
FADE = "#8aa0b8b0"
GLOW = "#cfe6ff40"

A_START, A_END = -45.0, 45.0
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


def stab_line(c, x0, y0, x1, y1, col, thick=1):
    c.line(x0, y0, x1, y1, col, thick)


def frame(i):
    c = Canvas(SIZE, SIZE)
    cx, cy = int(PIVOT[0]), int(PIVOT[1])
    if i == 0:      # anticipation: short glint
        crescent(c, -20, 10, R_OUT, 1.4, EDGE)
    elif i == 1:    # fast slash/thrust
        crescent(c, A_START, A_END, R_OUT + 1, 5.0, GLOW, taper=True)
        crescent(c, A_START, A_END, R_OUT, 3.2, STEEL)
        crescent(c, A_START + 5, A_END - 5, R_OUT, 1.8, EDGE)
        crescent(c, -10, 10, R_OUT, 1.0, CORE)
    elif i == 2:    # trail fading
        crescent(c, -10, A_END, R_OUT, 2.2, FADE)
        crescent(c, 10, A_END - 5, R_OUT, 1.0, EDGE)
    else:           # dissipate
        for a in (5, 25):
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
DURATIONS = [40.0, 50.0, 50.0, 40.0]
HIT = {"shape": "rect", "center": list(PIVOT), "active": [1, 2]}
ANIMATIONS = [
    ("slash_right", RIGHT, 18, False, {"durations_ms": DURATIONS, "hitbox": dict(HIT)}),
    ("slash_left", turned(RIGHT, Image.Transpose.FLIP_LEFT_RIGHT), 18, False,
     {"durations_ms": DURATIONS, "hitbox": dict(HIT)}),
    ("slash_up", turned(RIGHT, Image.Transpose.ROTATE_90), 18, False,
     {"durations_ms": DURATIONS, "hitbox": dict(HIT)}),
    ("slash_down", turned(RIGHT, Image.Transpose.ROTATE_270), 18, False,
     {"durations_ms": DURATIONS, "hitbox": dict(HIT)}),
]


if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print(f"OK {NAME}")
