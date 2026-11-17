#!/usr/bin/env python3
"""magnetic-shield-pickup — nam châm hút vật phẩm (buff magnetic trong Bách Ải).
Nam châm móng ngựa: thân đỏ chữ U, hai đầu cực bạc ở trên. Miệng chữ U hở và
đáy cong kín nên nhìn 1x vẫn ra "nam châm" (khác khiên xanh cũ, vốn giống khiên chung).
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
    ".SS....SS.",
    ".ST....ST.",
    ".RL....RD.",
    ".RL....RD.",
    ".RL....RD.",
    ".RL....RD.",
    ".RL....RD.",
    ".RL....RD.",
    ".RLLLLLDD.",
    "..RLLLDD..",
    "...RLDD...",
]
PAL = {
    "S": "#eef3fa", "T": "#a9b8cf",
    "R": "#d63a3a", "L": "#f27a7a", "D": "#8f2020",
}

if __name__ == "__main__":
    build(HERE, NAME, ROWS, PAL, "#9fd8ff", export)
    print("OK", NAME)
