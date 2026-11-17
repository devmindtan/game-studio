#!/usr/bin/env python3
"""Ground Slam I — cú đập đất cơ bản: hố nhỏ nứt, một vòng xung kích gãy, vài mảnh đá văng.

Cùng dòng Ground Slam (impact nhìn từ trên xuống, không phải Earth Strike):
điểm va chạm → hố nứt → sóng bụi gãy → đá văng → lắng thành hố và sỏi.
Bậc I là bản gọn nhất; II nứt dài, III khối đất trồi, IV đất lở, V sụp caldera.
Neo = tâm (điểm cast). Chạy: gamekit art run ground-slam-i
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
    "size": 48, "tier": 1, "seed": 11,
    "crater": (7, 4),
    "cracks": [(165, 0.6, 2), (20, 0.5, 2), (250, 0.45, 2)],
    "chips": [
        (200, 0.62, 0.8, 4, 1, 1), (340, 0.64, 0.78, 3, 1, 1),
        (120, 0.66, 0.76, 4, 0, 2),
    ],
    "puffs": [
        (200, 0.58, 0, 1), (340, 0.58, 0, 2),
    ],
    "gaps": ((35, 52), (205, 220)),
    "gaps2": ((120, 140), (260, 280)),
    "magma": 0,
}
C = SPEC["size"] / 2.0
ANIM = [("burst", frames(SPEC), 14, False,
         {"hitbox": {"shape": "circle", "center": [C, C], "active": [2, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C))
    print("OK", NAME)
