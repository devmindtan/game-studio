#!/usr/bin/env python3
"""Generator cho sprite "tower-shield": khiên tháp lớn (vật phẩm/giáp).

  idle    6 frame lặp: khiên tháp tựa đứng, bề mặt thép phản sáng.

Neo (16, 30) đáy khiên (sprite 32x32).

Chạy:  gamekit art run tower-shield
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

NAME = "tower-shield"
W, H = 32, 32
ANCHOR = (16.0, 30.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

STEEL = "#b8c7d9"
STEEL_D = "#5f7187"
EDGE = "#e8f4ff"
DARK = "#3a4657"
GOLD = "#d9b44a"
BLUE = "#2f5f8a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def shield(c, glint=False):
    # thân khiên tháp (trên thẳng, dưới bo/vát)
    pts = [(8, 4), (24, 4), (25, 22), (16, 28), (7, 22)]
    c.polygon(pts, STEEL_D)
    inner = [(9, 5), (23, 5), (24, 22), (16, 27), (8, 22)]
    c.polygon(inner, STEEL)
    # viền
    c.line(8, 4, 24, 4, EDGE)
    c.line(8, 4, 7, 22, DARK)
    c.line(24, 4, 25, 22, DARK)
    c.line(7, 22, 16, 28, DARK)
    c.line(25, 22, 16, 28, DARK)
    # huy hiệu
    c.polygon([(12, 8), (20, 8), (21, 18), (16, 22), (11, 18)], BLUE)
    c.line(16, 9, 16, 20, GOLD)
    c.line(13, 14, 19, 14, GOLD)
    # gân gia cố
    c.line(10, 6, 10, 22, STEEL_D)
    c.line(22, 6, 22, 22, STEEL_D)
    if glint:
        c.line(11, 6, 11, 12, EDGE)
        p(c, 12, 7, "#ffffff")


def idle(i):
    c = Canvas(W, H)
    c.ellipse(9, 29, 23, 31, "#00000033")
    shield(c, glint=(i in (1, 2, 3)))
    return c


ANIMATIONS=[("idle",[idle(0)],1,False)]


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
                    [{"name": n, "frames": f, "fps": fps, "loop": loop,
                      "hitbox": {"shape": "rect", "center": [float(ANCHOR[0]), float(ANCHOR[1])], "active": [0, len(f)-1]}}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
