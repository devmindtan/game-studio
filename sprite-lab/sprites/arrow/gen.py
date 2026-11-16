#!/usr/bin/env python3
"""Generator cho sprite "arrow": mũi tên cơ bản của hệ cung.

  fly     4 frame lặp: mũi tên bay thẳng, rung nhẹ;
  impact  5 frame một lần: cắm vào mục tiêu và mảnh gỗ văng.

Bay sang phải. Neo (10, 4) tại đầu mũi tên (sprite 20x8).

Chạy:  gamekit art run arrow
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("no workspace")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "arrow"
W, H = 20, 8
ANCHOR = (17.0, 4.0)  # tip
HERE = Path(__file__).resolve().parent
OUT = HERE

WOOD = "#8a5a2e"; WOOD_D = "#563418"; STEEL = "#c5d4e6"; TIP = "#e8f4ff"; FEATHER = "#d94a4a"; FEATHER_D = "#8a2f2f"


def p(c, x, y, col): c.pixel(x, y, col)


def draw_arrow(c, ox=0, oy=0):
    y = 4 + oy
    # shaft
    c.line(2 + ox, y, 15 + ox, y, WOOD)
    c.line(2 + ox, y, 14 + ox, y, WOOD_D)
    # tip
    c.line(15 + ox, y, 17 + ox, y, STEEL)
    p(c, 18 + ox, y, TIP); p(c, 17 + ox, y - 1, STEEL); p(c, 17 + ox, y + 1, STEEL)
    # fletching
    c.line(2 + ox, y, 4 + ox, y - 2, FEATHER)
    c.line(2 + ox, y, 4 + ox, y + 2, FEATHER_D)
    p(c, 1 + ox, y - 1, FEATHER); p(c, 1 + ox, y + 1, FEATHER_D)


def fly(i):
    c = Canvas(W, H)
    oy = (0, -1, 0, 1)[i]
    # speed streak
    for x in (0, 2):
        if (i + x) % 2 == 0: p(c, x, 4 + oy, WOOD_D)
    draw_arrow(c, oy=oy)
    return c


def impact(i):
    c = Canvas(W, H)
    if i == 0:
        draw_arrow(c)
        p(c, 19, 4, TIP)
        return c
    if i == 1:
        # stuck, head buried
        y = 4
        c.line(2, y, 14, y, WOOD); c.line(2, y, 13, y, WOOD_D)
        c.line(14, y, 16, y, STEEL)
        c.line(2, y, 4, y - 2, FEATHER); c.line(2, y, 4, y + 2, FEATHER_D)
        for dx, dy in ((17, 3), (17, 5), (18, 4)): p(c, dx, dy, STEEL)
        return c
    # shaft wobble/settle + splinters
    y = 4 + (1 if i == 2 else 0)
    c.line(2, y, 14, y, WOOD); c.line(2, y, 13, y, WOOD_D)
    c.line(14, y, 16, y + (1 if i < 4 else 0), STEEL)
    c.line(2, y, 4, y - 2, FEATHER); c.line(2, y, 4, y + 2, FEATHER_D)
    if i == 2:
        for dx, dy in ((17, 2), (18, 5)): p(c, dx, dy, WOOD_D)
    if i == 3:
        p(c, 18, 3, WOOD_D)
    return c


ANIMATIONS = [
    ("fly", [fly(i) for i in range(4)], 16, True),
    ("impact", [impact(i) for i in range(5)], 14, False),
]


def main():
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(fr) for _, fr, _, _ in ANIMATIONS)
    sheet = Canvas(cols * W, len(ANIMATIONS) * H)
    for r, (_, fr, _, _) in enumerate(ANIMATIONS): sheet.paste(strip(fr), 0, r * H)
    preview([sheet], HERE / "preview.png", scale=8)
    for a, fr, fps, _ in ANIMATIONS: gif(fr, HERE / f"{a}.gif", fps=fps, scale=8)
    write_anim_meta(OUT / f"{NAME}.json", [{"name": n, "frames": f, "fps": fps, "loop": lp} for n, f, fps, lp in ANIMATIONS], anchor=ANCHOR)
    print(OUT / "preview.png")


if __name__ == "__main__":
    main()
