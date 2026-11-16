#!/usr/bin/env python3
"""Generator cho sprite "magnetic-shield": khiên từ trường bao bọc quanh pháp sư.

  form   6 frame một lần: màn từ trường hiện dần và khép kín quanh người;
  loop   8 frame lặp: màng khiên lục giác xoay tại chỗ, tia từ trường chạy viền;
  break  6 frame một lần: nứt vỡ và tan rã tại chỗ (không bay đi).

Neo (16, 16) tại tâm khiên (sprite 32x32), để game đặt bao quanh nhân vật.

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
    """Hiện dần và khép kín quanh người, không phóng ra từ tâm."""
    c = Canvas(SIZE, SIZE)
    r = 11
    rot = i * 6
    if i == 0:
        # viền mờ xuất hiện rải rác quanh vị trí khiên
        glow(c, CX, CY, 6, "#2f8fd614")
        for k in (0, 2, 4):
            a = math.radians(rot + k * 60)
            x = round(CX + math.cos(a) * r)
            y = round(CY + math.sin(a) * r)
            p(c, x, y, CYAN_M)
            p(c, x + (1 if math.cos(a) > 0 else -1), y, BLUE)
        return c
    if i == 1:
        glow(c, CX, CY, 6, "#2f8fd618")
        # các đoạn cung lục giác bắt đầu khép
        pts = hex_points(CX, CY, r, rot)
        for k in (0, 1, 3, 4):
            x0, y0 = pts[k]; x1, y1 = pts[(k + 1) % 6]
            c.line(x0, y0, x1, y1, BLUE)
        for k in range(6):
            if k % 2 == 0:
                a = math.radians(rot + k * 60)
                p(c, round(CX + math.cos(a) * r), round(CY + math.sin(a) * r), CYAN)
        return c
    if i == 2:
        glow(c, CX, CY, 6, "#2f8fd61a")
        draw_poly(c, hex_points(CX, CY, r, rot), BLUE)
        # lồng trong còn chập chờn
        pts = hex_points(CX, CY, r - 2, -rot * 0.5)
        for k in (0, 2, 3, 5):
            x0, y0 = pts[k]; x1, y1 = pts[(k + 1) % 6]
            c.line(x0, y0, x1, y1, CYAN_M)
        return c
    if i == 3:
        glow(c, CX, CY, 6, "#2f8fd61c")
        draw_poly(c, hex_points(CX, CY, r, rot), BLUE)
        draw_poly(c, hex_points(CX, CY, r - 2, -rot * 0.6), CYAN_M)
        for k in range(6):
            a = math.radians(rot + k * 60)
            p(c, round(CX + math.cos(a) * r), round(CY + math.sin(a) * r), CYAN)
        return c
    # i == 4: kín hoàn chỉnh, màng trong mờ xuất hiện
    field(c, 1, r=11, inner=True)
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
    """Nứt và tan rã tại chỗ, mảnh rơi xuống thay vì bay đi."""
    c = Canvas(SIZE, SIZE)
    if i == 0:
        field(c, 7, r=11, inner=True)
        for k in range(6):
            a = math.radians(k * 60)
            p(c, round(CX + math.cos(a) * 11), round(CY + math.sin(a) * 11), CORE)
        return c
    if i == 1:
        # nứt lan trên bề mặt, vẫn giữ hình bao bọc
        draw_poly(c, hex_points(CX, CY, 11, 50), CYAN_M)
        draw_poly(c, hex_points(CX, CY, 9, -20), BLUE)
        for a in (20, 80, 140, 220, 300):
            rad = math.radians(a)
            c.line(round(CX + math.cos(rad) * 4), round(CY + math.sin(rad) * 4),
                   round(CX + math.cos(rad) * 10), round(CY + math.sin(rad) * 10), CYAN)
        return c
    frags = [(9, -2), (-9, 0), (5, -8), (-6, 7), (7, 6), (-7, -6), (2, 9), (-3, -9)]
    if i == 2:
        # vỡ thành mảnh nhưng còn quanh vị trí cũ
        for dx, dy in frags:
            p(c, CX + dx, CY + dy, CYAN)
            p(c, CX + dx // 2, CY + dy // 2, CYAN_M)
        glow(c, CX, CY, 3, "#7ef0ff18")
        return c
    if i == 3:
        # mảnh rơi/xẹp xuống nhẹ
        for dx, dy in frags:
            p(c, CX + dx, CY + dy + 1, BLUE)
            p(c, CX + dx // 2, CY + dy // 2 + 1, CYAN_M)
        return c
    if i == 4:
        for j, (dx, dy) in enumerate(frags):
            if j % 2 == 0:
                p(c, CX + dx, CY + dy + 2, DEEP)
            else:
                p(c, CX + dx // 2, CY + dy // 2 + 2, BLUE)
        return c
    for j, (dx, dy) in enumerate(frags):
        if j % 3 == 0:
            p(c, CX + dx // 2, CY + dy // 2 + 3, DEEP)
    return c


ANIMATIONS = [
    ("form", [form(i) for i in range(6)], 12, False),
    ("loop", [loop(i) for i in range(8)], 10, True),
    ("break", [break_anim(i) for i in range(6)], 12, False),
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
