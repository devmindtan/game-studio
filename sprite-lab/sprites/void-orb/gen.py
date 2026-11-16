#!/usr/bin/env python3
"""Generator cho sprite "void-orb": cầu hư không tím đen, xoáy và hút vào.

  fly     6 frame lặp: lõi tối, vòng xoáy tím, hạt năng lượng lệch quỹ đạo;
  impact  6 frame một lần: co rút rồi bùng nổ thành vòng tím tan biến.

Bay sang phải. Neo (10, 10) là tâm quả cầu.

Chạy:  gamekit art run void-orb
"""

import sys
from pathlib import Path
import math


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "void-orb"
SIZE = 20
CX, CY = 10, 10
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#120816"
INK = "#231033"
VIO = "#6b3fa0"
VIO_L = "#a855f7"
MAG = "#d946ef"
SPARK = "#f5d0fe"


def p(c, x, y, col):
    c.pixel(x, y, col)


def glow(c, x, y, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(x - r, y - r, x + r, y + r, col)
    c.paste(ring)


def orb(c, x, y, phase):
    glow(c, x, y, 6, "#a855f722")
    c.ellipse(x - 4, y - 4, x + 4, y + 4, INK)
    c.ellipse(x - 3, y - 3, x + 3, y + 3, VIO)
    c.ellipse(x - 2, y - 2, x + 2, y + 2, VIO_L)
    c.ellipse(x - 1, y - 1, x + 1, y + 1, CORE)
    # xoáy: 4 mảnh cung quay theo pha
    for k in range(4):
        ang = (phase * 60 + k * 90) * math.pi / 180.0
        for t in (0, 0.35, 0.7):
            a = ang + t
            r = 4 + t
            p(c, round(x + math.cos(a) * r), round(y + math.sin(a) * r), MAG if k % 2 == 0 else VIO_L)


def trail(c, x, y, phase):
    for i in range(5):
        tx = x - 5 - i
        ty = y + ((0, -1, 1, 0)[(i + phase) % 4])
        col = VIO_L if i < 2 else VIO if i < 4 else INK
        p(c, tx, ty, col)
    for k, (dx, dy) in enumerate(((-7, -3), (-9, 2), (-11, -1))):
        if (phase + k) % 2 == 0:
            p(c, x + dx, y + dy, MAG if k == 0 else VIO_L)


def fly(i):
    c = Canvas(SIZE, SIZE)
    trail(c, CX, CY, i)
    orb(c, CX, CY, i)
    # hạt hút về phía sau
    for k, (dx, dy) in enumerate(((5, -4), (4, 4), (-3, -6))):
        if (i + k) % 3 == 0:
            p(c, CX + dx, CY + dy, SPARK)
    return c


def impact(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:  # co rút
        glow(c, CX, CY, 5, "#d946ef33")
        c.ellipse(CX - 5, CY - 5, CX + 5, CY + 5, VIO, fill=False)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, MAG)
        c.ellipse(CX - 1, CY - 1, CX + 1, CY + 1, SPARK)
        return c
    if i == 1:  # nén cực đại
        glow(c, CX, CY, 4, "#f5d0fe44")
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, VIO_L)
        c.ellipse(CX - 1, CY - 1, CX + 1, CY + 1, SPARK)
        for dx, dy in ((4, 0), (-4, 0), (0, 4), (0, -4)):
            p(c, CX + dx, CY + dy, MAG)
        return c
    if i == 2:  # bùng nổ
        glow(c, CX, CY, 7, "#a855f733")
        c.ellipse(CX - 6, CY - 6, CX + 6, CY + 6, VIO, fill=False)
        c.ellipse(CX - 4, CY - 4, CX + 4, CY + 4, VIO_L, fill=False)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, MAG)
        for dx, dy in ((7, 0), (-7, 0), (0, 7), (0, -7), (5, 5), (-5, -5), (5, -5), (-5, 5)):
            p(c, CX + dx, CY + dy, VIO_L)
        return c
    if i == 3:
        c.ellipse(CX - 8, CY - 8, CX + 8, CY + 8, INK, fill=False)
        c.ellipse(CX - 6, CY - 6, CX + 6, CY + 6, VIO, fill=False)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, VIO_L)
        for dx, dy in ((8, -2), (-8, 2), (2, 8), (-3, -8), (6, 6), (-6, -6)):
            p(c, CX + dx, CY + dy, VIO)
        return c
    if i == 4:
        c.ellipse(CX - 8, CY - 8, CX + 8, CY + 8, INK, fill=False)
        for dx, dy in ((9, -3), (-9, 3), (3, 9), (-4, -9), (7, 5), (-7, -5)):
            p(c, CX + dx, CY + dy, INK)
        p(c, CX, CY, VIO)
        return c
    for dx, dy in ((9, -4), (-9, 4), (4, 9), (-5, -9)):
        p(c, CX + dx, CY + dy, INK)
    return c


ANIMATIONS = [
    ("fly", [fly(i) for i in range(6)], 13, True),
    ("impact", [impact(i) for i in range(6)], 14, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=8)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=8)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
