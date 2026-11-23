#!/usr/bin/env python3
"""Generator cho "moc-nhan" (Bù nhìn rơm / cọc tập ở Làng Hạc, Thất Tinh Ấn): cột gỗ mộc nhân ba tay gỗ, đai ngọc.
Người dùng chọn phương án B (sprite-lab/designs/dong-que-mobs/variants.py, 2026-11-23).
Vật thể đứng yên, không đi/không đánh nên không theo creature-v1: idle 2 (đứng), hurt 4 (rung lắc khi trúng
đòn, tay gỗ xoay), death 5 (rung mạnh rồi mờ tại chỗ, hồi sinh sau). Frame 32x32, neo (16, 30) chân cột (ground=True).
"""
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("workspace?")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from PIL import Image  # noqa: E402
from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = "moc-nhan"
N = 32
ANCHOR = (16.0, 30.0)
OUT = "#1b1726"
WOOD, WOOD_D, WOOD_L, BAND = "#8a5a36", "#64401f", "#a8744a", "#3a7866"


def post(s=0, arms=0, flash=0.0, lean=0.0, fade=1.0):
    """s: rung ngang phần trên (px); arms: tay gỗ xoay (0/1); lean: đổ nghiêng 0..1."""
    c = Canvas(N, N)
    for y in range(4, 29):
        dx = round(s * (28 - y) / 24)
        c.rect(12 + dx, y, 19 + dx, y, WOOD)
        c.pixel(12 + dx, y, WOOD_D); c.pixel(19 + dx, y, WOOD_L)
    c.rect(11, 27, 20, 28, WOOD_D)                                   # chân đế
    c.rect(12 + s // 2, 21, 19 + s // 2, 22, BAND)
    top = round(s * 0.8)
    if arms == 0:
        c.rect(20 + top, 10, 25 + top, 11, WOOD_L); c.rect(20 + top, 16, 24 + top, 17, WOOD_L); c.rect(6 + top, 13, 11 + top, 14, WOOD_L)
    else:
        c.rect(20 + top, 9, 24 + top, 10, WOOD_L); c.rect(20 + top, 17, 25 + top, 18, WOOD_L); c.rect(7 + top, 12, 11 + top, 13, WOOD_L)
    c.pixel(15 + top, 8, WOOD_D); c.pixel(17 + top, 8, WOOD_D)      # vân gỗ như mắt
    c.outline(OUT)
    if flash:
        p = c.img.load()
        for y in range(N):
            for x in range(N):
                r, g, b, a = p[x, y]
                if a and (r, g, b) != (0x1b, 0x17, 0x26):
                    p[x, y] = (round(r + (255 - r) * flash), round(g + (255 - g) * flash), round(b + (255 - b) * flash), a)
    if lean:
        im = c.img.rotate(-80 * lean, resample=Image.NEAREST, expand=True)
        bb = im.getbbox(); part = im.crop(bb)
        c = Canvas(N, N)
        c.img.alpha_composite(part, (max(0, min(N - part.width, 12)), 30 - part.height))
    if fade < 1:
        p = c.img.load()
        for y in range(N):
            for x in range(N):
                r, g, b, a = p[x, y]
                p[x, y] = (r, g, b, round(a * fade))
    return c


ANIMATIONS = [
    ("idle", [post(), post(arms=0)], 2, True, {}),
    ("hurt", [post(s=2, arms=1, flash=0.7), post(s=-2, arms=1), post(s=1, arms=0), post()], 14, False, {"durations_ms": [60, 70, 70, 90]}),
    ("death", [post(s=3, arms=1, flash=0.8), post(s=-3, arms=1), post(s=2, fade=0.7), post(s=-1, fade=0.45), post(fade=0.2)], 8, False,
     {"durations_ms": [80, 90, 90, 300, 200]}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="idle")
    print(f"OK {NAME}")
