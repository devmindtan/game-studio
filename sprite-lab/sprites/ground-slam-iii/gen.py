#!/usr/bin/env python3
"""Ground Slam III — khối đất bị đấm trồi lên: hố vuông vỡ, phiến đất nhô cao, đá văng.

Cùng dòng Ground Slam (impact nhìn từ trên xuống, không phải Earth Strike).
Bậc III khác II ở cấu trúc: hố dạng khối (không tròn), một phiến đất lớn
được đẩy lên giữa hố và vỡ quanh mép — đúng DNA "dịch chuyển khối" của đất.
Neo = tâm. Chạy: gamekit art run ground-slam-iii
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
    "size": 64, "tier": 3, "seed": 37,
    "crater": (10, 6),
    "cracks": [(10, 0.8, 3), (140, 0.7, 2), (230, 0.7, 2), (320, 0.6, 2)],
    "chips": [
        (10, 0.5, 0.82, 7, 2, 1), (140, 0.52, 0.8, 7, 1, 2),
        (230, 0.52, 0.78, 6, 2, 2), (320, 0.54, 0.76, 6, 1, 3),
        (90, 0.55, 0.7, 5, 0, 4), (270, 0.55, 0.72, 5, 1, 4),
    ],
    "puffs": [
        (10, 0.56, 1, 1), (35, 0.6, 1, 1), (140, 0.6, 1, 2),
        (230, 0.58, 1, 2), (320, 0.55, 0, 3), (90, 0.58, 0, 3),
        (180, 0.55, 0, 4),
    ],
    "gaps": ((20, 44), (120, 138), (210, 228), (300, 318)),
    "gaps2": ((60, 80), (240, 260)),
    "magma": 2,
}
C = SPEC["size"] / 2.0
ANIM = [("burst", frames(SPEC), 14, False,
         {"hitbox": {"shape": "circle", "center": [C, C], "active": [2, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C))
    print("OK", NAME)
