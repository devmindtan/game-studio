#!/usr/bin/env python3
"""health-pickup — cục máu hồi máu rơi từ quái (Bách Ải).
Trái tim đỏ có dấu cộng trắng; idle nổi/lấp lánh, collect flash rồi vỡ thành đốm sáng.
Neo (8,8) = tâm item. Chạy: gamekit art run health-pickup
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

NAME = "health-pickup"
ROWS = [
    "..rrr..rrr..",
    ".rrrrr.rrrrr",
    "rrrrrrrrrrrr",
    "rrrwwwwwrrrr",
    "rrrwwwwwrrrr",
    "rrrwwwwwrrrr",
    ".rrrwwwwwrrr",
    "..rrwwwwrr..",
    "...rrwwrr...",
    "....rrrr....",
    ".....rr.....",
]
PAL = {"r": "#d9364a", "w": "#ffffff"}

if __name__ == "__main__":
    build(HERE, NAME, ROWS, PAL, "#ffd0d0", export)
    print("OK", NAME)
