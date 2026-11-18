#!/usr/bin/env python3
"""Generator cho "toad-king" (Cóc Chúa): boss vùng Đầm Lầy Độc (Bách Ải 6A).

Mô tả đầy đủ + tham khảo: games/bach-ai/design/art/toads.md. Cùng giải phẫu với Cóc Độc nhưng to x1.75, vẽ
theo bộ phận bằng sprite-lab/lib/toadkit.py (khung lớn đủ chỗ cho hình học): đùi sau gập, tay trước chống,
mắt lồi có gờ mày và đồng tử ngang, tuyến độc, miệng rộng, mụn độc tròn to nhỏ khác nhau, lưng lốm đốm,
vương miện nấm độc tím, dãi độc khi gồng. Frame 56x44, quay phải, neo (28, 43).
move 4 (ngồi, họng phập phồng), crouch 2 (lấy đà, dãi độc), jump 4 (bật → đỉnh → rơi → đáp; game nâng sprite
theo đường cong), hurt 2, death 4 (bẹp, chảy thành vũng độc, vương miện nấm còn lại). Chạy: gamekit art run toad-king
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
from toadkit import POSES, PAL, draw_toad, CAP, CAP_L, STEM  # noqa: E402

NAME = "toad-king"
W, H = 56, 44
ANCHOR = (28.0, 43.0)
OUTLINE = "#14160c"
S = 1.75
KPAL = {**PAL, "lit": "#7a7a30", "back": "#4e5a22", "side": "#2e3418",
        "wart_l": "#e8964a", "wart": "#b8581e", "wart_d": "#6a2a12"}   # darker, duller warts on the king   # a shade darker than Cóc Độc
POOL, POOL_L = "#4a8a22", "#8ad040"


def to_floor(c, floor=41):
    """Every pose sits on the floor inside the frame: the game lifts the sprite along the hop arc."""
    box = c.img.getbbox()
    out = Canvas(c.width, c.height)
    if box:
        out.img.alpha_composite(c.img, (0, floor - (box[3] - 1)))
    return out


def frame(pose, **extra):
    c = Canvas(W, H)
    p = {**POSES[pose], **extra}
    draw_toad(c, p, S, 0, 2, KPAL, king=True)
    return to_floor(c).outline(OUTLINE)


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
    c = Canvas(W, H)
    w = [20, 24, 26][k]
    c.ellipse(28 - w, 38, 28 + w, 41, POOL, fill=True)
    c.ellipse(28 - w + 6, 38, 28 + w - 10, 39, POOL_L, fill=True)
    if k < 2:
        c.ellipse(18, 33 + 2 * k, 38, 40, KPAL["back"], fill=True)
        c.pixel(24, 34 + 2 * k, PAL["wart"]); c.pixel(31, 35 + 2 * k, PAL["wart"])
    c.line(28, 37 - (3 if k < 2 else 0), 28, 39, STEM, 2)   # the mushroom crown left on top
    top = 33 - (3 if k < 2 else 0)
    c.ellipse(24, top, 32, top + 4, CAP, fill=True)
    c.pixel(26, top + 1, CAP_L)
    return to_floor(c).outline(OUTLINE)


HB = {"shape": "rect", "center": [28.0, 43.0]}
ANIMATIONS = [
    ("move", [frame("sit"), frame("sit_puff"), frame("sit_low"), frame("sit_puff")], 6, True,
     {"durations_ms": [260, 200, 240, 200], "hitbox": {**HB, "active": [0, 3]}}),
    ("crouch", [frame("crouch", drool=True), frame("crouch_deep", drool=True)], 6, False,
     {"durations_ms": [300, 600], "hitbox": {**HB, "active": [0, 1]}}),
    ("jump", [frame("takeoff"), frame("apex"), frame("fall"), frame("land")], 6, False,
     {"durations_ms": [150, 230, 180, 140], "hitbox": {**HB, "active": [0, 3]}}),
    ("attack", [frame("crouch_deep", drool=True), frame("apex"), frame("land")], 6, False,
     {"durations_ms": [300, 200, 240], "hitbox": {**HB, "active": [1, 2]}}),
    ("hurt", [flash(frame("sit")), frame("sit_low")], 12, False, {"durations_ms": [80, 140], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [flash(frame("flat"), 0.4), melt(0), melt(1), melt(2)], 6, False,
     {"durations_ms": [160, 220, 260, 400], "hitbox": {**HB, "active": [0, 3]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=5, gif_scale=3)
    print(f"OK {NAME}")
