#!/usr/bin/env python3
"""earthquake-rift-v: bậc V của earthquake-rift (bậc I là sprite earthquake-rift). Kế thừa bậc trước và thêm một ý
(lib/tierfx.py: II quầng sáng, III tia lửa, IV vỏ năng lượng, V tia sáng + lõi trắng). Chạy: gamekit art run earthquake-rift-v
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
from tierfx import build
from sheet import export

if __name__ == "__main__":
    build(HERE, "earthquake-rift", 5, "#ffe2a0", "#d08a3a", export, thin=True)
    print("OK", HERE.name)
