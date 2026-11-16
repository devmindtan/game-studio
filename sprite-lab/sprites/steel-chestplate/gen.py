#!/usr/bin/env python3
"""Generator cho sprite "steel-chestplate": áo giáp ngực thép (vật phẩm/giáp).

  idle    6 frame lặp: giáp ngực đặt trưng bày, ánh kim nhẹ.

Neo (16, 26) đáy giáp (sprite 32x28).

Chạy:  gamekit art run steel-chestplate
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

NAME = "steel-chestplate"
W, H = 32, 28
ANCHOR = (16.0, 26.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

STEEL = "#b8c7d9"
STEEL_D = "#5f7187"
EDGE = "#e8f4ff"
DARK = "#3a4657"
GOLD = "#d9b44a"
LEATHER = "#6b4a2e"


def p(c, x, y, col):
    c.pixel(x, y, col)


def chest(c, glint=False):
    # thân giáp
    c.polygon([(10, 6), (22, 6), (24, 12), (23, 24), (9, 24), (8, 12)], STEEL_D)
    c.polygon([(11, 7), (21, 7), (23, 12), (22, 23), (10, 23), (9, 12)], STEEL)
    # vai
    c.ellipse(7, 6, 12, 12, STEEL_D); c.ellipse(8, 7, 11, 11, STEEL)
    c.ellipse(20, 6, 25, 12, STEEL_D); c.ellipse(21, 7, 24, 11, STEEL)
    # cổ
    c.ellipse(12, 4, 20, 9, DARK)
    c.line(12, 6, 20, 6, GOLD)
    # sống giữa
    c.line(16, 8, 16, 22, EDGE)
    c.line(15, 9, 15, 21, STEEL_D)
    # đường gân cơ ngực
    c.line(12, 10, 15, 12, STEEL_D)
    c.line(20, 10, 17, 12, STEEL_D)
    # đai bụng
    c.rect(10, 20, 22, 22, LEATHER)
    c.rect(14, 20, 18, 22, GOLD)
    c.line(10, 20, 22, 20, GOLD)
    # viền dưới
    c.line(9, 24, 23, 24, DARK)
    if glint:
        p(c, 12, 8, EDGE); p(c, 13, 9, "#ffffff")


def idle(i):
    c = Canvas(W, H)
    c.ellipse(9, 25, 23, 27, "#00000033")
    chest(c, glint=(i in (1, 2, 3)))
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
