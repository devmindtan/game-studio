#!/usr/bin/env python3
"""Generator cho sprite "flame-geyser": trụ lửa phun lên từ dưới đất (AOE, mage).

  erupt   8 frame một lần: mặt đất rạn, lửa phụt thẳng lên thành trụ rồi lắng.

Neo (24, 44) tại mặt đất (sprite 48x48). Lửa bốc lên phía trên neo.

Chạy:  gamekit art run flame-geyser
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "flame-geyser"
W, H = 48, 48
CX, GY = 24, 44
ANCHOR = (float(CX), float(GY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#fffbe0"
YEL = "#ffd84a"
ORG = "#ff8a2a"
RED = "#e0421b"
DARK = "#7a1a0a"
ROCK = "#5a3a2a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def ground(c):
    c.line(8, GY, W - 9, GY, ROCK)
    c.line(10, GY + 1, W - 11, GY + 1, "#3a2218")


def flame_column(c, top_y, width, phase):
    # trụ lửa từ GY lên top_y
    for y in range(top_y, GY):
        t = (GY - y) / max(1, GY - top_y)
        w = max(1, int(width * (0.5 + 0.5 * (1 - t))))
        wobble = (1 if (y + phase) % 4 == 0 else 0)
        for x in range(CX - w, CX + w + 1):
            dx = abs(x - CX)
            if dx == w:
                col = DARK if t > 0.3 else RED
            elif dx >= w - 1:
                col = RED if t > 0.5 else ORG
            elif t > 0.7:
                col = YEL
            elif t > 0.4:
                col = ORG
            else:
                col = RED
            c.pixel(x + wobble, y, col)
        if t > 0.8:
            c.pixel(CX, y, CORE)


def erupt(i):
    c = Canvas(W, H)
    ground(c)
    if i == 0:
        # nứt và than hồng
        for x in (CX - 3, CX, CX + 3):
            c.line(x, GY, x, GY - 2, DARK)
        c.ellipse(CX - 4, GY - 1, CX + 4, GY, RED)
        p(c, CX, GY - 2, ORG)
        return c
    if i == 1:
        flame_column(c, GY - 10, 3, i)
        for x in (CX - 6, CX + 6):
            p(c, x, GY - 4, ORG)
        return c
    if i == 2:
        flame_column(c, GY - 22, 4, i)
        for dx, dy in ((-7, -8), (7, -10), (-5, -16), (6, -14)):
            p(c, CX + dx, GY + dy, YEL if dy < -12 else ORG)
        return c
    if i == 3:
        # đỉnh trụ
        flame_column(c, GY - 34, 5, i)
        for dx, dy in ((-8, -12), (8, -14), (-6, -22), (7, -24), (0, -36)):
            p(c, CX + dx, GY + dy, YEL if dy < -20 else ORG)
        return c
    if i == 4:
        flame_column(c, GY - 30, 5, i)
        for dx, dy in ((-9, -14), (9, -16), (-6, -24), (6, -26)):
            p(c, CX + dx, GY + dy, ORG)
        return c
    if i == 5:
        flame_column(c, GY - 22, 4, i)
        c.ellipse(CX - 6, GY - 24, CX + 6, GY - 18, "#ff8a2a44")
        for dx, dy in ((-8, -16), (8, -18)):
            p(c, CX + dx, GY + dy, RED)
        return c
    if i == 6:
        flame_column(c, GY - 12, 3, i)
        for dx in (-5, 0, 5):
            p(c, CX + dx, GY - 14, DARK)
        return c
    c.ellipse(CX - 4, GY - 4, CX + 4, GY, RED)
    c.ellipse(CX - 2, GY - 3, CX + 2, GY, ORG)
    for dx, dy in ((-4, -6), (4, -7), (0, -8)):
        p(c, CX + dx, GY + dy, DARK)
    return c


ANIMATIONS = [
    ("erupt", [erupt(i) for i in range(8)], 12, False),
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
