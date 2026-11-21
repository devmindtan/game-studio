#!/usr/bin/env python3
"""Family generator for the arcane-bolt tiers (arcane-bolt-ii, arcane-bolt-iii, arcane-bolt-iv, arcane-bolt-v).

One file per skill family (review 2026-11-21: the tier gen.py files were copies that only differed in a
few numbers). Each tier folder's gen.py runs this file with its own __file__; TIERS holds the numbers that
change per tier. First tier's original notes:
arcane-bolt-ii: bậc II của arcane-bolt (bậc I là sprite arcane-bolt). Kế thừa bậc trước và thêm một ý

Vẽ lại 2026-11-18 (người dùng: đạn phóng to bị nhòe): sprite-lab/lib/boltfx.py vẽ trực tiếp từng hướng bay
(fly, fly_right/left/up/down, fly_000..fly_337) ở mật độ gấp đôi ("px_scale": 0.5), không xoay ảnh nên không vỡ nét.
Hitbox đo từ mặt nạ là đầu đạn (đuôi không làm hitbox dài ra). Vụ nổ khi chạm: sprite riêng (impact_tiers). Bậc 2.
Chạy: gamekit art run arcane-bolt-ii
"""
TIER_FILE = globals().get("TIER_FILE", __file__)   # the tier folder's gen.py, set by its stub
TIERS = {"arcane-bolt-ii": [2], "arcane-bolt-iii": [3], "arcane-bolt-iv": [4], "arcane-bolt-v": [5]}
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
SIZE = 80
C = SIZE / 2
KIND, TIER, FPS = "arcane", _V[0], 14.0
HB = {"shape": "rect", "center": [C, C], "active": [0, 5]}
DIRS = [("fly", 0), ("fly_right", 0), ("fly_left", 180), ("fly_up", 270), ("fly_down", 90)] + \
    [("fly_%03d" % round(k * 22.5), k * 22.5) for k in range(16)]
ANIM = [(n, boltfx.projectile(KIND, TIER, SIZE, d), FPS, True, {"hitbox": dict(HB)}) for n, d in DIRS]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
