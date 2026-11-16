#!/usr/bin/env python3
"""Generator cho sprite "splash": nước tóe khi giọt mưa chạm đất hoặc trúng đom đóm.

10x6, 3 frame: vương miện nước, bắn tung, tan. Neo ở giữa cạnh dưới.
Chạy:  gamekit art run splash
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import from_rows, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "splash"
FPS = 10
ANCHOR = (5.0, 6.0)  # giữa cạnh dưới, đặt lên điểm chạm
LOOP = False
HERE = Path(__file__).resolve().parent
OUT = HERE  # sprite-lab/sprites/<name>/: strip + json next to gen.py

PALETTE = {
    "a": "#cfe0ff",
    "b": "#8faee8",
    "f": "#8faee870",  # mờ dần
}

FRAMES = [
    [
        "..........",
        "..........",
        "..........",
        "...a..a...",
        "....bb....",
        "..bbbbbb..",
    ],
    [
        "..........",
        ".a......a.",
        "..a....a..",
        "...b..b...",
        "..........",
        ".bb....bb.",
    ],
    [
        "a........a",
        "..........",
        ".f......f.",
        "..........",
        "..........",
        "f........f",
    ],
]


def main() -> None:
    frames = [from_rows(rows, PALETTE) for rows in FRAMES]
    OUT.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT / f"{NAME}.png")
    strip(frames).save(OUT / f"{NAME}_strip.png")
    preview(frames, HERE / "preview.png", scale=24)
    gif(frames, HERE / "anim.gif", fps=10, scale=12)
    anim = {"name": "idle", "frames": frames, "fps": float(FPS), "loop": LOOP,
            "hitbox": {"shape": "rect", "center": [ANCHOR[0] if ANCHOR else frames[0].width/2, ANCHOR[1] if ANCHOR else frames[0].height/2], "active": [0, len(frames)-1]}}
    write_anim_meta(OUT / f"{NAME}.json", [anim], anchor=ANCHOR)
    print(f"strip: {OUT / f'{NAME}_strip.png'}")


if __name__ == "__main__":
    main()
