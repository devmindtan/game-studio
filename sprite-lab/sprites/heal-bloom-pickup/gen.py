#!/usr/bin/env python3
"""heal-bloom-pickup — Hoa hồi phục: buff tạm thời hồi máu mỗi giây. Huy hiệu xanh lá, dấu cộng.
Họ vật phẩm buff dùng chung lib/buffitem.py (huy hiệu tròn + biểu tượng), thiết kế lại 2026-11-17.
Neo (9,9) = tâm huy hiệu (khung 18 px). Chạy: gamekit art run heal-bloom-pickup
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

NAME = "heal-bloom-pickup"
SYMBOL = ['...LLLM...', '...LLMM...', '...LLMM...', 'LLLLLMMMMD', 'LLMMMMMMMD', 'DDDLMMMDDD', '...LMMD...', '...LMMD...', '...DDDD...']
PAL = {'L': '#f4fff0', 'M': '#7be476', 'D': '#1c5a24'}
RIM = ('#b8f5a0', '#46b84c', '#1f6128')   # light, mid, dark
CORE = "#102c18"

if __name__ == "__main__":
    build(HERE, NAME, SYMBOL, PAL, RIM, CORE, export)
    print("OK", NAME)
