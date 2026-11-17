#!/usr/bin/env python3
"""Ground Slam V — địa tầng sụp: caldera rộng, vòng cột đá trồi lên, magma lộ giữa các khe.

Cùng dòng Ground Slam (impact nhìn từ trên xuống, không phải Earth Strike).
Bậc V là bố cục mới hẳn: không còn là hố + đá văng, mà là một vòng cột đá
dựng quanh miệng caldera có magma — đọc như địa hình bị đấm sụp, không giống
bậc V của dòng băng (mandala) hay Earth Strike (nhiều khe nứt).
Neo = tâm. Chạy: gamekit art run ground-slam-v
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
    "size": 88, "tier": 5, "seed": 53,
    "crater": (13, 7),
    "cracks": [
        (15, 0.85, 3), (75, 0.75, 2), (140, 0.8, 3),
        (200, 0.75, 2), (265, 0.8, 2), (330, 0.7, 2),
    ],
    "chips": [
        (15, 0.52, 0.85, 9, 2, 1), (75, 0.55, 0.8, 8, 1, 1),
        (140, 0.52, 0.86, 9, 2, 2), (200, 0.55, 0.82, 8, 1, 2),
        (265, 0.52, 0.85, 9, 2, 3), (330, 0.55, 0.8, 8, 1, 3),
    ],
    "puffs": [
        (15, 0.55, 2, 1), (75, 0.6, 2, 1), (140, 0.58, 2, 2),
        (200, 0.6, 1, 2), (265, 0.55, 2, 3), (330, 0.58, 1, 3),
        (45, 0.62, 1, 4), (170, 0.6, 0, 4),
    ],
    "pillars": [
        (25, 0.62, 9, 3), (120, 0.66, 7, 2), (195, 0.62, 10, 3), (300, 0.66, 7, 2),
    ],
    "gaps": ((18, 40), (95, 110), (175, 192), (255, 270), (330, 345)),
    "gaps2": ((50, 70), (210, 230), (300, 315)),
    "magma": 3,
    "embers": True,
}
C = SPEC["size"] / 2.0
ANIM = [("burst", frames(SPEC), 14, False,
         {"hitbox": {"shape": "circle", "center": [C, C], "active": [2, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C))
    print("OK", NAME)
