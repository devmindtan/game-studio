#!/usr/bin/env python3
"""Generator cho sprite "firefly": người chơi, đom đóm nhìn nghiêng, quay phải.

16x16, 4 frame: cánh vỗ (lên, giữa, xuống, giữa); đuôi sáng nhấp nháy theo nhịp.
Game lật ngang khi bay sang trái. Chạy:  gamekit art run firefly
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import from_rows, gif, preview, strip, write_meta  # noqa: E402

NAME = "firefly"
FPS = 12
ANCHOR = (7.5, 8.5)  # tâm thân; khung bao nhảy theo cánh nên không dùng tâm hình
LOOP = True
HERE = Path(__file__).resolve().parent
OUT = HERE  # sprite-lab/sprites/<name>/: strip + json next to gen.py

PALETTE = {
    "b": "#3b2a22",   # thân
    "d": "#241812",   # đầu, chân
    "p": "#c8553d",   # khiên ngực (đỏ cam như đom đóm thật)
    "e": "#f0e6d0",   # mắt
    "a": "#5a4334",   # râu
    "g": "#9fb83a",   # đuôi sáng mờ
    "G": "#e6f25a",   # đuôi sáng
    "L": "#fffbd0",   # lõi sáng nhất
    "w": "#d6e8ffc8", # cánh trước (bán trong suốt)
    "v": "#9fb8e080", # cánh sau
}

# Thân: đuôi (trái) - ngực - đầu (phải). Cánh vẽ đè lên theo từng frame.
BODY = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "............a...",
    "...........a....",
    "......pppp.dd...",
    "..gGgbbdbbbdde..",
    ".LGGgbbdbbbdd...",
    "..gGg.bdbb......",
    "......d.d.d.....",
    "................",
    "................",
    "................",
    "................",
]

# Đuôi tối hơn ở frame 0 và 2 (nhịp nhấp nháy chậm hơn nhịp cánh).
TAIL_DIM = {"L": "G", "G": "g"}

WINGS = [
    [  # lên
        "................",
        "................",
        ".....vv.........",
        ".....vvww.......",
        "......vwww......",
        ".......www......",
        "........ww......",
    ],
    [  # giữa
        "................",
        "................",
        "................",
        "................",
        "................",
        "..vvvww.........",
        "...vwwwww.......",
    ],
    [  # xuống, gập ra sau
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "...vvwwww.......",
        "..vvwwww........",
    ],
    [  # giữa
        "................",
        "................",
        "................",
        "................",
        "................",
        "..vvvww.........",
        "...vwwwww.......",
    ],
]


def frame(i: int):
    rows = BODY
    if i % 2 == 0:
        rows = ["".join(TAIL_DIM.get(ch, ch) for ch in r) for r in BODY]
    c = from_rows(rows, PALETTE)
    c.outline("#0d0a12")
    wing = from_rows(WINGS[i] + ["." * 16] * (16 - len(WINGS[i])), PALETTE)
    return c.paste(wing)


def main() -> None:
    frames = [frame(i) for i in range(4)]
    OUT.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT / f"{NAME}.png")
    strip(frames).save(OUT / f"{NAME}_strip.png")
    preview(frames, HERE / "preview.png", scale=16)
    gif(frames, HERE / "anim.gif", fps=12, scale=8)
    write_meta(OUT / f"{NAME}.json", frames, fps=FPS, anchor=ANCHOR, loop=LOOP)
    print(f"strip: {OUT / f'{NAME}_strip.png'}")


if __name__ == "__main__":
    main()
