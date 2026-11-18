#!/usr/bin/env python3
"""Frost Bloom II — hoa băng nở từ mặt đất, cánh hoa đa góc.

Vẽ lại 2026-11-18 (người dùng: hiệu ứng xuất hiện và mất quá nhanh, làm mịn Scale2x không đẹp):
dùng sprite-lab/lib/icefx.py, khung 112x112 = gấp đôi mật độ điểm ảnh, "px_scale": 0.5 để game vẽ
cùng cỡ trên màn hình; có pha mở đầu, pha chính, pha đọng lại và pha tan (dither). Bậc 2.
Chạy: gamekit art run frost-nova-ii
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
import icefx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = 112
RADIUS = 44.0   # hit radius in this frame's pixels (twice the old sprite's)
TIER = 2
C = SIZE / 2

ANIM = [("burst", icefx.frost_nova(TIER, SIZE, RADIUS), 12, False,
         {"durations_ms": icefx.FROST_MS,
          "hitbox": {"shape": "circle", "center": [C, C], "active": [4, 7], "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5   # drawn at half scale: same size on screen, twice the pixels
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
