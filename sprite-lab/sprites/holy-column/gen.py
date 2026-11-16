#!/usr/bin/env python3
"""Generator cho sprite "holy-column": cột thánh quang giáng xuống từ trên cao (AOE, mage).

  descend  8 frame một lần: ánh sáng hội tụ trên cao rồi dội thẳng xuống mặt đất
           thành cột sáng, tỏa hào quang rồi tan.

Neo (24, 52) tại điểm chạm đất (sprite 48x56).

Chạy:  gamekit art run holy-column
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

NAME = "holy-column"
W, H = 48, 56
CX, GY = 24, 52
ANCHOR = (float(CX), float(GY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
LIGHT = "#fff6bf"
GOLD = "#ffd36b"
GLOW = "#ffe8a855"
RING = "#ffd36b"


def p(c, x, y, col):
    c.pixel(x, y, col)


def ring(c, cx, cy, rx, ry, col):
    c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, col, fill=False)


def column(c, top, width, alpha_glow=True):
    if alpha_glow:
        g = Canvas(c.width, c.height)
        g.ellipse(CX - width - 3, top, CX + width + 3, GY + 1, GLOW)
        c.paste(g)
    for y in range(top, GY + 1):
        for x in range(CX - width, CX + width + 1):
            dx = abs(x - CX)
            if dx == width:
                c.pixel(x, y, GOLD)
            elif dx >= width - 1:
                c.pixel(x, y, LIGHT)
            else:
                c.pixel(x, y, CORE if (y % 3 != 0) else LIGHT)
    ring(c, CX, GY, width + 4, 2, GOLD)
    ring(c, CX, GY, width + 7, 3, LIGHT)


def descend(i):
    c = Canvas(W, H)
    if i == 0:
        # hội tụ trên cao
        c.ellipse(CX - 3, 2, CX + 3, 6, LIGHT)
        c.ellipse(CX - 1, 3, CX + 1, 5, CORE)
        ring(c, CX, GY, 5, 2, "#ffd36b44")
        return c
    if i == 1:
        # tia sáng bắt đầu dội xuống
        c.ellipse(CX - 2, 2, CX + 2, 6, CORE)
        c.line(CX, 6, CX, 28, LIGHT)
        c.line(CX - 1, 8, CX - 1, 22, GOLD)
        c.line(CX + 1, 10, CX + 1, 24, GOLD)
        ring(c, CX, GY, 6, 2, GOLD)
        return c
    if i == 2:
        # chạm đất, cột hình thành
        column(c, 4, 2, alpha_glow=True)
        return c
    if i == 3:
        # cột đầy đủ
        column(c, 0, 3, alpha_glow=True)
        for dx in (-10, 10):
            c.line(CX + dx, GY - 6, CX + dx, GY, GOLD)
        return c
    if i == 4:
        column(c, 0, 4, alpha_glow=True)
        ring(c, CX, GY, 14, 4, GOLD)
        for dx, dy in ((-12, -2), (12, -2), (-9, -8), (9, -10)):
            p(c, CX + dx, GY + dy, LIGHT)
        return c
    if i == 5:
        column(c, 0, 3, alpha_glow=True)
        ring(c, CX, GY, 16, 4, LIGHT)
        return c
    if i == 6:
        g = Canvas(c.width, c.height)
        g.ellipse(CX - 5, 6, CX + 5, GY + 1, "#ffe8a833")
        c.paste(g)
        for y in range(10, GY + 1):
            c.pixel(CX, y, LIGHT if y % 2 == 0 else GOLD)
            c.pixel(CX - 1, y, GOLD)
            c.pixel(CX + 1, y, GOLD)
        ring(c, CX, GY, 12, 3, GOLD)
        return c
    ring(c, CX, GY, 10, 3, GOLD)
    ring(c, CX, GY, 6, 2, LIGHT)
    for dx in (-8, 0, 8):
        p(c, CX + dx, GY - 4, GOLD)
    return c


ANIMATIONS = [
    ("descend", [descend(i) for i in range(8)], 12, False),
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
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
