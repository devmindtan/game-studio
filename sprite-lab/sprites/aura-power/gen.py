#!/usr/bin/env python3
"""aura-power — Ngọc sức mạnh: ngọn lửa tím trên đầu (vùng: y 1..9, trên đỉnh bong bóng khiên),
hai đốm sáng hai bên. Khung 48 px, neo chân (24,44) như nhân vật. Chạy: gamekit art run aura-power
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

CORE = "#ffffff"; LIGHT = "#e6c8ff"; MID = "#b47cf0"; DARK = "#6a3cb0"

FLAMES = [
    ["...M....", "..MLM...", "..MLLM..", ".MLCLM..", ".MLCCLM.", "MMLCCLMM", ".DMLLMD.", "..DDDD.."],
    ["....M...", "...MLM..", "..MLLM..", "..MLCLM.", ".MLCCLM.", "MMLCCLMM", ".DMLLMD.", "..DDDD.."],
]
PAL = {"M": MID, "L": LIGHT, "C": CORE, "D": DARK}


def frame(i):
    c = canvas()
    rows = FLAMES[(i // 2) % 2]
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != ".":
                px(c, 20 + x, 1 + y, PAL[ch])
    for side in (-1, 1):
        y = 5 + (1 if (i + (side > 0)) % 4 < 2 else 0)
        px(c, 24 + side * 8, y, LIGHT if i % 2 else MID)
    return c


ANIM = [("loop", [frame(i) for i in range(8)], 10, True, {})]
if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print("OK", NAME)
