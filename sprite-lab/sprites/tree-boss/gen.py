#!/usr/bin/env python3
"""Generator cho "tree-boss" (Mộc Yêu): boss vùng Rừng Âm U (Bách Ải 6A, design/bosses.md).

Một cây cổ thụ còng lưng biết đi: tán lá rậm tối trên đầu, thân gỗ nứt có khuôn mặt (hốc mắt lục phát sáng,
miệng khe), hai tay là cành khô, phần dưới là nhiều rễ riêng rẽ xoắn, có gai, đầu rễ cong vểnh lên. Quay phải. Frame 48x48, neo giữa chân trên đất (24, 47).
move 4 (lắc lư; các rễ lần lượt cuộn đầu lên rồi duỗi, bám và kéo thân đi), attack 3 (giơ cành → cắm xuống đất: rễ trồi), hurt 2, death 4 (gãy đổ, lá rụng).
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
# Phase 2, Cổ Thụ Trụi Lá (bach-ai design/bosses.md, user 2026-11-19): BARE drops the canopy for dry
# twigs round a glowing jade crystal core, and the roots curl into two thick root legs that run.
BARE = False
# The transform animation (phase 1 -> 2) switches the parts one by one: CROWN (bare crown + crystal) and
# LEGS (root legs); None follows BARE.
CROWN = None
LEGS = None
CURL = 0   # transform: every root tip lifts this many px (the roots draw in before they become legs)


def _crown_on():
    return BARE if CROWN is None else CROWN


def _legs_on():
    return BARE if LEGS is None else LEGS
JADE_D, JADE, JADE_L = "#1a7a6a", "#3ad8b8", "#c8fff0"
TWIG = "#5a4630"


def disk(c, x, y, r, col):
    c.ellipse(round(x - r), round(y - r), round(x + r), round(y + r), col, fill=True)


# The base is sunk in a mound of earth (user 2026-11-18, third try: arched roots read as spider legs,
# wedges still did not read as moving roots). Thick roots leave the trunk and plunge into the soil; a few
# root loops break the surface and dive back in, like real roots; walking churns the mound and throws clods
# behind. Roots that vanish into the ground are what makes them read as roots, not legs.
SOIL_D, SOIL, SOIL_L = "#2e2014", "#4a3422", "#6a4c30"
GRASS = "#4a7a32"


# User 2026-11-18 (fourth try): the roots are MANY separate parts that curl up, gnarled and thorny, not
# one mass. Each root is hand-placed: thick at the trunk, tapering, twisting, its tip hooking up; thorn
# spurs and knots along it; lengths and directions uneven (an even fan of thin arcs reads as spider legs).
# Points are (x, y above the floor) from the trunk foot to the tip; thorns are indexes of points with a spur.
ROOT_PATHS = [
    ([(16, 7), (11, 4), (6, 2), (3, 3), (1, 6), (2, 9)], (2,)),          # long left, hooks up
    ([(19, 5), (16, 1), (12, 0), (10, 2), (10, 4)], (1,)),               # left, curls up
    ([(22, 4), (21, 1), (20, 0)], ()),                                   # short stub
    ([(27, 4), (29, 1), (31, 0), (33, 2)], ()),                          # short right
    ([(30, 6), (34, 2), (38, 1), (41, 3), (41, 6)], (2,)),               # right, curls up
    ([(32, 8), (37, 5), (42, 3), (45, 4), (46, 7), (44, 10)], (1, 3)),   # long right, hooks back
]


def roots(c, base, phase, front=False):
    """Front pass only: every root drawn on its own with a dark rim, so the parts stay separate.
    Walking: the roots take turns curling their tips up a pixel and straightening (they grip and drag)."""
    if not front:
        return
    if _legs_on():
        legs(c, base, phase)
        return
    for k, (path, thorns) in enumerate(ROOT_PATHS):
        lift = CURL if CURL else (2 if (k + phase) % 3 == 0 else 0)
        pts = []
        for n, (x, y) in enumerate(path):
            tip = n >= len(path) - 2 and len(path) > 2
            pts.append((x, base - y - (lift if tip else 0)))
        n = len(pts) - 1
        widths = [max(1, round(3.0 * (1 - t / max(1, n)))) for t in range(n)]
        for (ax, ay), (bx, by), w in zip(pts, pts[1:], widths):   # dark rim first: keeps roots apart
            c.line(ax, ay, bx, by, OUTLINE, w + 1)
        for (ax, ay), (bx, by), w in zip(pts, pts[1:], widths):
            c.line(ax, ay, bx, by, ROOT if k % 2 else BARK, w)
        for (ax, ay), (bx, by), w in zip(pts, pts[1:], widths):   # lit upper edge
            if w > 1:
                c.line(ax, ay - 1, bx, by - 1, BARK_L)
        for t in thorns:   # thorn spurs pointing up and out
            x, y = pts[t]
            out = 1 if x >= 24 else -1
            c.pixel(x + out, y - 2, BARK_D)
            c.pixel(x + 2 * out, y - 3, BARK_L)
        if n >= 3:   # a knot on the longer roots
            kx, ky = pts[1]
            c.pixel(kx, ky - 1, BARK_L)
            c.pixel(kx + 1, ky - 1, BARK_D)
    for yy in range(base + 1, base + 4):   # thick strokes must not sink below the floor row
        c.line(0, yy, 47, yy, (0, 0, 0, 0))


def legs(c, base, phase):
    """Cổ Thụ Trụi Lá: the roots curled into two massive legs (user 2026-11-20: the first stubby legs looked
    clumsy, it must look ferocious). Bow-legged wide stance, thick root-bundle thighs tapering to thorny shins,
    feet of three root claws digging forward plus a heel spur. A charging run over 8 phases: long strides,
    the lifted foot high, soil kicked up behind the planted heel. Refs: OpenGameArt treant, pixie.haus
    menacing treants (weight on two thick root legs, low wide stance)."""
    import math
    t = phase / 8.0 * 2.0 * math.pi
    swing = math.sin(t)
    hip_y = base - 11
    for side, hip_x in ((-1, 18), (1, 30)):
        s = swing * side   # > 0: this leg reaches forward (right, the facing)
        foot_x = round(hip_x + side * 6 + 4 * s)   # a stride that stays under the body (long ones read as spider legs)
        up = max(0.0, s)
        foot_y = base - round(3 * up)
        knee_x = round((hip_x + foot_x) / 2 + side * 3)   # knees bowed out
        knee_y = hip_y + 5 - round(3 * up)   # the forward knee drives up
        col = BARK if side < 0 else ROOT
        thigh = [(hip_x - 3, hip_y), (hip_x + 3, hip_y), (knee_x + 2, knee_y), (knee_x - 2, knee_y)]
        shin = [(knee_x - 2, knee_y), (knee_x + 2, knee_y), (foot_x + 1, foot_y - 1), (foot_x - 1, foot_y - 1)]
        for poly in (thigh, shin):   # dark rim, then the bark
            c.polygon([(x + dx, y + dy) for x, y in poly for dx, dy in ((0, 0),)], OUTLINE)
        c.polygon(thigh, col)
        c.polygon(shin, col)
        c.line(hip_x - 1, hip_y + 1, knee_x - 1, knee_y, BARK_L)   # twisted strands of the root bundle
        c.line(hip_x + 1, hip_y + 2, knee_x + 1, knee_y - 1, BARK_D)
        c.line(knee_x, knee_y + 1, foot_x, foot_y - 2, BARK_L)
        c.pixel(knee_x + side * 2, knee_y, BARK_L)   # knobby knee
        c.pixel(knee_x + side * 3, knee_y - 1, BARK_D)
        for k in (2, 4):   # thorns on the outer shin
            tx = round(knee_x + (foot_x - knee_x) * k / 6) + side * 2
            ty = round(knee_y + (foot_y - knee_y) * k / 6)
            c.pixel(tx, ty, BARK_D)
            c.pixel(tx + side, ty - 1, BARK_L)
        for dx, dy2 in ((2, 0), (4, -1), (3, 1)):   # three root claws digging forward, a heel spur behind
            c.line(foot_x, foot_y - 1, foot_x + dx, foot_y - 1 + dy2, BARK_D)
            c.pixel(foot_x + dx, foot_y - 1 + dy2, BARK_L)
        c.line(foot_x, foot_y - 1, foot_x - 3, foot_y, BARK_D)
        if s < -0.6:   # the planted back foot kicks soil up behind it
            c.pixel(foot_x - 5, foot_y - 3, SOIL_L)
            c.pixel(foot_x - 6, foot_y - 5, SOIL)
            c.pixel(foot_x - 4, foot_y - 6, SOIL_L)
    for yy in range(base + 1, base + 4):
        c.line(0, yy, 47, yy, (0, 0, 0, 0))


def crown(c, cx, cy, pulse):
    """Cổ Thụ Trụi Lá's crown: dry bare twigs fanning out and a jade crystal core that pulses."""
    for dx, dy2 in ((-9, -4), (-6, -9), (0, -11), (6, -9), (9, -4), (-11, 1), (11, 1)):
        c.line(cx, cy + 2, cx + dx, cy + dy2, TWIG, 1)
        c.pixel(cx + dx, cy + dy2, BARK_L)
    c.polygon([(cx, cy - 7), (cx + 4, cy - 2), (cx + 2, cy + 3), (cx - 2, cy + 3), (cx - 4, cy - 2)], JADE_D)
    c.polygon([(cx, cy - 6), (cx + 3, cy - 2), (cx + 1, cy + 2), (cx - 1, cy + 2), (cx - 3, cy - 2)], JADE)
    c.line(cx - 1, cy - 4, cx - 2, cy - 1, JADE_L)
    if pulse:   # the core flares: a glint and a halo of light
        c.pixel(cx + 1, cy - 5, "#ffffff")
        for hx, hy in ((-5, -6), (5, -6), (-6, 0), (6, 0), (0, -9)):
            c.pixel(cx + hx, cy + hy, JADE_L)


