#!/usr/bin/env python3
"""scorch: vùng đất cháy (vòng lặp 6 frame) mà game vẽ dưới quái trong suốt thời gian một vùng thiêu đốt
còn hiệu lực (zone "burn" của skill, ví dụ hố thiên thạch; người dùng 2026-11-18). Vết nứt dung nham lập loè,
lưỡi lửa nhỏ, tàn lửa bay lên. Mật độ gấp đôi ("px_scale": 0.5); game co theo bán kính vùng.
Chạy: gamekit art run scorch
"""
import json
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
import firefx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = 96
ANIM = [("loop", firefx.scorch(SIZE, 3), 8, True, {})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(SIZE / 2, SIZE / 2), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
