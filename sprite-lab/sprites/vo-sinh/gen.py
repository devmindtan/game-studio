#!/usr/bin/env python3
"""Generator cho sprite "vo-sinh": nhân vật chính Thất Tinh Ấn (người dùng chọn phương án A "Quyền", 2026-11-23,
sprite-lab/designs/vo-sinh/variants.py). Võ sinh tay không, võ phục trắng, đai đỏ dài bay sau hông.

Frame 48x48 minifig, neo (24, 44) giữa hai bàn chân (ground=True). Quay phải, trái = lật.
Animation: idle 4 (thế thủ nảy mũi chân), run 8 (nảy nhanh), attack 5 (thu tay → đấm thẳng xoay hông → giữ →
thu về), hurt 3, death 5. Đòn đấm là động tác thân; hitbox ở khung đấm (tầm = nắm tay).
Chạy: gamekit art run vo-sinh · thử: gamekit art shot vo-sinh sheet|move
"""

import math
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

import minifig as mf  # noqa: E402
from minifig import pose, put, rect  # noqa: E402
from sheet import export_layered  # noqa: E402

NAME = "vo-sinh"
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))
PAL = {"skin": "#f0c4a0", "skin_d": "#c98f72", "eye": "#1b1726", "hair": "#2a2230",
       "tunic": "#ece6d6", "tunic_d": "#bdb5a2", "tunic_l": "#ffffff", "sleeve": "#f0c4a0", "sleeve_d": "#c98f72",
       "belt": "#c23b32", "buckle": "#c23b32", "pants": "#ece6d6", "pants_d": "#bdb5a2",
       "boot": "#2a2230", "boot_d": "#1b1726"}


def head(c, p, g):
    hx, hy = g["head"]
    rect(c, hx - 3, hy - 6, hx + 4, hy, PAL["skin"])
    put(c, hx - 3, hy, PAL["skin_d"])
    mf.eyes(c, hx + 2, hy - 4, p["eyes"], PAL)


def hair(c, p, g):
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 6, PAL["hair"])
    rect(c, hx - 4, hy - 6, hx - 2, hy - 3, PAL["hair"])
    put(c, hx + 4, hy - 7, PAL["hair"])


def belt_tail(c, p, g):
    hip = g["hip"]
    for k in range(5):
        y = hip[1] - 2 + round(k * 0.25 * (1 - p["speed"])) + round(math.sin(p["phase"] + k * 0.7) * 0.6 * p["speed"])
        put(c, hip[0] - 4 - k, y, "#c23b32" if k < 4 else "#8a2620")


CHAR = {"pal": PAL, "body": "tunic", "head": head, "hair": hair, "behind": belt_tail}


def frame(**kw):
    return mf.draw_layers(CHAR, pose(**kw))


def idle(i):
    return frame(bob=[0, 1, 1, 0][i], feet=((-4, 0), (4, 0)), hands=((3, 3), (5, 2)), phase=i * 0.8,
                 eyes="closed" if i == 3 else "open")


def run(i):
    return mf.draw_layers(CHAR, mf.run_pose(i, bob=[0, 1, -1, -2, 0, 1, -1, -2][i], hands=((2, 3), (4, 3))))


def attack(i):
    return [
        frame(bob=1, lean=-1, feet=((-5, 0), (4, 0)), hands=((3, 3), (1, 4)), speed=0.2),          # thu tay
        frame(bob=0, lean=2, feet=((-6, 0), (5, 0)), hands=((-1, 4), (10, 0)), speed=0.8, phase=1),  # đấm
        frame(bob=0, lean=2, feet=((-6, 0), (5, 0)), hands=((-1, 4), (10, 0)), speed=0.5, phase=2),  # giữ
        frame(bob=1, lean=1, feet=((-5, 0), (4, 0)), hands=((2, 3), (6, 1)), speed=0.3, phase=3),
        frame(bob=0, feet=((-4, 0), (4, 0)), hands=((3, 3), (5, 2))),                               # về thế thủ
    ][i]


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 4)), eyes="wince", flash=0.75, speed=0.5),
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 4), (1, 5)), eyes="wince", speed=0.3, phase=1.0),
        frame(feet=((-4, 0), (4, 0)), hands=((3, 3), (5, 2))),
    ][i]


def death(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 4)), eyes="x", flash=0.5),
        frame(bob=3, lean=-1, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), eyes="x"),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), eyes="x", lie=0.4),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), eyes="x", lie=0.85),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), eyes="x", lie=1.0),
    ][i]


ANIMATIONS = [
    ("idle", [idle(i) for i in range(4)], 6, True, {"durations_ms": [200, 160, 200, 140]}),
    ("run", [run(i) for i in range(8)], 14, True, {}),
    ("attack", [attack(i) for i in range(5)], 14, False,
     {"durations_ms": [70, 60, 90, 70, 80], "hitbox": {"shape": "circle", "center": [36.0, 32.0], "active": [1, 2]}}),
    ("hurt", [hurt(i) for i in range(3)], 12, False, {"durations_ms": [90, 110, 120]}),
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [120, 140, 110, 100, 400]}),
]


if __name__ == "__main__":
    export_layered(HERE, NAME, ANIMATIONS, anchor=ANCHOR, outline=mf.OUTLINE, ground=True, body="idle",
                   preview_scale=4, gif_scale=4)
    print(f"OK {NAME}")
