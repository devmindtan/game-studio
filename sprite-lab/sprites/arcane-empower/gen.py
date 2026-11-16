#!/usr/bin/env python3
"""Generator cho sprite "arcane-empower": hiệu ứng buff cường hóa phép thuật.

  cast     6 frame một lần: ấn chú tụ năng lượng từ dưới lên quanh pháp sư;
  loop     8 frame lặp: ấn chú và tinh thể ma lực xoay quanh, hào quang tím;
  release  5 frame một lần: bùng năng lượng rồi tan.

Neo (16, 22) gần thân trên (sprite 32x32) để hiệu ứng quấn quanh người.

Chạy:  gamekit art run arcane-empower
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

NAME = "arcane-empower"
SIZE = 32
CX, CY = 16, 22
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
LILAC = "#e9b8ff"
VIO = "#b06cff"
VIO_M = "#7c3aed"
DEEP = "#3b1d6b"
GOLD = "#ffd36b"


def p(c, x, y, col):
    c.pixel(x, y, col)


def glow(c, x, y, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(x - r, y - r, x + r, y + r, col)
    c.paste(ring)


def sigil(c, x, y, r, rot, col, inner=True):
    # ấn chú tam giác lồng nhau
    for i in range(3):
        a0 = math.radians(rot + i * 120)
        a1 = math.radians(rot + (i + 1) * 120)
        x0, y0 = round(x + math.cos(a0) * r), round(y + math.sin(a0) * r)
        x1, y1 = round(x + math.cos(a1) * r), round(y + math.sin(a1) * r)
        c.line(x0, y0, x1, y1, col)
    if inner and r > 4:
        for i in range(3):
            a0 = math.radians(-rot + i * 120 + 60)
            a1 = math.radians(-rot + (i + 1) * 120 + 60)
            x0, y0 = round(x + math.cos(a0) * (r - 3)), round(y + math.sin(a0) * (r - 3))
            x1, y1 = round(x + math.cos(a1) * (r - 3)), round(y + math.sin(a1) * (r - 3))
            c.line(x0, y0, x1, y1, VIO_M if col == VIO else col)


def orbit_crystals(c, phase, r=11):
    for k in range(4):
        a = math.radians(phase * 45 + k * 90)
        x = round(CX + math.cos(a) * r)
        y = round(CY + math.sin(a) * (r * 0.55))
        col = GOLD if k % 2 == 0 else LILAC
        p(c, x, y, col)
        p(c, x, y - 1, col)
        p(c, x - 1, y, VIO if k % 2 else VIO_M)
        p(c, x + 1, y, VIO if k % 2 else VIO_M)
        p(c, x, y + 1, VIO_M)


def rising_motes(c, phase, count=5):
    for k in range(count):
        a = math.radians(k * 73)
        x = round(CX + math.cos(a) * (6 + k % 3))
        y = CY + 4 - ((phase * 2 + k * 4) % 20)
        if 2 <= y <= SIZE - 3:
            p(c, x, y, CORE if k % 2 == 0 else LILAC)


def cast(i):
    c = Canvas(SIZE, SIZE)
    # năng lượng tụ từ dưới lên
    for k in range(6):
        a = math.radians(k * 60 + i * 10)
        rr = 12 - i
        x = round(CX + math.cos(a) * rr)
        y = round(CY + math.sin(a) * rr * 0.6 + (4 - i))
        if 2 <= y <= SIZE - 2:
            p(c, x, y, VIO if k % 2 else VIO_M)
    if i >= 2:
        glow(c, CX, CY, 3 + (i - 2), "#b06cff22")
        sigil(c, CX, CY, 4 + (i - 2), i * 12, VIO_M, inner=i >= 4)
    if i >= 4:
        orbit_crystals(c, i, r=9)
        p(c, CX, CY - 2, CORE)
    return c


def loop(i):
    c = Canvas(SIZE, SIZE)
    glow(c, CX, CY, 7, "#7c3aed18")
    # cột hào quang mờ
    col = Canvas(c.width, c.height)
    col.ellipse(CX - 8, CY - 10, CX + 8, CY + 8, "#b06cff14")
    c.paste(col)
    sigil(c, CX, CY - 1, 7, i * 15, VIO, inner=True)
    sigil(c, CX, CY - 1, 4, -i * 20, LILAC, inner=False)
    orbit_crystals(c, i, r=11)
    rising_motes(c, i, count=6)
    if i % 4 == 0:
        glow(c, CX, CY - 2, 4, "#e9b8ff22")
    return c


def release(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        glow(c, CX, CY, 8, "#e9b8ff33")
        sigil(c, CX, CY, 8, 80, LILAC, inner=True)
        orbit_crystals(c, 7, r=12)
        return c
    if i == 1:
        glow(c, CX, CY, 9, "#b06cff33")
        c.ellipse(CX - 9, CY - 9, CX + 9, CY + 9, VIO, fill=False)
        c.ellipse(CX - 6, CY - 6, CX + 6, CY + 6, LILAC, fill=False)
        for k in range(8):
            a = math.radians(k * 45)
            p(c, round(CX + math.cos(a) * 10), round(CY + math.sin(a) * 10), CORE)
        return c
    r = 8 + i
    c.ellipse(CX - r, CY - r, CX + r, CY + r, VIO_M if i < 3 else DEEP, fill=False)
    for k in range(8):
        a = math.radians(k * 45 + i * 10)
        rr = r + 1
        p(c, round(CX + math.cos(a) * rr), round(CY + math.sin(a) * rr), VIO if i < 3 else DEEP)
    for k in range(4):
        a = math.radians(k * 90 + 20)
        rr = 5 + i
        p(c, round(CX + math.cos(a) * rr), round(CY + math.sin(a) * rr), GOLD if i == 2 else VIO_M)
    return c


ANIMATIONS = [
    ("cast", [cast(i) for i in range(6)], 12, False),
    ("loop", [loop(i) for i in range(8)], 10, True),
    ("release", [release(i) for i in range(5)], 12, False),
]


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
                    [{"name": n, "frames": f, "fps": fps, "loop": loop,
                      "hitbox": {"shape": "rect", "center": [float(ANCHOR[0]), float(ANCHOR[1])], "active": [0, len(f)-1]}}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
