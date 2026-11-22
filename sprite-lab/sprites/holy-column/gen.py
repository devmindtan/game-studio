#!/usr/bin/env python3
"""holy-column

Vẽ lại 2026-11-22: sprite-lab/lib/holyfx.py (ấn thánh báo trước, cột mép thẳng, không đám chấm). Chuẩn fx_craft, mật độ gấp đôi ("px_scale": 0.5), >= 12 frame, mở đầu ->
trúng (chớp + tia) -> đọng lại -> tan. Bậc 1.  Chạy: gamekit art run holy-column
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
import holyfx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
W, H = 170, 256
RADIUS = 33
GROUND = H - RADIUS - 6.0   # 2D round sigil (2026-11-22): the ground sits so the circle fits the frame
ANCHOR = (W / 2, GROUND)
ANIM = [("descend", holyfx.holy_column(1, W, H, GROUND, RADIUS), 12, False,
         {"durations_ms": holyfx.MS, "hitbox": {"shape": "rect", "center": [W / 2, GROUND], "active": [3, 6]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=1, gif_scale=1)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
