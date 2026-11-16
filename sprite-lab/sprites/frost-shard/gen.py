#!/usr/bin/env python3
"""Generator cho sprite "frost-shard": mũi băng mà pháp sư bắn ra.

  fly     6 frame lặp: mảnh băng xoay nhẹ, vệt lạnh phía sau, hạt tuyết rơi;
  impact  6 frame một lần: nứt vỡ, mảnh băng bắn ra rồi tan.

Đầu mũi tên băng quay sang phải. Neo (11, 10) là tâm mũi băng.

Chạy:  gamekit art run frost-shard
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

NAME = "frost-shard"
SIZE = 20
CX, CY = 11, 10
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
ICE = "#b9f3ff"
ICE_MID = "#63d8ff"
ICE_DEEP = "#2a8fd6"
ICE_DARK = "#1b4f8a"
MIST = "#b9f3ff44"



def p(c, x, y, col):
    c.pixel(x, y, col)


def glow(c, x, y, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(x - r, y - r, x + r, y + r, col)
    c.paste(ring)


def shard(c, x, y, tilt=0):
    # thân mũi băng: nhọn phải, đáy trái, hơi nghiêng theo tilt
    pts = [(x + 5, y + tilt), (x - 1, y - 3 + tilt), (x - 4, y), (x - 1, y + 3 + tilt)]
    c.polygon(pts, ICE_DEEP)
    inner = [(x + 3, y + tilt), (x - 1, y - 2 + tilt), (x - 3, y), (x - 1, y + 2 + tilt)]
    c.polygon(inner, ICE_MID)
    c.line(x - 1, y - 1 + tilt, x + 2, y + tilt, ICE)
    p(c, x + 1, y + tilt, CORE)
    # vết nứt trong băng
    p(c, x - 2, y - 1, ICE)
    p(c, x - 1, y + 1, ICE_DEEP)


def trail(c, x, y, phase):
    for i in range(6):
        tx = x - 6 - i
        ty = y + ((0, -1, 0, 1)[(i + phase) % 4])
        col = ICE if i < 2 else ICE_MID if i < 4 else ICE_DEEP
        p(c, tx, ty, col)
    for k, (dx, dy) in enumerate(((-7, -3), (-9, 3), (-11, -1), (-13, 2))):
        if (phase + k) % 3 != 2:
            p(c, x + dx, y + dy, CORE if k == 0 else ICE)


def fly(i):
    c = Canvas(SIZE, SIZE)
    glow(c, CX, CY, 5, MIST)
    trail(c, CX, CY, i)
    shard(c, CX, CY, tilt=(-1, 0, 1, 0, -1, 0)[i])
    # bông tuyết nhỏ lượn quanh
    for k, (dx, dy) in enumerate(((4, -4), (-2, -5), (5, 4), (-8, 4))):
        if (i + k) % 3 == 0:
            p(c, CX + dx, CY + dy, CORE)
    return c


def impact(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        glow(c, CX, CY, 4, "#ffffff55")
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, CORE)
        for dx, dy in ((3, 0), (-3, 0), (0, 3), (0, -3)):
            p(c, CX + dx, CY + dy, ICE)
        return c
    frags = [(-5, -3), (4, -4), (-6, 2), (5, 3), (0, -6), (1, 6), (-3, 5), (6, 0)]
    if i == 1:
        c.ellipse(CX - 3, CY - 3, CX + 3, CY + 3, ICE_MID)
        c.ellipse(CX - 2, CY - 2, CX + 2, CY + 2, CORE)
        for dx, dy in frags[:6]:
            p(c, CX + dx, CY + dy, ICE)
        return c
    if i == 2:
        c.ellipse(CX - 4, CY - 4, CX + 4, CY + 4, ICE_DEEP, fill=False)
        for dx, dy in frags:
            p(c, CX + dx, CY + dy, ICE if (dx + dy) % 2 else ICE_MID)
            p(c, CX + dx + (1 if dx > 0 else -1), CY + dy, ICE_DEEP)
        return c
    if i == 3:
        c.ellipse(CX - 6, CY - 6, CX + 6, CY + 6, ICE_DARK, fill=False)
        for j, (dx, dy) in enumerate(frags):
            s = 1 + (j % 2)
            p(c, CX + dx + s, CY + dy + (1 if dy > 0 else 0), ICE_MID)
        return c
    if i == 4:
        for j, (dx, dy) in enumerate(frags):
            s = 2
            p(c, CX + dx + s, CY + dy + 1, ICE_DEEP)
        p(c, CX, CY, ICE_MID)
        return c
    for dx, dy in ((-8, -4), (7, -5), (-7, 4), (8, 5), (2, 8)):
        p(c, CX + dx, CY + dy, ICE_DARK)
    return c


from PIL import Image


def rot(c, deg):
    nc = Canvas(c.width, c.height)
    nc.img = c.img.rotate(deg, resample=Image.Resampling.NEAREST, expand=False)
    return nc


_SIDE = [fly(i) for i in range(6)]

def dir_frames(base_frames, direction):
    if direction == "right": return [f.copy() for f in base_frames]
    if direction == "up": return [rot(f, 90) for f in base_frames]
    if direction == "left": return [rot(f, 180) for f in base_frames]
    if direction == "down": return [rot(f, 270) for f in base_frames]
    raise ValueError(direction)


ANIMATIONS = [
    ("fly", dir_frames(_SIDE, "right"), 14, True),
    ("fly_right", dir_frames(_SIDE, "right"), 14, True),
    ("fly_left", dir_frames(_SIDE, "left"), 14, True),
    ("fly_up", dir_frames(_SIDE, "up"), 14, True),
    ("fly_down", dir_frames(_SIDE, "down"), 14, True),
    ("impact", [impact(i) for i in range(6)], 15, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=8)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=8)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": lp,
                      "hitbox": {"shape": "circle", "center": [float(ANCHOR[0]), float(ANCHOR[1])],
                                 "active": [0, len(f)-1] if n.startswith("fly") else [0, min(2, len(f)-1)]}}
                     for n, f, fps, lp in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
