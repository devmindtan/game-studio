#!/usr/bin/env python3
"""Generator cho sprite "whirlwind": xoáy chém AOE của hệ đại kiếm.

  spin    8 frame lặp: vòng chém xoay quanh người, vệt thép và gió bao tròn.

Neo (24, 24) tại tâm (sprite 48x48) để đặt quanh nhân vật.

Chạy:  gamekit art run whirlwind
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

NAME = "whirlwind"
SIZE = 48
CX, CY = 24, 24
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
EDGE = "#e8f4ff"
STEEL = "#aabbd0"
WIND = "#cfe8ff"
WIND_D = "#7fa6c9"


def p(c, x, y, col):
    c.pixel(x, y, col)


def arc_stroke(c, cx, cy, r, a0, a1, col, step=4):
    a = a0
    while a <= a1:
        rad = math.radians(a)
        p(c, round(cx + math.cos(rad) * r), round(cy + math.sin(rad) * r), col)
        a += step


def spin(i):
    c = Canvas(SIZE, SIZE)
    base = i * 45
    # hai cung chém đối xứng quay tròn
    for k, (r, col, span) in enumerate(((18, WIND_D, 120), (15, EDGE, 90), (12, CORE, 60))):
        a0 = base + k * 10
        arc_stroke(c, CX, CY, r, a0, a0 + span, col, step=3)
        arc_stroke(c, CX, CY, r, a0 + 180, a0 + 180 + span, col, step=3)
    # vòng gió ngoài
    arc_stroke(c, CX, CY, 20, base + 30, base + 110, WIND, step=5)
    arc_stroke(c, CX, CY, 20, base + 210, base + 290, WIND, step=5)
    # tia lửa/gió nhỏ
    for k in range(6):
        a = math.radians(base * 2 + k * 60)
        r = 16 + (k % 2) * 3
        p(c, round(CX + math.cos(a) * r), round(CY + math.sin(a) * r), EDGE if k % 2 else STEEL)
    # tâm gió mờ
    c.ellipse(CX - 4, CY - 4, CX + 4, CY + 4, "#cfe8ff22")
    return c


ANIMATIONS = [
    ("spin", [spin(i) for i in range(8)], 14, True),
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
