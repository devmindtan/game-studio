#!/usr/bin/env python3
"""holy-column-v

Chuẩn fx_craft (2026-11-18): sprite-lab/lib/burstfx.py, mật độ gấp đôi ("px_scale": 0.5), >= 12 frame, mở đầu ->
trúng (chớp + tia) -> đọng lại -> tan. Bậc 5.  Chạy: gamekit art run holy-column-v
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
import burstfx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
W, H = 120, 177
GROUND = 116.0
RADIUS = 53
ANCHOR = (W / 2, GROUND)
ANIM = [("descend", burstfx.holy_column(5, W, H, GROUND, RADIUS), 12, False,
         {"durations_ms": burstfx.HOLY_MS, "hitbox": {"shape": "rect", "center": [W / 2, GROUND - 45.0], "half_w": 53.0, "half_h": 65.0, "active": [3, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
