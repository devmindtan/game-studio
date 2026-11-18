#!/usr/bin/env python3
"""war-hammer-strike-ii — Búa thần, bậc 2.

Chuẩn fx_craft (2026-11-18): lib/hammerfx.py, mật độ gấp đôi ("px_scale": 0.5), 12 frame,
3 frame rơi -> trúng -> đọng lại -> tan; 4 hướng (strike_right/left/up/down).
Kế thừa: búa vàng + chớp + vòng xung kích + tia lửa của bậc trước, thêm vòng xung kích thứ hai chạy chậm hơn.
Chạy: gamekit art run war-hammer-strike-ii
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
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import hammerfx  # noqa: E402
from sheet import export  # noqa: E402

if __name__ == "__main__":
    hammerfx.build(HERE, HERE.name, 2, export)
    print("OK", HERE.name)
