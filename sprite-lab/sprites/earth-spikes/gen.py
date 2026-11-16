#!/usr/bin/env python3
"""Generator cho sprite "earth-spikes": gai đá trồi lên từ dưới đất (AOE).

  erupt   8 frame một lần: mặt đất nứt, gai đá nhọn phóng lên rồi ổn định và sụp.

Neo (24, 40) tại mặt đất (sprite 48x44). Gai mọc lên phía trên neo.

Chạy:  gamekit art run earth-spikes
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "earth-spikes"
W, H = 48, 44
CX, GY = 24, 40
ANCHOR = (float(CX), float(GY))
HERE = Path(__file__).resolve().parent
OUT = HERE

ROCK = "#7a5a3a"
ROCK_L = "#a88355"
ROCK_D = "#4a3524"
DUST = "#b08a5a"
CRACK = "#3a2818"


def p(c, x, y, col):
    c.pixel(x, y, col)


def ground_line(c):
    c.line(4, GY, W - 5, GY, ROCK_D)


def spike(c, base_x, height, lean=0):
    # tam giác gai đá hướng lên
    top = (base_x + lean, GY - height)
    left = (base_x - max(2, height // 3), GY)
    right = (base_x + max(2, height // 3), GY)
    c.polygon([top, left, right], ROCK)
    c.line(top[0], top[1], left[0], left[1], ROCK_D)
    c.line(top[0], top[1], base_x, GY, ROCK_L)
    p(c, top[0], top[1], ROCK_L)


def erupt(i):
    c = Canvas(W, H)
    bases = [10, 18, 24, 30, 38]
    if i == 0:
        # nứt mặt đất
        ground_line(c)
        for x in (12, 20, 28, 36):
            c.line(x, GY, x + 2, GY - 2, CRACK)
            c.line(x, GY, x - 1, GY - 1, CRACK)
        p(c, 24, GY - 3, DUST)
        return c
    if i == 1:
        ground_line(c)
        for b in bases:
            spike(c, b, 4, lean=(b % 3 - 1))
        for x in (8, 16, 32, 40):
            p(c, x, GY - 3, DUST)
        return c
    if i == 2:
        ground_line(c)
        heights = [10, 14, 18, 13, 9]
        for b, h in zip(bases, heights):
            spike(c, b, h, lean=(b % 5 - 2))
        for x in (6, 14, 34, 42):
            p(c, x, GY - 5, DUST); p(c, x, GY - 4, DUST)
        return c
    if i == 3:
        # cao nhất
        ground_line(c)
        heights = [14, 20, 26, 19, 13]
        for b, h in zip(bases, heights):
            spike(c, b, h, lean=(b % 5 - 2))
        for x, y in ((7, GY - 7), (15, GY - 8), (33, GY - 7), (41, GY - 6), (24, GY - 28)):
            p(c, x, y, DUST)
        return c
    if i == 4:
        ground_line(c)
        heights = [13, 19, 24, 18, 12]
        for b, h in zip(bases, heights):
            spike(c, b, h, lean=(b % 5 - 2))
        for x in (8, 40):
            p(c, x, GY - 5, DUST)
        return c
    if i == 5:
        ground_line(c)
        heights = [11, 16, 20, 15, 10]
        for b, h in zip(bases, heights):
            spike(c, b, h, lean=(b % 5 - 2))
        return c
    if i == 6:
        # sụp xuống
        ground_line(c)
        heights = [7, 10, 12, 9, 6]
        for b, h in zip(bases, heights):
            spike(c, b, h, lean=(b % 5 - 2))
        c.line(6, GY, W - 7, GY, ROCK)
        return c
    ground_line(c)
    for b, h in zip(bases, [3, 5, 6, 4, 3]):
        spike(c, b, h, lean=0)
    for x in (12, 20, 28, 36):
        p(c, x, GY - 1, DUST)
    return c


ANIMATIONS = [
    ("erupt", [erupt(i) for i in range(8)], 12, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * W, len(ANIMATIONS) * H)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * H)
    preview([sheet], HERE / "preview.png", scale=4)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=4)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop,
                      "hitbox": {"shape": "circle", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1]}}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
