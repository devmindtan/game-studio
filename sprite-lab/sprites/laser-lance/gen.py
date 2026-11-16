#!/usr/bin/env python3
"""Laser xuyên dài xanh dương (projectile, 4 hướng + impact)."""

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

NAME = "laser-lance"
SIZE = 32
CX, CY = 16, 16
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

# Laser xuyên dài, mảnh: chùm tia thẳng, đầu nhọn, đuôi dài.
CORE = "#ffffff"
BODY = "#6ff2ff"
MID = "#29b6f6"
DEEP = "#1b5fbf"
GLOW = "#29b6f633"


def glow(c, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(CX - r, CY - r, CX + r, CY + r, col)
    c.paste(ring)


def fly(i):
    c = Canvas(SIZE, SIZE)
    glow(c, 6, GLOW)
    # đuôi dài mỏng dần
    for k in range(10):
        x = CX - 5 - k
        p(c, x, CY, MID if k < 5 else DEEP)
        if k < 3:
            p(c, x, CY - 1, DEEP)
            p(c, x, CY + 1, DEEP)
    # thân chùm tia
    for x in range(CX - 5, CX + 12):
        p(c, x, CY, BODY)
        if x > CX - 3:
            p(c, x, CY - 1, MID)
            p(c, x, CY + 1, MID)
    # lõi trắng chạy theo pha
    for x in range(CX - 2 + (i % 2), CX + 12):
        p(c, x, CY, CORE)
    # đầu xuyên nhọn
    p(c, CX + 12, CY, BODY)
    p(c, CX + 13, CY, CORE)
    p(c, CX + 14, CY, BODY)
    if i % 2:
        p(c, CX + 11, CY - 1, CORE)
        p(c, CX + 11, CY + 1, CORE)
    return c


def impact(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        glow(c, 8, "#ffffff66")
        c.ellipse(CX - 4, CY - 4, CX + 4, CY + 4, CORE)
        for dx, dy in ((7, 0), (-7, 0), (0, 7), (0, -7)):
            p(c, CX + dx, CY + dy, BODY)
        return c
    if i == 1:
        c.ellipse(CX - 6, CY - 6, CX + 6, CY + 6, BODY, fill=False)
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, CORE)
        return c
    if i == 2:
        c.ellipse(CX - 10, CY - 10, CX + 10, CY + 10, MID, fill=False)
        c.ellipse(CX - 5, CY - 5, CX + 5, CY + 5, BODY, fill=False)
        p(c, CX, CY, CORE)
        for dx, dy in ((11, 0), (-11, 0), (0, 11), (0, -11), (7, 7), (-7, -7)):
            p(c, CX + dx, CY + dy, BODY)
        return c
    if i == 3:
        c.ellipse(CX - 7, CY - 7, CX + 7, CY + 7, DEEP, fill=False)
        for dx, dy in ((9, -4), (-9, 4), (4, 9), (-4, -9)):
            p(c, CX + dx, CY + dy, MID)
        return c
    for dx, dy in ((12, -5), (-12, 5), (5, 12), (-5, -12)):
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
        ("fly", side, 18, True),
        ("fly_right", side, 18, True),
        ("fly_up", dir_frames(side, "up"), 18, True),
        ("fly_left", dir_frames(side, "left"), 18, True),
        ("fly_down", dir_frames(side, "down"), 18, True),
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
