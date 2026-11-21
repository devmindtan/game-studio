#!/usr/bin/env python3
"""Family generator for the whirlwind tiers (whirlwind-ii, whirlwind-iii, whirlwind-iv, whirlwind-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
whirlwind-ii: bậc II của whirlwind (bậc I là sprite whirlwind). Kế thừa bậc trước và thêm một ý
(lib/tierfx.py: II quầng sáng, III tia lửa, IV vỏ năng lượng, V tia sáng + lõi trắng). Chạy: gamekit art run whirlwind-ii
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"whirlwind-ii": [2], "whirlwind-iii": [3], "whirlwind-iv": [4], "whirlwind-v": [5]}
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
    build(HERE, "whirlwind", _V[0], "#e8fff8", "#5fe0c0", export)
    print("OK", HERE.name)
