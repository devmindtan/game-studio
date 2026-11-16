#!/usr/bin/env python3
"""Generator cho sprite "magnetic-shield": khiên từ trường của pháp sư.

  form   5 frame một lần: vòng năng lượng hình thành từ tâm ra;
  loop   8 frame lặp: màng khiên lục giác xoay, tia từ trường chạy dọc viền;
  break  6 frame một lần: vỡ mảnh, tia điện tắt dần.

Neo (16, 16) tại tâm khiên (sprite 32x32), để game đặt quanh nhân vật.

Chạy:  gamekit art run magnetic-shield
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

NAME = "magnetic-shield"
SIZE = 32
CX, CY = 16, 16
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#e8fbff"
CYAN = "#7ef0ff"
CYAN_M = "#37b9e8"
BLUE = "#2f6bd6"
DEEP = "#1a2f66"
FILL = "#2f8fd622"


def p(c, x, y, col):
    c.pixel(x, y, col)


def glow(c, x, y, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(x - r, y - r, x + r, y + r, col)
    c.paste(ring)


def hex_points(cx, cy, r, rot=0.0):
    pts = []
    for i in range(6):
        a = math.radians(rot + i * 60)
        pts.append((round(cx + math.cos(a) * r), round(cy + math.sin(a) * r)))
    return pts


def draw_poly(c, pts, col):
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        c.line(x0, y0, x1, y1, col)


def field(c, phase, r=11, strength=2, inner=True):
    rot = phase * 7
    # màng trong mờ
    if inner:
        fill = Canvas(c.width, c.height)
        pts = hex_points(CX, CY, r - 1, rot)
        # fill xấp xỉ bằng các vòng ellipse mờ
        fill.ellipse(CX - r + 2, CY - r + 3, CX + r - 2, CY + r - 3, FILL)
        c.paste(fill)
    draw_poly(c, hex_points(CX, CY, r, rot), BLUE)
    draw_poly(c, hex_points(CX, CY, r - 2, -rot * 0.6), CYAN_M)
    if r > 8:
        draw_poly(c, hex_points(CX, CY, r - 4, rot * 0.4), DEEP)
    # tia từ trường chạy dọc cạnh
    for k in range(6):
        a = math.radians(rot + k * 60 + phase * 20)
        rr = r - (k % 3)
        x = round(CX + math.cos(a) * rr)
        y = round(CY + math.sin(a) * rr)
        p(c, x, y, CORE if (k + phase) % 2 == 0 else CYAN)
    # hạt năng lượng lượn quanh
    for k in range(4):
        a = math.radians(phase * 45 + k * 90 + 20)
        rr = r + 1
        x = round(CX + math.cos(a) * rr)
        y = round(CY + math.sin(a) * rr)
        if (phase + k) % 3 != 2:
            p(c, x, y, CYAN if k % 2 else CYAN_M)


def form(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        glow(c, CX, CY, 3, "#7ef0ff33")
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, CYAN_M)
        p(c, CX, CY, CORE)
        return c
    r = 4 + i * 2
    glow(c, CX, CY, r // 2, "#37b9e822")
    draw_poly(c, hex_points(CX, CY, r, i * 10), CYAN_M if i < 3 else BLUE)
    draw_poly(c, hex_points(CX, CY, max(2, r - 2), -i * 8), CYAN)
    if i >= 2:
        for k in range(6):
            a = math.radians(k * 60 + i * 15)
            p(c, round(CX + math.cos(a) * r), round(CY + math.sin(a) * r), CORE)
    if i == 4:
        field(c, 0, r=11, inner=True)
    return c


def loop(i):
    c = Canvas(SIZE, SIZE)
    glow(c, CX, CY, 6, "#2f8fd618")
    field(c, i, r=11, inner=True)
    # nhịp sáng nhẹ bên trong
    if i % 4 == 0:
        glow(c, CX, CY, 4, "#7ef0ff18")
    return c


def break_anim(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        field(c, 7, r=11, inner=True)
        for k in range(6):
            a = math.radians(k * 60)
            p(c, round(CX + math.cos(a) * 11), round(CY + math.sin(a) * 11), CORE)
        return c
    if i == 1:
        # nứt
        draw_poly(c, hex_points(CX, CY, 11, 50), CYAN_M)
        for a in (20, 80, 140, 220, 300):
            rad = math.radians(a)
            c.line(CX, CY, round(CX + math.cos(rad) * 10), round(CY + math.sin(rad) * 10), BLUE)
        return c
    frags = [(10, 0), (-10, 1), (5, -9), (-6, 9), (8, 7), (-8, -7), (3, 10), (-4, -10)]
    if i == 2:
        for dx, dy in frags:
            p(c, CX + dx, CY + dy, CYAN)
            p(c, CX + dx//2, CY + dy//2, CYAN_M)
        return c
    if i == 3:
        for dx, dy in frags:
            p(c, CX + dx + (1 if dx > 0 else -1), CY + dy + (1 if dy > 0 else -1), BLUE)
        return c
    if i == 4:
        for dx, dy in frags[::2]:
            p(c, CX + dx + (2 if dx > 0 else -2), CY + dy, DEEP)
        return c
    for dx, dy in frags[1::3]:
        p(c, CX + dx + (2 if dx > 0 else -2), CY + dy, DEEP)
    return c


ANIMATIONS = [
    ("form", [form(i) for i in range(5)], 14, False),
    ("loop", [loop(i) for i in range(8)], 10, True),
    ("break", [break_anim(i) for i in range(6)], 14, False),
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
