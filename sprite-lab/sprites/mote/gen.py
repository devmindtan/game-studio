#!/usr/bin/env python3
"""Generator cho sprite "mote": đốm sáng người chơi nhặt để nạp đèn.

8x8, 4 frame nhịp thở (nhỏ, vừa, lớn, vừa). Không viền: nó tự phát sáng trên nền đêm.
Chạy:  gamekit art run mote
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

NAME = "mote"
FPS = 6
ANCHOR = None  # hình đối xứng: tâm phần có hình
LOOP = True
HERE = Path(__file__).resolve().parent
OUT = HERE  # sprite-lab/sprites/<name>/: strip + json next to gen.py

PALETTE = {
    "o": "#4f8a3a80",  # quầng ngoài, bán trong suốt
    "l": "#8fd16a",
    "m": "#d9f77a",
    "W": "#ffffff",
}

FRAMES = [
    [
        "........",
        "........",
        "...l....",
        "..lWl...",
        "...l....",
        "........",
        "........",
        "........",
    ],
    [
        "........",
        "...o....",
        "..lml...",
        ".omWmo..",
        "..lml...",
        "...o....",
        "........",
        "........",
    ],
    [
        "...o....",
        "..olo...",
        ".olmlo..",
        "olmWmlo.",
        ".olmlo..",
        "..olo...",
        "...o....",
        "........",
    ],
    [
        "........",
        "...o....",
        "..lml...",
        ".omWmo..",
        "..lml...",
        "...o....",
        "........",
        "........",
    ],
]


def main() -> None:
    frames = [from_rows(rows, PALETTE) for rows in FRAMES]
    OUT.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT / f"{NAME}.png")
    strip(frames).save(OUT / f"{NAME}_strip.png")
    preview(frames, HERE / "preview.png", scale=24)
    gif(frames, HERE / "anim.gif", fps=6, scale=12)
    anim = {"name": "idle", "frames": frames, "fps": float(FPS), "loop": LOOP,
            "hitbox": {"shape": "rect", "center": [ANCHOR[0] if ANCHOR else frames[0].width/2, ANCHOR[1] if ANCHOR else frames[0].height/2], "active": [0, len(frames)-1]}}
    write_anim_meta(OUT / f"{NAME}.json", [anim], anchor=ANCHOR)
    print(f"strip: {OUT / f'{NAME}_strip.png'}")


if __name__ == "__main__":
    main()
