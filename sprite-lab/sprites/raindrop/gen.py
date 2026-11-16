#!/usr/bin/env python3
"""Generator cho sprite "raindrop": giọt mưa rơi xiên (gió thổi sang trái).

4x10, 1 frame. Đầu giọt ở dưới bên trái, vệt mờ kéo lên trên bên phải.
Chạy:  gamekit art run raindrop
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import from_rows, preview, strip, write_anim_meta  # noqa: E402

NAME = "raindrop"
FPS = 1
ANCHOR = (1.5, 8.5)  # đầu giọt = điểm tính va chạm
LOOP = False
HERE = Path(__file__).resolve().parent
OUT = HERE  # sprite-lab/sprites/<name>/: strip + json next to gen.py

PALETTE = {
    "a": "#9fb6e650",  # đuôi rất mờ
    "t": "#a8c4ffa0",  # đuôi
    "b": "#a8c4ff",    # thân giọt
    "c": "#eef4ff",    # chỗ phản sáng
}

ROWS = [
    "...a",
    "...a",
    "..t.",
    "..t.",
    "..b.",
    ".b..",
    ".bc.",
    "bcc.",
    "bcb.",
    ".b..",
]


def main() -> None:
    frames = [from_rows(ROWS, PALETTE)]
    OUT.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT / f"{NAME}.png")
    strip(frames).save(OUT / f"{NAME}_strip.png")
    preview(frames, HERE / "preview.png", scale=24)
    anim = {"name": "idle", "frames": frames, "fps": float(FPS), "loop": LOOP,
            "hitbox": {"shape": "rect", "center": [ANCHOR[0] if ANCHOR else frames[0].width/2, ANCHOR[1] if ANCHOR else frames[0].height/2], "active": [0, len(frames)-1]}}
    write_anim_meta(OUT / f"{NAME}.json", [anim], anchor=ANCHOR)
    print(f"sprite: {OUT / f'{NAME}.png'}")


if __name__ == "__main__":
    main()
