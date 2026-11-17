#!/usr/bin/env python3
"""Ground Slam IV — đất lở: cú đập biến thành sóng đất cuộn về một hướng, đá lăn theo.

Cùng dòng Ground Slam (impact nhìn từ trên xuống, không phải Earth Strike).
Bậc IV khác III ở chuyển động: xung kích không còn tròn đều mà là một lưỡi
sóng lệch hẳn sang phải — DNA "đất trượt/lở" của hệ đất, có đá lớn lăn theo.
Neo = tâm. Chạy: gamekit art run ground-slam-iv
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
from slam import frames  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SPEC = {
    "size": 72, "tier": 4, "seed": 41, "wave": 0,
    "crater": (10, 6),
    "cracks": [(160, 0.85, 3), (200, 0.75, 2), (110, 0.5, 2), (250, 0.5, 2)],
    "chips": [
        (-30, 0.5, 0.9, 6, 1, 1), (10, 0.52, 0.95, 7, 2, 1),
        (35, 0.55, 0.85, 5, 1, 2), (-10, 0.55, 0.98, 8, 2, 2),
        (60, 0.55, 0.78, 4, 0, 3), (180, 0.55, 0.72, 5, 1, 3),
    ],
    "puffs": [
        (-25, 0.55, 2, 1), (10, 0.6, 2, 1), (35, 0.55, 1, 2),
        (-45, 0.5, 1, 2), (60, 0.55, 1, 3), (170, 0.55, 0, 3),
        (200, 0.5, 0, 4), (120, 0.5, 1, 4),
    ],
    "gaps": ((30, 52), (150, 170), (240, 260)),
    "gaps2": ((80, 100), (270, 290)),
    "magma": 2,
}
C = SPEC["size"] / 2.0
ANIM = [("burst", frames(SPEC), 14, False,
         {"hitbox": {"shape": "circle", "center": [C, C], "active": [2, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C))
    print("OK", NAME)
