#!/usr/bin/env python3
"""Generator cho "tree-boss" (Mộc Yêu): boss vùng Rừng Âm U (Bách Ải 6A, design/bosses.md).

Một cây cổ thụ còng lưng biết đi: tán lá rậm tối trên đầu, thân gỗ nứt có khuôn mặt (hốc mắt lục phát sáng,
miệng khe), hai tay là cành khô, gốc ngập trong một gò đất, rễ to cắm xuống đất. Quay phải. Frame 48x48, neo giữa chân trên đất (24, 47).
move 4 (lắc lư; gốc ngập trong gò đất, rễ cắm xuống đất, vòng rễ trồi lên lặn xuống, đất văng phía sau), attack 3 (giơ cành → cắm xuống đất: rễ trồi), hurt 2, death 4 (gãy đổ, lá rụng).
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


# The base is sunk in a mound of earth (user 2026-11-18, third try: arched roots read as spider legs,
# wedges still did not read as moving roots). Thick roots leave the trunk and plunge into the soil; a few
# root loops break the surface and dive back in, like real roots; walking churns the mound and throws clods
# behind. Roots that vanish into the ground are what makes them read as roots, not legs.
SOIL_D, SOIL, SOIL_L = "#2e2014", "#4a3422", "#6a4c30"
GRASS = "#4a7a32"


def roots(c, base, phase, front=False):
    """Back pass (front=False): two thick roots from the trunk foot down the mound.
    Front pass: the earth mound, root loops on it that rise out of the soil and dive back in (they ripple
    with the walk), grass tufts and clods thrown behind."""
    if not front:
        return
    # the mound: a dome of earth 8 rows high, lit top edge
    c.ellipse(3, base - 8, 45, base + 8, SOIL, fill=True)
    c.ellipse(7, base - 8, 41, base + 2, SOIL_L, fill=True)
    c.ellipse(8, base - 7, 40, base + 4, SOIL, fill=True)
    for yy in range(base + 1, base + 9):   # cut at the floor row: the mound sits on the ground
        c.line(0, yy, 47, yy, (0, 0, 0, 0))
    c.line(4, base, 44, base, SOIL_D)
    # thick roots from the trunk foot down the mound, diving in
    for x0, x1, y1 in ((17, 10, base - 2), (31, 38, base - 2)):
        for o in (0, 1, 2):
            c.line(x0, base - 9 + o, x1, y1 + o // 2, BARK if o < 2 else OUTLINE)
        c.line(x0, base - 10, x1, y1 - 1, BARK_L)
    # loops breaking the surface and diving back in
    for k, (lx, w) in enumerate(((5, 5), (19, 4), (26, 4), (39, 5))):
        up = 3 + (1 if (k + phase) % 2 else 0)
        y0 = base - 3 + (1 if lx in (5, 39) else -1)
        pts = [(lx, y0), (lx + w // 2, y0 - up), (lx + w, y0)]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):   # bark, lighter than the soil, with a dark underside
            c.line(ax, ay + 1, bx, by + 1, OUTLINE)
            c.line(ax, ay, bx, by, BARK, 2)
        c.line(pts[0][0], pts[0][1] - 1, pts[1][0], pts[1][1] - 1, BARK_L)
        c.line(pts[1][0], pts[1][1] - 1, pts[2][0], pts[2][1] - 1, BARK_L)
        c.pixel(pts[0][0], pts[0][1] + 1, SOIL_D)   # the dark hole where it enters the soil
        c.pixel(pts[2][0], pts[2][1] + 1, SOIL_D)
    for gx in (9, 15, 33, 40):
        c.pixel(gx, base - 7 + (2 if gx in (9, 40) else 0), GRASS)
        c.pixel(gx + 1, base - 8 + (2 if gx in (9, 40) else 0), GRASS)
    # clods thrown behind (to the left: it moves right), shifting with the walk
    for k in range(3):
        cx = 2 - ((k * 3 + phase * 2) % 6)
        cy = base - 4 - ((k + phase) % 3) * 2
        if cx >= 0:
            c.rect(cx, cy, cx + 1, cy + 1, SOIL_L, fill=True)


def tree(sway=0, arms=0, legs=0, dy=0, eyes=True, lean=0):
    """sway: canopy offset; arms 0 down, 1 raised, 2 slammed; legs 0/1 shuffle."""
    c = Canvas(S, S)
    base = 45
    # trunk (slightly wider at the bottom)
    top = 18 + dy
    roots(c, base, legs)   # roots behind the mound
    # the trunk flares into the root mass at the bottom (no legs)
    c.polygon([(16 + lean, top), (32 + lean, top), (33, base - 5), (32, base - 2), (16, base - 2), (15, base - 5)], BARK)
    c.line(18 + lean, top + 2, 14, base - 5, BARK_L)
    c.line(30 + lean, top + 4, 34, base - 6, BARK_D)
    c.line(24 + lean, top + 14, 23, base - 5, BARK_D)   # crack
    roots(c, base, legs, front=True)   # the mound over the trunk foot and the root ends
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
        # resting branches stay at the shoulders and bend up: branches reaching the ground read as legs
        c.line(16, top + 6, 10, top + 9, BARK, 2); c.line(10, top + 9, 7, top + 5, BARK_D); c.pixel(6, top + 4, LEAF)
        c.line(32, top + 6, 38, top + 9, BARK, 2); c.line(38, top + 9, 41, top + 5, BARK_D); c.pixel(42, top + 4, LEAF)
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
    roots(c, base, k, front=True)   # the stump stays in its mound of earth
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
