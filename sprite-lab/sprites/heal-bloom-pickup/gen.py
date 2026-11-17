#!/usr/bin/env python3
"""heal-bloom-pickup — nụ hoa hồi máu (buff heal-over-time trong roadmap Bách Ải).
Nụ hồng ba sắc trên đài xanh, có lá và cọng — đọc là "nở" chứ không phải dấu cộng
như health-pickup. Idle nổi/lấp lánh, collect flash rồi vỡ thành đốm sáng.
Neo (8,8) = tâm item. Chạy: gamekit art run heal-bloom-pickup
"""
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
from itemfx import build
from sheet import export

NAME = "heal-bloom-pickup"
ROWS = [
    "....PPP....",
    "...PPPPP...",
    "...PWWPP...",
    "...PPPPP...",
    "....PPP....",
    "....GGG....",
    "...GGGGG...",
    "..LGGGGGL..",
    ".LLL...LLL.",
    "..L.....L..",
    ".....S.....",
    ".....S.....",
    ".....S.....",
]
PAL = {
    "P": "#e0679b", "W": "#ffd3e6",
    "G": "#3f8f4a", "L": "#8fe06a", "S": "#2c6a38",
}

if __name__ == "__main__":
    build(HERE, NAME, ROWS, PAL, "#ffd3e6", export)
    print("OK", NAME)
