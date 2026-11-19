#!/usr/bin/env python3
"""Generator cho "king-slime": boss ải 10 (Bách Ải), Vua Slime. Cùng dáng với slime (dùng lại bản đồ pixel
của slime) nhưng màu đậm, đội vương miện vàng có ngọc đỏ. Game vẽ ở tỉ lệ lớn (monsters.json scale).
Frame 32x32, neo (16, 31) giữa đáy (ground=True).
Animation: move 4 (nảy), windup 3 (lấy đà: bẹt dần, vương miện rung), jump 2 (vươn cao), hurt 2, death 4.
Chạy: gamekit art run king-slime
"""
import math
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
CROWN = ["g...g...g...g", "gg.ggg.ggg.gg", "ggggggrgggggg", "sgggggggggggs", "GGGGGGGGGGGGG"]
CROWN_PAL = {"g": "#ffd04a", "G": "#b8862a", "r": "#e8364a", "s": "#fff2a0"}
GLOB = ["...mmm...", ".mmllmm..", "mmmmmmmd.", ".mmmmmd..", "..mmd...."]
# the old king's shapes, as squash/stretch of the same dome (old: 18 px wide, here x1.9)
FORMS = {"normal": (1.0, 1.0), "squash": (1.12, 0.82), "stretch": (0.86, 1.22), "flat": (1.25, 0.42), "puddle": (1.3, 0.16)}


def dome(c, cx, base, rx, ry, col):
    pts = [(round(cx + math.cos(math.pi * k / 40) * rx), round(base - 2 - math.sin(math.pi * k / 40) * ry)) for k in range(41)]
    pts += [(round(cx - rx + 2), base), (round(cx + rx - 2), base)][::-1]
    c.polygon(pts, col)


