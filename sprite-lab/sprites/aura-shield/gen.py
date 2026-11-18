#!/usr/bin/env python3
"""aura-shield — Khiên thần hộ: a glowing bubble wrapped around the hero.

Buff aura, not a skill effect: same 48x48 frame and feet anchor as the hero,
so it lines up exactly. The zone stays the bubble (centre 24,27 / rx 21 / ry 17);
the hero's body is never covered by more than a faint tinted glass.

Animation (user 2026-11-18: give the divine shield a real animation):
  form 4 frames, 16 fps - the barrier snaps open: small ring -> overshoot -> a
                          white flash at the centre settles into the bubble
  loop 8 frames, 10 fps - six runes crawl around the glass, one burning brighter,
                          hex facets shimmer, the inner rim pulses and three
                          glints run the edge; a few motes drift upward inside

Art references: internet step skipped (search HTTP 402). Palette follows the
local cold-light ramps (blue-glass / frozen-fire): deep blue outline, pale cyan
rim, white specular arc. Conservative rule: detail lives on the rim/surface,
the interior stays transparent so the hero reads through it.
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
from heroaura import canvas, px, ellipse_points, BUBBLE, ANCHOR  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name

RIM = "#dff9ff"      # bright leading edge
RIM2 = "#6fc3ff"     # glass body
OUT = "#2a6ab0"      # dark outside edge, separates it from the grass
FILL = "#6fc3ff14"   # almost clear interior
HEX = "#9fdcff30"    # faint facets
RUNE = "#bff0ff"     # crawling runes
HOT = "#ffffff"      # active rune / specular
MOTE = "#8fd8ff"

TAU = math.tau


def _h01(x, y, salt):
    h = (int(x) * 374761393 + int(y) * 668265263 + int(salt) * 1103515245) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65536.0


def _fill(c, cx, cy, rx, ry):
    for y in range(int(cy - ry) + 1, int(cy + ry)):
        dy = (y - cy) / ry
        half = rx * math.sqrt(max(0.0, 1 - dy * dy)) - 1.5
        for x in range(int(round(cx - half)), int(round(cx + half)) + 1):
            px(c, x, y, FILL)


def _inner_ring(c, cx, cy, rx, ry, i):
    """A second, broken ring just inside the rim: the barrier's inner layer."""
    for (x, y), _ in ellipse_points(cx, cy, rx - 2, ry - 2, 220):
        if _h01(x, y, 11 + i % 4) < 0.55:
            continue
        px(c, x, y, RIM2 if i % 2 else "#4a92d0")


def _facets(c, cx, cy, rx, ry, i):
    for k in range(6):
        a = k * TAU / 6 + i * 0.08
        x0, y0 = cx + math.cos(a) * rx * 0.62, cy + math.sin(a) * ry * 0.62
        x1, y1 = cx + math.cos(a + TAU / 6) * rx * 0.62, cy + math.sin(a + TAU / 6) * ry * 0.62
        for t in range(1, 8):
            if (t + i) % 3 == 0:
                continue
            col = RUNE if (k == i % 6 and t in (2, 3, 4)) else HEX
            px(c, x0 + (x1 - x0) * t / 8, y0 + (y1 - y0) * t / 8, col)


def _runes(c, cx, cy, rx, ry, i):
    """Four diamond glyphs turn with the barrier; one is lit by the pulse."""
    for k in range(4):
        a = k * TAU / 4 + i * 0.10
        x = cx + math.cos(a) * rx * 0.74
        y = cy + math.sin(a) * ry * 0.74
        lit = k == i % 4
        col = HOT if lit else RUNE
        px(c, x, y - 1, col)          # a tiny diamond, readable at game scale
        px(c, x - 1, y, col)
        px(c, x + 1, y, col)
        px(c, x, y + 1, col)
        px(c, x, y, col)
        if lit:
            px(c, x - 1, y - 1, RIM2)
            px(c, x + 1, y + 1, RIM2)


def _motes(c, cx, cy, i):
    for j in range(3):
        x = cx - 9 + j * 9 + int(2 * math.sin(i * 0.9 + j * 2))
        y = cy + 9 - ((i * 2 + j * 5) % 18)
        px(c, x, y, HOT if j == i % 3 else MOTE)


def frame(i, form=1.0):
    c = canvas()
    cx, cy, rx, ry = BUBBLE
    rx, ry = rx * form, ry * form

    if form >= 1.0:
        _fill(c, cx, cy, rx, ry)
        _inner_ring(c, cx, cy, rx, ry, i)
        _facets(c, cx, cy, rx, ry, i)
        _runes(c, cx, cy, rx, ry, i)
        _motes(c, cx, cy, i)
    else:
        # the forming bubble flashes and throws a few short rays before it settles
        for k in range(6):
            a = k * TAU / 6 + 0.2
            for s in range(2, 5):
                px(c, cx + math.cos(a) * s, cy + math.sin(a) * s, RIM2 if s > 2 else HOT)

    pts = ellipse_points(cx, cy, rx, ry, 240)
    for (x, y), _ in ellipse_points(cx, cy, rx + 1, ry + 1, 240):
        px(c, x, y, OUT)                       # dark edge outside the glass
    for (x, y), _ in pts:
        px(c, x, y, RIM2)
    for (x, y), a in pts:
        if 3.6 < a < 4.3:                      # glass highlight, upper-left
            px(c, x + 2, y + 1, HOT)
    if form >= 1.0:
        for k in range(3):
            g = (i / 8.0 + k / 3.0) * TAU
            px(c, cx + math.cos(g) * rx, cy + math.sin(g) * ry, HOT)
            px(c, cx + math.cos(g) * (rx - 1), cy + math.sin(g) * (ry - 1), RIM)
    else:
        px(c, cx, cy, HOT)
        px(c, cx + 1, cy, RIM)
        px(c, cx - 1, cy, RIM)
        px(c, cx, cy + 1, RIM)
    return c


ANIM = [("form", [frame(0, f) for f in (0.40, 0.68, 0.88, 1.08)], 16, False, {}),
        ("loop", [frame(i) for i in range(8)], 10, True, {})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=ANCHOR)
    print("OK", NAME)