def tree(sway=0, arms=0, legs=0, dy=0, eyes=True, lean=0, glow=False, leaf=-1, mouth=0, shed=0.0, curl=0):
    """sway: canopy offset; arms 0 down, 1 raised, 2 slammed; legs 0/1 shuffle."""
    if BARE:   # phase 2 always glares, snarls and leans into the charge
        glow = glow or eyes
        mouth = max(mouth, 2)   # a snarl of bark teeth
        lean = lean + 1
        dy = dy + (1 if legs % 4 in (0, 1) else 0)   # it drops onto each planted foot
    c = Canvas(S, S)
    base = 45
    # trunk (slightly wider at the bottom)
    top = 18 + dy
    # the trunk flares into the root mass at the bottom (no legs)
    lift = 9 if _legs_on() else 0   # phase 2: the trunk ends at the hips so the two root legs show below it
    flare = 2 if _legs_on() else 0   # and the hips flare wide over them
    c.polygon([(16 + lean, top), (32 + lean, top), (33 + flare, base - 6 - lift), (31 + flare, base - 3 - lift),
               (17 - flare, base - 3 - lift), (15 - flare, base - 6 - lift)], BARK)
    c.line(18 + lean, top + 2, 14, base - 5 - lift, BARK_L)
    c.line(30 + lean, top + 4, 34, base - 6 - lift, BARK_D)
    c.line(24 + lean, top + 14, 23, base - 5 - lift, BARK_D)   # crack
    roots(c, base, legs, front=True)   # many separate gnarled roots over the trunk foot
    # face
    fy = top + 7
    if eyes:
        for ex in (20, 27):
            c.rect(ex + lean, fy, ex + 2 + lean, fy + 1, EYE, fill=True)
            c.pixel(ex + 1 + lean, fy, EYE_L)
            if glow:   # rage: the eyes blaze and slant into a scowl
                c.pixel(ex - 1 + lean, fy - 1, BARK_D)
                c.pixel(ex + 3 + lean, fy - 1, BARK_D)
                c.rect(ex + lean, fy - 1, ex + 2 + lean, fy - 1, EYE, fill=True)
    else:
        for ex in (20, 27):
            c.rect(ex + lean, fy, ex + 2 + lean, fy + 1, BARK_D, fill=True)
    if mouth:   # a split in the bark roars open
        c.rect(21 + lean, fy + 4, 28 + lean, fy + 4 + mouth, "#1a0e08", fill=True)
        for tx in range(22, 28, 2):
            c.pixel(tx + lean, fy + 4, BARK_L)
    else:
        c.line(21 + lean, fy + 5, 28 + lean, fy + 5, BARK_D)
        c.pixel(29 + lean, fy + 6, BARK_D)
    # branch arms
    if arms == 0:
        # resting branches stay at the shoulders and bend up: branches reaching the ground read as legs
        c.line(16, top + 6, 10, top + 9, BARK, 2); c.line(10, top + 9, 7, top + 5, BARK_D); c.pixel(6, top + 4, LEAF)
        c.line(32, top + 6, 38, top + 9, BARK, 2); c.line(38, top + 9, 41, top + 5, BARK_D); c.pixel(42, top + 4, LEAF)
    elif arms == 0.5:
        c.line(16, top + 6, 9, top + 2, BARK, 2); c.line(9, top + 2, 6, top - 2, BARK_D)
        c.line(32, top + 6, 39, top + 2, BARK, 2); c.line(39, top + 2, 42, top - 2, BARK_D)
    elif arms == 1.5:
        c.line(16, top + 6, 8, top + 12, BARK, 2); c.line(8, top + 12, 6, top + 16, BARK_D)
        c.line(32, top + 6, 40, top + 12, BARK, 2); c.line(40, top + 12, 42, top + 16, BARK_D)
    elif arms == 1:
        c.line(16, top + 5, 8, top - 4, BARK, 2); c.line(8, top - 4, 6, top - 8, BARK_D)
        c.line(32, top + 5, 41, top - 4, BARK, 2); c.line(41, top - 4, 43, top - 8, BARK_D)
    else:
        c.line(16, top + 6, 8, base - 2, BARK, 2); c.line(8, base - 2, 7, base, BARK_D)
        c.line(32, top + 6, 41, base - 2, BARK, 2); c.line(41, base - 2, 42, base, BARK_D)
    # canopy
    cx = 24 + sway + lean
    cy = top - 4
    if _crown_on():   # phase 2: no leaves, a bare crown round the crystal core
        crown(c, cx, cy, legs % 2 == 0)
        c.pixel(17 + lean, top + 1, MOSS)
        return c.outline(OUTLINE)
    keep = 1.0 - shed   # transform: the canopy thins and its leaves burst outward
    for dx, ddy, r in ((-8, 2, 7), (8, 2, 7), (0, -3, 9), (-4, 4, 6), (5, 4, 6)):
        if r * keep >= 1:
            disk(c, cx + dx, cy + ddy, r * keep, LEAF)
    for dx, ddy, r in ((-6, -1, 3), (4, -6, 3), (9, 0, 2)):
        if r * keep >= 1:
            disk(c, cx + dx, cy + ddy, r * keep, LEAF_L)
    for dx, ddy in ((-10, 6), (0, 7), (9, 6), (-3, 5)):
        if keep > 0.5:
            disk(c, cx + dx, cy + ddy, 2, LEAF_D)
    if shed > 0:
        import math
        for n in range(14):   # torn leaves flying out of the canopy all round
            a = n / 14.0 * 2.0 * math.pi + n * 0.3
            dist = 6 + shed * 16 + (n % 3) * 2
            lx, ly = round(cx + math.cos(a) * dist), round(cy + math.sin(a) * dist * 0.8)
            if 0 <= lx < S - 1 and 0 <= ly < S:
                c.pixel(lx, ly, LEAF_L if n % 2 else LEAF)
                c.pixel(lx + 1, ly, LEAF)
    c.pixel(17 + lean, top + 1, MOSS); c.pixel(30 + lean, top + 2, MOSS)
    if leaf >= 0:   # a leaf drifting down from the canopy (secondary motion)
        lx = 10 + (leaf * 5) % 30 + (1 if leaf % 2 else -1)
        ly = top + 2 + leaf * 3
        c.pixel(lx, ly, LEAF_L)
        c.pixel(lx + 1, ly, LEAF)
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


