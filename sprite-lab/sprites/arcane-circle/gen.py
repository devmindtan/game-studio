#!/usr/bin/env python3
"""Generator cho sprite "arcane-circle": vòng phép AOE duy trì của hệ pháp sư.

  cast  6 frame một lần: vòng tròn ma thuật khắc trên mặt đất hiện dần;
  loop  8 frame lặp: ấn chú xoay, rune phát sáng, năng lượng dâng lên;
  end   5 frame một lần: ánh sáng mờ và tắt.

Neo (24, 24) tại tâm vòng tròn (sprite 48x48, nhìn từ trên/xéo).

Chạy:  gamekit art run arcane-circle
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

NAME = "arcane-circle"
SIZE = 48
CX, CY = 24, 26
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
GLOW = "#e0c8ff"
VIO = "#b06cff"
VIO_M = "#7c3aed"
DEEP = "#3b1d6b"


def p(c, x, y, col):
    c.pixel(x, y, col)


def ellipse_pts(cx, cy, rx, ry, step=6):
    a = 0
    while a < 360:
        rad = math.radians(a)
        yield (round(cx + math.cos(rad) * rx), round(cy + math.sin(rad) * ry), a)
        a += step


def ring(c, cx, cy, rx, ry, col, step=6):
    for x, y, _ in ellipse_pts(cx, cy, rx, ry, step):
        p(c, x, y, col)


def star(c, cx, cy, r, rot, col):
    # ngôi sao 6 cánh trong vòng tròn (2 tam giác)
    for off in (0, 60):
        pts = []
        for i in range(3):
            a = math.radians(rot + off + i * 120)
            pts.append((round(cx + math.cos(a) * r), round(cy + math.sin(a) * r * 0.45)))
        for i in range(3):
            c.line(pts[i][0], pts[i][1], pts[(i + 1) % 3][0], pts[(i + 1) % 3][1], col)


def runes(c, phase, rx=16, ry=7):
    for k in range(8):
        a = math.radians(phase * 20 + k * 45)
        x = round(CX + math.cos(a) * rx)
        y = round(CY + math.sin(a) * ry)
        col = CORE if (k + phase) % 4 == 0 else GLOW if (k + phase) % 2 == 0 else VIO
        p(c, x, y, col)
        p(c, x + 1, y, col)


def base(c, phase, alpha=1.0):
    ring(c, CX, CY, 18, 8, DEEP, step=4)
    ring(c, CX, CY, 15, 6, VIO_M, step=5)
    ring(c, CX, CY, 10, 4, VIO, step=6)
    star(c, CX, CY, 9, phase * 15, VIO_M)
    runes(c, phase)
    # glow nền
    fill = Canvas(c.width, c.height)
    fill.ellipse(CX - 14, CY - 6, CX + 14, CY + 6, "#7c3aed18")
    c.paste(fill)


def cast(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        ring(c, CX, CY, 6, 3, DEEP, step=10)
        p(c, CX, CY, VIO_M)
        return c
    rxs = (9, 12, 15, 17, 18)
    rys = (4, 5, 6, 7, 8)
    rx, ry = rxs[i - 1], rys[i - 1]
    ring(c, CX, CY, rx, ry, VIO_M, step=6)
    if i >= 2:
        ring(c, CX, CY, max(4, rx - 5), max(2, ry - 2), VIO, step=8)
    if i >= 3:
        star(c, CX, CY, 7, i * 10, VIO_M)
    if i >= 4:
        runes(c, i)
    if i == 5:
        fill = Canvas(c.width, c.height)
        fill.ellipse(CX - 12, CY - 5, CX + 12, CY + 5, "#7c3aed14")
        c.paste(fill)
    return c


def loop(i):
    c = Canvas(SIZE, SIZE)
    base(c, i)
    # hạt năng lượng bay lên từ vòng tròn
    for k in range(5):
        a = math.radians(k * 72 + i * 10)
        x = round(CX + math.cos(a) * (8 + k % 3))
        y = CY - 2 - ((i + k * 2) % 10)
        if 4 <= y < CY:
            p(c, x, y, CORE if k == 0 else GLOW)
    if i % 4 == 0:
        fill = Canvas(c.width, c.height)
        fill.ellipse(CX - 10, CY - 12, CX + 10, CY + 4, "#b06cff14")
        c.paste(fill)
    return c


def end(i):
    c = Canvas(SIZE, SIZE)
    if i <= 1:
        ring(c, CX, CY, 18 - i * 2, 8 - i, VIO_M if i == 0 else DEEP, step=6)
        ring(c, CX, CY, 12 - i * 2, 5, DEEP, step=8)
        runes(c, 8 + i)
    elif i == 2:
        ring(c, CX, CY, 14, 6, DEEP, step=8)
        star(c, CX, CY, 6, 40, DEEP)
    elif i == 3:
        ring(c, CX, CY, 10, 4, DEEP, step=10)
    else:
        for x, y, _ in ellipse_pts(CX, CY, 8, 3, step=20):
            p(c, x, y, DEEP)
    # hạt tàn rơi
    for k in range(4):
        a = math.radians(k * 90 + 30)
        x = round(CX + math.cos(a) * (6 + i))
        y = CY - 4 + i * 2
        if y < CY + 4:
            p(c, x, y, VIO_M if i < 3 else DEEP)
    return c


ANIMATIONS = [
    ("cast", [cast(i) for i in range(6)], 12, False),
    ("loop", [loop(i) for i in range(8)], 10, True),
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
    preview([sheet], HERE / "preview.png", scale=4)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=4)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop,
                      "hitbox": {"shape": "rect", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1]}}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
