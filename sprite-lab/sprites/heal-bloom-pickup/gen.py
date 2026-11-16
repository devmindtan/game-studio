#!/usr/bin/env python3
"""heal-bloom-pickup — chồi hồi phục (buff roadmap Bách Ải).
Dấu cộng xanh có lõi trắng; idle nổi/lấp lánh, collect flash rồi vỡ thành đốm sáng.
Khác bản hiệu ứng trạng thái heal-bloom — đây là item nhặt được.
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
    "....gggg....",
    "....gwwg....",
    "ggggwwwwgggg",
    "gggwwwwwwggg",
    "gggwwwwwwggg",
    "ggggwwwwgggg",
    "....gwwg....",
    "....gggg....",
]
PAL = {"g": "#6ee06e", "w": "#d9ffe0"}

if __name__ == "__main__":
    build(HERE, NAME, ROWS, PAL, "#d9ffe0", export)
    print("OK", NAME)
