#!/usr/bin/env python3
"""Laser ngắn đỏ (projectile, 4 hướng + impact)."""

import sys
from pathlib import Path
from PIL import Image


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "laser-bolt"
SIZE = 24
CX, CY = 12, 12
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

# Laser ngắn, bay nhanh: lõi trắng, thân đỏ, đuôi mờ.
CORE = "#ffffff"
BODY = "#ff5a5a"
MID = "#ff2d3d"
DEEP = "#a80f2a"
GLOW = "#ff2d3d33"


def glow(c, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(CX - r, CY - r, CX + r, CY + r, col)
    c.paste(ring)


def fly(i):
    c = Canvas(SIZE, SIZE)
    glow(c, 6, GLOW)
    # đuôi mờ dần về sau, nhấp nháy nhẹ theo pha
    tail = 7 + (i % 2)
    for k in range(tail):
        x = CX - 3 - k
        col = BODY if k < 3 else MID if k < 5 else DEEP
        p(c, x, CY, col)
        if k < 4:
            p(c, x, CY - 1, DEEP)
            p(c, x, CY + 1, DEEP)
    # thân laser
    for x in range(CX - 3, CX + 6):
        p(c, x, CY, BODY)
        p(c, x, CY - 1, MID)
        p(c, x, CY + 1, MID)
    # lõi sáng
    for x in range(CX - 1, CX + 6):
        p(c, x, CY, CORE)
    # đầu nhọn
    p(c, CX + 6, CY, BODY)
    p(c, CX + 7, CY, CORE)
    if i % 2:
        p(c, CX + 5, CY - 1, CORE)
    return c


def impact(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        glow(c, 6, "#ffffff66")
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, CORE)
        for dx, dy in ((5, 0), (-5, 0), (0, 5), (0, -5)):
            p(c, CX + dx, CY + dy, BODY)
        return c
    if i == 1:
        c.ellipse(CX - 5, CY - 5, CX + 5, CY + 5, BODY, fill=False)
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, CORE)
        return c
    if i == 2:
        c.ellipse(CX - 8, CY - 8, CX + 8, CY + 8, MID, fill=False)
        c.ellipse(CX - 4, CY - 4, CX + 4, CY + 4, BODY, fill=False)
        p(c, CX, CY, CORE)
        for dx, dy in ((9, 0), (-9, 0), (0, 9), (0, -9), (6, 6), (-6, -6)):
            p(c, CX + dx, CY + dy, BODY)
        return c
    if i == 3:
        c.ellipse(CX - 6, CY - 6, CX + 6, CY + 6, DEEP, fill=False)
        for dx, dy in ((8, -3), (-8, 3), (3, 8), (-3, -8)):
            p(c, CX + dx, CY + dy, MID)
        return c
    for dx, dy in ((10, -4), (-10, 4), (4, 10), (-4, -10)):
        p(c, CX + dx, CY + dy, DEEP)
    return c


def p(c, x, y, col):
    c.pixel(x, y, col)


def rot(c, deg):
    nc = Canvas(c.width, c.height)
    nc.img = c.img.rotate(deg, resample=Image.Resampling.NEAREST, expand=False)
    return nc


def dir_frames(base, direction):
    if direction == "right":
        return [f.copy() for f in base]
    if direction == "up":
        return [rot(f, 90) for f in base]
    if direction == "left":
        return [rot(f, 180) for f in base]
    if direction == "down":
        return [rot(f, 270) for f in base]
    raise ValueError(direction)


def main():
    side = [fly(i) for i in range(6)]
    hit = [impact(i) for i in range(5)]
    anims = [
        ("fly", side, 20, True),
        ("fly_right", side, 20, True),
        ("fly_up", dir_frames(side, "up"), 20, True),
        ("fly_left", dir_frames(side, "left"), 20, True),
        ("fly_down", dir_frames(side, "down"), 20, True),
        ("impact", hit, 16, False),
    ]
    flat = [f for _, frames, _, _ in anims for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in anims)
    sheet = Canvas(cols * SIZE, len(anims) * SIZE)
    for row, (_, frames, _, _) in enumerate(anims):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=5)
    for anim, frames, fps, _ in anims:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=5)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": [f.copy() for f in frames], "fps": fps, "loop": loop,
                      "hitbox": {"shape": "circle" if n == "impact" else "rect",
                                 "center": [float(CX), float(CY)],
                                 "active": [0, len(frames) - 1]}}
                     for n, frames, fps, loop in anims],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
