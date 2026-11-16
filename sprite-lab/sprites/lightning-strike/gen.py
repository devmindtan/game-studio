#!/usr/bin/env python3
"""Generator cho sprite "lightning-strike": sét đánh thẳng từ trên xuống (AOE).

  strike  7 frame một lần: tia sét giáng từ đỉnh khung xuống điểm va chạm,
          lóe sáng và tỏa điện trên mặt đất.

Neo (24, 52) tại điểm đánh trên mặt đất (sprite 48x56).

Chạy:  gamekit art run lightning-strike
"""

import sys
from pathlib import Path
import random


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "lightning-strike"
W, H = 48, 56
CX, GY = 24, 52
ANCHOR = (float(CX), float(GY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
BOLT = "#f8ff9a"
BOLT_M = "#ffd84a"
ELEC = "#8ad8ff"
ELEC_D = "#3a7bd5"


def p(c, x, y, col):
    c.pixel(x, y, col)


def zigzag(c, x0, y0, x1, y1, col, seed=0):
    rnd = random.Random(seed)
    x, y = x0, y0
    while y < y1:
        nx = x + rnd.choice([-2, -1, 0, 1, 2])
        ny = min(y + rnd.choice([3, 4, 5]), y1)
        nx = max(6, min(W - 7, nx))
        c.line(x, y, nx, ny, col)
        x, y = nx, ny


def strike(i):
    c = Canvas(W, H)
    if i == 0:
        # báo hiệu trên trời và điểm đất
        for x, y in ((CX - 2, 4), (CX + 1, 3), (CX, 5)):
            p(c, x, y, ELEC)
        c.ellipse(CX - 3, GY - 1, CX + 3, GY + 1, "#8ad8ff33")
        p(c, CX, GY, ELEC)
        return c
    if i == 1:
        # tia sét giáng xuống
        zigzag(c, CX, 2, CX, GY, ELEC_D, seed=3)
        zigzag(c, CX, 2, CX + 1, GY, BOLT_M, seed=7)
        zigzag(c, CX - 1, 4, CX, GY, CORE, seed=11)
        c.ellipse(CX - 4, GY - 2, CX + 4, GY + 1, ELEC)
        return c
    if i == 2:
        # lóe cực đại
        flash = Canvas(W, H)
        flash.ellipse(CX - 10, GY - 6, CX + 10, GY + 2, "#f8ff9a22")
        c.paste(flash)
        zigzag(c, CX, 0, CX, GY, BOLT, seed=3)
        zigzag(c, CX + 1, 1, CX, GY, CORE, seed=5)
        # nhánh phụ
        c.line(CX - 2, 18, CX - 8, 26, ELEC)
        c.line(CX + 2, 28, CX + 9, 34, ELEC)
        c.ellipse(CX - 6, GY - 3, CX + 6, GY + 1, BOLT_M)
        c.ellipse(CX - 3, GY - 2, CX + 3, GY, CORE)
        return c
    if i == 3:
        zigzag(c, CX, 2, CX, GY, BOLT_M, seed=3)
        for dx, dy in ((8, -1), (-8, 0), (12, 1), (-12, 1), (5, -3), (-6, -3)):
            c.line(CX, GY, CX + dx, GY + dy, ELEC)
        c.ellipse(CX - 4, GY - 2, CX + 4, GY + 1, BOLT)
        return c
    if i == 4:
        zigzag(c, CX, 8, CX, GY, ELEC, seed=3)
        for dx, dy in ((10, 0), (-10, 0), (14, 1), (-14, 1)):
            c.line(CX + dx // 2, GY, CX + dx, GY + dy, ELEC_D)
        c.ellipse(CX - 3, GY - 1, CX + 3, GY + 1, ELEC)
        return c
    if i == 5:
        for dx, dy in ((12, 0), (-12, 0), (16, 1), (-16, 1)):
            p(c, CX + dx, GY + dy, ELEC_D)
        p(c, CX, GY, ELEC)
        p(c, CX, GY - 8, ELEC_D)
        p(c, CX + 1, GY - 16, ELEC_D)
        return c
    for dx, dy in ((14, 1), (-14, 1), (8, 0), (-8, 0)):
        p(c, CX + dx, GY + dy, ELEC_D)
    return c


ANIMATIONS = [
    ("strike", [strike(i) for i in range(7)], 14, False),
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
