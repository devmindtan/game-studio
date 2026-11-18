#!/usr/bin/env python3
"""aura-aegis — Khiên thần hộ của món Thần hộ (giáp ảo).

Riêng với khiên từ của buff item (aura-shield): vàng + xanh, sáu rune xoay trên
một tấm khiên kính. 4 frame hình thành + 8 frame lặp, khung/neo như nhân vật.
Chạy: gamekit art run aura-aegis
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
import wardaura  # noqa: E402
from sheet import export  # noqa: E402

if __name__ == "__main__":
    wardaura.build(HERE, HERE.name, {"motif": "runic", "palette": wardaura.RUNIC}, export)
    print("OK", HERE.name)
