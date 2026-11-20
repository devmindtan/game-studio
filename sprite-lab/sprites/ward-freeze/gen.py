#!/usr/bin/env python3
"""ward-freeze — hiệu ứng riêng cho Băng ấn (kỹ năng trang bị).

Vẽ bằng sprite-lab/lib/itemprocfx.py: 12 frame, khung/neo như nhân vật,
animation "cast". Chạy: gamekit art run ward-freeze
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
import itemprocfx  # noqa: E402
from sheet import export  # noqa: E402

if __name__ == "__main__":
    itemprocfx.build(HERE, HERE.name, "freeze", export)
    print("OK", HERE.name)
