#!/usr/bin/env python3
"""Generator cho "king-slime": boss ải 10 (Bách Ải), Vua Slime. Cùng dáng với slime (dùng lại bản đồ pixel
của slime) nhưng màu đậm, đội vương miện vàng có ngọc đỏ. Game vẽ ở tỉ lệ lớn (monsters.json scale).
Frame 32x32, neo (16, 31) giữa đáy (ground=True).
Animation: move 4 (nảy), windup 3 (lấy đà: bẹt dần, vương miện rung), jump 2 (vươn cao), hurt 2, death 4.
Chạy: gamekit art run king-slime
"""
import importlib.util
import sys
from pathlib import Path

def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from spritekit import Canvas, from_rows
from sheet import export

NAME = "king-slime"
SIZE = 48                       # user 2026-11-19: a boss is at least 48x48
ANCHOR = (24.0, 47.0)
FLOOR = 45                      # lowest body row; the outline adds 46
OUTLINE = "#1b1726"
PAL = {"m": "#3fae6e", "d": "#1f6b45", "l": "#9ff0b8", "w": "#ffffff", "e": "#1b1726", "p": "#ffffff", "t": "#1f5a3a"}
# rage (user 2026-11-19): below rage_at the body turns red; king-slime-rage renders these frames with RAGE_PAL
RAGE_PAL = {"m": "#d8483a", "d": "#8a1e1e", "l": "#ffb0a0", "w": "#ffffff", "e": "#1b1726", "p": "#ffe070", "t": "#6a1414"}
CROWN = ["g...g...g...g", "gg.ggg.ggg.gg", "ggggggrgggggg", "sgggggggggggs", "GGGGGGGGGGGGG"]
CROWN_PAL = {"g": "#ffd04a", "G": "#b8862a", "r": "#e8364a", "s": "#fff2a0"}
RAGE = False   # king-slime-rage sets it: always angry eyes and the anger mark (user 2026-11-19)
# the anger mark (as the user's picture): four curled red brackets, big and small to pulse
ANGER = {   # as the user's picture: two bent strokes on top, an arch below; 2 px strokes, pulsing big/small
    "big": [
        "....rr...rr....",
        "....rr...rr....",
        "....rr...rr....",
        ".rrrrr...rrrrr.",
        ".rrrr.....rrrr.",
        "...............",
        ".....rrrrr.....",
        "....rr...rr....",
        "...rr.....rr...",
        "..rr.......rr..",
    ],
    "small": [
        "...rr.rr...",
        "...rr.rr...",
        ".rrrr.rrrr.",
        "...........",
        "....rrr....",
        "...rr.rr...",
        "..rr...rr..",
    ],
}
ANGER_PAL = {"r": "#ff1a1a"}
S = 1.9   # the old 18x11 king outline, traced and redrawn smooth at boss size (user: keep the old proportions)
_spec = importlib.util.spec_from_file_location("slime_gen", HERE.parent / "slime" / "gen.py")
slime = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(slime)


def _outline_poly(rows, ox, oy):
    """A smooth polygon through the old shape's row extents, scaled by S (same proportions, no blocky upscale)."""
    spans = [(r.find(next(ch for ch in r if ch != ".")), len(r.rstrip(".")) - 1, y) for y, r in enumerate(rows) if r.strip(".")]
    left = [(ox + x0 * S, oy + (y + 0.5) * S) for x0, _, y in spans]
    right = [(ox + (x1 + 1) * S, oy + (y + 0.5) * S) for _, x1, y in spans]
    top = [(ox + spans[0][0] * S + S * 0.5, oy), (ox + (spans[0][1] + 1) * S - S * 0.5, oy)]
    bot = [(ox + (spans[-1][1] + 1) * S - S, oy + len(rows) * S), (ox + spans[-1][0] * S + S, oy + len(rows) * S)]
    pts = top + right + bot + left[::-1]
    return [(round(x), round(y)) for x, y in pts]


