"""Statuses drawn ON monsters (Bach Ai), redesigned 2026-11-17 (the first set was
16 px icons stuck on top; user: too plain, a freeze must be a block of ice).

Every status wraps the monster's body. Frames are 32 px, made for a body of
radius R = 8 px centred in the frame; the game scales them by the monster's own
body radius, so they fit a slime, a bat or a goblin. Anchor: the body centre,
except stun (anchor at the bottom of the star orbit, placed on top of the head).
  freeze  the monster is locked in a translucent ice block (front, top, side,
          cracks, a glint sweeping across); the game also stops its animation
  stun    three five-point stars circling the head with depth (back ones dimmer)
  burn    flames rising round the body from the feet, embers flying up
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


# --- freeze: an ice block -------------------------------------------------------
def freeze(i):
    c = Canvas(S, S)
    x0, x1 = 5, 25           # front face
    y0, y1 = 9, 27
    top = 4                  # depth of the top face / side
    FRONT, TOP, SIDE = "#9fdcffa8", "#dff7ffc8", "#5aa8dcb8"
    EDGE, OUT, FROST = "#f2fcff", "#2a5f8a", "#ffffff70"
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            _px(c, x, y, FRONT)
    for k in range(top):                     # top face, slanted right
        for x in range(x0 + k + 1, x1 + k + 2):
            _px(c, x, y0 - k - 1, TOP)
    for k in range(top):                     # right side
        for y in range(y0 - k, y1 - k + 1):
            _px(c, x1 + k + 1, y, SIDE)
    # outline
    _line(c, x0, y0, x0, y1, OUT); _line(c, x0, y1, x1, y1, OUT)
    _line(c, x1 + top, y0 - top, x1 + top, y1 - top, OUT); _line(c, x1, y1, x1 + top, y1 - top, OUT)
    _line(c, x0, y0, x0 + top, y0 - top, OUT); _line(c, x0 + top, y0 - top, x1 + top, y0 - top, OUT)
    # lit edges
    _line(c, x0 + 1, y0, x1, y0, EDGE); _line(c, x1, y0, x1, y1 - 1, EDGE)
    _line(c, x0 + 1, y0 + 1, x0 + 1, y0 + 6, EDGE)
    # cracks and frost specks
    _line(c, x0 + 4, y1 - 2, x0 + 8, y1 - 7, "#e8fbffb0"); _line(c, x0 + 8, y1 - 7, x0 + 7, y1 - 11, "#e8fbffb0")
    _line(c, x1 - 3, y0 + 3, x1 - 7, y0 + 7, "#e8fbffb0")
    for k in range(7):
        _px(c, x0 + 2 + (k * 7) % 18, y0 + 3 + (k * 5) % 14, FROST)
    # glint sweeping across the front face
    g = (i * 6) % 34 - 6
    for k in range(5):
        _px(c, x0 + g + k, y1 - k * 3, "#ffffffc0")
        _px(c, x0 + g + k + 1, y1 - k * 3, "#ffffff80")
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


# --- burn: flames round the body ------------------------------------------------
def burn(i):
    c = Canvas(S, S)
    cols = ["#8a1f10", "#ff5a1f", "#ffa23a", "#fff2a8"]
    tongues = [(-7, 10), (-3, 14), (1, 11), (5, 15), (8, 9)]
    for k, (dx, h) in enumerate(tongues):
        hh = h + (2 if (i + k) % 3 == 0 else 0) - (1 if (i + k) % 4 == 1 else 0)
        base = 26
        for j in range(hh):
            w = max(1, int(3 * (1 - j / hh) + 0.5))
            sway = math.sin(i * 0.9 + k + j * 0.4) * (j / hh) * 1.5
            band = 0 if j < 2 else (1 if j < hh * 0.55 else (2 if j < hh * 0.85 else 3))
            for q in range(-w // 2, w - w // 2):
                _px(c, C + dx + q + sway, base - j, cols[band] + ("e0" if band < 3 else ""))
    for k in range(3):                       # embers
        y = 22 - ((i * 3 + k * 7) % 20)
        _px(c, C - 6 + k * 6 + (i % 2), y, "#ffd04a")
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
