#!/usr/bin/env python3
"""Generator cho "archer-ai": nữ cung thủ nhìn nghiêng, quay phải — làm bằng QUY TRÌNH CÓ MODEL.

Thử nghiệm 2026-11-21 (người dùng): so với "archer-classic" (cùng đề bài, quy trình cũ), hai bản độc lập.
Ngoại hình: gamekit art concept archer-ai "..." --seeds 4 -> chọn concept/102.png (tóc đỏ dài xoã, áo olive,
bao tay + thắt lưng da, ủng nâu, cung cong lớn); palette lấy từ concept/102.json.
Chuẩn như swordsman: 48x48, neo (24, 44), ground=True, lớp đồ; idle 4, run 8, hurt 3, dash 5, death 5.
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

import minifig as mf  # noqa: E402
from minifig import line, pose, put, rect, run_pose  # noqa: E402
from sheet import export_layered  # noqa: E402

NAME = "archer-ai"
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))

PAL = {   # concept/102.json, thêm bậc tối/sáng cho đủ ramp
    "skin": "#ebae8d", "skin_d": "#d69670",
    "hair": "#955134", "hair_d": "#843b31", "hair_l": "#c6745c",
    "tunic": "#676153", "tunic_d": "#4e4a3f", "tunic_l": "#7b8370",
    "sleeve": "#676153", "sleeve_d": "#4e4a3f",
    "belt": "#624836", "buckle": "#939190",
    "pants": "#56574a", "pants_d": "#3f4036",
    "boot": "#624836", "boot_d": "#5b362e",
    "bracer": "#624836",
    "wood": "#b0653e", "wood_d": "#843b31", "string": "#c8c4bd",
    "eye": "#2a1a1a",
}


def neck(c, p, g):
    """Cổ áo da (chest slot)."""
    t = g["top"]
    rect(c, t[0] - 2, t[1], t[0] + 2, t[1], PAL["belt"])


def head(c, p, g):
    hx, hy = g["head"]
    rect(c, hx - 3, hy - 6, hx + 4, hy, PAL["skin"])
    put(c, hx - 3, hy, PAL["skin_d"])
    mf.eyes(c, hx + 2, hy - 4, p["eyes"], PAL)
    put(c, hx + 3, hy - 1, PAL["hair_d"])                    # môi


def hair(c, p, g):
    """Tóc đỏ: đỉnh đầu, mái lệch, gáy dài (head-gear slot)."""
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 7, PAL["hair"])
    rect(c, hx - 4, hy - 7, hx - 1, hy - 1, PAL["hair"])
    rect(c, hx + 2, hy - 6, hx + 4, hy - 6, PAL["hair"])
    put(c, hx + 4, hy - 7, PAL["hair"])
    put(c, hx, hy - 8, PAL["hair_l"])
    put(c, hx + 1, hy - 8, PAL["hair_l"])
    put(c, hx - 4, hy - 1, PAL["hair_d"])


def long_hair(c, p, g):
    """Sau lưng: tóc xoã dài tới giữa lưng, bay ra sau khi chạy."""
    hx, hy = g["head"]
    for k in range(9):
        back = round(k * (0.15 + 0.55 * p["speed"]))
        wave = round(math.sin(p["phase"] + k * 0.6) * 0.7 * p["speed"])
        y = hy - 6 + k - round(k * 0.4 * p["speed"]) + wave
        x1 = hx - 3 - back
        w = 3 if k < 6 else 2
        rect(c, x1 - w, y, x1, y, PAL["hair"] if k < 7 else PAL["hair_d"])
        put(c, x1 - w, y, PAL["hair_d"])


def bow(c, p, g):
    """Cung cong (recurve) ở tay trước: thân cong ra trước, hai đầu cong ngược, dây sát tay. Bao tay da."""
    hx, hy = g["hand_front"]
    rect(c, hx - 1, hy, hx, hy + 1, PAL["bracer"])
    top, bot = hy - 8, min(hy + 8, mf.FLOOR - 2)
    prev = None
    for y in range(top + 1, bot):
        t = (y - hy) / 8.0
        x = hx + 1 + round(3.5 * (1 - t * t))
        if prev:
            line(c, prev[0], prev[1], x, y, PAL["wood"], 1)
        prev = (x, y)
    put(c, hx + 1, hy, PAL["wood_d"])                         # tay cầm
    put(c, hx + 2, top, PAL["wood"])                          # đầu cong ngược
    put(c, hx + 2, bot, PAL["wood"])
    line(c, hx + 1, top + 1, hx + 1, bot - 1, PAL["string"], 1)


CHAR = {"pal": PAL, "body": "tunic", "head": head, "hair": hair, "neck": neck, "behind": long_hair, "held": bow}



def frame(**kw):
    return mf.draw_layers(CHAR, pose(**kw))


# --- animations: movement and state only (attacks are effect sprites) -------------

def idle(i):
    bob = [0, 0, 1, 0][i]
    return frame(bob=bob, hands=((-2, 7), (3, 5)), weapon=20, phase=i * 1.2,
                 eyes="closed" if i == 3 else "open")


def run(i):
    return mf.draw_layers(CHAR, run_pose(i, weapon=205 + 8 * math.sin(i * math.pi / 4)))


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 4)),
              weapon=200, eyes="wince", flash=0.75, speed=0.5),
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 4), (1, 5)),
              weapon=200, eyes="wince", speed=0.3, phase=1.0),
        frame(bob=0, lean=0, hands=((-2, 7), (3, 5)), weapon=20),
    ][i]


def dash(i):
    """Dash (2026-11-17, for the dash skill): wind-up, launch, two glide frames, recover.
    Feet stay on the floor (ground=True); the body leans hard, arms and sword trail back,
    the scarf flies out at full speed."""
    return [
        frame(bob=2, lean=1, feet=((-4, 0), (3, 0)), hands=((-3, 5), (3, 5)), weapon=200, speed=0.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-6, 4), (-1, 5)), weapon=190, speed=1.0, phase=0.6),
        frame(bob=2, lean=3, feet=((-7, 2), (5, 0)), hands=((-7, 3), (-2, 4)), weapon=185, speed=1.0, phase=1.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-7, 4), (-2, 5)), weapon=188, speed=1.0, phase=2.2),
        frame(bob=1, lean=1, feet=((-3, 0), (3, 0)), hands=((-2, 6), (3, 5)), weapon=30, speed=0.5, phase=3.0),
    ][i]


def death(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 4)),
              weapon=110, eyes="x", flash=0.5),
        frame(bob=3, lean=-1, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), weapon=95, eyes="x"),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), weapon=120, eyes="x",
              lie=0.4),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), weapon=150, eyes="x",
              lie=0.85),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), weapon=150, eyes="x",
              lie=1.0),
    ][i]


# (name, [layers per frame], fps, loop, extra)
ANIMATIONS = [
    ("idle", [idle(i) for i in range(4)], 5, True, {"durations_ms": [240, 160, 240, 120], "hitbox": {"shape":"rect","center":[24.0,44.0],"active":[0,3]}}),
    ("run", [run(i) for i in range(8)], 12, True, {"hitbox": {"shape":"rect","center":[24.0,44.0],"active":[0,7]}}),
    ("hurt", [hurt(i) for i in range(3)], 12, False, {"durations_ms": [90, 110, 120], "hitbox": {"shape":"rect","center":[24.0,44.0],"active":[0,2]}}),
    ("dash", [dash(i) for i in range(5)], 14, False, {"durations_ms": [60, 50, 70, 70, 90], "hitbox": {"shape":"rect","center":[24.0,44.0],"active":[0,4]}}),
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [120, 140, 110, 100, 400], "hitbox": {"shape":"rect","center":[24.0,44.0],"active":[0,4]}}),
]


if __name__ == "__main__":
    export_layered(HERE, NAME, ANIMATIONS, anchor=ANCHOR, outline=mf.OUTLINE, ground=True, body="idle",
                   preview_scale=4, gif_scale=4)
    print(f"OK {NAME}")
