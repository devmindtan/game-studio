#!/usr/bin/env python3
"""Generator cho sprite "heal-bloom": hiệu ứng hồi máu/buff trị liệu.

  cast  5 frame một lần: tia sáng xanh tụ lại và nở hoa ánh sáng;
  loop  8 frame lặp: vòng chữa lành xoay, hạt sáng và dấu cộng bay lên;
  end   5 frame một lần: tàn sáng lắng xuống.

Neo (16, 26) gần chân (sprite 32x32) để hào quang bao quanh mục tiêu.

Chạy:  gamekit art run heal-bloom
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

NAME = "heal-bloom"
SIZE = 32
CX, GY = 16, 26
ANCHOR = (float(CX), float(GY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
MINT = "#c9ffe8"
GREEN = "#6ff2b6"
TEAL = "#2ec48f"
DEEP = "#1a6b4d"
GOLD = "#ffe6a0"


def p(c, x, y, col):
    c.pixel(x, y, col)


def glow(c, x, y, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(x - r, y - r, x + r, y + r, col)
    c.paste(ring)


def cross(c, x, y, col):
    p(c, x, y, col); p(c, x - 1, y, col); p(c, x + 1, y, col)
    p(c, x, y - 1, col); p(c, x, y + 1, col)


def base_ring(c, phase, r=10):
    ring = Canvas(c.width, c.height)
    ring.ellipse(CX - r, GY - 3, CX + r, GY + 3, "#6ff2b622")
    c.paste(ring)
    c.ellipse(CX - r, GY - 3, CX + r, GY + 3, TEAL, fill=False)
    for k in range(6):
        a = math.radians(phase * 25 + k * 60)
        x = round(CX + math.cos(a) * r)
        y = round(GY + math.sin(a) * 3)
        p(c, x, y, GOLD if k % 3 == 0 else MINT)


def petals(c, cx, cy, r, rot, col):
    for k in range(4):
        a = math.radians(rot + k * 90)
        x = round(cx + math.cos(a) * r)
        y = round(cy + math.sin(a) * r)
        c.ellipse(x - 2, y - 2, x + 2, y + 2, col)


def cast(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        for k in range(6):
            a = math.radians(k * 60)
            p(c, round(CX + math.cos(a) * 8), round(GY - 4 + math.sin(a) * 4), MINT)
        return c
    if i <= 2:
        glow(c, CX, GY - 4, 3 + i, "#c9ffe833")
        for k in range(6):
            a = math.radians(k * 60 + i * 8)
            rr = 8 - i * 2
            p(c, round(CX + math.cos(a) * rr), round(GY - 4 + math.sin(a) * rr * 0.6), GREEN)
        c.ellipse(CX - 2, GY - 6, CX + 2, GY - 2, MINT)
        p(c, CX, GY - 4, CORE)
        return c
    base_ring(c, i, r=8 + (i - 3) * 2)
    glow(c, CX, GY - 6, 4, "#6ff2b62a")
    petals(c, CX, GY - 8, 4, i * 10, GREEN)
    cross(c, CX, GY - 8, CORE)
    for k in range(4):
        a = math.radians(k * 90 + 45)
        p(c, round(CX + math.cos(a) * 6), round(GY - 8 + math.sin(a) * 4), MINT)
    return c


def loop(i):
    c = Canvas(SIZE, SIZE)
    glow(c, CX, GY - 8, 7, "#2ec48f18")
    base_ring(c, i, r=10)
    petals(c, CX, GY - 10, 4, i * 12, GREEN if i % 2 == 0 else TEAL)
    cross(c, CX, GY - 10, CORE)
    # tia sáng dọc
    c.line(CX, GY - 16, CX, GY - 13, MINT)
    c.line(CX - 1, GY - 10, CX + 1, GY - 10, GOLD)
    # hạt và dấu cộng bay lên
    for k in range(4):
        y = GY - 4 - ((i * 2 + k * 5) % 18)
        x = CX - 7 + (k % 4) * 5 - (0 if k != 1 else 1)
        if 3 <= y <= GY - 2:
            if k % 2 == 0:
                cross(c, x, y, MINT if k == 0 else GREEN)
            else:
                p(c, x, y, CORE)
    for k, (dx, dy) in enumerate(((-9, -12), (9, -16), (0, -20))):
        yy = dy - (i % 3)
        if (i + k) % 3 != 2 and GY + yy > 2:
            p(c, CX + dx, GY + yy, GOLD)
    return c


def end(i):
    c = Canvas(SIZE, SIZE)
    r = 10 - i * 2
    if r > 1:
        c.ellipse(CX - r, GY - 3, CX + r, GY + 3, TEAL if i < 3 else DEEP, fill=False)
    if i <= 2:
        cross(c, CX, GY - 10 + i * 2, MINT if i < 2 else GREEN)
    for k, (dx, dy0) in enumerate(((-7, -14), (7, -18), (-3, -10), (4, -20), (0, -16))):
        y = dy0 + i * 3
        if GY + y < GY:
            p(c, CX + dx, GY + y, GREEN if i < 2 else TEAL if i < 4 else DEEP)
    return c


ANIMATIONS = [
    ("cast", [cast(i) for i in range(5)], 12, False),
    ("loop", [loop(i) for i in range(8)], 11, True),
    ("end", [end(i) for i in range(5)], 12, False),
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
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
