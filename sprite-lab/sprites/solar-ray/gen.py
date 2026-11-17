#!/usr/bin/env python3
"""Tia laser mặt trời vàng, có nút sáng nhấp nháy (projectile, 4 hướng + impact)."""

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

NAME = "solar-ray"
SIZE = 32
CX, CY = 16, 16
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

# Tia plasma dày, rung nhẹ: lõi trắng, thân xanh lá, quầng mờ.
CORE = "#ffffff"
BODY = "#ffe066"
MID = "#ffb020"
DEEP = "#a85a10"
GLOW = "#ffb02033"


def glow(c, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(CX - r, CY - r, CX + r, CY + r, col)
    c.paste(ring)


def fly(i):
    c = Canvas(SIZE, SIZE)
    glow(c, 7, GLOW)
    for k in range(9):
        x = CX - 4 - k
        p(c, x, CY, MID if k < 4 else DEEP)
    # chùm plasma rung theo pha (dao động 1px quanh trục)
    for x in range(CX - 4, CX + 11):
        wave = (0, -1, 0, 1, 0, -1)[(x + i) % 6]
        y = CY + wave
        p(c, x, y - 2, DEEP)
        p(c, x, y - 1, MID)
        p(c, x, y, BODY)
        p(c, x, y + 1, MID)
        p(c, x, y + 2, DEEP)
        if x >= CX - 1:
            p(c, x, y, CORE)
    p(c, CX + 11, CY, CORE)
    p(c, CX + 12, CY, BODY)
    # nut sang nhap nhay doc chum tia
    for nx in (CX, CX + 4, CX + 8):
        if (nx + i) % 2 == 0:
            p(c, nx, CY - 3, CORE)
            p(c, nx, CY + 3, CORE)
    return c


def impact(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        glow(c, 8, "#ffffff66")
        c.ellipse(CX - 4, CY - 4, CX + 4, CY + 4, CORE)
        for dx, dy in ((6, 0), (-6, 0), (0, 6), (0, -6)):
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
        for dx, dy in ((10, 0), (-10, 0), (0, 10), (0, -10), (7, 7), (-7, -7)):
            p(c, CX + dx, CY + dy, BODY)
        return c
    if i == 3:
        c.ellipse(CX - 7, CY - 7, CX + 7, CY + 7, DEEP, fill=False)
        for dx, dy in ((8, -4), (-8, 4), (4, 8), (-4, -8)):
            p(c, CX + dx, CY + dy, MID)
        return c
    for dx, dy in ((11, -5), (-11, 5), (5, 11), (-5, -11)):
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
        ("fly", side, 16, True),
        ("fly_right", side, 16, True),
        ("fly_up", dir_frames(side, "up"), 16, True),
        ("fly_left", dir_frames(side, "left"), 16, True),
        ("fly_down", dir_frames(side, "down"), 16, True),
        ("impact", hit, 16, False),
    ]
    # 16 flight directions (lib/dirs16.py): a bigger square frame, fly_000..fly_337
    global SIZE, ANCHOR, CX, CY
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
    import dirs16  # noqa: E402
    anims, ANCHOR = dirs16.with_directions(anims, ANCHOR, 44)
    SIZE = 44
    CX, CY = ANCHOR
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
