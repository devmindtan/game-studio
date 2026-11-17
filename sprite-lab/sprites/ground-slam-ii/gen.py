#!/usr/bin/env python3
"""Ground Slam II — cú đập làm mặt đất nứt dài: một khe chính + nhánh phụ, hai vòng xung kích.

Cùng dòng Ground Slam (impact nhìn từ trên xuống, không phải Earth Strike).
Bậc II khác I ở silhouette: khe nứt chạy xa về một phía, đá trồi dọc khe,
vòng xung kích kép. Neo = tâm. Chạy: gamekit art run ground-slam-ii
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
    "size": 56, "tier": 2, "seed": 23,
    "crater": (8, 4),
    "cracks": [(200, 0.95, 3), (15, 0.65, 2), (110, 0.55, 2), (300, 0.5, 2)],
    "chips": [
        (190, 0.45, 0.78, 6, 1, 1), (210, 0.46, 0.76, 7, 2, 1),
        (10, 0.46, 0.8, 6, 1, 2), (110, 0.48, 0.72, 6, 1, 3),
        (290, 0.5, 0.7, 5, 2, 4),
    ],
    "puffs": [
        (190, 0.58, 1, 1), (20, 0.58, 1, 2), (110, 0.55, 0, 3),
    ],
    "gaps": ((25, 45), (150, 165), (250, 265)),
    "gaps2": ((70, 95), (210, 225)),
    "magma": 1,
}
C = SPEC["size"] / 2.0
ANIM = [("burst", frames(SPEC), 14, False,
         {"hitbox": {"shape": "circle", "center": [C, C], "active": [2, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C))
    print("OK", NAME)
