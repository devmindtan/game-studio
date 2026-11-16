#!/usr/bin/env python3
"""magnetic-shield-pickup — khiên nam châm (buff roadmap Bách Ải).
Khiên xanh có lõi trắng; idle nổi/lấp lánh, collect flash rồi vỡ thành đốm sáng.
Khác bản hiệu ứng trạng thái magnetic-shield — đây là item nhặt được.
Neo (8,8) = tâm item. Chạy: gamekit art run magnetic-shield-pickup
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

NAME = "magnetic-shield-pickup"
ROWS = [
    "....bbbb....",
    "..bbbbbbbb..",
    ".bbbbbbbbbb.",
    ".bbwwwwwwbb.",
    ".bbbwwwwbbb.",
    "..bbbwwbbb..",
    "...bbbbbb...",
    "....bbbb....",
    ".....bb.....",
]
PAL = {"b": "#4fa3e0", "w": "#dff6ff"}

if __name__ == "__main__":
    build(HERE, NAME, ROWS, PAL, "#dff6ff", export)
    print("OK", NAME)
