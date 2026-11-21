#!/usr/bin/env python3
"""Family generator for the meteor-fall tiers (meteor-fall-ii, meteor-fall-iii, meteor-fall-iv, meteor-fall-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
meteor-fall-ii: bậc II của meteor-fall (bậc I là sprite meteor-fall). Kế thừa bậc trước và thêm một ý

Vẽ bằng sprite-lab/lib/firefx.py (2026-11-18): mật độ điểm ảnh gấp đôi ("px_scale": 0.5, cùng cỡ trên màn hình),
có pha mở đầu, nổ, đọng lại và tan. Bậc 2.  Chạy: gamekit art run meteor-fall-ii
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"meteor-fall-ii": [2], "meteor-fall-iii": [3], "meteor-fall-iv": [4], "meteor-fall-v": [5]}
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
W, H = 120, 174   # room below the impact point for the whole ring and burst
GROUND = 116.0
RADIUS = 50
ANCHOR = (W / 2, GROUND)
ANIM = [("strike", firefx.meteor(_V[0], W, H, GROUND, RADIUS), 12, False,
         {"durations_ms": firefx.METEOR_MS, "hitbox": {"shape": "circle", "center": [W / 2, GROUND], "active": [8, 10], "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
