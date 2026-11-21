#!/usr/bin/env python3
"""Family generator for the solar-ray-impact tiers (solar-ray-impact-i, solar-ray-impact-ii, solar-ray-impact-iii, solar-ray-impact-iv, solar-ray-impact-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
solar-ray impact I: vụ nổ khi đạn chạm (impact_tiers).

Chuẩn fx_craft (2026-11-18): sprite-lab/lib/burstfx.py, mật độ gấp đôi ("px_scale": 0.5), >= 12 frame, mở đầu ->
trúng (chớp + tia) -> đọng lại -> tan. Bậc 1.  Chạy: gamekit art run solar-ray-impact-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"solar-ray-impact-i": [88, 26, 1], "solar-ray-impact-ii": [112, 30, 2], "solar-ray-impact-iii": [112, 34, 3], "solar-ray-impact-iv": [112, 34, 4], "solar-ray-impact-v": [112, 34, 5]}
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
ANIM = [("impact", burstfx.impact_burst(_V[2], SIZE, RADIUS, "solar"), 12, False,
         {"durations_ms": burstfx.IMPACT_MS, "hitbox": {"shape": "circle", "center": [C, C], "active": [1, 4], "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
