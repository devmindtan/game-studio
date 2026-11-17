#!/usr/bin/env python3
"""arcane-empower-pickup — Ngọc sức mạnh: buff tạm thời tăng sát thương. Huy hiệu tím, thanh kiếm hướng lên.
Họ vật phẩm buff dùng chung lib/buffitem.py (huy hiệu tròn + biểu tượng), thiết kế lại 2026-11-17.
Neo (9,9) = tâm huy hiệu (khung 18 px). Chạy: gamekit art run arcane-empower-pickup
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

NAME = "arcane-empower-pickup"
SYMBOL = ['....LL....', '....LM....', '....LM....', '....LM....', '....LM....', '..GGLMGG..', '.GGGGGGGG.', '....GG....', '....GG....', '....HH....']
PAL = {'L': '#ffffff', 'M': '#efe2ff', 'G': '#d9a6ff', 'H': '#f7d36b'}
RIM = ('#d6a8ff', '#9356dc', '#46247e')   # light, mid, dark
CORE = "#21143a"

if __name__ == "__main__":
    build(HERE, NAME, SYMBOL, PAL, RIM, CORE, export)
    print("OK", NAME)
