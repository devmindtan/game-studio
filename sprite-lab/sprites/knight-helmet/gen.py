#!/usr/bin/env python3
"""Generator cho sprite "knight-helmet": mũ giáp hiệp sĩ (vật phẩm/giáp).

  idle    6 frame lặp: mũ giáp đặt trên đất, ánh kim phản chiếu nhẹ.

Neo (16, 26) đáy mũ (sprite 32x28).

Chạy:  gamekit art run knight-helmet
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

NAME = "knight-helmet"
W, H = 32, 28
ANCHOR = (16.0, 26.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

STEEL = "#b8c7d9"
STEEL_D = "#5f7187"
EDGE = "#e8f4ff"
DARK = "#2e3542"
GOLD = "#d9b44a"
VISOR = "#1a2230"


def p(c, x, y, col):
    c.pixel(x, y, col)


def helmet(c, glint=False):
    # vòm mũ
    c.ellipse(9, 6, 23, 24, STEEL_D)
    c.ellipse(10, 7, 22, 23, STEEL)
    c.ellipse(11, 8, 21, 20, STEEL)
    # đỉnh
    c.line(16, 4, 16, 7, STEEL_D, 2)
    c.rect(15, 4, 17, 5, GOLD)
    # sống mũ
    c.line(16, 7, 16, 20, EDGE)
    # tấm che mắt (visor)
    c.rect(11, 14, 21, 18, VISOR)
    c.line(11, 14, 21, 14, STEEL_D)
    # khe nhìn
    for x in (13, 15, 17, 19):
        c.rect(x, 15, x, 17, DARK)
    c.line(12, 16, 20, 16, "#3a4657")
    # viền cổ
    c.rect(10, 22, 22, 24, STEEL_D)
    c.line(10, 22, 22, 22, GOLD)
    # má giáp
    c.rect(9, 16, 10, 22, STEEL_D)
    c.rect(22, 16, 23, 22, STEEL_D)
    if glint:
        p(c, 12, 9, EDGE); p(c, 13, 10, "#ffffff")


def idle(i):
    c = Canvas(W, H)
    c.ellipse(10, 25, 22, 27, "#00000033")
    helmet(c, glint=(i in (2, 3)))
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
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