def _cells(rows, chars):
    return [(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch in chars]


def shape(name, dx=0, eyes="open", crown_dy=0, crown=True, crown_at=None, bubble=-1, sparkle=False, pal=None):
    """The old king (user 2026-11-19 prefers it): the plain slime's shapes traced at boss size, a pixel crown.
    crown_dy lets the crown lag the body; crown_at=(x, y) puts a fallen crown on the ground; pal=RAGE_PAL
    draws the red enraged body."""
    P = pal or PAL
    if RAGE and eyes == "open":
        eyes = "angry"
    rows = slime.SHAPES[name]
    w = max(len(r) for r in rows)
    ox = round((SIZE - w * S) / 2) + dx
    oy = FLOOR + 1 - round(len(rows) * S)
    c = Canvas(SIZE, SIZE)
    body = _outline_poly(rows, ox, oy)
    c.polygon(body, P["d"])
    # the lit body: the same outline lifted and nudged right, clipped to the body -> the old dark crescent below
    lit = Canvas(SIZE, SIZE)
    lit.polygon([(x + 1, y - max(2, round(S * 1.4))) for x, y in body], P["m"])
    mask = Canvas(SIZE, SIZE)
    mask.polygon(body, "#ffffff")
    lp, mp = lit.img.load(), mask.img.load()
    for yy in range(SIZE):
        for xx in range(SIZE):
            if lp[xx, yy][3] and mp[xx, yy][3]:
                c.pixel(xx, yy, P["m"])
    for x, y in _cells(rows, "l"):   # the old highlight, and its white glints
        c.rect(round(ox + x * S), round(oy + y * S), round(ox + (x + 1) * S) - 1, round(oy + (y + 1) * S) - 1, P["l"], fill=True)
    for x, y in _cells(rows, "w"):
        c.rect(round(ox + x * S), round(oy + y * S), round(ox + x * S) + 1, round(oy + y * S) + 1, P["w"], fill=True)
    eye = _cells(rows, "e")   # the dark eye only: the white "p" glint sits inside/at its edge
    if eye:
        ex0, ey0 = min(x for x, _ in eye), min(y for _, y in eye)
        ex1, ey1 = max(x for x, _ in eye), max(y for _, y in eye)
        X0, Y0 = round(ox + ex0 * S), round(oy + ey0 * S)
        X1, Y1 = round(ox + (ex1 + 1) * S) - 1, round(oy + (ey1 + 1) * S) - 1
        if eyes == "closed":
            c.line(X0, (Y0 + Y1) // 2, X1, (Y0 + Y1) // 2, P["e"])
        else:
            c.rect(X0, Y0, X1, Y1, P["e"], fill=True)
            px_, py_ = _cells(rows, "p")[0] if _cells(rows, "p") else (ex1, (ey0 + ey1) // 2)
            gx = min(round(ox + px_ * S), X1) - 1                      # glint inside the eye, right edge
            c.rect(gx, round(oy + py_ * S), gx + 1, round(oy + py_ * S) + 1, P["p"], fill=True)
            if eyes == "angry":   # a thick brow slanting down to the nose: a scowl
                c.line(X0 - 3, Y0 - 3, X1 + 1, Y0 - 1, P["e"])
                c.line(X0 - 3, Y0 - 2, X1 + 1, Y0, P["e"])
    if bubble >= 0 and len(rows) > 6:
        for k in range(2):
            by = FLOOR - 4 - ((bubble * 2 + k * 5) % max(3, round(len(rows) * S * 0.6)))
            c.pixel(round(SIZE / 2 - 5 + k * 7 + dx), by, P["l"])
    cr = from_rows(CROWN, CROWN_PAL)
    if crown:
        cx0, cy0 = round(SIZE / 2 - cr.width / 2) + dx, oy - cr.height + 2 + crown_dy
        c.paste(cr, cx0, cy0)
        if sparkle:
            c.pixel(cx0 + 6, cy0 + 1, "#ffffff")
            c.pixel(cx0 + 6, cy0 - 1, "#fff2a0")
    if crown_at:
        c.paste(cr, crown_at[0], crown_at[1])
    if RAGE and crown:   # the anger mark beside the head, pulsing
        size = "big" if (bubble if bubble >= 0 else crown_dy) % 2 == 0 else "small"
        am = from_rows(ANGER[size], ANGER_PAL)
        c.paste(am, min(SIZE - am.width - 1, round(SIZE / 2 + 8) + dx), max(1, oy - 12 + crown_dy))
    for yy in range(FLOOR + 1, SIZE):
        c.line(0, yy, SIZE - 1, yy, (0, 0, 0, 0))
    return c.outline(OUTLINE)


def flash(c, amount=0.7):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x1b, 0x17, 0x26):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


HB = {"shape": "rect", "center": [16.0, 31.0]}
def build():
    """All animations with the current PAL (king-slime-rage sets PAL = RAGE_PAL and calls this)."""
    return [
    ("move", [shape("normal", bubble=0, sparkle=True), shape("squash", crown_dy=1, bubble=1), shape("squash", crown_dy=2, bubble=2),
              shape("normal", crown_dy=1, bubble=3), shape("stretch", bubble=4), shape("stretch", crown_dy=-1, bubble=5, sparkle=True),
              shape("normal", crown_dy=-1, bubble=6), shape("normal", crown_dy=1, dx=1, bubble=7)], 8, True,
     {"durations_ms": [150, 120, 140, 120, 150, 120, 140, 120], "hitbox": {**HB, "active": [0, 7]}}),
    ("crouch", [shape("squash", crown_dy=1, eyes="angry"), shape("squash", crown_dy=2, eyes="angry"), shape("flat", crown_dy=0), shape("flat", crown_dy=1)], 6, False,
     {"durations_ms": [200, 250, 300, 400], "hitbox": {**HB, "active": [0, 3]}}),
    ("jump", [shape("stretch", crown_dy=2), shape("stretch", crown_dy=3), shape("stretch", crown_dy=1), shape("normal", crown_dy=-2),
              shape("normal", crown_dy=-3), shape("stretch", crown_dy=-1), shape("flat", eyes="closed", crown_dy=2), shape("squash", crown_dy=1)], 8, False,
     {"durations_ms": [70, 90, 100, 120, 100, 90, 110, 120], "hitbox": {**HB, "active": [0, 7]}}),
    # attack 8 = the stomp (user 2026-11-19: it only jumps and slams, no spitting)
    ("attack", [shape("squash", crown_dy=2, eyes="angry"), shape("flat", crown_dy=2, eyes="angry"), shape("stretch", crown_dy=3),
                shape("stretch", crown_dy=1), shape("normal", crown_dy=-3), shape("stretch", crown_dy=-1),
                shape("flat", eyes="closed", crown_dy=2), shape("squash", crown_dy=1, sparkle=True)], 8, False,
     {"durations_ms": [160, 220, 80, 100, 120, 90, 160, 140], "hitbox": {**HB, "active": [6, 7]}}),
    ("hurt", [flash(shape("squash", eyes="closed")), shape("stretch", eyes="closed", crown_dy=-2),
              shape("squash", crown_dy=1), shape("normal")], 12, False,
     {"durations_ms": [70, 100, 100, 120], "hitbox": {**HB, "active": [0, 3]}}),
    ("death", [flash(shape("squash", eyes="closed"), 0.5), shape("stretch", eyes="closed", crown_dy=-3),
               shape("squash", eyes="closed", crown_dy=-4), shape("flat", crown=False, crown_at=(30, 28)),
               shape("flat", crown=False, crown_at=(31, 36)), shape("puddle", crown=False, crown_at=(32, 40)),
               shape("puddle", crown=False, crown_at=(33, 40)), shape("puddle", crown=False, crown_at=(33, 40))], 6, False,
     {"durations_ms": [120, 140, 160, 160, 160, 220, 280, 400], "hitbox": {**HB, "active": [0, 7]}}),
    ]


ANIMATIONS = build()

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=5, gif_scale=3)
    print("OK", NAME)
