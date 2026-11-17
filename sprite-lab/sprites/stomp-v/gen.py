#!/usr/bin/env python3
"""stomp-v — Dậm đất bậc v: sóng xung kích lan ra quanh người chơi (giữa để trống).
Thiết kế chung ở lib/stomp.py; mỗi bậc kế thừa bậc trước. Neo = tâm = tâm thân nhân vật.
Chạy: gamekit art run stomp-v
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
from stomp import build
from sheet import export

if __name__ == "__main__":
    build(HERE, HERE.name, 5, 88, export)
    print("OK", HERE.name)
