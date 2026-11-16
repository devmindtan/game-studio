#!/usr/bin/env python3
"""Generator cho sprite "iron-sword": kiếm sắt (vật phẩm/trang bị).

  idle    6 frame lặp: kiếm đặt chéo, ánh sáng lướt nhẹ trên lưỡi.

Neo (12, 22) gần chuôi (sprite 24x24), đặt như vật phẩm trên mặt đất/kệ.

Chạy:  gamekit art run iron-sword
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

NAME = "iron-sword"
SIZE = 24
ANCHOR = (12.0, 22.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

EDGE = "#e8f4ff"
STEEL = "#b8c7d9"
STEEL_D = "#6b7f96"
HILT = "#8a5a2e"
HILT_D = "#563418"
GOLD = "#d9b44a"
GLOW = "#ffffff44"


def p(c, x, y, col):
    c.pixel(x, y, col)


def sword(c, shine_y=None):
    # lưỡi kiếm chéo hướng lên-phải
    c.line(11, 21, 18, 5, STEEL_D, 2)
    c.line(10, 21, 17, 5, STEEL, 1)
    c.line(10, 20, 16, 6, EDGE, 1)
    # mũi
    p(c, 18, 4, EDGE); p(c, 18, 5, STEEL); p(c, 17, 4, STEEL)
    # chắn tay
    c.line(8, 19, 14, 17, GOLD)
    c.line(8, 20, 14, 18, HILT_D)
    # chuôi
    c.line(10, 20, 9, 22, HILT, 2)
    c.line(10, 20, 9, 22, HILT_D, 1)
    p(c, 9, 22, GOLD)
    # ánh lướt
    if shine_y is not None:
        for dy in range(3):
            y = shine_y + dy
            x = 10 + (21 - y) * (7 / 16)
            if 5 <= y <= 20:
                p(c, round(x), y, EDGE)
                p(c, round(x) - 1, y, "#ffffff")


def idle(i):
    c = Canvas(SIZE, SIZE)
    # bóng nhẹ dưới đất
    c.ellipse(8, 21, 15, 23, "#00000033")
    shine = None
    if 1 <= i <= 4:
        shine = 18 - i * 3
    sword(c, shine_y=shine)
    if i in (2, 3):
        # lấp lánh nhỏ
        p(c, 19, 3, EDGE)
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
    preview([sheet], HERE / "preview.png", scale=6)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=6)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop,
                      "hitbox": {"shape": "rect", "center": [float(ANCHOR[0]), float(ANCHOR[1])], "active": [0, len(f)-1]}}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
