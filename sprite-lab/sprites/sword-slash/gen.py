#!/usr/bin/env python3
"""Generator cho sprite "sword-slash": vệt chém của kiếm ngắn (đòn đánh mặc định của kiếm sĩ, Bách Ải).

Khung 48x48, neo (24, 24) = điểm xoay (vai/tay cầm kiếm). Vệt là một lưỡi liềm hẹp sát người, bán kính
ngoài ~20 px = tay + lưỡi kiếm 10 px của swordsman, quét từ trên-trước xuống dưới-trước (~130 độ).
Không phải sóng chém bay xa (đó là cleave-wave, dành cho nâng cấp sau).

Animation (mỗi hướng 5 frame, một lần): lấy đà (vệt mảnh) → chém (lưỡi liềm đầy) → vệt mờ dần → tan.
  slash_right / slash_left (lật ngang) / slash_up / slash_down (xoay 90 độ quanh neo).
Hitbox: hình quạt quanh neo, đo tự động từ pixel của frame gây sát thương (1..2) bởi spritekit.fit_hitbox;
quầng sáng mờ (alpha < 96) không tính. Chạy: gamekit art run sword-slash
"""

import json
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

NAME = "sword-slash"
D = 2   # double density (px_scale 0.5): same size on screen, finer pixels (review 2026-11-21)
SIZE = 48 * D
PIVOT = (20.0 * D, 26.0 * D)
ANCHOR = PIVOT
CORE = "#ffffff"
EDGE = "#e8f0f6"   # swordsman blade
STEEL = "#9fb3c8"  # swordsman blade shade
FADE = "#9fb3c8b0"
GLOW = "#cfe6ff50"  # haze, alpha < 96: not part of the hit area

A_START, A_END = -70.0, 60.0   # swing from up-front to down-front (0 = right, + = down)
R_OUT = 20.0 * D                # hand + 10 px blade


def crescent(c, a0, a1, r_out, thick_max, col, taper=True):
    """Fill pixels between r_out - thickness(a) and r_out, for angles a0..a1.
    Thickness swells in the middle of the swing (a crescent), thin at both ends."""
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
            if r_out - max(float(D), th) <= d <= r_out:
                c.pixel(x, y, col)


def frame(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:      # anticipation: a thin streak where the blade starts
        crescent(c, A_START, A_START + 30, R_OUT, 1.6 * D, EDGE)
    elif i == 1:    # the cut, front half
        crescent(c, A_START, 10, R_OUT + 1 * D, 6.0 * D, GLOW, taper=True)
        crescent(c, A_START, 10, R_OUT, 4.0 * D, STEEL)
        crescent(c, A_START, 10, R_OUT, 2.4 * D, EDGE)
        crescent(c, A_START + 8, 2, R_OUT, 1.2 * D, CORE)
    elif i == 2:    # full crescent
        crescent(c, A_START, A_END, R_OUT + 1 * D, 7.0 * D, GLOW)
        crescent(c, A_START, A_END, R_OUT, 5.0 * D, STEEL)
        crescent(c, A_START, A_END, R_OUT, 3.2 * D, EDGE)
        crescent(c, A_START + 20, A_END - 10, R_OUT, 1.5 * D, CORE)
    elif i == 3:    # trail fading from the start of the swing
        crescent(c, -15, A_END, R_OUT, 3.0 * D, FADE)
        crescent(c, 10, A_END, R_OUT, 1.4 * D, EDGE)
    else:           # dissolving sparks along the end of the arc
        cx, cy = PIVOT
        for a in (15, 32, 50):
            r = R_OUT - D
            x0, y0 = round(cx + math.cos(math.radians(a)) * r - 0.5), round(cy + math.sin(math.radians(a)) * r - 0.5)
            c.rect(x0, y0, x0 + D - 1, y0 + D - 1, FADE)
    return c


def turned(frames, op):
    out = []
    for f in frames:
        c = Canvas(SIZE, SIZE)
        c.img = f.img.transpose(op) if op is not None else f.img.copy()
        out.append(c)
    return out


RIGHT = [frame(i) for i in range(5)]
DURATIONS = [50.0, 50.0, 70.0, 70.0, 60.0]
HIT = {"shape": "arc", "center": list(PIVOT), "active": [1, 2]}
ANIMATIONS = [
    ("slash_right", RIGHT, 16, False, {"durations_ms": DURATIONS, "hitbox": {**HIT, "dir_deg": 0.0}}),
    ("slash_left", turned(RIGHT, Image.Transpose.FLIP_LEFT_RIGHT), 16, False,
     {"durations_ms": DURATIONS, "hitbox": {**HIT, "dir_deg": 180.0}}),
    ("slash_up", turned(RIGHT, Image.Transpose.ROTATE_90), 16, False,
     {"durations_ms": DURATIONS, "hitbox": {**HIT, "dir_deg": -90.0}}),
    ("slash_down", turned(RIGHT, Image.Transpose.ROTATE_270), 16, False,
     {"durations_ms": DURATIONS, "hitbox": {**HIT, "dir_deg": 90.0}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 1.0 / D
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print(f"OK {NAME}")
