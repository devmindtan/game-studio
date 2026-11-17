"""Shared look for the temporary-buff pickups (haste, power, heal, shield).

One family, so the player reads "buff" at a glance and never confuses it with
an xp gem or a coin (round): a hexagonal badge, dark outline, coloured rim lit
from the top-left, a dark core in the same hue, and one clear 10 px symbol.
  idle     8 frames: 1 px bob, a glint running round the rim
  collect  5 frames: rim flashes white, the symbol rises, the badge breaks
           into a ring of specks that fades
Anchor = badge centre (9, 9) of the 18 px frame. Flat colours, no anti-alias.
"""
import math

from spritekit import Canvas

SIZE = 18
C = 8.5          # centre of the 18 px canvas
OUTLINE = "#140f1e"
WHITE = "#ffffff"


def _badge(c, dy, rim, core, glint_a=None):
    """Draws the badge. rim = (light, mid, dark)."""
    for y in range(SIZE):
        for x in range(SIZE):
            dx, ddy = x - C, y - C - dy
            # pointy-top hexagon "radius" (not a circle: coins are round)
            d = max(abs(dx) * 1.1547, abs(dx) * 0.57735 + abs(ddy))
            if d > 8.4:
                continue
            if d > 7.3:
                col = OUTLINE
            elif d > 5.9:
                lit = -dx - ddy          # top-left is lit
                col = rim[0] if lit > 3.0 else (rim[2] if lit < -3.0 else rim[1])
            else:
                col = core
            c.pixel(x, y, col)
    if glint_a is not None:
        gx = round(C + math.cos(glint_a) * 6.3)
        gy = round(C + dy + math.sin(glint_a) * 6.3)
        c.pixel(gx, gy, WHITE)
    # fixed highlight on the lit rim
    c.pixel(5, 3 + dy, WHITE)
    c.pixel(4, 4 + dy, WHITE)


def _symbol(c, rows, pal, dy):
    h = len(rows)
    oy = 4 + (10 - h) // 2 + dy
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != ".":
                c.pixel(4 + i, oy + j, pal[ch])


def build(here, name, rows, pal, rim, core, export_fn):
    assert all(len(r) == 10 for r in rows) and len(rows) <= 10, f"{name}: symbol must be 10 wide, <= 10 tall"
    bob = [0, 0, 0, 1, 1, 1, 0, 0]   # down only: the hexagon tips touch the frame top
    idle = []
    for i, dy in enumerate(bob):
        c = Canvas(SIZE, SIZE)
        _badge(c, dy, rim, core, glint_a=-math.pi * 0.75 + i * math.pi / 4)
        _symbol(c, rows, pal, dy)
        idle.append(c)
    collect = []
    for i in range(5):
        c = Canvas(SIZE, SIZE)
        if i == 0:
            _badge(c, 0, (WHITE, WHITE, rim[0]), core)
            _symbol(c, rows, pal, -1)
        elif i == 1:
            _symbol(c, rows, pal, -2)
            for k in range(8):
                a = k * math.pi / 4
                c.pixel(round(C + math.cos(a) * 7), round(C + math.sin(a) * 7), rim[0])
        elif i == 2:
            for k in range(8):
                a = k * math.pi / 4 + 0.2
                c.pixel(round(C + math.cos(a) * 8), round(C + math.sin(a) * 8), rim[1])
            c.pixel(9, 3, pal["L"])
        elif i == 3:
            for k in range(4):
                a = k * math.pi / 2 + 0.6
                c.pixel(round(C + math.cos(a) * 8), round(C + math.sin(a) * 8), rim[2])
        else:
            c.pixel(9, 2, rim[1])
        collect.append(c)
    export_fn(here, name, [("idle", idle, 8, True, {}), ("collect", collect, 12, False, {})],
              anchor=(9.0, 9.0), preview_scale=10, gif_scale=6)
