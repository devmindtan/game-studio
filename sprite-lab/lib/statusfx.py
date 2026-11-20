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
    """Three solid, outlined five-point stars circling the head (user 2026-11-20: crisp, no faint dots);
    the back stars are smaller and darker. Opacity comes from the game (statuses.json alpha)."""
    c = Canvas(S, 14)
    cx, cy = 15.5, 7.0

    def star(x, y, r, fill, light):
        pts = []
        for k in range(10):
            a = -math.pi / 2 + k * math.pi / 5
            rr = r if k % 2 == 0 else r * 0.45
            pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
        c.polygon(pts, fill)
        _px(c, x, y - r * 0.4, light)

    order = sorted(range(3), key=lambda k: math.sin(i * math.tau / N + k * math.tau / 3))
    for k in order:                           # back stars first
        a = i * math.tau / N + k * math.tau / 3
        x, y = cx + math.cos(a) * 10, cy + math.sin(a) * 3.0
        front = math.sin(a) > 0
        star(x, y, 3.4 if front else 2.4, "#ffd04a" if front else "#c9922a", "#ffffff" if front else "#ffe8a0")
    return c.outline("#3a2a10")


# --- burn: a fire halo hugging the monster, not a row of campfires ---------------
# The old version drew five little flames in a line at the feet. This one wraps
# the body: a warm ring, a few solid tongues rising from the sides and the head,
# and embers drifting up. Bands are filled per row so no checkerboard holes.
_BURN = ["#7a1c0e", "#e43d12", "#ff8a1f", "#ffd24a", "#fff3b0"]


def burn(i):
    """Crisp flames (user 2026-11-20: the old translucent, outline-free dot spray read as a blur, worst on
    big monsters): three solid tongues with a white-yellow core, orange body, red rim and a dark outline,
    swaying with the loop, plus a few solid embers. The game tiles this at whole scale on big bodies."""
    c = Canvas(S, S)
    core, mid, body, rim = "#fff3b0", "#ffd24a", "#ff8a1f", "#e43d12"

    def tongue(cx, base, h, w, phase):
        """A teardrop flame as three nested filled polygons (rim, body, core); the tip sways."""
        sway = math.sin(i * math.tau / N + phase) * 2.0
        def shape(scale, lift):
            hh, ww = h * scale, w * scale
            tip = (cx + sway * scale, base - hh - lift)
            return [(cx - ww, base - lift), (cx - ww * 0.9, base - hh * 0.45 - lift), tip,
                    (cx + ww * 0.9, base - hh * 0.4 - lift), (cx + ww, base - lift), (cx, base + 1 - lift)]
        c.polygon(shape(1.0, 0), rim)
        c.polygon(shape(0.72, 0), body)
        c.polygon(shape(0.42, 0), mid)
        c.polygon(shape(0.2, 0), core)

    lick = [0, 1, 2, 1, 0, -1, -1, 0][i % N]
    tongue(C - 5, C + 8, 10 + lick, 3.2, 0.0)
    tongue(C + 1, C + 8, 14 - lick, 4.2, 2.1)
    tongue(C + 6, C + 8, 9 + (1 if i % 4 < 2 else 0), 2.8, 4.0)
    for k in range(3):                        # solid embers rising and drifting
        y = int(C + 2 - ((i * 2 + k * 5) % 14))
        x = C - 4 + k * 5 + round(math.sin(i * 0.8 + k * 1.7) * 1.5)
        _px(c, x, y, mid if k % 2 else core)
    return c.outline("#4a0e06")


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


# --- slow: viscous drag, not a solid ice block ------------------------------------
# Palette: blue-glass (Lospec, 8 colours) - cold blue/teal. Layout: a sticky pool
# with drips at the feet, big DOWN arrows sinking past the body, and short drag
# streaks at the sides. Freeze keeps the solid crystal, so the two read apart.
def slow(i):
    c = Canvas(S, S)
    DEEP, MID, FIELD = "#394c62c0", "#626d83d0", "#83aa9ca8"
    LIGHT, BRIGHT = "#a4c2cd", "#cbdbfc"
    # sticky pool with a lit surface and two drips
    for y, half in ((26, 9), (27, 11), (28, 9)):
        for x in range(int(C - half), int(C + half) + 1):
            _px(c, x, y, DEEP if y == 28 or abs(x - C) >= half - 1 else MID)
    for dx in (-6, 5):
        for j in range(2):
            _px(c, C + dx, 29 + j, DEEP)
    for k in range(3):                        # slow bubbles
        x = C - 6 + ((i + k * 3) % 7) * 2
        _px(c, x, 25 - (i + k) % 2, LIGHT)
    # short drag streaks at both sides (the monster is being pulled back)
    for k in range(2):
        for x in range(int(C - 13), int(C - 9)):
            _px(c, x, 11 + k * 6 + (i % 2), FIELD)
        for x in range(int(C + 9), int(C + 13)):
            _px(c, x, 13 + k * 6 + (i % 2), FIELD)
    # two big downward arrows, sinking through the loop
    for k, x in enumerate((C - 11, C + 11)):
        y = 6 + ((i * 2 + k * 7) % 14)
        for j in range(4):
            _px(c, x, y + j, MID)
        _px(c, x - 1, y + 3, LIGHT); _px(c, x + 1, y + 3, LIGHT)
        _px(c, x - 2, y + 2, BRIGHT); _px(c, x + 2, y + 2, BRIGHT)
        _px(c, x, y + 4, BRIGHT)
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
