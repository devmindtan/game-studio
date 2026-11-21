#!/usr/bin/env python3
"""Family generator for the war-hammer-strike tiers (war-hammer-strike-ii, war-hammer-strike-iii, war-hammer-strike-iv, war-hammer-strike-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
war-hammer-strike-ii — Búa thần, bậc 2.

Chuẩn fx_craft (2026-11-18): lib/hammerfx.py, mật độ gấp đôi ("px_scale": 0.5), 12 frame,
3 frame rơi -> trúng -> đọng lại -> tan; 4 hướng (strike_right/left/up/down).
Kế thừa: búa vàng + chớp + vòng xung kích + tia lửa của bậc trước, thêm vòng xung kích thứ hai chạy chậm hơn.
Chạy: gamekit art run war-hammer-strike-ii
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"war-hammer-strike-ii": [2], "war-hammer-strike-iii": [3], "war-hammer-strike-iv": [4], "war-hammer-strike-v": [5]}
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
sys.path.insert(0, str(Path(TIER_FILE).resolve().parents[2] / "lib"))
import hammerfx  # noqa: E402
from sheet import export  # noqa: E402

if __name__ == "__main__":
    hammerfx.build(HERE, HERE.name, _V[0], export)
    print("OK", HERE.name)
