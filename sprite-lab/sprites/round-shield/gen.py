#!/usr/bin/env python3
"""Generator cho sprite "round-shield": khiên tròn (vật phẩm/giáp).

  idle    6 frame lặp: khiên tròn tựa đứng, ánh kim nhẹ.

Neo (16, 28) đáy khiên (sprite 32x30).

Chạy:  gamekit art run round-shield
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

NAME = "round-shield"
W, H = 32, 30
ANCHOR = (16.0, 28.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

WOOD = "#7a4f2a"
WOOD_D = "#4a2f18"
STEEL = "#b8c7d9"
STEEL_D = "#5f7187"
EDGE = "#e8f4ff"
GOLD = "#d9b44a"
RED = "#8a2f2f"


def p(c, x, y, col):
    c.pixel(x, y, col)


def shield(c, glint=False):
    # mặt gỗ
    c.ellipse(6, 4, 26, 26, WOOD_D)
    c.ellipse(7, 5, 25, 25, WOOD)
    # viền thép
    c.ellipse(6, 4, 26, 26, STEEL_D, fill=False)
    c.ellipse(7, 5, 25, 25, STEEL_D, fill=False)
    # vòng trang trí
    c.ellipse(10, 8, 22, 22, STEEL_D, fill=False)
    c.ellipse(13, 11, 19, 19, RED)
    c.ellipse(14, 12, 18, 18, "#a83a3a")
    # ụm giữa (boss)
    c.ellipse(14, 13, 18, 17, STEEL_D)
    c.ellipse(15, 14, 17, 16, STEEL)
    p(c, 15, 14, EDGE)
    # đinh tán
    for x, y in ((16, 6), (16, 24), (8, 15), (24, 15)):
        p(c, x, y, GOLD)
    if glint:
        p(c, 11, 9, EDGE); p(c, 12, 10, "#ffffff")


def idle(i):
    c = Canvas(W, H)
    c.ellipse(9, 27, 23, 29, "#00000033")
    shield(c, glint=(i in (2, 3)))
    return c


ANIMATIONS = [("idle", [idle(i) for i in range(6)], 5, True)]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * W, len(ANIMATIONS) * H)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * H)
    preview([sheet], HERE / "preview.png", scale=5)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=5)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
