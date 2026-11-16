#!/usr/bin/env python3
"""Generator cho sprite "cleave-wave": sóng chém AOE của hệ đại kiếm.

  sweep/sweep_right  7 frame một lần: quét/chém sang phải;
  sweep_left         7 frame một lần: quét/chém sang trái;
  sweep_up           7 frame một lần: quét/chém lên trên;
  sweep_down         7 frame một lần: quét/chém xuống dưới.

AOE định hướng cho game top-down. Neo tâm (sprite 48x48).

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
from PIL import Image

NAME = "cleave-wave"
SIZE = 48
ANCHOR = (24.0, 24.0)
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


def sweep_base(i):
    c = Canvas(SIZE, SIZE)
    ox, oy = 8, 24
    if i == 0:
        arc_stroke(c, ox, oy, 10, -60, -10, EDGE, 2)
        arc_stroke(c, ox, oy, 8, -55, -15, CORE, 1)
        return c
    if i == 1:
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
    for dx, dy in ((36, -2), (38, 0), (36, 2), (32, -8), (32, 8)):
        p(c, ox + dx, oy + dy, SLASH)
    return c


def rot(c, deg):
    nc = Canvas(c.width, c.height)
    nc.img = c.img.rotate(deg, resample=Image.Resampling.NEAREST, expand=False)
    return nc


_SIDE = [sweep_base(i) for i in range(7)]

def dir_frames(base_frames, direction):
    if direction == "right": return [f.copy() for f in base_frames]
    if direction == "up": return [rot(f, 90) for f in base_frames]
    if direction == "left": return [rot(f, 180) for f in base_frames]
    if direction == "down": return [rot(f, 270) for f in base_frames]
    raise ValueError(direction)


ANIMATIONS = [
    ("sweep", dir_frames(_SIDE, "right"), 16, False),
    ("sweep_right", dir_frames(_SIDE, "right"), 16, False),
    ("sweep_left", dir_frames(_SIDE, "left"), 16, False),
    ("sweep_up", dir_frames(_SIDE, "up"), 16, False),
    ("sweep_down", dir_frames(_SIDE, "down"), 16, False),
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
    meta_anims = []
    for n, f, fps, loop in ANIMATIONS:
        meta_anims.append({"name": n, "frames": f, "fps": fps, "loop": loop,
                           "hitbox": {"shape": "rect", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                      "active": [1, min(4, len(f)-1)]}})
    write_anim_meta(OUT / f"{NAME}.json", meta_anims, anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
