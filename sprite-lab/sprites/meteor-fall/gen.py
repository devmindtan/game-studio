#!/usr/bin/env python3
"""Generator cho sprite "meteor-fall": thiên thạch rơi từ trên cao xuống (AOE).

  strike  9 frame một lần: thiên thạch rơi dọc từ trên xuống điểm va chạm,
          nổ và sóng xung kích lan ra mặt đất.

Neo (24, 52) tại điểm va chạm trên mặt đất (sprite 48x56).

Chạy:  gamekit art run meteor-fall
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

NAME = "meteor-fall"
W, H = 48, 56
CX, GY = 24, 52
ANCHOR = (float(CX), float(GY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#fffbe0"
YEL = "#ffd84a"
ORG = "#ff8a2a"
RED = "#e0421b"
DARK = "#6b1a0a"
ROCK = "#5a3a2a"
SMOKE = "#6b4a3a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def ring(c, cx, cy, rx, ry, col):
    c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, col, fill=False)


def meteor(c, x, y, r=4):
    c.ellipse(x - r, y - r, x + r, y + r, ROCK)
    c.ellipse(x - r + 1, y - r + 1, x + r - 1, y + r - 1, RED)
    c.ellipse(x - 2, y - 2, x + 1, y + 1, ORG)
    p(c, x - 1, y - 1, YEL)
    # đuôi lửa hướng lên trên
    for i in range(1, 10):
        tx = x + (1 if i % 3 == 0 else 0 if i % 3 == 1 else -1)
        ty = y - r - i
        if ty < 0:
            break
        col = ORG if i < 4 else RED if i < 7 else DARK
        p(c, tx, ty, col)
        if i < 5:
            p(c, tx + 1, ty, col)


def strike(i):
    c = Canvas(W, H)
    # vệt rơi / bóng trên đất
    if i <= 3:
        y = 6 + i * 10
        meteor(c, CX, y)
        # mục tiêu lóe nhẹ trên đất
        c.ellipse(CX - 4, GY - 1, CX + 4, GY + 1, "#ff8a2a33")
        p(c, CX, GY, YEL)
        return c
    if i == 4:
        # chạm đất
        meteor(c, CX, GY - 4, r=4)
        c.ellipse(CX - 6, GY - 2, CX + 6, GY + 1, YEL)
        c.ellipse(CX - 3, GY - 1, CX + 3, GY + 1, CORE)
        for dx, dy in ((8, 0), (-8, 0), (0, -6), (5, -4), (-5, -4)):
            p(c, CX + dx, GY + dy, ORG)
        return c
    if i == 5:
        c.ellipse(CX - 10, GY - 6, CX + 10, GY + 2, ORG)
        c.ellipse(CX - 6, GY - 4, CX + 6, GY + 1, YEL)
        c.ellipse(CX - 3, GY - 3, CX + 3, GY, CORE)
        ring(c, CX, GY, 12, 3, RED)
        for dx, dy in ((14, 0), (-14, 0), (0, -10), (8, -8), (-8, -8), (10, 2), (-10, 2)):
            p(c, CX + dx, GY + dy, RED)
        return c
    if i == 6:
        c.ellipse(CX - 12, GY - 8, CX + 12, GY + 3, RED)
        c.ellipse(CX - 7, GY - 6, CX + 7, GY + 2, ORG)
        c.ellipse(CX - 3, GY - 4, CX + 3, GY, YEL)
        ring(c, CX, GY, 16, 4, DARK)
        for dx, dy in ((17, 0), (-17, 0), (0, -14), (10, -10), (-10, -10), (12, 2), (-12, 2)):
            p(c, CX + dx, GY + dy, SMOKE)
        return c
    if i == 7:
        c.ellipse(CX - 9, GY - 6, CX + 9, GY + 3, DARK)
        c.ellipse(CX - 4, GY - 4, CX + 4, GY + 1, RED)
        ring(c, CX, GY, 18, 5, SMOKE)
        for dx, dy in ((19, 0), (-19, 0), (0, -16), (12, -12), (-12, -12)):
            p(c, CX + dx, GY + dy, SMOKE)
        return c
    ring(c, CX, GY, 20, 5, SMOKE)
    c.ellipse(CX - 5, GY - 3, CX + 5, GY + 2, DARK)
    for dx, dy in ((20, 0), (-20, 0), (0, -18)):
        p(c, CX + dx, GY + dy, SMOKE)
    return c


ANIMATIONS = [
    ("strike", [strike(i) for i in range(9)], 12, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * W, len(ANIMATIONS) * H)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * H)
    preview([sheet], HERE / "preview.png", scale=3)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=3)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop,
                      "hitbox": {"shape": "circle", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1]}}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
