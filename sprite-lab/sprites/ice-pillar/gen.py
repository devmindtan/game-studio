#!/usr/bin/env python3
"""Generator cho sprite "ice-pillar": trụ băng trồi lên từ dưới đất (AOE, mage).

  erupt   8 frame một lần: mặt đất đóng băng, cột băng nhọn mọc vút lên rồi vỡ.

Neo (24, 44) tại mặt đất (sprite 48x48). Cột mọc lên phía trên neo.

Chạy:  gamekit art run ice-pillar
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

NAME = "ice-pillar"
W, H = 48, 48
CX, GY = 24, 44
ANCHOR = (float(CX), float(GY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
ICE = "#c8f6ff"
ICE_M = "#6fe0ff"
ICE_D = "#2a8fd6"
DEEP = "#1b4f8a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def ground(c, frozen=0):
    col = ICE_D if frozen else "#5a4a3a"
    c.line(6, GY, W - 7, GY, col)
    if frozen:
        c.line(10, GY - 1, W - 11, GY - 1, ICE_M)
        for x in (12, 18, 24, 30, 36):
            p(c, x, GY, ICE)


def pillar(c, height, width):
    top = GY - height
    # thân trụ băng (thoi nhọn trên)
    pts = [(CX, top), (CX - width, GY - 4), (CX - width + 1, GY), (CX + width - 1, GY), (CX + width, GY - 4)]
    c.polygon(pts, ICE_D)
    # mặt sáng
    inner = [(CX, top + 2), (CX - width + 2, GY - 5), (CX, GY), (CX + 1, GY), (CX + width - 2, GY - 5)]
    c.polygon(inner, ICE_M)
    c.line(CX, top + 3, CX, GY - 2, ICE)
    c.line(CX - 1, top + 6, CX - 1, GY - 6, CORE)
    # cạnh sáng
    c.line(CX, top, CX - width, GY - 4, ICE)


def erupt(i):
    c = Canvas(W, H)
    if i == 0:
        ground(c, frozen=1)
        # đóng băng lan ra
        c.ellipse(CX - 6, GY - 2, CX + 6, GY, "#6fe0ff44")
        for x in (CX - 4, CX, CX + 4):
            p(c, x, GY - 2, ICE)
        return c
    if i == 1:
        ground(c, frozen=1)
        pillar(c, 8, 3)
        for dx in (-8, 8):
            p(c, CX + dx, GY - 2, ICE_M)
        return c
    if i == 2:
        ground(c, frozen=1)
        pillar(c, 18, 4)
        for dx, dy in ((-9, -4), (9, -6), (-6, -10), (7, -12)):
            p(c, CX + dx, GY + dy, ICE)
        return c
    if i == 3:
        ground(c, frozen=1)
        pillar(c, 30, 5)
        for dx, dy in ((-10, -8), (10, -10), (-7, -18), (8, -20), (0, -32)):
            p(c, CX + dx, GY + dy, CORE if dy < -28 else ICE)
        return c
    if i == 4:
        ground(c, frozen=1)
        pillar(c, 34, 5)
        # vết nứt trên trụ
        c.line(CX - 1, GY - 20, CX + 2, GY - 14, DEEP)
        c.line(CX + 1, GY - 28, CX - 1, GY - 22, DEEP)
        for dx, dy in ((-10, -12), (10, -14)):
            p(c, CX + dx, GY + dy, ICE_M)
        return c
    if i == 5:
        ground(c, frozen=1)
        pillar(c, 30, 5)
        c.line(CX - 2, GY - 18, CX + 2, GY - 10, DEEP)
        c.line(CX + 1, GY - 26, CX - 2, GY - 20, DEEP)
        # mảnh vỡ bắt đầu rơi
        for dx, dy in ((-6, -24), (5, -18), (0, -32)):
            p(c, CX + dx, GY + dy, ICE)
        return c
    if i == 6:
        ground(c, frozen=1)
        pillar(c, 18, 4)
        # vỡ thành mảnh
        for dx, dy in ((-8, -20), (7, -22), (-4, -28), (5, -14), (0, -30), (-10, -10), (10, -12)):
            p(c, CX + dx, GY + dy, ICE if dy > -24 else ICE_M)
        return c
    ground(c, frozen=1)
    pillar(c, 8, 3)
    for dx, dy in ((-10, -18), (9, -20), (-6, -24), (7, -14), (2, -26), (-12, -8), (12, -10)):
        p(c, CX + dx, GY + dy, ICE_D)
    return c


ANIMATIONS = [
    ("erupt", [erupt(i) for i in range(8)], 12, False),
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
                    [{"name": n, "frames": f, "fps": fps, "loop": loop,
                      "hitbox": {"shape": "circle", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1]}}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
