#!/usr/bin/env python3
"""haste-rune-pickup — rune tăng tốc (buff haste trong roadmap Bách Ải).
Tia sét vàng có lõi trắng; idle nổi/lấp lánh, collect flash rồi vỡ thành đốm sáng.
Neo (8,8) = tâm item. Chạy: gamekit art run haste-rune-pickup
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

NAME = "haste-rune-pickup"
ROWS = [
    "......yyyy..",
    ".....yyyyy..",
    "....yyyyyy..",
    "...yyyyyyy..",
    "..yyyywwyy..",
    "...yyywwyy..",
    "....yyywy...",
    "...yyyyy....",
    "..yyyy......",
    ".yyyy.......",
]
PAL = {"y": "#f2c14e", "w": "#fff2a8"}

if __name__ == "__main__":
    build(HERE, NAME, ROWS, PAL, "#fff2a8", export)
    print("OK", NAME)
