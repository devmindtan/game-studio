#!/usr/bin/env python3
"""Family generator for the sword-wave tiers (sword-wave-ii, sword-wave-iii, sword-wave-iv, sword-wave-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
sword-wave-ii: bậc II của sword-wave (bậc I là sprite sword-wave). Kế thừa bậc trước và thêm một ý
(lib/tierfx.py: II quầng sáng, III tia lửa, IV vỏ năng lượng, V tia sáng + lõi trắng). Chạy: gamekit art run sword-wave-ii
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"sword-wave-ii": [2], "sword-wave-iii": [3], "sword-wave-iv": [4], "sword-wave-v": [5]}
import sys
from pathlib import Path

def _ws():
    for p in Path(TIER_FILE).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")

HERE = Path(TIER_FILE).resolve().parent
_V = TIERS[HERE.name]   # this tier's numbers (the rest is shared by the family)
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from tierfx import build
from sheet import export

if __name__ == "__main__":
    build(HERE, "sword-wave", _V[0], "#e8f4ff", "#7fc8ff", export)
    print("OK", HERE.name)
