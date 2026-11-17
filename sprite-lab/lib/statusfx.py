"""Statuses drawn ON monsters (Bach Ai), redesigned 2026-11-17 (the first set was
16 px icons stuck on top; user: too plain, a freeze must be a block of ice).

Every status wraps the monster's body. Frames are 32 px, made for a body of
radius R = 8 px centred in the frame; the game scales them by the monster's own
body radius, so they fit a slime, a bat or a goblin. Anchor: the body centre,
except stun (anchor at the bottom of the star orbit, placed on top of the head).
  freeze  the monster is locked in a translucent ice block (front, top, side,
          cracks, a glint sweeping across); the game also stops its animation
  stun    three five-point stars circling the head with depth (back ones dimmer)
  burn    a warm halo hugging the body, flames on the sides/head, embers rising
  bleed   a wound, drops running down, a small pool under the feet
  slow    a sticky blue puddle at the feet, down-arrows sinking along the sides
  shock   jagged arcs crackling round the body, sparks
"""
import math

from spritekit import Canvas

S = 32
C = 15.5          # body centre of the frame
R = 8.0           # design body radius
N = 8


def _px(c, x, y, col):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < c.width and 0 <= y < c.height:
        c.pixel(x, y, col)


def _line(c, x0, y0, x1, y1, col):
    n = int(max(abs(x1 - x0), abs(y1 - y0))) or 1
    for t in range(n + 1):
        _px(c, x0 + (x1 - x0) * t / n, y0 + (y1 - y0) * t / n, col)


# --- freeze: a jagged ice crystal round the body ---------------------------------
# The first version was a rectangular ice cube (user: "too boxy"). Now it is a
# lump with chipped corners and three planes, translucent so the monster shows
# through, with frost and icicle-free edges. Any flat face is broken by a seam.
_ICE = ["#e2f7ffa0", "#b4e0ffa4", "#7ec1eda6", "#4f8fbca8"]   # light -> deep
_ICE_EDGE, _ICE_OUT = "#eaf9ffa4", "#3f6f96a8"
_FROST = "#ffffff88"


def _poly(c, pts, shade=None):
    """Fill a polygon per row; returns the set of covered pixels."""
    mask = set()
    ys = [p[1] for p in pts]
    for y in range(int(math.floor(min(ys))), int(math.ceil(max(ys))) + 1):
        xs = []
        for (xa, ya), (xb, yb) in zip(pts, pts[1:] + pts[:1]):
            if (ya <= y < yb) or (yb <= y < ya):
                xs.append(xa + (xb - xa) * (y - ya) / (yb - ya))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(int(math.ceil(xs[k])), int(math.floor(xs[k + 1])) + 1):
                mask.add((x, y))
                _px(c, x, y, shade(x, y) if shade else _ICE[1])
    return mask


