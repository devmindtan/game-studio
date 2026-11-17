#!/usr/bin/env python3
"""arcane-empower-pickup — tinh thể phép (buff power trong roadmap Bách Ải).
Tinh thể lục giác tím, mặt sáng ở trên trái, lõi trắng — khác viên ngọc kinh
nghiệm bốn cánh màu xanh và khác quả cầu rỗng cũ (trông như cái vòng).
Neo (8,8) = tâm item. Chạy: gamekit art run arcane-empower-pickup
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

NAME = "arcane-empower-pickup"
ROWS = [
    "..LLLLLL..",
    ".LLWWMMML.",
    "LLWWMMMMDD",
    "LLWMMMMMDD",
    "LMMMMMMMDD",
    "LMMMMMMMDD",
    "LMMMMMMMDD",
    ".LMMMMMDD.",
    "..LMMMDD..",
    "..LMMMDD..",
    "...LMDD...",
    "...LMDD...",
    "....LD....",
]
PAL = {"L": "#d9a6ff", "M": "#9a5cf0", "D": "#5c2ea0", "W": "#fff3ff"}

if __name__ == "__main__":
    build(HERE, NAME, ROWS, PAL, "#e6c2ff", export)
    print("OK", NAME)
