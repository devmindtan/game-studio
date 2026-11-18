#!/usr/bin/env python3
"""aura-stoneguard — Bàn thạch của món giáp chân (chặn một lần sát thương).

Riêng với khiên từ và khiên thần hộ: vỏ đá xám nứt đứt đoạn, một hạt sáng duy
nhất ở giữa là số lần chặn còn lại. 4 frame hình thành + 8 frame lặp.
Chạy: gamekit art run aura-stoneguard
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
    wardaura.build(HERE, HERE.name, {"motif": "stone", "palette": wardaura.STONE}, export)
    print("OK", HERE.name)
