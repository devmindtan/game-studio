#!/usr/bin/env python3
"""Generator cho sprite "meteor-burst": vụ nổ thiên thạch AOE của hệ pháp sư.

  blast   9 frame một lần: nổ lớn tại vùng mục tiêu, lửa và sóng xung kích lan
          trên mặt đất, khói bụi bốc lên.

Neo (24, 28) tại tâm vùng nổ trên mặt đất (sprite 48x40).

Chạy:  gamekit art run meteor-burst
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

NAME = "meteor-burst"
W, H = 48, 40
CX, CY = 24, 28
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#fffbe0"
YEL = "#ffd84a"
ORG = "#ff8a2a"
RED = "#e0421b"
DARK = "#7a1a0a"
SMOKE = "#5a3a2a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def ring(c, cx, cy, rx, ry, col):
    c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, col, fill=False)


def blast(i):
    c = Canvas(W, H)
    if i == 0:
        c.ellipse(CX - 5, CY - 3, CX + 5, CY + 2, YEL)
        c.ellipse(CX - 3, CY - 2, CX + 3, CY + 1, CORE)
        for dx, dy in ((0, -8), (-4, -6), (4, -6), (7, 0), (-7, 0)):
            p(c, CX + dx, CY + dy, FLASH if (dx+dy)%2==0 else YEL)
        return c
    if i == 1:
        c.ellipse(CX - 8, CY - 5, CX + 8, CY + 3, ORG)
        c.ellipse(CX - 5, CY - 4, CX + 5, CY + 2, YEL)
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 1, CORE)
        ring(c, CX, CY, 10, 3, RED)
        for dx, dy in ((0, -12), (-6, -10), (6, -10), (10, -4), (-10, -4), (12, 0), (-12, 0)):
            p(c, CX + dx, CY + dy, ORG)
        return c
    if i == 2:
        c.ellipse(CX - 11, CY - 8, CX + 11, CY + 4, RED)
        c.ellipse(CX - 7, CY - 6, CX + 7, CY + 3, ORG)
        c.ellipse(CX - 4, CY - 4, CX + 4, CY + 1, YEL)
        c.ellipse(CX - 2, CY - 3, CX + 2, CY, CORE)
        ring(c, CX, CY, 14, 4, DARK)
        for dx, dy in ((0, -16), (-8, -14), (8, -14), (14, -6), (-14, -6), (16, 0), (-16, 0), (10, 3), (-10, 3)):
            p(c, CX + dx, CY + dy, RED if abs(dy) > 5 else SMOKE)
        return c
    if i == 3:
        c.ellipse(CX - 13, CY - 7, CX + 13, CY + 5, DARK)
        c.ellipse(CX - 9, CY - 6, CX + 9, CY + 3, RED)
        c.ellipse(CX - 5, CY - 5, CX + 5, CY + 2, ORG)
        c.ellipse(CX - 2, CY - 3, CX + 2, CY, YEL)
        ring(c, CX, CY, 17, 5, SMOKE)
        for dx, dy in ((0, -18), (-10, -16), (10, -16), (17, -8), (-17, -8), (18, 1), (-18, 1)):
            p(c, CX + dx, CY + dy, SMOKE)
        return c
    if i == 4:
        c.ellipse(CX - 11, CY - 6, CX + 11, CY + 5, DARK)
        c.ellipse(CX - 6, CY - 5, CX + 6, CY + 2, RED)
        c.ellipse(CX - 3, CY - 3, CX + 3, CY, ORG)
        ring(c, CX, CY, 19, 6, SMOKE)
        for dx, dy in ((-12, -16), (12, -17), (18, -10), (-18, -9), (20, 2), (-20, 2), (0, -20)):
            p(c, CX + dx, CY + dy, SMOKE)
        return c
    if i == 5:
        c.ellipse(CX - 8, CY - 4, CX + 8, CY + 4, DARK)
        c.ellipse(CX - 4, CY - 3, CX + 4, CY + 1, RED)
        ring(c, CX, CY, 20, 6, SMOKE)
        for dx, dy in ((-14, -17), (14, -18), (19, -11), (-19, -10), (21, 3), (-21, 3), (0, -22)):
            p(c, CX + dx, CY + dy, SMOKE)
        return c
    if i == 6:
        c.ellipse(CX - 5, CY - 2, CX + 5, CY + 3, DARK)
        ring(c, CX, CY, 21, 6, SMOKE)
        for dx, dy in ((-15, -18), (15, -19), (20, -12), (-20, -11), (0, -24)):
            p(c, CX + dx, CY + dy, SMOKE)
        return c
    if i == 7:
        ring(c, CX, CY, 21, 6, SMOKE)
        for dx, dy in ((-16, -19), (16, -20), (0, -25), (21, -12), (-21, -11)):
            p(c, CX + dx, CY + dy, SMOKE)
        return c
    for dx, dy in ((-16, -20), (16, -21), (0, -26)):
        p(c, CX + dx, CY + dy, SMOKE)
    return c

FLASH = "#ffe08a"

ANIMATIONS = [
    ("blast", [blast(i) for i in range(9)], 13, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * W, len(ANIMATIONS) * H)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * H)
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
