#!/usr/bin/env python3
"""arcane-empower-pickup — cục sáng tăng sát thương (buff roadmap Bách Ải).
Quả cầu tím có lõi trắng; idle nổi/lấp lánh, collect flash rồi vỡ thành đốm sáng.
Khác bản hiệu ứng trạng thái arcane-empower (cast/loop/release) — đây là item nhặt được.
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
    "...pppppp...",
    "..pppppppp..",
    ".pppppppppp.",
    ".pppwwwwppp.",
    "pppwwwlwwppp",
    "pppwwwlwwppp",
    ".pppwwwwppp.",
    ".pppppppppp.",
    "..pppppppp..",
    "...pppppp...",
]
PAL = {"p": "#8b5cf6", "l": "#d8c4ff", "w": "#ffffff"}

if __name__ == "__main__":
    build(HERE, NAME, ROWS, PAL, "#e0d0ff", export)
    print("OK", NAME)
