#!/usr/bin/env python3
"""Generator cho sprite "ranger": Cung thủ (Du hiệp) của Bách Ải, phương án C người dùng chọn 2026-11-23
(sprite-lab/designs/cung-thu/variants.py). Nhìn nghiêng, quay phải; frame 48x48, neo giữa hai bàn chân.
Dấu hiệu: tóc đuôi ngựa cam bay theo nhịp, áo chẽn sáng, cung dài dựng đứng trong tay trước buông
bên hông, dây quay về phía lưng (lớp weapon; người dùng 2026-11-23 kèm ảnh tham khảo). Bắn là sprite hiệu ứng riêng, nên chỉ có: idle 4, run 8, hurt 3, dash 5, death 5.
Chạy:  gamekit art run ranger  ·  thử: gamekit art shot ranger sheet|move
"""

import math
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

from sheet import export_layered  # noqa: E402
import minifig as mf  # noqa: E402
from minifig import line, pose, put, rect, run_pose  # noqa: E402

NAME = "ranger"
OUT = HERE
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))

PAL = {"skin": "#f0c4a0", "skin_d": "#c98f72", "eye": "#1b1726", "hair": "#c26a2a", "hair_d": "#8e4a1e",
       "tunic": "#d8cfb0", "tunic_d": "#a89e80", "tunic_l": "#f0e8cc", "sleeve": "#2f5f6e", "sleeve_d": "#1f4050",
       "belt": "#2f5f6e", "buckle": "#e0b250", "pants": "#2f5f6e", "pants_d": "#1f4050",
       "boot": "#5a3d28", "boot_d": "#3d2919", "wood": "#c08a4a", "wood_d": "#7a5228", "string": "#e8e2d0"}


def head(c, p, g):
    hx, hy = g["head"]
    rect(c, hx - 3, hy - 6, hx + 4, hy, PAL["skin"])
    put(c, hx - 3, hy, PAL["skin_d"])
    mf.eyes(c, hx + 2, hy - 4, p["eyes"], PAL)


def hair(c, p, g):
    """Orange ponytail swinging with the run (head slot)."""
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 6, PAL["hair"])
    rect(c, hx - 4, hy - 6, hx - 3, hy - 4, PAL["hair"])
    put(c, hx + 3, hy - 6, PAL["hair_d"])
    for k in range(4):
        y = hy - 6 + k // 2 + round(math.sin(p["phase"] + k * 0.6) * p["speed"]) + (1 if p["tilt"] < 0 else 0)
        put(c, hx - 5 - k, y, PAL["hair"] if k < 3 else PAL["hair_d"])


def longbow(c, p, g):
    """The longbow carried as archers walk with it (user 2026-11-23, with a reference photo; carrying guides, e.g. battlbox.com
    "how to carry bow while hunting": hold the riser, bow vertical, arm down at the side, string toward the back): upright in the front hand, the grip
    in the fist, the limbs bowing forward, the straight string behind them. The lower limb is cut short above
    the floor in low poses."""
    hx, hy = g["hand_front"]
    up, down = 13, 8                               # a longbow: the upper tip at the shoulder
    down = min(down, mf.FLOOR - 3 - hy)            # string + outline stay above the floor
    for dy in range(-up, down + 1):
        half = up if dy < 0 else max(1, down)
        bulge = round(2.5 * (1 - (dy / half) ** 2))   # limbs bow forward, most at the grip
        put(c, hx + bulge, hy + dy, PAL["wood_d"] if abs(dy) <= 1 else PAL["wood"])
    for dy in range(-up + 1, down):
        put(c, hx - 1, hy + dy, PAL["string"])       # the string, straight, on the body side
    put(c, hx, hy - up, PAL["wood_d"])
    put(c, hx, hy + down, PAL["wood_d"])


CHAR = {"pal": PAL, "body": "tunic", "head": head, "hair": hair, "held": longbow}


def frame(**kw):
    return mf.draw_layers(CHAR, pose(**kw))


def idle(i):
    return frame(bob=[0, 0, 1, 1][i], lean=-1, feet=((-4, 0), (4, 0)), hands=((-2, 6), (3, 6)), phase=i * 0.8,
                 eyes="closed" if i == 3 else "open")


def run(i):
    return mf.draw_layers(CHAR, run_pose(i, bob=[1, 1, 1, 0, 1, 1, 1, 0][i], lean=2, hands=((-2, 5), (3, 6))))


def dash(i):
    """Dash: crouch, launch, two glide frames, recover; the ponytail streams back."""
    return [
        frame(bob=2, lean=1, feet=((-4, 0), (3, 0)), hands=((-3, 5), (2, 6)), speed=0.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-6, 4), (-1, 6)), speed=1.0, phase=0.6),
        frame(bob=2, lean=3, feet=((-7, 2), (5, 0)), hands=((-7, 3), (-2, 6)), speed=1.0, phase=1.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-7, 4), (-2, 6)), speed=1.0, phase=2.2),
        frame(bob=1, lean=1, feet=((-3, 0), (3, 0)), hands=((-2, 6), (3, 6)), speed=0.5, phase=3.0),
    ][i]


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 3)),
              eyes="wince", flash=0.75, speed=0.6, tilt=-1),
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 4), (3, 4)),
              eyes="wince", speed=0.4, phase=1.0, tilt=-1),
        frame(bob=0, lean=-1, feet=((-4, 0), (4, 0)), hands=((-2, 6), (3, 6))),
    ][i]


def death(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 3)), eyes="x", flash=0.5, tilt=-1),
        frame(bob=3, lean=-1, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 6)), eyes="x"),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 6)), eyes="x", lie=0.4),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 6)), eyes="x", lie=0.85),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 6)), eyes="x", lie=1.0),
    ][i]


# (name, [layers per frame], fps, loop, extra)
ANIMATIONS = [
    ("idle", [idle(i) for i in range(4)], 5, True, {"durations_ms": [240, 160, 240, 120], "hitbox": {"shape": "rect", "center": [24.0, 44.0], "active": [0, 3]}}),
    ("run", [run(i) for i in range(8)], 12, True, {"hitbox": {"shape": "rect", "center": [24.0, 44.0], "active": [0, 7]}}),
    ("hurt", [hurt(i) for i in range(3)], 12, False, {"durations_ms": [90, 110, 120], "hitbox": {"shape": "rect", "center": [24.0, 44.0], "active": [0, 2]}}),
    ("dash", [dash(i) for i in range(5)], 14, False, {"durations_ms": [60, 50, 70, 70, 90], "hitbox": {"shape": "rect", "center": [24.0, 44.0], "active": [0, 4]}}),
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [120, 140, 110, 100, 400], "hitbox": {"shape": "rect", "center": [24.0, 44.0], "active": [0, 4]}}),
]


if __name__ == "__main__":
    export_layered(HERE, NAME, ANIMATIONS, anchor=ANCHOR, outline=mf.OUTLINE, ground=True, body="idle",
                   preview_scale=4, gif_scale=4)
    print(f"OK {NAME}")
