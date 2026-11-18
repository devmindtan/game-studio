#!/usr/bin/env python3
"""Generator cho sprite "meteor-fall": thiên thạch rơi từ trên cao xuống (AOE).

Vẽ bằng sprite-lab/lib/firefx.py (2026-11-18): mật độ điểm ảnh gấp đôi ("px_scale": 0.5, cùng cỡ trên màn hình),
có pha mở đầu, nổ, đọng lại và tan. Bậc 1.  Chạy: gamekit art run meteor-fall
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
import firefx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
W, H = 96, 152   # room below the impact point for the whole ring and burst
GROUND = 104.0
RADIUS = 40
ANCHOR = (W / 2, GROUND)
ANIM = [("strike", firefx.meteor(1, W, H, GROUND, RADIUS), 12, False,
         {"durations_ms": firefx.METEOR_MS, "hitbox": {"shape": "circle", "center": [W / 2, GROUND], "active": [5, 7], "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
