"""Dậm đất (stomp) I-V: a shockwave that spreads out from the hero standing in the
middle, so the centre stays clear (the old ground-slam sprites are craters drawn
top-down with rocks in the middle: under the hero they covered it).

The map is seen from above, so the wave is a circle on the ground (it matches the
circle hitbox). Anchor = centre = the hero's body centre. Each tier keeps the
previous one and adds one idea (pixel-sprite rule, tiers inherit):
  I   a dust ring spreading out, puffs on its edge
  II  + cracks radiating outward from the clear centre
  III + rocks popping up on the ring edge
  IV  + a second, echo ring following the first
  V   + magma glowing in the cracks, the widest
"""
import math

from spritekit import Canvas

DUST_L = "#f2dcb0"; DUST = "#d9bb8c"; DUST_D = "#9a7a55"; OUT = "#2a2018"; CRACK = "#3a2a1e"; CRACK_L = "#6b4f38"
ROCK = "#9a8066"; ROCK_L = "#c9b08f"; ROCK_D = "#5a4535"
MAGMA = "#ff6a2a"; MAGMA_L = "#ffc04a"
CLEAR = 9            # radius of the clear centre (the hero stands there)
FRAMES = 8


def _px(c, size, x, y, col):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < size and 0 <= y < size:
        c.pixel(x, y, col)


def _ring(c, size, cx, cy, r, col, gap_seed=0, dotted=False):
    n = max(12, int(r * 6.4))
    for i in range(n):
        a = i * math.tau / n
        if dotted and (i + gap_seed) % 3 == 0:
            continue
        _px(c, size, cx + math.cos(a) * r, cy + math.sin(a) * r, col)


def _blob(c, size, x, y, w, h, col, edge):
    for dy in range(h):
        for dx in range(w):
            corner = (dx in (0, w - 1)) and (dy in (0, h - 1))
            if not corner:
                _px(c, size, x + dx - w // 2, y + dy - h // 2, col)
    _px(c, size, x - w // 2, y + h // 2, edge)


def frame(tier, i, size):
    c = Canvas(size, size)
    cx = cy = (size - 1) / 2.0
    rmax = size / 2.0 - 4
    t = i / (FRAMES - 1)
    r = CLEAR + (rmax - CLEAR) * min(1.0, t * 1.25)      # main ring radius
    fade = 1.0 if t < 0.7 else max(0.0, 1.0 - (t - 0.7) / 0.3)
    # impact flash under the feet, first two frames
    if i < 2:
        rf = CLEAR + 2 + i * 3
        for y in range(size):
            for x in range(size):
                d = math.hypot(x - cx, y - cy)
                if CLEAR - 2 < d <= rf:
                    _px(c, size, x, y, DUST_L if d > rf - 1.5 else "#f2dcb066")
    # II+: cracks from the clear centre outward (2 px, lit edge), grown with the ring
    if tier >= 2:
        for k in range(8):
            a = k * math.pi / 4 + 0.2 * math.sin(k * 2.1)
            reach = min(r - 3, rmax * 0.85)
            for s_ in range(max(0, int(reach - CLEAR))):
                rr = CLEAR + s_
                wob = math.sin(rr * 0.7 + k) * 1.0
                x = cx + math.cos(a) * rr - math.sin(a) * wob
                y = cy + math.sin(a) * rr + math.cos(a) * wob
                hot = tier >= 5 and t > 0.2
                _px(c, size, x, y, (MAGMA_L if (s_ + i) % 4 == 0 else MAGMA) if hot else CRACK)
                _px(c, size, x + 1, y, MAGMA if hot else CRACK)
                _px(c, size, x, y - 1, CRACK_L if not hot else "#b8481a")
    # IV+: echo ring, behind the main one
    if tier >= 4 and t > 0.25:
        re = CLEAR + (r - CLEAR) * 0.6
        _ring(c, size, cx, cy, re, DUST_D, gap_seed=i, dotted=True)
        _ring(c, size, cx, cy, re + 1, DUST, gap_seed=i + 1, dotted=True)
    # main ring: a 3 px band (light outside, dark inside) with dust clumps
    if fade > 0.0:
        light = DUST_L if fade > 0.6 else DUST
        _ring(c, size, cx, cy, r + 1, OUT if fade > 0.6 else DUST_D)
        _ring(c, size, cx, cy, r, light)
        _ring(c, size, cx, cy, r - 1, DUST)
        _ring(c, size, cx, cy, r - 2, DUST_D, gap_seed=i, dotted=True)
        for k in range(10):
            a = k * math.tau / 10 + i * 0.11
            if (k + i) % 2 == 0:
                _blob(c, size, cx + math.cos(a) * (r + 1), cy + math.sin(a) * (r + 1) - 1, 3, 2, light, DUST_D)
    # III+: rocks popping up on the ring edge (rise then fall)
    if tier >= 3 and 0.15 < t < 0.95:
        hop = math.sin((t - 0.15) / 0.8 * math.pi) * 4
        for k in range(6):
            a = k * math.tau / 6 + 0.5
            x = int(round(cx + math.cos(a) * r))
            y = int(round(cy + math.sin(a) * r - hop))
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    if abs(dx) + abs(dy) <= 2:
                        edge = abs(dx) + abs(dy) == 2
                        col = OUT if edge else (ROCK_L if dx + dy < 0 else (ROCK_D if dx + dy > 0 else ROCK))
                        _px(c, size, x + dx, y + dy, col)
    return c


def build(here, name, tier, size, export_fn):
    frames = [frame(tier, i, size) for i in range(FRAMES)]
    c = (size - 1) / 2.0
    export_fn(here, name, [("burst", frames, 16, False,
                            {"hitbox": {"shape": "circle", "center": [c, c], "active": [2, 5]}})],
              anchor=(c, c))
