#!/usr/bin/env python3
"""Generator cho sprite "ranger": Cung thủ (Du hiệp) của Bách Ải, phương án C người dùng chọn 2026-11-23
(sprite-lab/designs/cung-thu/variants.py). Nhìn nghiêng, quay phải; frame 48x48, neo giữa hai bàn chân.
Dấu hiệu: tóc đuôi ngựa cam bay theo nhịp, áo chẽn sáng, cung dài cầm tay trước, nằm ngang dưới tay
(lớp weapon, người dùng 2026-11-23: không đeo sau lưng; trang bị thay được). Bắn là sprite hiệu ứng riêng, nên chỉ có: idle 4, run 8, hurt 3, dash 5, death 5.
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
    """The longbow held in the front hand, lying level below it (user 2026-11-23: not slung on the back): the grip
    in the hand, both limbs curving down to the tips, the string straight under them."""
    hx, hy = g["hand_front"]
    hx += 2                                        # most of the bow ahead of the body
    half = 7
    hy = min(hy, mf.FLOOR - 3 - (half * half) // 14)   # low hands (a fall): string + its outline stay above the floor
    for dx in range(-half, half + 1):
        y = hy + (dx * dx) // 14                      # limbs bend down from the grip
        put(c, hx + dx, y, PAL["wood"] if abs(dx) > 1 else PAL["wood_d"])
    tip_y = hy + (half * half) // 14
    for dx in range(-half + 1, half):
        put(c, hx + dx, tip_y + 1, PAL["string"])
    put(c, hx - half, tip_y + 1, PAL["wood_d"])
    put(c, hx + half, tip_y + 1, PAL["wood_d"])


CHAR = {"pal": PAL, "body": "tunic", "head": head, "hair": hair, "held": longbow}


def frame(**kw):
    return mf.draw_layers(CHAR, pose(**kw))


def idle(i):
    return frame(bob=[0, 0, 1, 1][i], lean=-1, feet=((-4, 0), (4, 0)), hands=((-2, 6), (5, 3)), phase=i * 0.8,
                 eyes="closed" if i == 3 else "open")


def run(i):
    return mf.draw_layers(CHAR, run_pose(i, bob=[1, 1, 1, 0, 1, 1, 1, 0][i], lean=2, hands=((-2, 5), (5, 3))))


def dash(i):
    """Dash: crouch, launch, two glide frames, recover; the ponytail streams back."""
    return [
        frame(bob=2, lean=1, feet=((-4, 0), (3, 0)), hands=((-3, 5), (4, 3)), speed=0.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-6, 4), (-1, 3)), speed=1.0, phase=0.6),
        frame(bob=2, lean=3, feet=((-7, 2), (5, 0)), hands=((-7, 3), (-2, 3)), speed=1.0, phase=1.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-7, 4), (-2, 3)), speed=1.0, phase=2.2),
        frame(bob=1, lean=1, feet=((-3, 0), (3, 0)), hands=((-2, 6), (5, 3)), speed=0.5, phase=3.0),
    ][i]


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 3)),
              eyes="wince", flash=0.75, speed=0.6, tilt=-1),
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 4), (3, 4)),
              eyes="wince", speed=0.4, phase=1.0, tilt=-1),
        frame(bob=0, lean=-1, feet=((-4, 0), (4, 0)), hands=((-2, 6), (5, 3))),
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
