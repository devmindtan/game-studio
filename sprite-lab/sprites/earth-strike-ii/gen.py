#!/usr/bin/env python3
"""Earth Strike II — hai khe nứt lệch qua tâm, ba phiến đá trồi, magma lóe ở tâm.

Cùng dòng với Earth Strike I (vết đứt lệch nhìn từ trên xuống): khe nứt lệch trục chạy ra từ điểm va chạm,
phiến đá trồi lên dọc khe đúng các frame gây sát thương (2..6), magma lộ ở bậc cao, rồi nguội và vỡ vụn.
Hình dựng bằng sprite-lab/lib/fissure.py (DNA chung cho bậc II-V). Bậc sau = nhiều nhánh, nhiều đá, nhiều magma,
khung lớn hơn: 56x56. Neo = tâm (điểm cast). Chạy: gamekit art run earth-strike-ii
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
from fissure import frames  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SPEC = {'size': 56, 'seed': 21, 'arms': [(-28, 1.0), (160, 0.8)], 'rocks': [(0, 0.55, 4), (0, 0.95, 3), (1, 0.7, 4)], 'magma': 1}
C = SPEC["size"] / 2.0
ANIM = [("burst", frames(SPEC), 14, False,
         {"hitbox": {"shape": "circle", "center": [C, C], "active": [2, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C))
    print("OK", NAME)
