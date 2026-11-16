#!/usr/bin/env python3
"""Generator cho sprite "frost-nova": tân băng AOE của hệ pháp sư.

  burst   8 frame một lần: vụ nổ băng từ tâm, vòng băng và mảnh băng lan tròn ra.

Neo (24, 24) tại tâm (sprite 48x48).

Chạy:  gamekit art run frost-nova
"""

import math
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "frost-nova"
SIZE = 48
CX, CY = 24, 24
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
ICE = "#c8f6ff"
ICE_M = "#6fe0ff"
ICE_D = "#2a8fd6"
DEEP = "#1b4f8a"


def p(c, x, y, col):
    c.pixel(x, y, col)


def ring(c, cx, cy, r, col):
    c.ellipse(cx - r, cy - r, cx + r, cy + r, col, fill=False)


def shard(c, x, y, ang, col):
    dx = 1 if math.cos(ang) >= 0 else -1
    dy = 1 if math.sin(ang) >= 0 else -1
    p(c, x, y, col)
    p(c, x + dx, y, col)
    p(c, x, y + dy, col)


def burst(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, ICE_M)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, CORE)
        for k in range(8):
            a = math.radians(k * 45)
            p(c, round(CX + math.cos(a) * 5), round(CY + math.sin(a) * 5), ICE)
        return c
    if i == 1:
        ring(c, CX, CY, 6, ICE_M)
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, ICE)
        p(c, CX, CY, CORE)
        for k in range(8):
            a = math.radians(k * 45 + 10)
            shard(c, round(CX + math.cos(a) * 8), round(CY + math.sin(a) * 8), a, ICE_M)
        return c
    if i == 2:
        ring(c, CX, CY, 10, ICE_D)
        ring(c, CX, CY, 7, ICE_M)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, ICE)
        for k in range(12):
            a = math.radians(k * 30)
            r = 12 + (k % 2)
            shard(c, round(CX + math.cos(a) * r), round(CY + math.sin(a) * r), a, ICE if k % 2 == 0 else ICE_M)
        return c
    if i == 3:
        ring(c, CX, CY, 14, DEEP)
        ring(c, CX, CY, 11, ICE_D)
        ring(c, CX, CY, 8, ICE_M)
        for k in range(12):
            a = math.radians(k * 30 + 8)
            r = 16
            shard(c, round(CX + math.cos(a) * r), round(CY + math.sin(a) * r), a, ICE_M)
        return c
    if i == 4:
        ring(c, CX, CY, 17, DEEP)
        ring(c, CX, CY, 14, ICE_D)
        for k in range(12):
            a = math.radians(k * 30)
            r = 19
            shard(c, round(CX + math.cos(a) * r), round(CY + math.sin(a) * r), a, ICE_D)
        for k in range(8):
            a = math.radians(k * 45 + 20)
            p(c, round(CX + math.cos(a) * 12), round(CY + math.sin(a) * 12), ICE)
        return c
    if i == 5:
        ring(c, CX, CY, 19, DEEP)
        for k in range(12):
            a = math.radians(k * 30 + 10)
            r = 21
            p(c, round(CX + math.cos(a) * r), round(CY + math.sin(a) * r), DEEP)
        for k in range(8):
            a = math.radians(k * 45)
            p(c, round(CX + math.cos(a) * 15), round(CY + math.sin(a) * 15), ICE_D)
        return c
    if i == 6:
        ring(c, CX, CY, 20, DEEP)
        for k in range(12):
            a = math.radians(k * 30)
            p(c, round(CX + math.cos(a) * 22), round(CY + math.sin(a) * 22), DEEP)
        return c
    for k in range(8):
        a = math.radians(k * 45 + 12)
        p(c, round(CX + math.cos(a) * 22), round(CY + math.sin(a) * 22), DEEP)
    return c


ANIMATIONS = [
    ("burst", [burst(i) for i in range(8)], 14, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=4)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=4)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop,
                      "hitbox": {"shape": "rect", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1]}}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