def freeze(i):
    c = Canvas(S, S)
    # A lump of ice round the body: irregular hexagon, chipped corners, slightly
    # slanted top, three big planes. Nothing of it is a straight cube face.
    top = [(13, 5), (18, 4), (22, 9), (17, 11), (12, 10), (9, 7)]
    left = [(12, 10), (17, 11), (16, 27), (12, 26), (8, 22), (7, 16), (9, 7)]
    right = [(18, 4), (22, 9), (24, 15), (23, 21), (19, 26), (16, 28),
             (16, 27), (17, 11)]
    sil = [(13, 5), (18, 4), (22, 9), (24, 15), (23, 21), (19, 26), (16, 28),
           (12, 26), (8, 22), (7, 16), (9, 7)]

    mask = _poly(c, sil, lambda x, y: _ICE[1])
    _poly(c, top, lambda x, y: _ICE[0])
    _poly(c, left, lambda x, y: _ICE[1])
    _poly(c, right, lambda x, y: _ICE[2])

    def inside(x, y):
        return (x, y) in mask

    # Plane seams: bright refraction lines where the faces meet.
    for a, b in (((13, 5), (17, 11)), ((17, 11), (16, 27)),
                 ((18, 4), (17, 11)), ((17, 11), (23, 21))):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) or 1
        for t in range(n + 1):
            x, y = a[0] + (b[0] - a[0]) * t / n, a[1] + (b[1] - a[1]) * t / n
            if inside(round(x), round(y)):
                _px(c, x, y, "#f2fdff9e")

    # Rim: pale where the light side meets the outline, blue under the crystal.
    for (x, y) in mask:
        if all(inside(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            continue
        _px(c, x, y, _ICE_EDGE if y < 17 else _ICE_OUT)

    # Frosty band just under the top face, so the ice reads as frozen water.
    for x in range(9, 23):
        for y in (12, 13):
            if inside(x, y) and (x + y) % 3 == 0:
                _px(c, x, y, "#f4fdff86")

    # Cracks.
    for (x0, y0), (x1, y1), (x2, y2) in (((8, 16), (12, 16), (13, 11)),
                                         ((20, 13), (17, 18), (18, 23))):
        _line(c, x0, y0, x1, y1, "#eefbffa8")
        _line(c, x1, y1, x2, y2, "#eefbffa8")

    # Frost specks.
    for k in range(5):
        x, y = 10 + (k * 5) % 9, 8 + (k * 7) % 11
        if inside(x, y):
            _px(c, x, y, _FROST)

    # Specular chip on the lit rim.
    for x, y in ((9, 7), (10, 6), (11, 6), (12, 5), (13, 5)):
        _px(c, x, y, "#ffffffd8")

    # Glint sweeping down the lit plane.
    g = (i * 6) % 20 - 3
    for k in range(3):
        for (x, y) in ((8 + g + k, 7 + k), (9 + g + k, 8 + k)):
            if inside(x, y):
                _px(c, x, y, "#ffffffc8")
    return c


# --- stun: stars circling the head -----------------------------------------------
STAR = ["..L..", ".LML.", "LMMML", ".M.M.", "M...M"]


def stun(i):
    c = Canvas(S, 14)
    cx, cy = 15.5, 7.0
    for k in range(3):
        a = i * math.tau / N + k * math.tau / 3
        x, y = cx + math.cos(a) * 11, cy + math.sin(a) * 3.5
        front = math.sin(a) > 0
        pal = {"L": "#ffffff" if front else "#fff2a8", "M": "#ffd04a" if front else "#c9922a"}
        rows = STAR if front else ["L.", "LM"]          # back stars smaller
        oy = -2 if front else -1
        for r, row in enumerate(rows):
            for q, ch in enumerate(row):
                if ch != ".":
                    _px(c, x - len(row) // 2 + q, y + oy + r, pal[ch])
    # dotted orbit
    for k in range(24):
        if (k + i) % 3 == 0:
            a = k * math.tau / 24
            if math.sin(a) < 0:
                _px(c, cx + math.cos(a) * 11, cy + math.sin(a) * 3.5, "#fff2a860")
    return c


# --- burn: a fire halo hugging the monster, not a row of campfires ---------------
# The old version drew five little flames in a line at the feet. This one wraps
# the body: a warm ring, a few solid tongues rising from the sides and the head,
# and embers drifting up. Bands are filled per row so no checkerboard holes.
_BURN = ["#7a1c0e", "#e43d12", "#ff8a1f", "#ffd24a", "#fff3b0"]


def burn(i):
    c = Canvas(S, S)
    # one solid flame = filled tapered rows with a dark rim and a bright core
    widths = [1, 3, 3, 5, 5, 7, 7, 9, 9, 11, 11, 11, 11, 9, 7]

    def flame(cx, base, phase):
        h = len(widths)
        for j, w in enumerate(widths):
            t = j / (h - 1)
            sway = round(math.sin(i * 0.9 + phase + j * 0.4) * t * 2)
            for q in range(-w // 2, w - w // 2):
                edge = abs(q) >= w // 2 - 1
                if edge:
                    col = "#7a1c0e"
                elif t < 0.18:
                    col = "#c42d10"
                elif abs(q) <= 1 and t > 0.72:
                    col = "#fff3b0"
                elif abs(q) <= 1 and t > 0.4:
                    col = "#ffd24a"
                else:
                    col = "#ff7a1fe0"
                _px(c, cx + q + sway, base - (h - 1 - j), col)

    # two side tongues and one above the head; nothing drawn under the feet
    flame(C - 9, C + 9, 0)
    flame(C + 9, C + 10, 2)
    flame(C + 1, C + 2, 4)
    for k in range(5):                       # embers rising off the flames
        y = 20 - ((i * 3 + k * 5) % 18)
        x = C - 9 + k * 5 + math.sin(i * 0.7 + k) * 2
        _px(c, x, y, "#ffd24a")
        if k % 2 == 0:
            _px(c, x, y + 1, "#ff8a1f80")
    return c


# --- bleed: wound, drops, pool ----------------------------------------------------
def bleed(i):
    c = Canvas(S, S)
    DARK, MID, LIGHT = "#5e0c1a", "#c4202f", "#ff6a6a"
    # two wounds on the body (3 px slashes, lit top edge)
    for ox, oy in ((-4, -2), (2, 2)):
        for k in range(5):
            x, y = C + ox + k, C + oy - k * 0.6
            _px(c, x, y, DARK); _px(c, x, y + 1, MID); _px(c, x, y - 1, LIGHT if k % 2 == 0 else MID)
    # drops (2 px wide) running down, each with a lit top
    for k, x in enumerate((C - 7, C + 6, C - 2, C + 2)):
        y = C - 1 + ((i * 2 + k * 4) % 12)
        for dx in (0, 1):
            _px(c, x + dx, y, LIGHT if dx == 0 else MID)
            _px(c, x + dx, y + 1, MID)
            _px(c, x + dx, y + 2, DARK)
    # pool under the feet, spreading and shrinking with the loop
    w = 8 + (i % 4 > 1)
    for y, half in ((26, w - 2), (27, w), (28, w - 1)):
        for x in range(int(C - half), int(C + half) + 1):
            _px(c, x, y, DARK if y == 28 or abs(x - C) > half - 1 else MID)
    _px(c, C - 3, 26, LIGHT); _px(c, C - 2, 26, LIGHT)
    return c


# --- slow: sticky puddle and sinking arrows ----------------------------------------
def slow(i):
    c = Canvas(S, S)
    GOO, GOO_L, GOO_D = "#5a8ee8c0", "#a8ccff", "#2f4f9a"
    for y, half in ((25, 9), (26, 11), (27, 11), (28, 9)):
        for x in range(int(C - half), int(C + half) + 1):
            _px(c, x, y, GOO_D if y == 28 or abs(x - C) >= half - 0.5 else GOO)
    for k in range(3):                        # bubbles on the goo
        x = C - 7 + ((i + k * 3) % 8) * 2
        _px(c, x, 25 - (i + k) % 2, GOO_L)
    for k, x in enumerate((C - 9, C + 9)):    # down arrows sinking along the sides
        y = 8 + ((i * 2 + k * 6) % 14)
        for j, col in enumerate((GOO_L, "#7fb4ff", GOO_D)):
            _px(c, x, y + j - 2, col)
        _px(c, x - 1, y, "#7fb4ff"); _px(c, x + 1, y, "#7fb4ff"); _px(c, x, y + 1, GOO_D)
    return c


# --- shock: arcs round the body ------------------------------------------------------
def shock(i):
    c = Canvas(S, S)
    for k in range(3):
        a0 = (i * 1.7 + k * 2.1) % math.tau
        pts = []
        for j in range(6):
            a = a0 + j * 0.32
            r = R + 2 + (2 if (j + i + k) % 2 else -1)
            pts.append((C + math.cos(a) * r, C + math.sin(a) * r))
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            _line(c, xa, ya, xb, yb, "#7fe8ff80")
            _line(c, xa, ya - 1, xb, yb - 1, "#fff6a0" if k != 1 else "#ffffff")
    for k in range(4):
        a = i * 0.9 + k * 1.6
        _px(c, C + math.cos(a) * (R + 5), C + math.sin(a) * (R + 5), "#ffe14a")
    return c


DRAW = {"slow": slow, "stun": stun, "freeze": freeze, "bleed": bleed, "burn": burn, "shock": shock}


def build(here, name, kind, export_fn):
    frames = [DRAW[kind](i) for i in range(N if kind != "shock" else 6)]
    anchor = (15.5, 13.0) if kind == "stun" else (C, C)
    export_fn(here, name, [("loop", frames, 10, True, {})], anchor=anchor, preview_scale=6, gif_scale=5)
