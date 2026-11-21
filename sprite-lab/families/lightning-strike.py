#!/usr/bin/env python3
"""Family generator for the lightning-strike tiers (lightning-strike-ii, lightning-strike-iii, lightning-strike-iv, lightning-strike-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
lightning-strike-ii

Chuẩn fx_craft (2026-11-18): sprite-lab/lib/burstfx.py, mật độ gấp đôi ("px_scale": 0.5), >= 12 frame, mở đầu ->
trúng (chớp + tia) -> đọng lại -> tan. Bậc 2.  Chạy: gamekit art run lightning-strike-ii
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"lightning-strike-ii": [207, 35, 2], "lightning-strike-iii": [211, 39, 3], "lightning-strike-iv": [212, 40, 4], "lightning-strike-v": [224, 52, 5]}
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
import boltfx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
W, H = 120, _V[0]   # 48 px taller: a long thin bolt from a small dark cloud
GROUND = 164.0
RADIUS = _V[1]
ANCHOR = (W / 2, GROUND)
ANIM = [("strike", boltfx.lightning_strike(_V[2], W, H, GROUND, RADIUS), 12, False,
         {"durations_ms": boltfx.BOLT_MS, "hitbox": {"shape": "circle", "center": [W / 2, GROUND], "active": [2, 3]}})]  # only where the bolt lands, only while it lands

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
