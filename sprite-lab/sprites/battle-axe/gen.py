#!/usr/bin/env python3
"""Generator cho sprite "battle-axe": rìu chiến (vật phẩm/trang bị).

  idle    6 frame lặp: rìu tựa chéo, lưỡi rìu lóe sáng nhẹ.

Neo (14, 30) gần đuôi cán (sprite 32x32).

Chạy:  gamekit art run battle-axe
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

NAME = "battle-axe"
SIZE = 32
ANCHOR = (14.0, 30.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

EDGE = "#e8f4ff"
STEEL = "#b8c7d9"
STEEL_D = "#5f7187"
WOOD = "#8a5a2e"
WOOD_D = "#563418"
WOOD_L = "#b07c44"
GOLD = "#d9b44a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def axe(c, glint=False):
    # cán
    c.line(13, 29, 20, 7, WOOD, 2)
    c.line(13, 29, 20, 7, WOOD_D, 1)
    c.line(14, 28, 20, 8, WOOD_L, 1)
    # đầu rìu hai lưỡi
    c.polygon([(18, 6), (12, 4), (8, 8), (10, 12), (16, 11)], STEEL_D)
    c.polygon([(18, 7), (13, 5), (10, 8), (11, 11), (16, 10)], STEEL)
    c.line(12, 6, 10, 8, EDGE)
    c.polygon([(20, 8), (26, 6), (28, 10), (25, 14), (20, 12)], STEEL_D)
    c.polygon([(20, 9), (25, 7), (27, 10), (24, 13), (20, 11)], STEEL)
    c.line(26, 7, 27, 10, EDGE)
    # đai cố định
    c.line(17, 9, 21, 8, GOLD)
    c.line(17, 10, 21, 9, GOLD)
    # đuôi cán
    p(c, 13, 30, GOLD)
    if glint:
        p(c, 11, 6, EDGE); p(c, 26, 8, EDGE)


def idle(i):
    c = Canvas(SIZE, SIZE)
    c.ellipse(10, 29, 20, 31, "#00000033")
    axe(c, glint=(i in (2, 3)))
    return c


ANIMATIONS=[("idle",[idle(0)],1,False)]


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
