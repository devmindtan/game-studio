#!/usr/bin/env python3
"""Bão sét: nhiều điểm sét giáng có chạm đất trong vùng tròn tích điện; hitbox circle.

Vẽ bằng sprite-lab/lib/stormfx.py (2026-11-18): mật độ điểm ảnh gấp đôi ("px_scale": 0.5, cùng cỡ trên màn hình),
có pha mở đầu, trúng, đọng lại và tan. Bậc 1.  Chạy: gamekit art run lightning-storm
"""
import json
import sys
from pathlib import Path


def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import stormfx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = 128
RADIUS = 58
C = SIZE / 2
ANIM = [("spell", stormfx.storm(1, SIZE, RADIUS), 12, False,
         {"durations_ms": stormfx.STORM_MS, "hitbox": {"shape": "circle", "center": [C, C], "active": [3, 6], "radius": float(RADIUS), "inner": 0.0, "swept": True}}),   # solid: the struck monster sits at the centre
        ("linger", stormfx.storm_linger(1, SIZE, RADIUS), 12, True, {"hitbox": {"shape": "circle", "center": [C, C], "active": [0, 7]}})]   # the 2 s pulse zone (user 2026-11-22; damage from the zone, the box is for the data rules)

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
