#!/usr/bin/env python3
"""Family generator for the fireball-blast tiers (fireball-blast-i, fireball-blast-ii, fireball-blast-iii, fireball-blast-iv, fireball-blast-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
Fireball blast I: vụ nổ khi Cầu lửa chạm quái (impact_sprite của skill fireball).

Vẽ bằng sprite-lab/lib/firefx.py (2026-11-18): mật độ điểm ảnh gấp đôi ("px_scale": 0.5, cùng cỡ trên màn hình),
có pha mở đầu, nổ, đọng lại và tan. Bậc 1.  Chạy: gamekit art run fireball-blast-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"fireball-blast-i": [64, 27, 1], "fireball-blast-ii": [88, 37, 2], "fireball-blast-iii": [88, 37, 3], "fireball-blast-iv": [88, 37, 4], "fireball-blast-v": [88, 37, 5]}
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
import firefx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = _V[0]
RADIUS = _V[1]
C = SIZE / 2
ANCHOR = (C, C)
ANIM = [("impact", firefx.blast(_V[2], SIZE, RADIUS), 12, False,
         {"durations_ms": firefx.BLAST_MS, "hitbox": {"shape": "circle", "center": [C, C], "active": [1, 4], "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
