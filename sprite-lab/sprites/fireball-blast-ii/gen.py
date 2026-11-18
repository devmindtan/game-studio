#!/usr/bin/env python3
"""Fireball blast II: vụ nổ khi Cầu lửa chạm quái (impact_sprite của skill fireball).

Vẽ bằng sprite-lab/lib/firefx.py (2026-11-18): mật độ điểm ảnh gấp đôi ("px_scale": 0.5, cùng cỡ trên màn hình),
có pha mở đầu, nổ, đọng lại và tan. Bậc 2.  Chạy: gamekit art run fireball-blast-ii
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
SIZE = 88
RADIUS = 37
C = SIZE / 2
ANCHOR = (C, C)
ANIM = [("impact", firefx.blast(2, SIZE, RADIUS), 12, False,
         {"durations_ms": firefx.BLAST_MS, "hitbox": {"shape": "circle", "center": [C, C], "active": [1, 4], "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR, preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
