#!/usr/bin/env python3
"""boss-slam — Vua Slime, boss ải 10 (Bách Ải): đáp đất + vương miện cắm vào nứt.

DNA: VƯƠNG MIỆN × SLIME — vương miện vàng nứt cắm sâu vào mặt đất, slime xanh
xoắn quanh mép nứt, các mảnh vương miện kim cương văng ra, vòng sóng chấn động
lan ra ngoài. Một đòn boss, không có bậc — rõ nét hơn `stomp-*` một cấp.

Neo: tâm (vị trí đáp đất). Chạy: gamekit art run boss-slam
"""
import math, sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists(): return p
    raise SystemExit("no workspace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from spritekit import Canvas
from sheet import export

NAME = "boss-slam"
SIZE = 72
CX = CY = SIZE // 2
ANCHOR = (CX + 0.5, CY + 0.5)

GOLD = "#ffd04a"; GOLD_L = "#fff3b0"; GOLD_D = "#b8862a"; OUT = "#2b1b0e"
SLIME = "#3fae6e"; SLIME_L = "#9ff0b8"; SLIME_D = "#1f6b45"
ROCK = "#6e503c"; ROCK_D = "#3a2a1e"; DUST = "#e6cfb0"; DUST_D = "#a9815c"
CRACK = "#1e161c"; CRACK_L = "#4a3528"; STRATA = "#3a2a1e"

def p(c, x, y, col):
    xi, yi = int(round(x)), int(round(y))
    if 0 <= xi < SIZE and 0 <= yi < SIZE: c.pixel(xi, yi, col)

def ring(c, r, col, dotted=False, seed=0):
    n = max(28, int(math.tau * r))
    for i in range(n):
        a = i * math.tau / n
        if dotted and (i + seed) % 4 == 0: continue
        p(c, CX + math.cos(a) * r, CY + math.sin(a) * r, col)

def crown(c, x, y, w, top_y, filled=True):
    """Draws a slime-king crown at (x, y) spanning w pixels below top_y."""
    pts = [(x - w // 2, y), (x - w // 2, y + 5), (x - w // 2 + 2, y + 2),
           (x - w // 2 + 4, y + 5), (x + w // 2 - 4, y + 5), (x + w // 2 - 2, y + 2),
           (x + w // 2, y + 5), (x + w // 2, y)]
    # simplified: trapezoid base with 3 points
    for dy in range(6):
        half = w // 2 - dy * 0.6
        for dx in range(-int(half), int(half) + 1):
            p(c, x + dx, top_y + dy, GOLD if filled and dy % 2 else GOLD_L)
    for k in (-w // 2 + 2, 0, w // 2 - 2):
        p(c, x + k, top_y, GOLD); p(c, x + k, top_y - 2, GOLD_L)
    # band line at bottom of crown
    for dx in range(-w // 2 + 1, w // 2):
        p(c, x + dx, top_y + 5, GOLD_D)

def frame(i):
    c = Canvas(SIZE, SIZE)
    t = i / 7.0
    if i == 0:
        # thin fissure opening on the ground
        for s in range(-13, 14):
            p(c, CX + s * 0.72, CY + 11 + (0 if s % 4 else 1), CRACK)
        p(c, CX, CY + 10, GOLD_L)
        return c
    if i == 1:
        # the crown descends toward the crack
        for dy in range(0, 5):
            for dx in range(-4, 5):
                p(c, CX + dx, CY - 2 + dy, GOLD if dy % 2 else GOLD_L)
        for k in (-4, 0, 4):
            p(c, CX + k, CY - 5, GOLD); p(c, CX + k, CY - 7, GOLD_L)
        for s in range(-11, 12):
            p(c, CX + s * 0.7, CY + 11 + (0 if s % 4 else 1), CRACK)
        p(c, CX, CY + 10, GOLD)
        return c
    if i == 2:
        # crown slams into the crack — maximum impact
        crown(c, CX, 0, 16, CY - 7)
        ring(c, 11, OUT); ring(c, 10, GOLD_D)
        ring(c, 11 + 4, DUST, dotted=True, seed=i)
        # slime bubbling out at edge
        p(c, CX - 9, CY + 4, SLIME_D); p(c, CX + 9, CY + 4, SLIME_D)
        p(c, CX - 7, CY + 5, SLIME); p(c, CX + 7, CY + 5, SLIME)
        for s in range(-10, 11):
            p(c, CX + s * 0.75, CY + 11, CRACK)
        return c
    if i == 3:
        # crown splits in half, slime bulges outward, gold splintering
        # left slab
        for dy in range(6):
            for dx in range(-5, 0):
                p(c, CX - 2 + dx, CY - 4 + dy, GOLD if dy % 2 else GOLD_L)
        # right slab
        for dy in range(6):
            for dx in range(1, 6):
                p(c, CX + 2 + dx, CY - 4 + dy, GOLD if dy % 2 else GOLD_L)
        for k in (-6, 6):
            p(c, CX + k, CY - 5, GOLD); p(c, CX + k, CY - 6, GOLD_L)
        # slime spread bulging out
        for k in range(-9, 10, 2):
            p(c, CX + k, CY + 6, SLIME_D); p(c, CX + k, CY + 7, SLIME)
        ring(c, 16, OUT); ring(c, 15, DUST_D)
        # gold sparks
        p(c, CX - 7, CY - 8, GOLD); p(c, CX + 7, CY - 8, GOLD)
        p(c, CX - 3, CY - 10, GOLD_L); p(c, CX + 3, CY - 10, GOLD_L)
        return c
    if i == 4:
        # the shockwave proper — crown only a base, chunks flying out
        for dx in range(-7, 8):
            p(c, CX + dx, CY + 5, GOLD_D); p(c, CX + dx, CY + 6, GOLD_D)
        # 4 chunks flying out
        chunk = [(-8, -2), (8, -2), (-12, 3), (12, 3)]
        for (cx, cy) in chunk:
            p(c, CX + cx, CY + cy, GOLD); p(c, CX + cx, CY + cy - 1, GOLD_L)
            p(c, CX + cx + 1, CY + cy, GOLD)
        ring(c, 20, OUT); ring(c, 19, DUST)
        for k in (-8, 0, 8):
            p(c, CX + k, CY + 9, SLIME_L)
        # gold dust raining
        for k in range(4):
            a = k * 1.7 + i * 0.35
            p(c, int(CX + math.cos(a) * 8), int(CY - 4 + math.sin(a) * 8), GOLD_D)
        return c
    if i == 5:
        # fading ring, scattered slime puddles on the ground
        ring(c, 25, ROCK_D); ring(c, 24, DUST_D, dotted=True, seed=i)
        for k in (-10, -2, 6):
            p(c, CX + k, CY + 10, SLIME); p(c, CX + k, CY + 11, SLIME_D)
        # few fading rocks
        p(c, CX - 13, CY - 4, ROCKROCK if False else ROCK)
        p(c, CX + 14, CY - 2, ROCK)
        return c
    if i == 6:
        # afterglow: a scorched ring of gold fading
        ring(c, 28, ROCK_D, dotted=True, seed=i + 3)
        for k in (-6, 4):
            p(c, CX + k, CY + 12, DUST)
        p(c, CX - 4, CY + 11, GOLD_D); p(c, CX + 5, CY + 11, GOLD_D)
        return c
    # i == 7: only the long crack remains, some gold chips still scattered
    for dy in range(-2, 3):
        for dx in range(-12, 13):
            d = math.hypot(dx, dy * 2.5)
            if d < 10: p(c, CX + dx, CY + 11 + dy, CRACK if d < 4 else STRATA)
    for s in range(-9, 10):
        p(c, CX + s * 0.8, CY + 11, CRACK_L)
    p(c, CX - 7, CY + 8, GOLD_D); p(c, CX + 8, CY + 9, GOLD_D)
    return c

ANIMATIONS = [("burst", [frame(i) for i in range(8)], 14, False,
               {"hitbox": {"shape": "circle", "center": [float(CX), float(CY)], "active": [2, 4]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("OK", NAME)
