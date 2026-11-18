#!/usr/bin/env python3
"""Generator cho "tree-boss" (Mộc Yêu): boss vùng Rừng Âm U (Bách Ải 6A, design/bosses.md).

Một cây cổ thụ còng lưng biết đi: tán lá rậm tối trên đầu, thân gỗ nứt có khuôn mặt (hốc mắt lục phát sáng,
miệng khe), hai tay là cành khô, phần dưới là chùm rễ bò sát đất. Quay phải. Frame 48x48, neo giữa chân trên đất (24, 47).
move 4 (lắc lư, chùm rễ trườn: từng cặp rễ vươn ra rồi co lại, không có chân), attack 3 (giơ cành → cắm xuống đất: rễ trồi), hurt 2, death 4 (gãy đổ, lá rụng).
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


# the root mass: (start x on the trunk flare, end x on the ground, bend up px); seven roots fan out
ROOTS = [(15, 2, 4), (18, 8, 3), (21, 14, 2), (24, 24, 1), (27, 34, 2), (30, 40, 3), (33, 46, 4)]


def roots(c, base, phase):
    """Crawling roots instead of legs (user 2026-11-18: the lower body must read as moving roots).
    phase 0..3 sends a wave along the fan: one root pair reaches out and lifts, its neighbours pull in,
    so the mass ripples like it drags itself forward."""
    for k, (x0, x1, bend) in enumerate(ROOTS):
        w = (k - phase) % 4            # 0 = reaching, 2 = pulled in
        reach = {0: 2, 1: 1, 2: -1, 3: 0}[w] * (1 if x1 >= x0 else -1)
        lift = 2 if w == 0 else 0
        xe = x1 + reach
        xm = (x0 + xe) / 2
        ym = base - 2 - bend - lift
        pts = [(x0, base - 8), (round(xm), round(ym)), (xe, base)]
        col = ROOT if k % 2 == 0 else BARK_D   # darker than the trunk, so each root reads on its own
        for o in (-1, 0, 1):   # 3 px thick where it leaves the trunk
            c.line(pts[0][0], pts[0][1] + o, pts[1][0], pts[1][1] + o, col)
        c.line(pts[1][0], pts[1][1], pts[2][0], pts[2][1], col)        # 2 px thick, ending on the floor row
        c.line(pts[1][0], pts[1][1] - 1, pts[2][0], pts[2][1] - 1, col)
        c.line(pts[0][0], pts[0][1] - 1, pts[1][0], pts[1][1] - 1, BARK_L)   # lit top edge
        c.pixel(pts[2][0], pts[2][1], BARK_D)
        if w == 0:                     # the reaching tip curls and kicks up a speck of earth
            c.pixel(xe + (1 if xe >= 24 else -1), base, BARK)
            c.pixel(xe + (2 if xe >= 24 else -2), base - 1, MOSS)


def tree(sway=0, arms=0, legs=0, dy=0, eyes=True, lean=0):
    """sway: canopy offset; arms 0 down, 1 raised, 2 slammed; legs 0/1 shuffle."""
    c = Canvas(S, S)
    base = 45
    # trunk (slightly wider at the bottom)
    top = 18 + dy
    # the trunk flares into the root mass at the bottom (no legs)
    c.polygon([(16 + lean, top), (32 + lean, top), (33, base - 7), (34, base - 5), (14, base - 5), (15, base - 7)], BARK)
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
