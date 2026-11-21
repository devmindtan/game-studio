#!/usr/bin/env python3
"""Family generator for the blizzard-vortex tiers (blizzard-vortex-ii, blizzard-vortex-iii, blizzard-vortex-iv, blizzard-vortex-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
blizzard-vortex-ii: bậc II của blizzard-vortex (bậc I là sprite blizzard-vortex). Kế thừa bậc trước và thêm một ý

Vẽ lại 2026-11-18 (người dùng: hiệu ứng xuất hiện và mất quá nhanh, làm mịn Scale2x không đẹp):
dùng sprite-lab/lib/icefx.py, khung 168x168 = gấp đôi mật độ điểm ảnh, "px_scale": 0.5 để game vẽ
cùng cỡ trên màn hình; có pha mở đầu, pha chính, pha đọng lại và pha tan (dither). Bậc 2.
Chạy: gamekit art run blizzard-vortex-ii
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"blizzard-vortex-ii": [70.0, 2], "blizzard-vortex-iii": [76.0, 3], "blizzard-vortex-iv": [76.0, 4], "blizzard-vortex-v": [76.0, 5]}
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
import icefx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = 168
RADIUS = _V[0]   # hit radius in this frame's pixels (twice the old sprite's)
TIER = _V[1]
C = SIZE / 2

ANIM = [("burst", icefx.blizzard(TIER, SIZE, RADIUS), 12, False,
         {"durations_ms": icefx.BLIZZ_MS,
          "hitbox": {"shape": "circle", "center": [C, C], "active": [4, 13], "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5   # drawn at half scale: same size on screen, twice the pixels
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
