"""Buff auras fitted to the Bach Ai hero (swordsman, 48 px frame, anchor at the
feet (24, 44)). Same frame and anchor as the hero, so the game draws an aura at
the hero's own position and scale and it lines up exactly.

Each buff owns a zone, so several buffs never draw over each other:
  shield  an ellipse bubble around the whole hero  (centre 24,27  rx 21  ry 17)
  haste   a flat ring and wind streaks at the feet  (y 45..47)
  heal    plus signs rising at both sides, inside the bubble (x 11 and 37)
  power   a flame crown above the head              (y 1..9)
Hero body: x 12..40, y 16..44 (idle / run).
"""
import math

from spritekit import Canvas

W = H = 48
ANCHOR = (24.0, 44.0)
BUBBLE = (24.0, 27.0, 21.0, 17.0)   # cx, cy, rx, ry


def canvas():
    return Canvas(W, H)


def px(c, x, y, col):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        c.pixel(x, y, col)


def ellipse_points(cx, cy, rx, ry, steps=160):
    seen, out = set(), []
    for i in range(steps):
        a = i * math.tau / steps
        p = (int(round(cx + math.cos(a) * rx)), int(round(cy + math.sin(a) * ry)))
        if p not in seen:
            seen.add(p)
            out.append((p, a))
    return out
