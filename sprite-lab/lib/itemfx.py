"""Shared generator for collectible buff items in Sprite Lab.

Each pickup is 16x16, anchor at its centre, with two animations:
  idle     - the item bobs in place, with a light sparkle orbiting it
  collect  - a bright flash, then the item breaks into specks and fades away

Colours stay flat (no anti-alias); a 1px dark outline keeps the silhouette
readable over both grass and dungeon floors. The art itself is always a
hand-authored pixel map passed in by each item's gen.py.
"""
import math

from spritekit import Canvas, from_rows

SIZE = 16
OUTLINE = "#1b1726"
BOB = [0, -1, -2, -1, 0, 1]


def build(here, name, rows, palette, accent, export_fn):
    art = from_rows(rows, palette)
    assert art.width <= SIZE and art.height <= SIZE, f"{name}: art larger than {SIZE}px"
    ox = (SIZE - art.width) // 2
    oy = (SIZE - art.height) // 2

    idle = []
    for i, dy in enumerate(BOB):
        c = Canvas(SIZE, SIZE)
        # tall art (13 rows) would lose its top row at the peak of the bob
        c.paste(art, ox, oy + max(dy, -oy))
        for k in range(2):
            a = i * 1.05 + k * math.pi
            c.pixel(8 + round(math.cos(a) * 6.5), 8 + round(math.sin(a) * 5.5), accent)
        c.outline(OUTLINE)
        idle.append(c)

    collect = []
    for i in range(5):
        c = Canvas(SIZE, SIZE)
        if i < 2:
            c.paste(art, ox, oy - i)
            for k in range(7 - i * 3):
                a = k * 1.05 + i * 0.7
                r = 5 + i * 2
                c.pixel(8 + round(math.cos(a) * r), 8 + round(math.sin(a) * r), accent)
        elif i == 2:
            for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0), (0, 0)):
                c.pixel(8 + dx, 8 + dy, accent)
        elif i == 3:
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                c.pixel(8 + dx, 8 + dy, accent)
        else:
            c.pixel(8, 8, accent)
        c.outline(OUTLINE)
        collect.append(c)

    export_fn(here, name, [("idle", idle, 8, True, {}), ("collect", collect, 12, False, {})],
              anchor=(8.0, 8.0), preview_scale=10, gif_scale=6)
