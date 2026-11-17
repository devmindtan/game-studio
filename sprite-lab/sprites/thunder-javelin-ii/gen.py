#!/usr/bin/env python3
"""thunder-javelin-ii: bậc II của thunder-javelin (bậc I là sprite thunder-javelin). Kế thừa bậc trước và thêm một ý
(lib/tierfx.py: II quầng sáng, III tia lửa, IV vỏ năng lượng, V tia sáng + lõi trắng). Chạy: gamekit art run thunder-javelin-ii
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
    build(HERE, "thunder-javelin", 2, "#fffbd0", "#7fe8ff", export)
    print("OK", HERE.name)
