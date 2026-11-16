#!/usr/bin/env python3
"""Generator cho sprite "arcane-bolt": tia phép mà pháp sư bắn ra.

Hai animation trong một dải:
  fly    6 frame lặp: đầu đạn sáng, đuôi lửa phía sau, tàn lửa nhấp nháy;
  impact 6 frame một lần: chớp sáng, vòng xung kích loang ra, tàn lửa tắt dần.

Đầu đạn quay sang phải (khớp hướng nhìn của mage). Điểm neo (11, 10) là tâm
đầu đạn, nên game đặt viên đạn đúng vị trí đầu gậy / điểm va chạm, lật hình
theo hướng bay bằng SpriteAnchor như mọi sprite khác.

Chạy:  gamekit art run arcane-bolt
"""

import math
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "arcane-bolt"
SIZE = 20
CX, CY = 11, 10          # tâm đầu đạn, cũng là điểm neo
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

# Cùng họ màu với quả cầu trên gậy của mage: lõi trắng, thân xanh, viền tím.
CORE = "#ffffff"
MAGIC = "#7ef0ff"
MAGIC_MID = "#37b9e8"
MAGIC_DEEP = "#8b5cf6"
MAGIC_DIM = "#5a3fb0"
DARK = "#1b1030"


def p(c, x, y, col):
    c.pixel(x, y, col)


def glow(c, x, y, r, col, col2=None):
    """Vòng mờ quanh đầu đạn; mỗi vòng một canvas riêng để alpha cộng dồn."""
    ring = Canvas(c.width, c.height)
    ring.ellipse(x - r, y - r, x + r, y + r, col)
    if col2:
        ring.ellipse(x - r + 1, y - r + 1, x + r - 1, y + r - 1, col2)
    c.paste(ring)


def head(c, x, y):
    """Đầu đạn hình giọt: lõi trắng lệch phải, thân xanh, viền tím loang phía sau."""
    c.ellipse(x - 4, y - 3, x + 2, y + 3, MAGIC_DEEP)
    c.ellipse(x - 3, y - 2, x + 2, y + 2, MAGIC_MID)
    c.ellipse(x - 2, y - 2, x + 2, y + 1, MAGIC)
    c.rect(x - 1, y - 1, x, y, CORE)
    p(c, x + 1, y, CORE)
    p(c, x + 2, y, MAGIC)


def tail(c, x, y, phase, length=5):
    """Đuôi lửa phía sau, hơi lượn theo pha để 6 frame không giống hệt nhau."""
    for i in range(length):
        tx = x - 4 - i
        ty = y + ((-1, 0, 1, 0)[(i + phase) % 4])
        col = MAGIC if i < 2 else MAGIC_MID if i < 4 else MAGIC_DEEP
        p(c, tx, ty, col)
        if i < 3:
            p(c, tx, ty + 1, MAGIC_DIM)


def embers(c, x, y, phase):
    """Hai tàn lửa gần, nhấp nháy theo pha."""
    for k, (dx, dy) in enumerate(((-6, -3), (-8, 2))):
        if (phase + k) % 3 != 2:
            p(c, x + dx, y + dy, CORE if k == 0 else MAGIC)


def fly(i):
    c = Canvas(SIZE, SIZE)
    glow(c, CX, CY, 5, "#7ef0ff20")
    tail(c, CX, CY, i, length=5 + (i % 2))
    head(c, CX, CY)
    embers(c, CX, CY, i)
    return c


def impact(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:  # chớp trắng
        glow(c, CX, CY, 4, "#ffffff40")
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, MAGIC)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, CORE)
        for dx, dy in ((4, 0), (-4, 0), (0, 4), (0, -4)):
            c.line(CX, CY, CX + dx, CY + dy, MAGIC)
        return c
    if i == 1:  # vòng xung kích đầu tiên
        c.ellipse(CX - 5, CY - 5, CX + 5, CY + 5, MAGIC, fill=False)
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, MAGIC_MID)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, CORE)
        for dx, dy in ((6, 0), (-6, 0), (0, 6), (0, -6), (4, 4), (-4, -4)):
            c.line(CX + dx, CY + dy, CX + dx + sign(dx), CY + dy + sign(dy), MAGIC)
        return c
    if i == 2:  # vòng loang rộng, lõi tắt dần
        c.ellipse(CX - 8, CY - 8, CX + 8, CY + 8, MAGIC_MID, fill=False)
        c.ellipse(CX - 5, CY - 5, CX + 5, CY + 5, MAGIC_DEEP, fill=False)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, MAGIC)
        p(c, CX, CY, CORE)
        for dx, dy in ((9, 0), (-9, 0), (0, 9), (0, -9), (6, 6), (-6, -6),
                       (6, -6), (-6, 6)):
            p(c, CX + dx, CY + dy, MAGIC)
        return c
    if i == 3:  # vòng vỡ thành tàn lửa
        for dx, dy in ((8, -3), (-8, 2), (3, 8), (-4, -8), (7, 6), (-7, -6)):
            p(c, CX + dx, CY + dy, MAGIC_DEEP)
        c.ellipse(CX - 6, CY - 6, CX + 6, CY + 6, MAGIC_DEEP, fill=False)
        p(c, CX - 1, CY, MAGIC)
        p(c, CX + 1, CY + 1, MAGIC_MID)
        return c
    if i == 4:  # tàn lửa rơi
        for dx, dy in ((9, -4), (-9, 3), (4, 9), (-5, -9), (6, 8), (-6, -7)):
            p(c, CX + dx, CY + dy, MAGIC_DIM)
        p(c, CX + 2, CY - 1, MAGIC_DEEP)
        return c
    # i == 5: gần như tan hết
    for dx, dy in ((10, -5), (-10, 4), (5, 10), (-6, -10)):
        p(c, CX + dx, CY + dy, MAGIC_DIM)
    return c


def sign(v):
    return 1 if v > 0 else -1 if v < 0 else 0


from PIL import Image


def rot(c, deg):
    """Rotate canvas by deg CCW (90/180/270), keeping size."""
    nc = Canvas(c.width, c.height)
    nc.img = c.img.rotate(deg, resample=Image.Resampling.NEAREST, expand=False)
    return nc


def fly_side_frames():
    return [fly(i) for i in range(6)]


def dir_frames(base_frames, direction):
    if direction == "right":
        return [f.copy() for f in base_frames]
    if direction == "up":
        return [rot(f, 90) for f in base_frames]
    if direction == "left":
        return [rot(f, 180) for f in base_frames]
    if direction == "down":
        return [rot(f, 270) for f in base_frames]
    raise ValueError(direction)


_SIDE = fly_side_frames()

ANIMATIONS = [
    ("fly", dir_frames(_SIDE, "right"), 14, True),
    ("fly_right", dir_frames(_SIDE, "right"), 14, True),
    ("fly_left", dir_frames(_SIDE, "left"), 14, True),
    ("fly_up", dir_frames(_SIDE, "up"), 14, True),
    ("fly_down", dir_frames(_SIDE, "down"), 14, True),
    ("impact", [impact(i) for i in range(6)], 16, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=6)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=6)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": lp,
                      "hitbox": {"shape": "rect", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1] if n.startswith("fly") else [0, len(f)-1]}}
                     for n, f, fps, lp in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
