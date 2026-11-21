#!/usr/bin/env python3
"""Family generator for the earth-strike tiers (earth-strike-i, earth-strike-ii, earth-strike-iii, earth-strike-iv, earth-strike-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
earth-strike-i

Chuẩn fx_craft (2026-11-18): sprite-lab/lib/burstfx.py, mật độ gấp đôi ("px_scale": 0.5), >= 12 frame, mở đầu ->
trúng (chớp + tia) -> đọng lại -> tan. Bậc 1.  Chạy: gamekit art run earth-strike-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"earth-strike-i": [96, 52, 1], "earth-strike-ii": [112, 54, 2], "earth-strike-iii": [128, 62, 3], "earth-strike-iv": [144, 74, 4], "earth-strike-v": [176, 94, 5]}
import json
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
import burstfx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = _V[0]
RADIUS = _V[1]
C = SIZE / 2
ANCHOR = (C, C)
ANIM = [("burst", burstfx.earth_burst(_V[2], SIZE, RADIUS), 12, False,
         {"durations_ms": burstfx.EARTH_MS, "hitbox": {"shape": "circle", "center": [C, C], "active": [2, 5], "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
