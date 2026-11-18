#!/usr/bin/env python3
"""arcane-bolt impact IV: vụ nổ khi đạn chạm (impact_tiers).

Chuẩn fx_craft (2026-11-18): sprite-lab/lib/burstfx.py, mật độ gấp đôi ("px_scale": 0.5), >= 12 frame, mở đầu ->
trúng (chớp + tia) -> đọng lại -> tan. Bậc 4.  Chạy: gamekit art run arcane-bolt-impact-iv
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
SIZE = 80
RADIUS = 27
C = SIZE / 2
ANCHOR = (C, C)
ANIM = [("impact", burstfx.impact_burst(4, SIZE, RADIUS, "arcane"), 12, False,
         {"durations_ms": burstfx.IMPACT_MS, "hitbox": {"shape": "circle", "center": [C, C], "active": [1, 4], "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
