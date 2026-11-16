#!/usr/bin/env python3
"""Generator cho sprite "magic-staff": trượng phép (vật phẩm/trang bị).

  idle    6 frame lặp: trượng dựng chéo, ngọc trên đầu phát sáng nhịp.

Neo (12, 30) đáy trượng (sprite 24x32).

Chạy:  gamekit art run magic-staff
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

NAME = "magic-staff"
W, H = 24, 32
ANCHOR = (12.0, 30.0)
HERE = Path(__file__).resolve().parent
OUT = HERE

WOOD = "#8a5a2e"
WOOD_D = "#563418"
WOOD_L = "#b07c44"
GOLD = "#d9b44a"
GEM = "#7ef0ff"
GEM_M = "#37b9e8"
GEM_D = "#2a6fa8"
CORE = "#ffffff"


def p(c, x, y, col):
    c.pixel(x, y, col)


def staff(c, glow=0):
    # thân trượng
    c.line(11, 29, 17, 8, WOOD, 2)
    c.line(11, 29, 17, 8, WOOD_D, 1)
    c.line(12, 28, 17, 9, WOOD_L, 1)
    # đai
    c.line(15, 14, 17, 13, GOLD)
    c.line(13, 22, 15, 21, GOLD)
    # đầu giữ ngọc
    c.line(16, 8, 14, 6, GOLD)
    c.line(17, 8, 19, 6, GOLD)
    c.line(14, 6, 16, 4, GOLD)
    c.line(19, 6, 17, 4, GOLD)
    # ngọc
    gx, gy = 16, 5
    if glow:
        g = Canvas(c.width, c.height)
        g.ellipse(gx - 3 - glow, gy - 3 - glow, gx + 3 + glow, gy + 3 + glow, "#7ef0ff22")
        c.paste(g)
    c.ellipse(gx - 2, gy - 2, gx + 2, gy + 2, GEM_D)
    c.ellipse(gx - 1, gy - 1, gx + 1, gy + 1, GEM_M)
    p(c, gx, gy, GEM if glow else GEM_M)
    p(c, gx - 1, gy - 1, CORE if glow >= 1 else GEM)
    # đáy
    p(c, 11, 30, GOLD)


def idle(i):
    c = Canvas(W, H)
    c.ellipse(8, 29, 15, 31, "#00000033")
    glow = 1 if i in (1, 2, 4) else 2 if i == 3 else 0
    staff(c, glow=glow)
    if i == 3:
        p(c, 13, 3, CORE); p(c, 20, 4, GEM)
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
