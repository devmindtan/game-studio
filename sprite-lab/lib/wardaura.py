"""wardaura: item-special shields drawn at the hero's own frame and feet anchor.

Effects (not characters): 48x48, anchor (24,44), the same bubble zone as
heroaura. Two distinct families so the legendary shields never reuse the pickup
buff's aura (user 2026-11-18):
  runic  - Thần hộ / phantom armour: golden ward, six turning runes, glass facets
  stone  - Bàn thạch / one-hit block: segmented stone shell, cracks, one bright
           charge at the centre that dies when the block is spent

Each is 4 form frames (snap open) + 8 loop frames, 48x48, no px_scale: the game
draws buff auras at the hero's own scale.
"""
from __future__ import annotations

import math

from heroaura import BUBBLE, canvas, ellipse_points, px

TAU = math.tau

# rim, rim2, outer edge, interior, facet, rune, hot, mote
RUNIC = {
    "rim": "#ffe9a8", "rim2": "#6fc3ff", "out": "#7a4a12", "fill": "#ffd96a14",
    "facet": "#ffe9a840", "rune": "#fff3c0", "hot": "#ffffff", "mote": "#ffd96a",
}
STONE = {
    "rim": "#d8c49a", "rim2": "#8a8070", "out": "#3a2a18", "fill": "#8a807016",
    "facet": "#c9b89a30", "rune": "#ffb04a", "hot": "#fff0b4", "mote": "#ffb04a",
}


def _h01(x, y, salt):
    h = (int(x) * 374761393 + int(y) * 668265263 + int(salt) * 1103515245) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _fill(c, cx, cy, rx, ry, col):
    for y in range(int(cy - ry) + 1, int(cy + ry)):
        dy = (y - cy) / ry
        half = rx * math.sqrt(max(0.0, 1 - dy * dy)) - 1.5
        for x in range(int(round(cx - half)), int(round(cx + half)) + 1):
            px(c, x, y, col)


def _runic_surface(c, cx, cy, rx, ry, i, pal):
    # glass facets, slowly turning; one edge catches the light
    for k in range(6):
        a = k * TAU / 6 + i * 0.08
        x0, y0 = cx + math.cos(a) * rx * 0.62, cy + math.sin(a) * ry * 0.62
        x1, y1 = cx + math.cos(a + TAU / 6) * rx * 0.62, cy + math.sin(a + TAU / 6) * ry * 0.62
        for t in range(1, 8):
            if (t + i) % 3 == 0:
                continue
            col = pal["rune"] if k == i % 6 and t in (2, 3, 4) else pal["facet"]
            px(c, x0 + (x1 - x0) * t / 8, y0 + (y1 - y0) * t / 8, col)
    # six diamond runes travel with the ward; one burns brighter each frame
    for k in range(6):
        a = k * TAU / 6 + i * 0.10
        x = cx + math.cos(a) * rx * 0.74
        y = cy + math.sin(a) * ry * 0.74
        lit = k == i % 6
        col = pal["hot"] if lit else pal["rune"]
        px(c, x, y - 1, col)
        px(c, x - 1, y, col)
        px(c, x + 1, y, col)
        px(c, x, y + 1, col)
        if lit:
            px(c, x - 1, y - 1, pal["rim2"])
            px(c, x + 1, y + 1, pal["rim2"])
    # motes drifting upward inside the glass
    for j in range(3):
        x = cx - 9 + j * 9 + int(2 * math.sin(i * 0.9 + j * 2))
        y = cy + 9 - ((i * 2 + j * 5) % 18)
        px(c, x, y, pal["mote"])


def _stone_surface(c, cx, cy, rx, ry, i, pal):
    # four short cracks, each with a hot tip; the ring reads as a hard shell
    for k in range(4):
        a = k * TAU / 4 + 0.3 + i * 0.02
        ux, uy = math.cos(a), math.sin(a)
        for s in range(3, 8):
            if _h01(k, s, 7 + i % 3) < 0.30:
                continue
            x = cx + ux * (rx - s)
            y = cy + uy * (ry - s)
            px(c, x, y, pal["rune"] if s >= 6 else pal["rim2"])
    # the single charge: a 2x2 gem in the middle, bright while the block holds
    x, y = int(cx), int(cy)
    px(c, x, y, pal["hot"])
    px(c, x + 1, y, pal["rune"])
    px(c, x, y + 1, pal["rune"])
    px(c, x + 1, y + 1, pal["hot"] if i % 2 == 0 else pal["rim2"])


def _rim(c, cx, cy, rx, ry, i, pal, motif):
    pts = ellipse_points(cx, cy, rx, ry, 240)
    for (x, y), _ in ellipse_points(cx, cy, rx + 1, ry + 1, 240):
        px(c, x, y, pal["out"])
    for (x, y), a in pts:
        if motif == "stone":     # segmented plates, not a continuous bubble
            if a % (TAU / 8) > TAU / 8 - 0.22:
                continue
        px(c, x, y, pal["rim2"])
    if motif == "runic":
        for (x, y), a in pts:
            if 3.6 < a < 4.3:
                px(c, x + 2, y + 1, pal["hot"])
        for k in range(3):
            g = (i / 8.0 + k / 3.0) * TAU
            px(c, cx + math.cos(g) * rx, cy + math.sin(g) * ry, pal["hot"])
            px(c, cx + math.cos(g) * (rx - 1), cy + math.sin(g) * (ry - 1), pal["rim"])
    else:
        for k in range(4):
            g = (i / 8.0 + k / 4.0) * TAU
            px(c, cx + math.cos(g) * rx, cy + math.sin(g) * ry, pal["hot"])


def frame(spec, i, form=1.0):
    c = canvas()
    cx, cy, rx, ry = BUBBLE
    rx, ry = rx * form, ry * form
    pal = spec["palette"]
    motif = spec["motif"]

    if form >= 1.0:
        _fill(c, cx, cy, rx, ry, pal["fill"])
        # a faint inner ring gives the ward thickness without hiding the hero
        for (x, y), _ in ellipse_points(cx, cy, rx - 2, ry - 2, 220):
            if _h01(x, y, 11 + i % 4) < 0.55:
                continue
            px(c, x, y, pal["rim2"])
        (_runic_surface if motif == "runic" else _stone_surface)(c, cx, cy, rx, ry, i, pal)
    else:
        for k in range(6):
            a = k * TAU / 6 + 0.2
            for s in range(2, 5):
                px(c, cx + math.cos(a) * s, cy + math.sin(a) * s,
                   pal["rim2"] if s > 2 else pal["hot"])
    _rim(c, cx, cy, rx, ry, i, pal, motif)
    if form < 1.0:
        px(c, cx, cy, pal["hot"])
        px(c, cx + 1, cy, pal["rim"])
        px(c, cx - 1, cy, pal["rim"])
        px(c, cx, cy + 1, pal["rim"])
    return c


def build(here, name, spec, export):
    anims = [("form", [frame(spec, 0, f) for f in (0.40, 0.68, 0.88, 1.08)], 16, False, {}),
             ("loop", [frame(spec, i) for i in range(8)], 10, True, {})]
    export(here, name, anims, anchor=(24.0, 44.0))
