#!/usr/bin/env python3
"""Generator cho "toad-king" (Cóc Chúa): boss vùng Đầm Lầy Độc (Bách Ải 6A).

Mô tả đầy đủ + tham khảo: games/bach-ai/design/art/toads.md. Cùng giải phẫu với Cóc Độc nhưng to x1.75, vẽ
theo bộ phận bằng sprite-lab/lib/toadkit.py (khung lớn đủ chỗ cho hình học): đùi sau gập, tay trước chống,
mắt lồi có gờ mày và đồng tử ngang, tuyến độc, miệng rộng, mụn độc tròn to nhỏ khác nhau, lưng lốm đốm,
vương miện nấm độc tím, dãi độc khi gồng. Frame 56x48, quay phải, neo (28, 47).
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
from toadkit import POSES, PAL, draw_toad, lerp_pose, CAP, CAP_L, STEM  # noqa: E402

NAME = "toad-king"
W, H = 56, 48
ANCHOR = (28.0, 47.0)
OUTLINE = "#14160c"
S = 1.75
KPAL = {**PAL, "lit": "#7a7a30", "back": "#4e5a22", "side": "#2e3418",
        "wart_l": "#e8964a", "wart": "#b8581e", "wart_d": "#6a2a12"}   # darker, duller warts on the king   # a shade darker than Cóc Độc
POOL, POOL_L = "#4a8a22", "#8ad040"


def to_floor(c, floor=45):
    """Every pose sits on the floor inside the frame: the game lifts the sprite along the hop arc."""
    box = c.img.getbbox()
    out = Canvas(c.width, c.height)
    if box:
        out.img.alpha_composite(c.img, (0, floor - (box[3] - 1)))
    return out


def frame(pose, **extra):
    c = Canvas(W, H)
    p = {**(POSES[pose] if isinstance(pose, str) else pose), **extra}
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


P = POSES


def mid(a, b, t=0.5, **extra):
    return {**lerp_pose(P[a], P[b], t), **extra}


SPIT_BACK = {**P["sit"], "body": (16, 15, 9.5, 5.8, -18), "puff": 3}

HB = {"shape": "rect", "center": [28.0, 47.0]}
ANIMATIONS = [
    # move 8: sitting, throat sac breathing in and out, body bobbing, a slow blink
    ("move", [frame("sit"), frame(mid("sit", "sit_low", 0.3), puff=1), frame("sit_puff"), frame(mid("sit", "sit_puff", 0.5), puff=3),
              frame("sit_puff"), frame(mid("sit", "sit_low", 0.6), puff=1, eyes="shut"), frame("sit_low"), frame(mid("sit_low", "sit", 0.5))], 8, True,
     {"durations_ms": [180, 140, 140, 200, 140, 120, 160, 140], "hitbox": {**HB, "active": [0, 7]}}),
    # crouch 4: sinks, thighs load, poison drool lengthens (the leap is coming)
    ("crouch", [frame(mid("sit", "crouch", 0.5), drool=True), frame("crouch", drool=True),
                frame(mid("crouch", "crouch_deep", 0.5), drool=True), frame("crouch_deep", drool=True)], 6, False,
     {"durations_ms": [150, 200, 250, 400], "hitbox": {**HB, "active": [0, 3]}}),
    # jump 8: push, takeoff, rising, apex stretched, turning down, falling legs forward, landing squash, settle
    ("jump", [frame(mid("crouch_deep", "takeoff", 0.4)), frame("takeoff"), frame(mid("takeoff", "apex", 0.5)), frame("apex"),
              frame(mid("apex", "fall", 0.5)), frame("fall"), frame("land"), frame(mid("land", "sit", 0.5))], 8, False,
     {"durations_ms": [80, 90, 100, 120, 100, 90, 90, 100], "hitbox": {**HB, "active": [0, 7]}}),
    # attack 8 (poison spit): rears back, throat swells, mouth opens, spits, a second glob, closes, settles
    ("attack", [frame(lerp_pose(P["sit"], SPIT_BACK, 0.5), puff=2), frame(lerp_pose(P["sit"], SPIT_BACK, 0.8), puff=3), frame(SPIT_BACK, drool=True),
                frame(mid("sit", "land", 0.3), mouth=0.6), frame(mid("sit", "land", 0.4), mouth=1.0),
                frame(mid("sit", "land", 0.3), mouth=0.9), frame("sit", mouth=0.4), frame("sit")], 8, False,
     {"durations_ms": [140, 160, 220, 80, 120, 100, 120, 140], "hitbox": {**HB, "active": [3, 5]}}),
    # hurt 4: flash, recoil (tips back), wobble, recover
    ("hurt", [flash(frame("sit")), frame(SPIT_BACK, eyes="shut"), frame("sit_low", eyes="shut"), frame("sit")], 12, False,
     {"durations_ms": [70, 100, 100, 120], "hitbox": {**HB, "active": [0, 3]}}),
    # death 8: struck (flash), rears up, topples, flops flat, small bounce, still, melts into poison
    ("death", [flash(frame("sit"), 0.5), frame("takeoff", eyes="shut"), frame(mid("takeoff", "flat", 0.5)), frame("flat"),
               frame(mid("flat", "land", 0.3), eyes="shut"), frame("flat"), melt(0), melt(1)], 6, False,
     {"durations_ms": [120, 160, 120, 120, 100, 300, 260, 400], "hitbox": {**HB, "active": [0, 7]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=5, gif_scale=3)
    print(f"OK {NAME}")
