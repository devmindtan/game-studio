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

_spec = importlib.util.spec_from_file_location("slime_gen", HERE.parent / "slime" / "gen.py")
slime = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(slime)

NAME = "king-slime"
SIZE = 32
ANCHOR = (16.0, 31.0)
OUTLINE = "#1b1726"
PAL = {"m": "#3fae6e", "d": "#1f6b45", "l": "#9ff0b8", "w": "#ffffff", "e": "#1b1726", "p": "#ffffff", "t": "#1f5a3a"}
CROWN = ["g.g.g.g", "ggrgggg", "GGGGGGG"]
CROWN_PAL = {"g": "#ffd04a", "G": "#b8862a", "r": "#e8364a"}


GLOB = ["..mm..", ".mlmm.", "mmmmmd", ".mmmd."]


def shape(name, dx=0, eyes="open", crown_dy=0, crown=True, crown_at=None, glob=None, bubble=-1, sparkle=False):
    """The old king (user 2026-11-19 prefers it; upgraded on that style, not redrawn): the plain slime's shapes with a crown. crown_dy lets the
    crown lag the body (8-frame boss tier); crown_at=(x, y) puts a fallen crown on the ground; glob=x
    draws a spat glob of slime at that x."""
    rows = slime.SHAPES[name]
    if eyes == "closed":
        rows = [r.replace("p", "e") for r in rows]
        rows = [r.replace("ee", "..") if i in (4, 3) else r for i, r in enumerate(rows)]
    angry = eyes == "angry"
    if angry:
        eyes = "open"
    art = from_rows(rows, PAL)
    c = Canvas(SIZE, SIZE)
    x = (SIZE - art.width) // 2 + dx
    y = 29 - (art.height - 1)
    c.paste(art, x, y)
    # upgrade on the old style (user 2026-11-19): bubbles drift up inside the gel
    if bubble >= 0 and art.height > 6:
        for k in range(2):
            by = y + art.height - 3 - ((bubble + k * 3) % max(2, art.height - 5))
            bx = x + art.width // 2 - 4 + k * 5
            c.pixel(bx, by, PAL["l"])
    if angry:   # a scowl over the eyes when it winds up or spits
        px = c.img.load()
        for yy in range(c.height):
            for xx in range(c.width):
                if px[xx, yy][:3] == (0x1b, 0x17, 0x26) and px[xx, yy][3] and yy > 0 and px[xx, yy - 1][3] and px[xx, yy - 1][:3] != (0x1b, 0x17, 0x26):
                    c.pixel(xx, yy - 1, PAL["d"])
                    break
    cr = from_rows(CROWN, CROWN_PAL)
    if crown:
        cx0, cy0 = (SIZE - cr.width) // 2 + dx, y - cr.height + 1 + crown_dy
        c.paste(cr, cx0, cy0)
        if sparkle:   # the crown jewel glints
            c.pixel(cx0 + 2, cy0 + 1, "#ffffff")
            c.pixel(cx0 + 2, cy0 - 1, "#fff2a0")
    if crown_at:
        c.paste(cr, crown_at[0], crown_at[1])
    if glob is not None:
        g = from_rows(GLOB, PAL)
        c.paste(g, glob, y + 2)
    return c.outline(OUTLINE)


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
                shape("stretch", crown_dy=-1, eyes="angry"), shape("normal", glob=24, eyes="angry"), shape("normal", glob=27, crown_dy=1),
                shape("squash", crown_dy=1), shape("normal", sparkle=True)], 8, False,
     {"durations_ms": [140, 160, 220, 80, 120, 100, 120, 140], "hitbox": {**HB, "active": [3, 5]}}),
    ("hurt", [slime.flash(shape("squash", eyes="closed")), shape("stretch", eyes="closed", crown_dy=-2),
              shape("squash", crown_dy=1), shape("normal")], 12, False,
     {"durations_ms": [70, 100, 100, 120], "hitbox": {**HB, "active": [0, 3]}}),
    ("death", [slime.flash(shape("squash", eyes="closed"), 0.5), shape("stretch", eyes="closed", crown_dy=-3),
               shape("squash", eyes="closed", crown_dy=-4), shape("flat", crown=False, crown_at=(20, 18)),
               shape("flat", crown=False, crown_at=(21, 23)), shape("puddle", crown=False, crown_at=(22, 26)),
               shape("puddle", crown=False, crown_at=(22, 27)), shape("puddle", crown=False, crown_at=(22, 27))], 6, False,
     {"durations_ms": [120, 140, 160, 160, 160, 220, 280, 400], "hitbox": {**HB, "active": [0, 7]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move")
    print("OK", NAME)
