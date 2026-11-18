#!/usr/bin/env python3
"""Generator cho "toad-king" (Cóc Chúa): boss vùng Đầm Lầy Độc (Bách Ải 6A, design/bosses.md).

Một con cóc khổng lồ ngồi bè: lưng ô liu sẫm đầy mụn cam độc, bụng vàng nhạt, bọng họng phồng, đôi mắt lồi
vàng to, đội vương miện bằng nấm độc tím. Nó nhảy đè (đáp xuống để lại vũng độc lớn) và phun chùm đạn độc.
Quay phải. Frame 48x48, neo giữa thân trên đất (24, 47), ground=True.
move 4 (họng phập phồng, thân nhún), attack 3 (nén người → vươn cao bật → đáp bẹp), hurt 2,
death 4 (xẹp, chảy thành vũng độc). Chạy: gamekit art run toad-king
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

NAME = "toad-king"
S = 48
ANCHOR = (24.0, 47.0)
OUTLINE = "#14160c"
DARK, BACK, LIT = "#2e3a1a", "#4a5a24", "#6e7e34"
WART, WART_L = "#c8661e", "#f0963a"
BELLY, THROAT = "#d8d07a", "#f0eaa0"
EYE, PUPIL = "#f0c040", "#14160c"
CAP, CAP_L, STEM = "#7a3aa8", "#b070e0", "#e0d8c0"
POOL, POOL_L = "#4a8a22", "#8ad040"


def blob(c, x0, y0, x1, y1, col):
    c.ellipse(round(x0), round(y0), round(x1), round(y1), col, fill=True)


def king(squash=0.0, puff=0, dy=0, crown=True, eyes=True):
    """squash > 0 flattens and widens (crouch / landing), < 0 stretches tall (leap)."""
    c = Canvas(S, S)
    base = 45 + dy
    w = 18 * (1 + squash * 0.35)
    h = 15 * (1 - squash * 0.45)
    cx = 23
    # hind legs folded at the sides
    blob(c, cx - w - 1, base - 7, cx - w + 9, base, DARK)
    blob(c, cx + w - 9, base - 7, cx + w + 1, base, DARK)
    # body
    blob(c, cx - w, base - 2 * h, cx + w, base, BACK)
    blob(c, cx - w + 3, base - 2 * h + 1, cx + w - 6, base - h, LIT)
    blob(c, cx - w + 2, base - h * 0.9, cx + w - 2, base, BACK)
    # belly and throat sac (on the facing side, right)
    blob(c, cx - 4, base - h * 0.9, cx + w - 1, base, BELLY)
    blob(c, cx + w - 10 - puff, base - h * 1.1 - puff, cx + w + 1 + puff // 2, base - 2, THROAT)
    # warts
    for wx, wy in ((-10, 1.6), (-4, 1.8), (2, 1.5), (-13, 1.1), (-7, 1.2), (6, 1.75), (-1, 1.05)):
        x = round(cx + wx * (1 + squash * 0.3))
        y = round(base - h * wy)
        c.rect(x, y, x + 1, y + 1, WART, fill=True)
        c.pixel(x, y, WART_L)
    # front foot
    c.rect(cx + 6, base - 3, cx + 11, base, DARK, fill=True)
    # eyes on top of the head (right side)
    ey = round(base - 2 * h) - 1
    for ex in (cx + 4, cx + 12):
        blob(c, ex - 3, ey - 3, ex + 3, ey + 3, BACK)
        if eyes:
            blob(c, ex - 2, ey - 2, ex + 2, ey + 2, EYE)
            c.rect(ex, ey - 1, ex + 1, ey + 1, PUPIL, fill=True)
        else:
            c.line(ex - 2, ey, ex + 2, ey, PUPIL)
    # mouth line
    c.line(cx + 5, round(base - h * 1.05), cx + w, round(base - h * 0.95), DARK)
    # crown of toxic mushrooms
    if crown:
        cy = ey - 3
        for k, (mx, r) in enumerate(((cx - 4, 3), (cx + 1, 4), (cx - 9, 2))):
            c.rect(mx - 1, cy - 1, mx, cy + 2, STEM, fill=True)
            blob(c, mx - r, cy - r - 1, mx + r, cy, CAP)
            c.pixel(mx - 1, cy - r, CAP_L)
            c.pixel(mx + 1, cy - 1, CAP_L)
    return c.outline(OUTLINE)


def flash(c, amount=0.7):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x14, 0x16, 0x0c):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def melt(k):
    """Deflates into a poison puddle with its mushroom crown left on top."""
    c = Canvas(S, S)
    base = 45
    hgt = [9, 5, 2][k]
    blob(c, 6 - 2 * k, base - hgt, 42 + 2 * k, base, BACK if k < 2 else POOL)
    blob(c, 10, base - hgt, 34, base - max(1, hgt // 2), LIT if k < 2 else POOL_L)
    for x in (12, 20, 28):
        c.pixel(x, base - hgt, WART)
    c.rect(22, base - hgt - 3, 23, base - hgt, STEM, fill=True)
    blob(c, 19, base - hgt - 6, 26, base - hgt - 2, CAP)
    return c.outline(OUTLINE)


HB = {"shape": "rect", "center": [24.0, 47.0]}
ANIMATIONS = [
    ("move", [king(0, 0), king(0.05, 2), king(0, 3), king(0.05, 1)], 6, True,
     {"durations_ms": [200, 180, 220, 180], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [king(0.5, 0), king(-0.45, 0), king(0.7, 1)], 8, False,
     {"durations_ms": [260, 180, 300], "hitbox": {**HB, "active": [2, 2]}}),
    ("hurt", [flash(king(0.1, 0)), king(0, 1)], 12, False, {"durations_ms": [80, 140], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(king(0.4, 0, eyes=False), 0.4), melt(0), melt(1), melt(2)], 6, False,
     {"durations_ms": [160, 220, 260, 400], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=6, gif_scale=4)
    print(f"OK {NAME}")
