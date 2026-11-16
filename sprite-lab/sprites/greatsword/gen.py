#!/usr/bin/env python3
"""Generator cho sprite "greatsword": đại kiếm (vật phẩm/trang bị).

  idle    6 frame lặp: đại kiếm lớn cắm chéo, ánh sáng quét dọc lưỡi.

Neo (16, 30) gần chuôi/điểm tựa (sprite 32x32).

Chạy:  gamekit art run greatsword
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

NAME = "greatsword"
SIZE = 32
ANCHOR = (16.0, 30.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

EDGE = "#f2fbff"
STEEL = "#c5d4e6"
STEEL_D = "#6b7f96"
DARK = "#3a4657"
HILT = "#7a4f2a"
HILT_D = "#4a2f18"
GOLD = "#d9b44a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def blade(c, shine=None):
    # lưỡi rộng, chéo lên-phải
    c.polygon([(14, 28), (10, 27), (22, 4), (25, 5)], STEEL_D)
    c.polygon([(14, 27), (11, 26), (22, 5), (24, 6)], STEEL)
    c.line(12, 26, 22, 6, EDGE)
    c.line(13, 26, 23, 6, STEEL)
    # rãnh giữa lưỡi
    c.line(13, 25, 22, 7, STEEL_D)
    # mũi
    p(c, 23, 4, EDGE); p(c, 24, 4, STEEL); p(c, 23, 5, STEEL)
    # chắn tay lớn
    c.line(8, 25, 18, 22, GOLD)
    c.line(8, 26, 18, 23, DARK)
    p(c, 8, 25, GOLD); p(c, 18, 22, GOLD)
    # chuôi dài
    c.line(13, 26, 11, 30, HILT, 2)
    c.line(13, 26, 11, 30, HILT_D, 1)
    p(c, 11, 30, GOLD)
    # núm
    c.rect(10, 29, 12, 30, GOLD)
    if shine is not None:
        for i in range(4):
            y = shine + i
            if 6 <= y <= 25:
                x = 12 + (26 - y) * (10 / 20)
                p(c, round(x), y, "#ffffff")
                p(c, round(x) - 1, y, EDGE)


def idle(i):
    c = Canvas(SIZE, SIZE)
    c.ellipse(9, 29, 20, 31, "#00000033")
    shine = 22 - i * 4 if i < 5 else None
    blade(c, shine=shine)
    if i == 3:
        p(c, 24, 3, EDGE)
    return c


ANIMATIONS=[("idle",[idle(0)],1,False)]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
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
