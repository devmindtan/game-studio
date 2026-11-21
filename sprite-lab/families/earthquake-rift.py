#!/usr/bin/env python3
"""Family generator for the earthquake-rift tiers (earthquake-rift-ii, earthquake-rift-iii, earthquake-rift-iv, earthquake-rift-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
earthquake-rift-ii: bậc II. Giữ vết nứt chính + bụi của bậc I, thêm nhiều mảnh đá nhô lên.

Vẽ bằng sprite-lab/lib/stormfx.py (2026-11-18): mật độ điểm ảnh gấp đôi ("px_scale": 0.5, cùng cỡ trên màn hình),
có pha mở đầu, trúng, đọng lại và tan. Bậc 2.  Chạy: gamekit art run earthquake-rift-ii
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"earthquake-rift-ii": [66, 2], "earthquake-rift-iii": [72, 3], "earthquake-rift-iv": [72, 4], "earthquake-rift-v": [72, 5]}
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
import stormfx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = 152
RADIUS = _V[0]
C = SIZE / 2
ANIM = [("spell", stormfx.earthquake(_V[1], SIZE, RADIUS), 12, False,
         {"durations_ms": stormfx.QUAKE_MS, "hitbox": {"shape": "rect", "center": [C, C], "active": [2, 5], "half_w": float(RADIUS), "half_h": float(RADIUS) * 0.4}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
