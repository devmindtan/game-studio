#!/usr/bin/env python3
"""status-freeze — trạng thái trên quái (xem lib/statusfx.py). Neo = tâm khung 16 px.
Chạy: gamekit art run status-freeze
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
from statusfx import build
from sheet import export

if __name__ == "__main__":
    build(HERE, HERE.name, "freeze", export)
    print("OK", HERE.name)