def shape(name, dx=0, eyes="open", crown_dy=0, crown=True, crown_at=None, glob=None, bubble=-1, sparkle=False):
    """The old king's look (user 2026-11-19 prefers it) drawn at boss size: a flat-coloured dome, a dark
    crescent at the bottom, a big highlight with two white glints at the top left, one tall eye with a
    white glint, no mouth, a pixel crown. crown_dy lets the crown lag the body; crown_at puts a fallen
    crown on the ground; glob=x draws a spat glob of slime; bubble drifts a bubble inside."""
    sx, sy = FORMS[name]
    c = Canvas(SIZE, SIZE)
    rx, ry = 17 * sx, 12 * sy          # wider than tall, as the old king (18 x 11)
    cx, base = 24 + dx, FLOOR
    # a round bulb sitting on the floor (an ellipse cut flat by the ground), as the old king
    cy = base - ry * 0.82
    c.ellipse(round(cx - rx), round(cy - ry), round(cx + rx), round(cy + ry), PAL["d"], fill=True)
    sh = max(1, round(2.5 * sy))                                          # the dark crescent, bottom left
    c.ellipse(round(cx - rx + 2), round(cy - ry), round(cx + rx), round(cy + ry - sh), PAL["m"], fill=True)
    if ry > 6:
        hx, hy = cx - rx * 0.4, cy - ry * 0.55
        c.ellipse(round(hx - 4 * sx), round(hy - 2 * sy), round(hx + 4 * sx), round(hy + 2 * sy), PAL["l"], fill=True)
        c.rect(round(hx - 1), round(hy - 1), round(hx), round(hy), PAL["w"], fill=True)   # glints
        c.pixel(round(hx + 2), round(hy - 1), PAL["w"])
    if bubble >= 0 and ry > 8:
        for k in range(2):
            by = round(cy + ry * 0.4) - ((bubble * 2 + k * 5) % max(3, round(ry * 0.9)))
            c.pixel(round(cx - 4 + k * 7), by, PAL["l"])
    if ry > 5:   # one tall eye on the right, as the old king
        ex, ey = round(cx + rx * 0.42), round(cy - ry * 0.35)
        eh = max(2, round(6 * sy))
        if eyes == "closed":
            c.line(ex - 1, ey + eh // 2, ex + 3, ey + eh // 2, PAL["e"])
        else:
            c.rect(ex, ey, ex + 3, ey + eh - 1, PAL["e"], fill=True)
            c.rect(ex + 2, ey + eh // 2 - 1, ex + 3, ey + eh // 2, PAL["p"], fill=True)
            if eyes == "angry":
                c.line(ex - 2, ey - 2, ex + 4, ey, PAL["e"])
    cr = from_rows(CROWN, CROWN_PAL)
    top = round(cy - ry)
    if crown:
        cx0, cy0 = round(cx - cr.width / 2) + 1, top - cr.height + 2 + crown_dy
        c.paste(cr, cx0, cy0)
        if sparkle:
            c.pixel(cx0 + 6, cy0 + 1, "#ffffff")
            c.pixel(cx0 + 6, cy0 - 1, "#fff2a0")
    if crown_at:
        c.paste(cr, crown_at[0], crown_at[1])
    if glob is not None:
        gl = from_rows(GLOB, PAL)
        c.paste(gl, glob, round(cy))
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
ANIMATIONS = [
    ("move", [shape("normal", bubble=0, sparkle=True), shape("squash", crown_dy=1, bubble=1), shape("squash", crown_dy=2, bubble=2),
              shape("normal", crown_dy=1, bubble=3), shape("stretch", bubble=4), shape("stretch", crown_dy=-1, bubble=5, sparkle=True),
              shape("normal", crown_dy=-1, bubble=6), shape("normal", crown_dy=1, dx=1, bubble=7)], 8, True,
     {"durations_ms": [150, 120, 140, 120, 150, 120, 140, 120], "hitbox": {**HB, "active": [0, 7]}}),
    ("crouch", [shape("squash", crown_dy=1, eyes="angry"), shape("squash", crown_dy=2, eyes="angry"), shape("flat", crown_dy=0), shape("flat", crown_dy=1)], 6, False,
     {"durations_ms": [200, 250, 300, 400], "hitbox": {**HB, "active": [0, 3]}}),
    ("jump", [shape("stretch", crown_dy=2), shape("stretch", crown_dy=3), shape("stretch", crown_dy=1), shape("normal", crown_dy=-2),
              shape("normal", crown_dy=-3), shape("stretch", crown_dy=-1), shape("flat", eyes="closed", crown_dy=2), shape("squash", crown_dy=1)], 8, False,
     {"durations_ms": [70, 90, 100, 120, 100, 90, 110, 120], "hitbox": {**HB, "active": [0, 7]}}),
    ("attack", [shape("squash", crown_dy=2, eyes="angry"), shape("squash", crown_dy=3, eyes="angry"), shape("flat", crown_dy=2),
                shape("stretch", crown_dy=-1, eyes="angry"), shape("normal", glob=38, eyes="angry"), shape("normal", glob=40, crown_dy=1),
                shape("squash", crown_dy=1), shape("normal", sparkle=True)], 8, False,
     {"durations_ms": [140, 160, 220, 80, 120, 100, 120, 140], "hitbox": {**HB, "active": [3, 5]}}),
    ("hurt", [flash(shape("squash", eyes="closed")), shape("stretch", eyes="closed", crown_dy=-2),
              shape("squash", crown_dy=1), shape("normal")], 12, False,
     {"durations_ms": [70, 100, 100, 120], "hitbox": {**HB, "active": [0, 3]}}),
    ("death", [flash(shape("squash", eyes="closed"), 0.5), shape("stretch", eyes="closed", crown_dy=-3),
               shape("squash", eyes="closed", crown_dy=-4), shape("flat", crown=False, crown_at=(30, 28)),
               shape("flat", crown=False, crown_at=(31, 36)), shape("puddle", crown=False, crown_at=(32, 40)),
               shape("puddle", crown=False, crown_at=(33, 40)), shape("puddle", crown=False, crown_at=(33, 40))], 6, False,
     {"durations_ms": [120, 140, 160, 160, 160, 220, 280, 400], "hitbox": {**HB, "active": [0, 7]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=5, gif_scale=3)
    print("OK", NAME)
