#!/usr/bin/env python3
"""magnetic-shield-pickup — Khiên từ: buff tạm thời chặn mọi sát thương và hút vật phẩm từ xa. Huy hiệu xanh dương, tấm khiên.
Họ vật phẩm buff dùng chung lib/buffitem.py (huy hiệu tròn + biểu tượng), thiết kế lại 2026-11-17.
Neo (9,9) = tâm huy hiệu (khung 18 px). Chạy: gamekit art run magnetic-shield-pickup
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

NAME = "magnetic-shield-pickup"
SYMBOL = ['.LLLLLMMM.', 'LLLLLMMMMD', 'LLLLMMMMMD', 'LLLLMMMMMD', 'LLLMMMMMMD', '.LLMMMMMD.', '.LLMMMMMD.', '..LMMMMD..', '...LMMD...', '....DD....']
PAL = {'L': '#f0fbff', 'M': '#7fcaff', 'D': '#123a78'}
RIM = ('#a8e4ff', '#3a8fe4', '#1a4890')   # light, mid, dark
CORE = "#0e203e"

if __name__ == "__main__":
    build(HERE, NAME, SYMBOL, PAL, RIM, CORE, export)
    print("OK", NAME)