def fallen(k, h=None):
    """Crumbles: the trunk sinks and splits, leaves scatter, then a stump and leaves. h overrides the height."""
    c = Canvas(S, S)
    base = 45
    k = min(k, 2)
    h = h if h is not None else [22, 14, 7][k]
    roots(c, base, k, front=True)   # the stump keeps its roots
    c.polygon([(15, base - h), (33, base - h + 3), (34, base), (14, base)], BARK)
    c.line(23, base - h, 25, base, BARK_D)
    if BARE:   # the crystal core lies shattered by the stump
        for n in range(4 + 2 * k):
            c.pixel(8 + (n * 11) % 32, base - 1 - (n * 5) % 6, JADE if n % 2 else JADE_L)
        return c.outline(OUTLINE)
    for n in range(10 + 4 * k):
        x = 6 + (n * 13) % 36
        y = base - 2 - (n * 7) % (8 + 6 * (2 - k))
        c.pixel(x, y, LEAF if n % 3 else LEAF_L)
    return c.outline(OUTLINE)


HB = {"shape": "rect", "center": [24.0, 47.0]}


def build():
    """The animations, built now (tree-boss-bare sets BARE first, then calls this)."""
    return [
        # move 8: canopy sways and lags the trunk, roots curl in turn, trunk bobs, a leaf drifts down
        ("move", [tree(0, 0, 0, 0, leaf=0), tree(1, 0, 1, 1, leaf=1), tree(2, 0, 2, 0, leaf=2), tree(1, 0, 3, 1, leaf=3),
                  tree(0, 0, 4, 0, leaf=4), tree(-1, 0, 5, 1, leaf=5), tree(-2, 0, 6, 0, leaf=6), tree(-1, 0, 7, 1)], 6, True,
         {"durations_ms": [170, 160, 160, 180, 170, 160, 160, 180], "hitbox": {**HB, "active": [0, 7]}}),
        # attack 8: eyes blaze, branches rise, roars, rears up high, slams the branches into the ground, impact, recovers
        ("attack", [tree(0, 0.5, 0, 0, glow=True), tree(0, 1, 0, -1, glow=True), tree(-1, 1, 1, -2, glow=True, mouth=2),
                    tree(-1, 1, 1, -3, glow=True, mouth=3), tree(1, 1.5, 2, -1, glow=True, mouth=2, lean=1),
                    tree(2, 2, 2, 1, glow=True, lean=1), tree(1, 2, 3, 1, glow=True), tree(0, 0.5, 0, 0)], 8, False,
         {"durations_ms": [160, 180, 200, 260, 80, 160, 160, 160], "hitbox": {**HB, "active": [5, 6]}}),
        # hurt 4: flash, canopy whips back, groan, settles
        ("hurt", [flash(tree(1, 0, 0)), tree(-2, 0.5, 1, 0, eyes=False, mouth=1), tree(-1, 0, 2, 1, mouth=1), tree(0, 0, 3)], 12, False,
         {"durations_ms": [70, 110, 110, 130], "hitbox": {**HB, "active": [0, 3]}}),
        # death 8: struck, roars, branches drop, the trunk cracks and sinks, splits, leaves scatter, a stump remains
        ("death", [flash(tree(0, 1, 0, -1, glow=True, mouth=3), 0.4), tree(-1, 1, 1, -1, mouth=3), tree(1, 2, 2, 1, eyes=False),
                   fallen(0, 26), fallen(0), fallen(1, 18), fallen(1), fallen(2)], 6, False,
         {"durations_ms": [140, 180, 180, 160, 200, 200, 240, 400], "hitbox": {**HB, "active": [0, 7]}}),
    ]


if __name__ == "__main__":
    export(HERE, NAME, build(), anchor=ANCHOR, ground=True, body="move", preview_scale=6, gif_scale=4)
    print(f"OK {NAME}")
