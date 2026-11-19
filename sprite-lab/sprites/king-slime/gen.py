#!/usr/bin/env python3
"""Generator cho "king-slime" (Vua Thạch Nhầy): boss Đồng cỏ (Bách Ải).

Chuẩn creature-v1 mức boss (sprite-lab/CREATURE_STANDARD.md), mô tả từng khung trong brief.json. Người dùng
2026-11-19: ba boss cần 8 khung. Bản cũ dùng chung hình thạch nhầy 32x32; bản này dựng khối gel ở cỡ boss:
thân vòm co giãn (giữ thể tích: bẹp thì bè ra, vươn thì hẹp lại), sóng rung trên bề mặt, bọt khí trôi trong
gel, mắt to, vương miện vàng xóc theo trễ một nhịp. Frame 48x40, neo (24, 39).
Chạy: gamekit art run king-slime
"""

import math
import sys
from pathlib import Path


def _ws() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = "king-slime"
W, H = 48, 40
ANCHOR = (24.0, 39.0)
FLOOR = 37                      # lowest drawn row; the outline adds 38
OUTLINE = "#1b1726"
G = {"d": "#1f6b45", "m": "#3fae6e", "l": "#7ad89a", "h": "#c8ffd8", "w": "#ffffff", "e": "#1b1726",
     "in": "#2a8a58", "mouth": "#0e3a24"}
CROWN = {"g": "#ffd04a", "G": "#b8862a", "r": "#e8364a", "s": "#fff2a0"}


def blob(c, cx, base, rx, ry, wave=0.0, phase=0.0, col=None):
    """A dome of gel standing on `base`, its outline rippling by `wave` px."""
    pts = []
    n = 36
    for k in range(n + 1):
        t = math.pi * k / n
        r = 1 + (wave / max(rx, 1)) * math.sin(t * 5 + phase)
        pts.append((round(cx + math.cos(t) * rx * r), round(base - math.sin(t) * ry * r)))
    pts.append((round(cx - rx), base))
    c.polygon(pts, col or G["m"])


def king(sx=1.0, sy=1.0, wave=0.0, phase=0.0, dy=0, crown_dy=0, crown_tilt=0, eyes="open", mouth=0,
         bubbles=0, crown=True, cheeks=0):
    """sx, sy: squash/stretch of the dome (keep sx*sy near 1); dy lifts the whole king (airborne frames
    stay on the floor, the game lifts the sprite); crown_dy/crown_tilt make the crown lag the body."""
    c = Canvas(W, H)
    rx, ry = 17 * sx + cheeks, 16 * sy
    base = FLOOR - dy
    cx = 24
    blob(c, cx, base, rx, ry, wave, phase, G["d"])
    blob(c, cx, base - 1, rx - 1.5, ry - 1.5, wave, phase, G["m"])
    # inner shade and the big highlight
    c.ellipse(round(cx - rx * 0.6), round(base - ry * 0.55), round(cx + rx * 0.7), base - 1, G["in"], fill=True)
    c.ellipse(round(cx - rx * 0.62), round(base - ry * 0.9), round(cx - rx * 0.15), round(base - ry * 0.6), G["l"], fill=True)
    c.ellipse(round(cx - rx * 0.5), round(base - ry * 0.86), round(cx - rx * 0.35), round(base - ry * 0.74), G["h"], fill=True)
    # bubbles drifting up inside the gel
    for k in range(3):
        by = base - 3 - ((bubbles * 3 + k * 7) % max(4, round(ry - 5)))
        bx = round(cx + (k - 1) * rx * 0.45 + math.sin(bubbles + k) * 2)
        c.pixel(bx, by, G["l"])
        c.pixel(bx + 1, by - 1, G["h"])
    # face
    ey = round(base - ry * 0.55)
    for ex in (cx - 6, cx + 4):
        if eyes == "open":
            c.ellipse(ex, ey - 3, ex + 4, ey + 2, G["w"], fill=True)
            c.rect(ex + 2, ey - 1, ex + 3, ey + 1, G["e"], fill=True)
        elif eyes == "angry":
            c.ellipse(ex, ey - 2, ex + 4, ey + 2, G["w"], fill=True)
            c.rect(ex + 2, ey - 1, ex + 3, ey + 1, G["e"], fill=True)
            c.line(ex, ey - 3 + (1 if ex < cx else 0), ex + 4, ey - 3 + (0 if ex < cx else 1), G["e"])   # scowl
        else:
            c.line(ex, ey, ex + 4, ey, G["e"])
    if mouth:
        c.ellipse(cx - 3, ey + 4, cx + 3, ey + 4 + mouth, G["mouth"], fill=True)
        if mouth > 2:   # a glob of slime leaving the mouth
            c.ellipse(cx + 5, ey + 3, cx + 9, ey + 7, G["l"], fill=True)
            c.pixel(cx + 6, ey + 4, G["h"])
    else:
        c.line(cx - 2, ey + 5, cx + 2, ey + 5, G["e"])
    # crown: lags the body by crown_dy and tilts
    if crown:
        top = round(base - ry * 0.98) - 5 + crown_dy
        x0 = cx - 7 + crown_tilt
        c.rect(x0, top + 3, x0 + 14, top + 5, CROWN["G"], fill=True)
        c.rect(x0, top + 2, x0 + 14, top + 3, CROWN["g"], fill=True)
        for k, px in enumerate(range(x0, x0 + 15, 4)):
            tip = top - (1 if k % 2 else 0) - (crown_tilt if k == 0 else 0) // 2
            c.line(px, top + 2, px, tip, CROWN["g"])
            c.pixel(px, tip, CROWN["s"])
        c.rect(x0 + 6, top + 3, x0 + 8, top + 4, CROWN["r"], fill=True)
    for yy in range(FLOOR + 1, H):
        c.line(0, yy, W - 1, yy, (0, 0, 0, 0))
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


