"""Status effects drawn ON monsters (and later any character): 16 px loops.
Anchor at the frame centre; the game places them at the monster's body centre,
above its head or at its feet (statuses.json "at").
  slow    blue streaks sinking at the feet
  stun    three stars circling above the head
  freeze  ice crystals over the body (the game also tints the body)
  bleed   drops of blood falling off the body
  burn    small flames licking up the body
  shock   an electric spark (where a shock lands)
"""
import math

from spritekit import Canvas

S = 16
OUT = "#1b1726"
N = 6


def _px(c, x, y, col):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < S and 0 <= y < S:
        c.pixel(x, y, col)


def slow(i):
    c = Canvas(S, S)
    for k, x in enumerate((3, 8, 12)):
        y0 = 4 + ((i * 2 + k * 3) % 9)
        for j, col in enumerate(("#d8ecff", "#7fb4ff", "#3d6fd0")):
            _px(c, x, y0 + j, col)
    # a flat ring at the feet
    for x in range(2, 14):
        _px(c, x, 14, "#3d6fd0" if (x + i) % 3 else "#7fb4ff")
    return c


def stun(i):
    c = Canvas(S, S)
    for k in range(3):
        a = i * math.tau / N + k * math.tau / 3
        x, y = 8 + math.cos(a) * 6, 8 + math.sin(a) * 2.5
        col = "#fff2a8" if math.sin(a) > 0 else "#f2c040"
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            _px(c, x + dx, y + dy, col)
        _px(c, x, y, "#ffffff")
    c.outline(OUT)
    return c


def freeze(i):
    c = Canvas(S, S)
    shards = [(4, 9, 5), (8, 6, 7), (12, 10, 5), (6, 13, 3), (11, 4, 3)]
    for k, (x, y, h) in enumerate(shards):
        for j in range(h):
            col = "#ffffff" if j == 0 else ("#c8f4ff" if j < h - 1 else "#6fc3ff")
            _px(c, x, y - h // 2 + j, col)
        _px(c, x + 1, y, "#6fc3ff")
    gx, gy = shards[i % len(shards)][:2]
    _px(c, gx - 1, gy - 2, "#ffffff")
    c.outline(OUT)
    return c


def bleed(i):
    c = Canvas(S, S)
    for k, x in enumerate((4, 9, 12)):
        y = 3 + ((i * 2 + k * 4) % 11)
        _px(c, x, y, "#ff5a5a")
        _px(c, x, y + 1, "#d9364a")
        _px(c, x + 1, y + 1, "#8f1f35")
        _px(c, x, y + 2, "#8f1f35")
    c.outline(OUT)
    return c


def burn(i):
    c = Canvas(S, S)
    for k, x in enumerate((4, 8, 12)):
        h = 4 + ((i + k * 2) % 3)
        base = 14
        for j in range(h):
            col = "#fff2a8" if j > h - 2 else ("#ffb43a" if j > h - 4 else "#ff5a1f")
            w = 1 if j > h - 3 else 2
            for dx in range(w):
                _px(c, x + dx - (1 if w == 2 else 0) + (1 if (j + i + k) % 4 == 0 else 0), base - j, col)
    c.outline(OUT)
    return c


def shock(i):
    c = Canvas(S, S)
    pts = [(8, 1), (6, 5), (9, 7), (6, 11), (8, 15)] if i % 2 == 0 else [(7, 1), (10, 5), (7, 8), (10, 11), (7, 15)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = max(abs(x1 - x0), abs(y1 - y0))
        for t in range(n + 1):
            _px(c, x0 + (x1 - x0) * t / n, y0 + (y1 - y0) * t / n, "#fff6a0" if t % 2 else "#ffffff")
    for k in range(3):
        a = i * 1.3 + k * 2.1
        _px(c, 8 + math.cos(a) * 6, 8 + math.sin(a) * 6, "#ffe14a")
    c.outline(OUT)
    return c


DRAW = {"slow": slow, "stun": stun, "freeze": freeze, "bleed": bleed, "burn": burn, "shock": shock}


def build(here, name, kind, export_fn):
    frames = [DRAW[kind](i) for i in range(N)]
    export_fn(here, name, [("loop", frames, 10, True, {})], anchor=(8.0, 8.0), preview_scale=8, gif_scale=6)
