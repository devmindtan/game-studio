#!/usr/bin/env python3
"""Generator cho sprite "cleave-wave": sóng chém AOE của hệ đại kiếm.

  sweep   7 frame một lần: vệt chém hình cung quét ngang rồi lan thành sóng khí
          hình lưỡi liềm về phía trước, kèm tia lửa va chạm.

Neo (8, 24) gần tay cầm/điểm xuất phát bên trái, để sóng vung ra phía trước (phải).
Sprite 48x48.

Chạy:  gamekit art run cleave-wave
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

NAME = "cleave-wave"
SIZE = 48
ANCHOR = (8.0, 24.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
EDGE = "#e8f4ff"
STEEL = "#b8c7d9"
SLASH = "#7fa6c9"
GLOW = "#9fd7ff55"
SPARK = "#ffd36b"


def p(c, x, y, col):
    c.pixel(x, y, col)


def arc_stroke(c, cx, cy, r, a0, a1, col, thick=1):
    a = a0
    while a <= a1:
        rad = math.radians(a)
        for t in range(thick):
            rr = r - t
            p(c, round(cx + math.cos(rad) * rr), round(cy + math.sin(rad) * rr), col)
        a += 3


def sweep(i):
    c = Canvas(SIZE, SIZE)
    ox, oy = 8, 24
    if i == 0:
        # khởi động vệt chém
        arc_stroke(c, ox, oy, 10, -60, -10, EDGE, 2)
        arc_stroke(c, ox, oy, 8, -55, -15, CORE, 1)
        return c
    if i == 1:
        # quét qua giữa
        glow = Canvas(SIZE, SIZE)
        arc_stroke(glow, ox, oy, 18, -70, 40, GLOW, 4)
        c.paste(glow)
        arc_stroke(c, ox, oy, 18, -70, 40, SLASH, 3)
        arc_stroke(c, ox, oy, 16, -65, 35, EDGE, 2)
        arc_stroke(c, ox, oy, 14, -60, 30, CORE, 1)
        for dx, dy in ((12, -6), (14, 0), (12, 6)):
            p(c, ox + dx, oy + dy, SPARK)
        return c
    if i == 2:
        # cung rộng nhất
        glow = Canvas(SIZE, SIZE)
        arc_stroke(glow, ox, oy, 26, -75, 60, GLOW, 5)
        c.paste(glow)
        arc_stroke(c, ox, oy, 26, -75, 60, SLASH, 3)
        arc_stroke(c, ox, oy, 23, -70, 55, EDGE, 2)
        arc_stroke(c, ox, oy, 20, -60, 45, CORE, 1)
        for dx, dy in ((18, -10), (22, -2), (22, 4), (18, 10), (10, 14)):
            p(c, ox + dx, oy + dy, SPARK)
        return c
    if i == 3:
        # sóng khí tách ra phía trước
        arc_stroke(c, ox + 4, oy, 30, -55, 55, SLASH, 2)
        arc_stroke(c, ox + 6, oy, 26, -50, 50, EDGE, 2)
        arc_stroke(c, ox + 8, oy, 22, -40, 40, CORE, 1)
        for dx, dy in ((26, -8), (30, 0), (26, 8), (20, -14), (20, 14)):
            p(c, ox + dx, oy + dy, STEEL)
        return c
    if i == 4:
        arc_stroke(c, ox + 8, oy, 32, -45, 45, STEEL, 2)
        arc_stroke(c, ox + 10, oy, 28, -35, 35, EDGE, 1)
        for dx, dy in ((30, -6), (34, 0), (30, 6), (24, -12), (24, 12)):
            p(c, ox + dx, oy + dy, SLASH)
        return c
    if i == 5:
        arc_stroke(c, ox + 12, oy, 34, -35, 35, SLASH, 1)
        for dx, dy in ((34, -4), (36, 0), (34, 4), (28, -10), (28, 10)):
            p(c, ox + dx, oy + dy, STEEL)
        return c
    # tàn sóng
    for dx, dy in ((36, -2), (38, 0), (36, 2), (32, -8), (32, 8)):
        p(c, ox + dx, oy + dy, SLASH)
    return c


ANIMATIONS = [
    ("sweep", [sweep(i) for i in range(7)], 16, False),
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
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
