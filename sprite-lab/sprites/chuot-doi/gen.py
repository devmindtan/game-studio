#!/usr/bin/env python3
"""Generator cho "chuot-doi" (Chuột đồi, Thất Tinh Ấn): chuột đứng hai chân, tai to hồng, cầm que gỗ, đi lạch bạch.
Người dùng chọn phương án B (sprite-lab/designs/dong-que-mobs/variants.py, 2026-11-23). Chuẩn creature-v1.

Frame 32x32, quay phải, neo (16, 30) giữa hai chân trên mặt đất (ground=True).
Hình dựng từ tham số tư thế (bob, lean, tai, góc que, chân); mỗi khung là một tư thế riêng.
Chạy: gamekit art run chuot-doi
"""
import math
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

from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = "chuot-doi"
N = 32
ANCHOR = (16.0, 30.0)
OUT = "#1b1726"
FUR, FUR_D, BELLY, EAR, NOSE, FOOT = "#9c8a78", "#7a6a5a", "#c8b8a0", "#d8a8a0", "#d07a7a", "#5a4636"
WOOD, WOOD_D = "#a8744a", "#7a5228"


def box(c, x0, y0, x1, y1, col):
    c.rect(int(x0), int(y0), int(x1), int(y1), col)


def px(c, x, y, col):
    c.pixel(int(round(x)), int(round(y)), col)


def rat(bob=0, lean=0, ears=0, stick=-55, feet=(0, 0), eye="open", flash=0.0, tail=0.0, lie=0.0, fade=1.0, mouth=False):
    """bob: thân xuống (+); lean: đầu/thân về trước; ears: tai dựng (-) / cụp (+); stick: góc que (độ, 0 = trước,
    -90 = dựng lên); feet: (dx chân sau, dx chân trước); tail: pha đuôi."""
    c = Canvas(N, N)
    # đuôi (sau lưng, lắc trễ nhịp)
    for k in range(7):
        px(c, 11 - k, 25 + bob // 2 - k * 0.4 + math.sin(tail + k * 0.8) * 1.2, NOSE)
    # chân
    bx, fx = feet
    box(c, 13 + bx, 27, 15 + bx, 28, FOOT)
    box(c, 17 + fx, 27, 19 + fx, 28, FOOT)
    # thân
    x0 = 12 + lean // 2
    box(c, x0, 15 + bob, x0 + 8, 26, FUR)
    box(c, x0, 15 + bob, x0, 26, FUR_D)
    box(c, x0 + 2, 20 + bob, x0 + 7, 25, BELLY)
    # đầu
    hx = 13 + lean
    hy = 8 + bob
    box(c, hx, hy, hx + 8, hy + 6, FUR)
    box(c, hx + 8, hy + 3, hx + 9, hy + 5, FUR)
    px(c, hx + 10, hy + 4, NOSE)
    if mouth:
        box(c, hx + 7, hy + 6, hx + 9, hy + 6, "#f0e8e0")      # nhe răng
    if eye == "open":
        px(c, hx + 6, hy + 2, OUT); px(c, hx + 6, hy + 3, OUT)
    elif eye == "wince":
        px(c, hx + 5, hy + 2, OUT); px(c, hx + 6, hy + 3, OUT)
    else:  # x
        px(c, hx + 5, hy + 2, OUT); px(c, hx + 7, hy + 2, OUT); px(c, hx + 6, hy + 3, OUT)
    # tai
    box(c, hx - 2, hy - 3 + ears, hx + 1, hy + 1, EAR)
    box(c, hx + 5, hy - 3 + ears, hx + 8, hy + 1 - (1 if ears < 0 else 0), EAR)
    # tay + que (cầm ở tay trước)
    hand = (x0 + 11, 20 + bob)   # tay đưa ra trước bụng, que không cắt qua mặt
    a = math.radians(stick)
    for k in range(-2, 8):
        px(c, hand[0] + math.cos(a) * k, hand[1] + math.sin(a) * k, WOOD if k < 7 else WOOD_D)
    box(c, hand[0] - 1, hand[1] - 1, hand[0], hand[1], FUR_D)
    c.outline(OUT)
    if flash:
        _tint(c, flash)
    if lie:
        c = _lie(c, lie)
    if fade < 1:
        _fade(c, fade)
    return c


def _tint(c, amount):
    p = c.img.load()
    for y in range(N):
        for x in range(N):
            r, g, b, a = p[x, y]
            if a and (r, g, b) != (0x1b, 0x17, 0x26):
                p[x, y] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount), round(b + (255 - b) * amount), a)


