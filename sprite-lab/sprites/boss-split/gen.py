#!/usr/bin/env python3
"""boss-split — Vua Slime, boss ải 10 (Bách Ải): vương miện nứt và slime tách thành 6 con.

DNA: VƯƠNG MIỆN BỊ NỨT RA GIỮA — hình tròn thân có vương miện liền mảnh (theo thân),
thu vào tâm rồi nứt ra, 3 mảnh văng ra 3 hướng, thân slime chính sụp (mắt đảo lên).
Bậc I làm với slime thường. Lúc viết file này chưa có animation split trên sprite
king-slime (xem `gamekit art shot king-slime sheet`); effect này được dùng làm lớp
phủ NHẤT QUÁN khi boss tách — không cần animation mới cho quái nhỏ.

Neo: tâm (vị trí boss tách). Chạy: gamekit art run boss-split
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

NAME = "boss-split"
SIZE = 64
CX = CY = SIZE // 2
ANCHOR = (CX + 0.5, CY + 0.5)

GOLD = "#ffd04a"; GOLD_L = "#fff3b0"; GOLD_D = "#b8862a"; OUT = "#2b1b0e"
SLIME = "#3fae6e"; SLIME_L = "#9ff0b8"; SLIME_D = "#1f6b45"
CRACK = "#1e161c"

def p(c, x, y, col):
    xi, yi = int(round(x)), int(round(y))
    if 0 <= xi < SIZE and 0 <= yi < SIZE: c.pixel(xi, yi, col)

def king(c, x, y, squash=0.0, split=False, look=0):
    """Draws the crowned slime boss standing on the floor."""
    for dy in range(20, -1, -1):
        half = 10 + dy * 0.35 + squash * dy * 0.1
        for dx in range(-int(half), int(half) + 1):
            if dy in (0, 19, 20, 18): continue
            p(c, x + dx, y + dy, SLIME if dy % 2 else SLIME_D)
    # crown: three points
    ctop = y - 16 + int(squash * 2)
    # band
    for dx in range(-6, 7):
        p(c, x + dx, ctop + 6, GOLD_D); p(c, x + dx, ctop + 7, GOLD_D)
    # three spikes
    for k in (-5, 0, 5):
        for dy in range(6):
            h = 4 - dy * 0.6
            for dx in range(-int(h), int(h) + 1):
                p(c, x + k + dx, ctop + 6 - dy, GOLD if dy % 2 else GOLD_L)
        p(c, x + k, ctop - 1, GOLD_L)
    if look != 0:
        # look: eyes drawn slightly to the side
        p(c, x - 2 + look, y + 9, OUT); p(c, x + 2 + look, y + 9, OUT)
    else:
        p(c, x - 2, y + 9, OUT); p(c, x + 2, y + 9, OUT)
    if split:
        for s in range(-10, 11):
            p(c, x + s * 0.6, y + 7 + (0 if s % 4 else 1), CRACK)
            p(c, x + s * 0.6, y + 8 + (0 if s % 4 else 1), CRACK)

def frame(i):
    c = Canvas(SIZE, SIZE)
    t = i / 7.0
    # 0: boss standing, eye tracking player
    if i == 0:
        king(c, CX, CY + 4, squash=0.0, split=False, look=-1)
        return c
    # 1: boss squash down, crown trembling
    if i == 1:
        king(c, CX, CY + 5, squash=1.5, split=False, look=1)
        return c
    # 2: maximum squash, a crack across the base
    if i == 2:
        king(c, CX, CY + 6, squash=2.4, split=False, look=0)
        for s in range(-9, 10):
            p(c, CX + s * 0.62, CY + 13, CRACK)
        return c
    # 3: the split — crown cracks, halves separate
    if i == 3:
        # left half
        for dy in range(20, -1, -1):
            half = 10 + dy * 0.35 + 2.4 * dy * 0.1
            for dx in range(-int(half), 0):
                p(c, CX - 2 + dx, CY + 5 + dy, SLIME if dy % 2 else SLIME_D)
        # right half
        for dy in range(20, -1, -1):
            half = 10 + dy * 0.35 + 2.4 * dy * 0.1
            for dx in range(1, int(half) + 1):
                p(c, CX + 2 + dx, CY + 5 + dy, SLIME if dy % 2 else SLIME_D)
        # crown at an angle: left half tilts down, right half tilts up
        for dx in range(-5, 0):
            p(c, CX - 2 + dx, CY - 10, GOLD)
            p(c, CX - 2 + dx, CY - 11 + (abs(dx) // 2), GOLD_L)
        for dx in range(1, 6):
            p(c, CX + 2 + dx, CY - 10, GOLD)
            p(c, CX + 2 + dx, CY - 13 + (dx // 3), GOLD_L)
        # eyes wide
        p(c, CX - 4, CY + 12, OUT); p(c, CX + 4, CY + 12, OUT)
        return c
    # 4: halves bounce apart, two crown shards flying
    if i == 4:
        # halves move away up
        for dx in range(-6, -1):
            for dy in range(14):
                p(c, CX - 7 + dx, CY + 11 - dy, SLIME if dy % 2 else SLIME_D)
        for dx in range(2, 7):
            for dy in range(14):
                p(c, CX + 8 + dx, CY + 11 - dy, SLIME if dy % 2 else SLIME_D)
        # shards flying at two directions
        for k in range(5):
            p(c, CX - 8 - k, CY - 2 - k, GOLD); p(c, CX - 8 - k, CY - 3 - k, GOLD_L)
            p(c, CX + 9 + k, CY - 4 - k, GOLD); p(c, CX + 9 + k, CY - 5 - k, GOLD_L)
        # eyes
        p(c, CX - 7, CY + 9, OUT); p(c, CX + 9, CY + 9, OUT)
        return c
    # 5: six slimes rear up around the split site, crown gone
    if i == 5:
        # slime puddles erupting in a ring
        ring = [(-13, 10), (-7, 3), (0, 0), (8, 2), (14, 10), (0, 13)]
        for (dx, dy) in ring:
            for k in range(3):
                p(c, CX + dx, CY + dy - 2 - k, SLIME if k % 2 else SLIME_D)
            p(c, CX + dx, CY + dy - 4, SLIME_L)
        # leftover crown chips on the floor
        p(c, CX - 10, CY + 12, GOLD_D); p(c, CX + 11, CY + 13, GOLD_D)
        p(c, CX, CY + 13, GOLD_D)
        return c
    # 6: slimes up high, crater fading
    if i == 6:
        ring = [(-14, 10), (-8, 1), (0, -2), (9, 0), (15, 9)]
        for (dx, dy) in ring:
            for k in range(3):
                p(c, CX + dx, CY + dy - 3 - k, SLIME if k % 2 else SLIME_D)
            p(c, CX + dx, CY + dy - 5, SLIME_L)
        # crater on the ground
        for dy in range(3):
            for dx in range(-9, 10):
                d = math.hypot(dx, dy * 2.6)
                if d < 8: p(c, CX + dx, CY + 12 + dy, CRACK if d < 3 else STRATA_dummy())
        for s in range(-7, 8):
            p(c, CX + s * 0.8, CY + 12, CRACK)
        return c
    # 7: quiet afterglow
    if i == 7:
        # slime puddles resting, no crown
        for dy in range(6):
            for dx in range(-9 + dy, 10 - dy):
                if dx + dy > 2: continue
                p(c, CX + dx, CY + 12 + dy * 0.5, CRACK)
        return c
    return c

def STRATA_dummy():
    return "#3a2a1e"

ANIMATIONS = [("burst", [frame(i) for i in range(8)], 12, False,
               {"hitbox": {"shape": "circle", "center": [float(CX), float(CY)], "active": [4, 5]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR)
    print("OK", NAME)
