#!/usr/bin/env python3
"""Generator cho sprite "oak-bow": cung gỗ (vật phẩm/trang bị).

  idle    6 frame lặp: cung dựng đứng, dây rung/ánh sáng nhẹ.

Neo (12, 30) đáy cung (sprite 24x32).

Chạy:  gamekit art run oak-bow
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

NAME = "oak-bow"
W, H = 24, 32
ANCHOR = (12.0, 30.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

WOOD = "#8a5a2e"
WOOD_D = "#563418"
WOOD_L = "#b07c44"
STR = "#e8e0c8"
TIP = "#b8c7d9"
GOLD = "#d9b44a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def bow(c, str_x=14):
    # thân cung cong
    pts = [(12, 2), (9, 6), (8, 12), (8, 20), (9, 26), (12, 30)]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], WOOD, 2)
    c.line(12, 2, 9, 10, WOOD_L)
    c.line(12, 30, 9, 22, WOOD_D)
    # đầu cung
    p(c, 12, 2, TIP); p(c, 12, 30, TIP)
    # tay cầm
    c.rect(7, 14, 9, 18, WOOD_D)
    c.line(7, 15, 9, 15, GOLD)
    c.line(7, 17, 9, 17, GOLD)
    # dây cung
    c.line(12, 3, str_x, 16, STR)
    c.line(str_x, 16, 12, 29, STR)


def idle(i):
    c = Canvas(W, H)
    c.ellipse(8, 29, 16, 31, "#00000033")
    # dây rung nhẹ
    sx = 14 if i % 3 == 0 else 15 if i % 3 == 1 else 13
    bow(c, str_x=sx)
    return c


ANIMATIONS = [("idle", [idle(i) for i in range(6)], 7, True)]


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
