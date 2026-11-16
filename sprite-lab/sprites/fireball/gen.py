#!/usr/bin/env python3
"""Generator cho sprite "fireball": cầu lửa bay và nổ.

  fly     6 frame lặp: lõi vàng trắng, lửa cam đỏ cuộn phía sau;
  impact  7 frame một lần: nổ chớp, sóng lửa lan, tro tàn rơi.

Bay sang phải. Neo (10, 12) là tâm cầu lửa.

Chạy:  gamekit art run fireball
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

NAME = "fireball"
SIZE = 24
CX, CY = 10, 12
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#fffbe0"
YEL = "#ffd84a"
ORG = "#ff8a2a"
RED = "#e0421b"
DARK = "#7a1a0a"
SMOKE = "#5a2a1a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def glow(c, x, y, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(x - r, y - r, x + r, y + r, col)
    c.paste(ring)


def fire_core(c, x, y, wobble=0):
    glow(c, x, y, 6, "#ff6a1a22")
    c.ellipse(x - 4, y - 4 + wobble, x + 3, y + 4, RED)
    c.ellipse(x - 3, y - 3 + wobble, x + 3, y + 3, ORG)
    c.ellipse(x - 2, y - 2, x + 2, y + 2, YEL)
    c.rect(x - 1, y - 1, x, y, CORE)
    p(c, x + 1, y - 1, CORE)


def flame_tail(c, x, y, phase):
    # lửa cuộn về phía sau (trái), nhấp nháy theo pha
    tongues = [
        (-6, -2, 3, RED), (-7, 0, 4, RED), (-6, 2, 3, ORG),
        (-9, -1, 3, ORG), (-10, 1, 3, DARK), (-11, 0, 2, DARK),
    ]
    for k, (dx, dy, ln, col) in enumerate(tongues):
        off = ((-1, 0, 1)[(k + phase) % 3])
        for i in range(ln):
            p(c, x + dx - i, y + dy + off, col if i < 2 else DARK)
    # tia lửa nhỏ
    for k, (dx, dy) in enumerate(((-12, -3), (-13, 2), (-14, 0), (-9, -4))):
        if (phase + k) % 2 == 0:
            p(c, x + dx, y + dy, YEL if k % 2 == 0 else ORG)


def fly(i):
    c = Canvas(SIZE, SIZE)
    flame_tail(c, CX, CY, i)
    fire_core(c, CX, CY, wobble=(0, -1, 0, 1, 0, -1)[i])
    # tia lửa phía trước
    for k, (dx, dy) in enumerate(((4, -2), (5, 1), (4, 3))):
        if (i + k) % 3 == 0:
            p(c, CX + dx, CY + dy, YEL)
    return c


def impact(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        glow(c, CX, CY, 5, "#fff0a055")
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, YEL)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, CORE)
        return c
    if i == 1:
        glow(c, CX, CY, 7, "#ff8a2a44")
        c.ellipse(CX - 5, CY - 5, CX + 5, CY + 5, ORG)
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, YEL)
        c.ellipse(CX - 1, CY - 1, CX + 1, CY + 1, CORE)
        return c
    if i == 2:
        glow(c, CX, CY, 8, "#ff6a1a33")
        c.ellipse(CX - 7, CY - 7, CX + 7, CY + 7, RED)
        c.ellipse(CX - 5, CY - 5, CX + 5, CY + 5, ORG)
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, YEL)
        c.ellipse(CX - 1, CY - 1, CX + 1, CY + 1, CORE)
        for dx, dy in ((8, 0), (-8, 0), (0, 8), (0, -8), (6, 6), (-6, -6), (6, -6), (-6, 6)):
            p(c, CX + dx, CY + dy, ORG)
        return c
    if i == 3:
        c.ellipse(CX - 8, CY - 8, CX + 8, CY + 8, DARK, fill=False)
        c.ellipse(CX - 6, CY - 6, CX + 6, CY + 6, RED, fill=False)
        c.ellipse(CX - 4, CY - 4, CX + 4, CY + 4, ORG)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, YEL)
        for dx, dy in ((9, -2), (-9, 2), (2, 9), (-3, -9), (7, 7), (-7, -7)):
            p(c, CX + dx, CY + dy, RED)
        return c
    if i == 4:
        c.ellipse(CX - 9, CY - 9, CX + 9, CY + 9, SMOKE, fill=False)
        c.ellipse(CX - 5, CY - 5, CX + 5, CY + 5, DARK, fill=False)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, ORG)
        for dx, dy in ((10, -3), (-10, 3), (3, 10), (-4, -10), (8, 6), (-8, -6)):
            p(c, CX + dx, CY + dy, DARK)
        return c
    if i == 5:
        c.ellipse(CX - 7, CY - 7, CX + 7, CY + 7, SMOKE, fill=False)
        p(c, CX, CY, RED)
        for dx, dy in ((10, -4), (-10, 4), (4, 10), (-5, -10), (8, 8)):
            p(c, CX + dx, CY + dy, SMOKE)
        return c
    for dx, dy in ((11, -4), (-11, 5), (5, 11), (-6, -11)):
        p(c, CX + dx, CY + dy, SMOKE)
    return c


from PIL import Image


def rot(c, deg):
    nc = Canvas(c.width, c.height)
    nc.img = c.img.rotate(deg, resample=Image.Resampling.NEAREST, expand=False)
    return nc


_SIDE = [fly(i) for i in range(6)]

def dir_frames(base_frames, direction):
    if direction == "right": return [f.copy() for f in base_frames]
    if direction == "up": return [rot(f, 90) for f in base_frames]
    if direction == "left": return [rot(f, 180) for f in base_frames]
    if direction == "down": return [rot(f, 270) for f in base_frames]
    raise ValueError(direction)


ANIMATIONS = [
    ("fly", dir_frames(_SIDE, "right"), 14, True),
    ("fly_right", dir_frames(_SIDE, "right"), 14, True),
    ("fly_left", dir_frames(_SIDE, "left"), 14, True),
    ("fly_up", dir_frames(_SIDE, "up"), 14, True),
    ("fly_down", dir_frames(_SIDE, "down"), 14, True),
    ("impact", [impact(i) for i in range(7)], 14, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=7)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=7)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": lp,
                      "hitbox": {"shape": "circle", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1] if n.startswith("fly") else [0, min(2, len(f)-1)]}}
                     for n, f, fps, lp in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
