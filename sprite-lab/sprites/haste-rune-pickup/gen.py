#!/usr/bin/env python3
"""haste-rune-pickup — Rune tốc độ: buff tạm thời tăng tốc chạy và giảm hồi chiêu. Huy hiệu vàng, tia sét.
Họ vật phẩm buff dùng chung lib/buffitem.py (huy hiệu tròn + biểu tượng), thiết kế lại 2026-11-17.
Neo (9,9) = tâm huy hiệu (khung 18 px). Chạy: gamekit art run haste-rune-pickup
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
from buffitem import build
from sheet import export

NAME = "haste-rune-pickup"
SYMBOL = ['......LLLD', '.....LLMD.', '....LLMD..', '...LLMD...', '..LLLLLLMD', '..DDLLMMD.', '....LMMD..', '...LMD....', '..LMD.....', '.LD.......']
PAL = {'L': '#fffbe0', 'M': '#ffd04a', 'D': '#6b3e08'}
RIM = ('#ffe98a', '#d9961f', '#7a4a0c')   # light, mid, dark
CORE = "#33240c"

if __name__ == "__main__":
    build(HERE, NAME, SYMBOL, PAL, RIM, CORE, export)
    print("OK", NAME)
