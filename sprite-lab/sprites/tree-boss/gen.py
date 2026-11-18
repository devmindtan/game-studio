#!/usr/bin/env python3
"""Generator cho "tree-boss" (Mộc Yêu): boss vùng Rừng Âm U (Bách Ải 6A, design/bosses.md).

Một cây cổ thụ còng lưng biết đi: tán lá rậm tối trên đầu, thân gỗ nứt có khuôn mặt (hốc mắt lục phát sáng,
miệng khe), hai tay là cành khô, phần dưới là rễ bạnh vè to ở gốc, bò thấp sát đất. Quay phải. Frame 48x48, neo giữa chân trên đất (24, 47).
move 4 (lắc lư; rễ bạnh vè bò sát đất lần lượt trượt đầu rễ tới trước, không nhấc lên, không có chân), attack 3 (giơ cành → cắm xuống đất: rễ trồi), hurt 2, death 4 (gãy đổ, lá rụng).
Chạy: gamekit art run tree-boss
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = "tree-boss"
S = 48
ANCHOR = (24.0, 47.0)
OUTLINE = "#140e0a"
BARK_D, BARK, BARK_L = "#3e2816", "#64412a", "#8e643e"
LEAF_D, LEAF, LEAF_L = "#1e3a22", "#2e5a30", "#4a8040"
EYE, EYE_L = "#7aff6a", "#e0ffd0"
MOSS = "#5a8a3a"
ROOT = "#4e3220"


def disk(c, x, y, r, col):
    c.ellipse(round(x - r), round(y - r), round(x + r), round(y + r), col, fill=True)


# buttress roots (user 2026-11-18: thin arched roots read as spider legs): wide wedges that grow out of
# the trunk foot and run LOW along the ground, uneven lengths, tapering, a forked rootlet at the end.
# (root x on the trunk, length, side -1 left / +1 right, wedge height at the trunk)
ROOTS = [(16, 12, -1, 6), (20, 6, -1, 4), (24, 3, 1, 3), (28, 7, 1, 4), (32, 13, 1, 6)]


def roots(c, base, phase):
    """Wedge-shaped buttress roots hugging the ground. Walking: the roots take turns sliding their tips
    forward a pixel or two and back (the tree drags itself), never lifting off the ground."""
    for k, (x0, length, side, hgt) in enumerate(ROOTS):
        slide = (0, 1, 2, 1)[(k + phase) % 4] * side
        tip = x0 + side * length + slide
        # the wedge: from the trunk foot down to the tip on the floor
        c.polygon([(x0, base - hgt), (x0 - side, base), (tip, base)], ROOT if k % 2 == 0 else BARK)
        c.line(x0, base - hgt, tip, base, BARK_L)            # lit top edge along the root
        c.line(x0, base - hgt + 1, x0 - side, base, OUTLINE)  # dark inner edge: a gap between roots
        # a forked rootlet near the tip, flat on the ground
        fx = x0 + side * (length * 2 // 3) + slide
        c.line(fx, base, fx + side * 3, base, BARK_D)
        c.pixel(fx + side * 2, base - 1, BARK_D)
        if (k + phase) % 4 == 2:   # the tip that slid forward kicks up a speck of earth
            c.pixel(tip + side, base - 1, MOSS)


def tree(sway=0, arms=0, legs=0, dy=0, eyes=True, lean=0):
    """sway: canopy offset; arms 0 down, 1 raised, 2 slammed; legs 0/1 shuffle."""
    c = Canvas(S, S)
    base = 45
    # trunk (slightly wider at the bottom)
    top = 18 + dy
    # the trunk flares into the root mass at the bottom (no legs)
    c.polygon([(16 + lean, top), (32 + lean, top), (33, base - 5), (32, base - 2), (16, base - 2), (15, base - 5)], BARK)
    c.line(18 + lean, top + 2, 14, base - 5, BARK_L)
    c.line(30 + lean, top + 4, 34, base - 6, BARK_D)
    c.line(24 + lean, top + 14, 23, base - 5, BARK_D)   # crack
    roots(c, base, legs)   # over the trunk foot: the roots grow out of it
    # face
    fy = top + 7
    if eyes:
        for ex in (20, 27):
            c.rect(ex + lean, fy, ex + 2 + lean, fy + 1, EYE, fill=True)
            c.pixel(ex + 1 + lean, fy, EYE_L)
    else:
        for ex in (20, 27):
            c.rect(ex + lean, fy, ex + 2 + lean, fy + 1, BARK_D, fill=True)
    c.line(21 + lean, fy + 5, 28 + lean, fy + 5, BARK_D)
    c.pixel(29 + lean, fy + 6, BARK_D)
    # branch arms
    if arms == 0:
        c.line(16, top + 6, 9, top + 16, BARK, 2); c.line(9, top + 16, 7, top + 20, BARK_D)
        c.line(32, top + 6, 39, top + 15, BARK, 2); c.line(39, top + 15, 42, top + 19, BARK_D)
    elif arms == 1:
        c.line(16, top + 5, 8, top - 4, BARK, 2); c.line(8, top - 4, 6, top - 8, BARK_D)
        c.line(32, top + 5, 41, top - 4, BARK, 2); c.line(41, top - 4, 43, top - 8, BARK_D)
    else:
        c.line(16, top + 6, 8, base - 2, BARK, 2); c.line(8, base - 2, 7, base, BARK_D)
        c.line(32, top + 6, 41, base - 2, BARK, 2); c.line(41, base - 2, 42, base, BARK_D)
    # canopy
    cx = 24 + sway + lean
    cy = top - 4
    for dx, ddy, r in ((-8, 2, 7), (8, 2, 7), (0, -3, 9), (-4, 4, 6), (5, 4, 6)):
        disk(c, cx + dx, cy + ddy, r, LEAF)
    for dx, ddy, r in ((-6, -1, 3), (4, -6, 3), (9, 0, 2)):
        disk(c, cx + dx, cy + ddy, r, LEAF_L)
    for dx, ddy in ((-10, 6), (0, 7), (9, 6), (-3, 5)):
        disk(c, cx + dx, cy + ddy, 2, LEAF_D)
    c.pixel(17 + lean, top + 1, MOSS); c.pixel(30 + lean, top + 2, MOSS)
    return c.outline(OUTLINE)


def flash(c, amount=0.7):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x14, 0x0e, 0x0a):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def fallen(k):
    """Crumbles: the trunk sinks and splits, leaves scatter, then a stump and leaves."""
    c = Canvas(S, S)
    base = 45
    h = [22, 14, 7][k]
    c.polygon([(15, base - h), (33, base - h + 3), (34, base), (14, base)], BARK)
    c.line(23, base - h, 25, base, BARK_D)
    for n in range(10 + 4 * k):
        x = 6 + (n * 13) % 36
        y = base - 2 - (n * 7) % (8 + 6 * (2 - k))
        c.pixel(x, y, LEAF if n % 3 else LEAF_L)
    return c.outline(OUTLINE)


HB = {"shape": "rect", "center": [24.0, 47.0]}
ANIMATIONS = [
    ("move", [tree(0, 0, 0), tree(1, 0, 1, 1), tree(0, 0, 2), tree(-1, 0, 3, 1)], 6, True,
     {"durations_ms": [180, 180, 180, 180], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [tree(0, 1, 0, -1), tree(0, 1, 0, -2), tree(1, 2, 0, 1, lean=1)], 8, False,
     {"durations_ms": [260, 220, 300], "hitbox": {**HB, "active": [2, 2]}}),
    ("hurt", [flash(tree(1, 0, 0)), tree(-1, 0, 1)], 12, False, {"durations_ms": [80, 140], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(tree(0, 2, 0, 1, eyes=False), 0.4), fallen(0), fallen(1), fallen(2)], 6, False,
     {"durations_ms": [160, 220, 260, 400], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=6, gif_scale=4)
    print(f"OK {NAME}")