def _fade(c, f):
    p = c.img.load()
    for y in range(N):
        for x in range(N):
            r, g, b, a = p[x, y]
            p[x, y] = (r, g, b, round(a * f))


def _lie(c, amount):
    """Ngã ngửa ra sau: xoay quanh gót, rồi đặt đáy hình lên mặt đất."""
    from PIL import Image
    im = c.img.rotate(90 * amount, resample=Image.NEAREST, expand=True)
    bb = im.getbbox()
    out = Canvas(N, N)
    if bb:
        part = im.crop(bb)
        out.img.alpha_composite(part, (max(0, 16 - part.width // 2), 30 - part.height))
    return out


MOVE = [  # lạch bạch: thân nghiêng trái/phải theo bước, tai và đuôi trễ nhịp
    rat(bob=0, lean=0, feet=(-1, 1), stick=-55, ears=0, tail=0.0),
    rat(bob=1, lean=1, feet=(0, 0), stick=-50, ears=1, tail=0.9),
    rat(bob=0, lean=2, feet=(1, -1), stick=-45, ears=0, tail=1.8),
    rat(bob=-1, lean=1, feet=(1, -1), stick=-50, ears=-1, tail=2.7),
    rat(bob=1, lean=0, feet=(0, 0), stick=-55, ears=1, tail=3.6),
    rat(bob=0, lean=-1, feet=(-1, 1), stick=-60, ears=-1, tail=4.5),
]
ATTACK = [  # gồng: lùi người, tai dựng, nhe răng, giơ que ra sau → bổ xuống → thu về
    rat(bob=1, lean=-2, ears=-2, stick=-85, mouth=True, tail=0.5),
    rat(bob=2, lean=-3, ears=-2, stick=-95, mouth=True, eye="wince", tail=1.0),
    rat(bob=0, lean=3, ears=1, stick=-20, mouth=True, feet=(0, 2), tail=1.6),
    rat(bob=1, lean=4, ears=1, stick=20, mouth=True, feet=(0, 2), tail=2.2),
    rat(bob=1, lean=2, ears=0, stick=-30, feet=(0, 1), tail=2.8),
    rat(bob=0, lean=0, ears=0, stick=-45, tail=3.4),
]
HURT = [
    rat(bob=1, lean=-2, ears=2, stick=-70, eye="wince", flash=0.75),
    rat(bob=1, lean=-3, ears=2, stick=-75, eye="wince", tail=1.0),
    rat(bob=0, lean=0, ears=0, stick=-55, tail=2.0),
]
DEATH = [
    rat(bob=1, lean=-2, ears=2, stick=-70, eye="x", flash=0.6),
    rat(bob=2, lean=-3, ears=2, stick=-80, eye="x"),
    rat(bob=2, lean=-3, ears=2, stick=-150, eye="x", lie=0.5),
    rat(bob=2, lean=-3, ears=2, stick=-160, eye="x", lie=1.0),
    rat(bob=2, lean=-3, ears=2, stick=-160, eye="x", lie=1.0, fade=0.6),
    rat(bob=2, lean=-3, ears=2, stick=-160, eye="x", lie=1.0, fade=0.25),
]

ANIMATIONS = [
    ("move", MOVE, 8, True, {}),
    ("attack", ATTACK, 10, False, {"durations_ms": [140, 160, 60, 90, 100, 120],
                                   "hitbox": {"shape": "arc", "center": [26.0, 20.0], "active": [2, 3], "dir_deg": 0}}),
    ("hurt", HURT, 12, False, {"durations_ms": [80, 110, 120]}),
    ("death", DEATH, 8, False, {"durations_ms": [90, 110, 90, 200, 150, 150]}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move")
    print(f"OK {NAME}")
