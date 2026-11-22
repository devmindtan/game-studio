#!/usr/bin/env python3
"""Family generator for the holy-column tiers (holy-column-ii, holy-column-iii, holy-column-iv, holy-column-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
holy-column-ii

Vẽ lại 2026-11-22: sprite-lab/lib/holyfx.py (ấn thánh báo trước, cột mép thẳng, không đám chấm). Chuẩn fx_craft, mật độ gấp đôi ("px_scale": 0.5), >= 12 frame, mở đầu ->
trúng (chớp + tia) -> đọng lại -> tan. Bậc 2.  Chạy: gamekit art run holy-column-ii
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"holy-column-ii": [180, 35, 2, 48.0, 35.0, 58.0], "holy-column-iii": [192, 39, 3, 46.0, 39.0, 62.0], "holy-column-iv": [192, 40, 4, 47.0, 40.0, 63.0], "holy-column-v": [192, 53, 5, 45.0, 53.0, 65.0]}
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
import holyfx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
W, H = _V[0], 256
GROUND = 226.0
RADIUS = _V[1]
ANCHOR = (W / 2, GROUND)
ANIM = [("descend", holyfx.holy_column(_V[2], W, H, GROUND, RADIUS), 12, False,
         {"durations_ms": holyfx.MS, "hitbox": {"shape": "rect", "center": [W / 2, GROUND], "active": [3, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=1, gif_scale=1)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
