#!/usr/bin/env python3
"""Generator cho sprite "war-hammer": búa chiến (vật phẩm/trang bị).

  idle    6 frame lặp: búa chiến tựa chéo, đầu búa ánh kim.

Neo (14, 30) gần đuôi cán (sprite 32x32).

Chạy:  gamekit art run war-hammer
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

NAME = "war-hammer"
SIZE = 32
ANCHOR = (14.0, 30.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

STEEL = "#b8c7d9"
STEEL_D = "#5f7187"
EDGE = "#e8f4ff"
WOOD = "#8a5a2e"
WOOD_D = "#563418"
GOLD = "#d9b44a"
DARK = "#3a4657"


def p(c, x, y, col):
    c.pixel(x, y, col)


def hammer(c, glint=False):
    # cán
    c.line(13, 29, 20, 8, WOOD, 2)
    c.line(13, 29, 20, 8, WOOD_D, 1)
    # đầu búa khối
    c.rect(14, 4, 26, 11, STEEL_D)
    c.rect(15, 5, 25, 10, STEEL)
    c.line(15, 5, 25, 5, EDGE)
    c.line(15, 5, 15, 10, EDGE)
    # mặt đập
    c.rect(14, 6, 15, 9, DARK)
    # mỏ nhọn phía sau
    c.polygon([(14, 6), (10, 8), (14, 10)], STEEL_D)
    c.line(10, 8, 14, 7, EDGE)
    # đai
    c.rect(18, 7, 21, 11, GOLD)
    c.line(19, 7, 19, 11, DARK)
    p(c, 13, 30, GOLD)
    if glint:
        p(c, 16, 5, "#ffffff"); p(c, 22, 5, EDGE)


def idle(i):
    c = Canvas(SIZE, SIZE)
    c.ellipse(10, 29, 20, 31, "#00000033")
    hammer(c, glint=(i == 2 or i == 3))
    return c


ANIMATIONS = [("idle", [idle(i) for i in range(6)], 5, True)]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=5)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=5)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
