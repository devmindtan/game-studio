#!/usr/bin/env python3
"""Generator cho sprite "ground-slam": đập đất AOE của hệ đại kiếm.

  slam    8 frame một lần: điểm va chạm lóe sáng, sóng xung kích tròn lan ra
          mặt đất kèm đá vụn và bụi.

Neo (24, 26) tại điểm va chạm trên mặt đất (sprite 48x32, nhìn từ trên/xéo nhẹ).

Chạy:  gamekit art run ground-slam
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

NAME = "ground-slam"
W, H = 48, 32
CX, CY = 24, 26
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#fff6d8"
FLASH = "#ffd36b"
RING = "#d9a441"
DUST = "#b08a5a"
ROCK = "#7a5a3a"
CRACK = "#4a3524"


def p(c, x, y, col):
    c.pixel(x, y, col)


def ring(c, cx, cy, rx, ry, col):
    c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, col, fill=False)


def slam(i):
    c = Canvas(W, H)
    if i == 0:
        # va chạm
        c.ellipse(CX - 4, CY - 2, CX + 4, CY + 2, FLASH)
        c.ellipse(CX - 2, CY - 1, CX + 2, CY + 1, CORE)
        for dx, dy in ((6, 0), (-6, 0), (0, -3), (0, 3)):
            p(c, CX + dx, CY + dy, FLASH)
        return c
    if i == 1:
        ring(c, CX, CY, 7, 3, RING)
        c.ellipse(CX - 3, CY - 1, CX + 3, CY + 1, FLASH)
        p(c, CX, CY, CORE)
        for dx, dy in ((9, -1), (-9, 0), (0, -4), (2, -5), (-3, 3)):
            p(c, CX + dx, CY + dy, DUST)
        return c
    if i == 2:
        ring(c, CX, CY, 11, 4, RING)
        ring(c, CX, CY, 6, 2, DUST)
        c.line(CX - 10, CY, CX - 4, CY, CRACK)
        c.line(CX + 4, CY, CX + 10, CY, CRACK)
        c.line(CX, CY - 1, CX - 6, CY - 4, CRACK)
        c.line(CX, CY - 1, CX + 7, CY - 4, CRACK)
        for dx, dy in ((-8, -5), (5, -6), (10, -2), (-12, 1), (0, 4)):
            p(c, CX + dx, CY + dy, ROCK)
        return c
    if i == 3:
        ring(c, CX, CY, 15, 5, DUST)
        ring(c, CX, CY, 10, 3, RING)
        c.line(CX - 14, CY, CX - 6, CY, CRACK)
        c.line(CX + 6, CY, CX + 14, CY, CRACK)
        c.line(CX - 2, CY, CX - 10, CY - 5, CRACK)
        c.line(CX + 2, CY, CX + 11, CY - 5, CRACK)
        for dx, dy in ((-11, -7), (8, -8), (14, -3), (-16, 1), (3, 5), (-4, 4)):
            p(c, CX + dx, CY + dy, ROCK if dx % 2 else DUST)
        return c
    if i == 4:
        ring(c, CX, CY, 18, 6, DUST)
        ring(c, CX, CY, 13, 4, DUST)
        c.line(CX - 17, CY, CX - 9, CY, CRACK)
        c.line(CX + 9, CY, CX + 17, CY, CRACK)
        for dx, dy in ((-14, -8), (11, -9), (17, -4), (-19, 2), (6, 5), (-7, 4)):
            p(c, CX + dx, CY + dy, DUST)
        return c
    if i == 5:
        ring(c, CX, CY, 20, 6, DUST)
        c.line(CX - 18, CY, CX - 12, CY, CRACK)
        c.line(CX + 12, CY, CX + 18, CY, CRACK)
        for dx, dy in ((-16, -9), (14, -10), (19, -5), (-20, 3), (8, 5)):
            p(c, CX + dx, CY + dy, DUST)
        return c
    if i == 6:
        ring(c, CX, CY, 21, 7, DUST)
        for dx, dy in ((-17, -9), (16, -10), (20, -5), (-21, 3)):
            p(c, CX + dx, CY + dy, DUST)
        return c
    for dx, dy in ((-18, -9), (18, -10), (21, -5)):
        p(c, CX + dx, CY + dy, DUST)
    return c


ANIMATIONS = [
    ("slam", [slam(i) for i in range(8)], 14, False),
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
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