def puddle(k, crown_x=None):
    c = Canvas(W, H)
    w = [20, 22, 23][k]
    c.ellipse(24 - w, FLOOR - 4 + k, 24 + w, FLOOR + 3, G["d"], fill=True)
    c.ellipse(24 - w + 2, FLOOR - 3 + k, 24 + w - 2, FLOOR + 2, G["m"], fill=True)
    c.ellipse(24 - w + 6, FLOOR - 3 + k, 24 - 2, FLOOR - 1 + k // 2, G["l"], fill=True)
    if crown_x is not None:   # the crown rolled off
        c.rect(crown_x, FLOOR - 4, crown_x + 8, FLOOR - 1, CROWN["g"], fill=True)
        c.pixel(crown_x + 4, FLOOR - 3, CROWN["r"])
        c.pixel(crown_x, FLOOR - 5, CROWN["s"])
    for yy in range(FLOOR + 1, H):
        c.line(0, yy, W - 1, yy, (0, 0, 0, 0))
    return c.outline(OUTLINE)


HB = {"shape": "rect", "center": [24.0, 39.0]}
# move 8: the gel wobbles through squash and stretch, the surface ripples, the crown lags a beat
WOB = [(1.0, 1.0, 0, 0), (1.06, 0.94, 1, 1), (1.1, 0.9, 1, 2), (1.04, 0.97, 0, 1),
       (0.96, 1.05, -1, 0), (0.92, 1.09, -1, -1), (0.95, 1.06, -1, -2), (0.99, 1.01, 0, -1)]
ANIMATIONS = [
    ("move", [king(sx, sy, 1.2, k * 0.8, crown_dy=cd, crown_tilt=ct, bubbles=k) for k, (sx, sy, ct, cd) in enumerate(WOB)], 8, True,
     {"durations_ms": [140, 120, 140, 120, 140, 120, 140, 120], "hitbox": {**HB, "active": [0, 7]}}),
    ("crouch", [king(1.08, 0.93, 1.5, 0, eyes="angry", crown_dy=1), king(1.16, 0.86, 2, 1, eyes="angry", crown_dy=2),
                king(1.22, 0.8, 2.5, 2, eyes="angry", crown_dy=3), king(1.26, 0.76, 3, 3, eyes="angry", crown_dy=4)], 6, False,
     {"durations_ms": [150, 200, 250, 400], "hitbox": {**HB, "active": [0, 3]}}),
    ("jump", [king(0.9, 1.12, 1, 0, crown_dy=3), king(0.8, 1.25, 1.5, 1, crown_dy=4), king(0.85, 1.18, 1, 2, crown_dy=1),
              king(1.0, 1.0, 0.5, 3, crown_dy=-2), king(0.95, 1.06, 1, 4, crown_dy=-3), king(0.86, 1.18, 1, 5, crown_dy=-1),
              king(1.35, 0.68, 3, 6, eyes="closed", crown_dy=5), king(1.12, 0.9, 2, 7, crown_dy=2)], 8, False,
     {"durations_ms": [70, 90, 100, 120, 100, 90, 110, 120], "hitbox": {**HB, "active": [0, 7]}}),
    ("attack", [king(1.04, 0.97, 1, 0, eyes="angry", cheeks=1), king(1.08, 0.94, 1.5, 1, eyes="angry", cheeks=2),
                king(1.12, 0.9, 1.5, 2, eyes="angry", cheeks=3), king(0.96, 1.06, 1, 3, eyes="angry", mouth=2),
                king(0.94, 1.08, 1, 4, eyes="angry", mouth=4), king(0.96, 1.06, 1, 5, eyes="angry", mouth=3),
                king(1.02, 0.99, 1, 6, mouth=1), king(1.0, 1.0, 1, 7)], 8, False,
     {"durations_ms": [130, 150, 220, 80, 120, 100, 120, 140], "hitbox": {**HB, "active": [3, 5]}}),
    ("hurt", [flash(king(1.1, 0.9, 2, 0, eyes="closed")), king(0.92, 1.08, 3, 2, eyes="closed", crown_dy=-2),
              king(1.06, 0.95, 2, 4, crown_dy=1), king(1.0, 1.0, 1, 6)], 12, False,
     {"durations_ms": [70, 100, 100, 120], "hitbox": {**HB, "active": [0, 3]}}),
    ("death", [flash(king(1.0, 1.0, 3, 0, eyes="closed"), 0.5), king(1.08, 0.92, 3.5, 2, eyes="closed", crown_dy=-3),
               king(0.94, 1.06, 3.5, 4, eyes="closed", crown_dy=-5), king(1.2, 0.8, 2.5, 5, eyes="closed", crown_dy=-2, crown_tilt=3),
               king(1.35, 0.62, 2, 6, eyes="closed", crown=False), puddle(0, 34), puddle(1, 36), puddle(2, 37)], 6, False,
     {"durations_ms": [120, 140, 140, 160, 180, 240, 280, 400], "hitbox": {**HB, "active": [0, 7]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=5, gif_scale=3)
    print("OK", NAME)
