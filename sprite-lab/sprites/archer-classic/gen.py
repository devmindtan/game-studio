#!/usr/bin/env python3
"""Generator cho "archer-classic": nữ cung thủ nhìn nghiêng, quay phải — làm bằng QUY TRÌNH CŨ (không AI).

Thử nghiệm 2026-11-21 (người dùng): so với "archer-ai" (cùng đề bài, quy trình có model), hai bản độc lập.
Tham khảo (skill art-reference): Pixel Redhead Archer (mewily.itch.io), Elthen Elven Archer, Pixollie archer.
  học: tóc đỏ là màu nổi trên trang phục xỉn; cung to để đọc ở cỡ nhỏ.  tránh: chi tiết 1 px (dây cung, tên).
  quyết định: mũ trùm + áo xanh rừng (palette afr-32), đuôi ngựa nâu đỏ, ống tên sau lưng, cung gỗ ~14 px.
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

NAME = "archer-classic"
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))

PAL = {   # afr-32 (Lospec)
    "skin": "#e8b796", "skin_d": "#b28b78",
    "hair": "#c5452b", "hair_d": "#723012",
    "hood": "#399a4d", "hood_d": "#204f1a", "hood_l": "#99e0a8",
    "tunic": "#406a3b", "tunic_d": "#204f1a", "tunic_l": "#399a4d",
    "sleeve": "#406a3b", "sleeve_d": "#204f1a",
    "belt": "#845425", "buckle": "#d3bd46",
    "pants": "#695b59", "pants_d": "#4f4240",
    "boot": "#723012", "boot_d": "#3e1909",
    "wood": "#a76343", "wood_d": "#723012", "string": "#ecebe7",
    "quiver": "#845425", "feather": "#ecebe7", "tip": "#cbc6c1",
    "eye": "#1a0a01",
}


def neck(c, p, g):
    """Vạt mũ trùm quanh cổ (chest slot)."""
    t = g["top"]
    rect(c, t[0] - 3, t[1], t[0] + 2, t[1] + 1, PAL["hood"])
    put(c, t[0] - 3, t[1] + 1, PAL["hood_d"])


def head(c, p, g):
    hx, hy = g["head"]
    rect(c, hx - 3, hy - 6, hx + 4, hy, PAL["skin"])
    put(c, hx - 3, hy, PAL["skin_d"])
    mf.eyes(c, hx + 2, hy - 4, p["eyes"], PAL)
    put(c, hx + 3, hy - 1, PAL["hair"])                      # môi


def hair(c, p, g):
    """Mũ trùm xanh, mái tóc đỏ lộ ra trước trán (head-gear slot)."""
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 7, PAL["hood"])
    rect(c, hx - 5, hy - 7, hx - 2, hy - 1, PAL["hood"])
    put(c, hx - 5, hy - 1, PAL["hood_d"])
    put(c, hx + 1, hy - 8, PAL["hood_l"])
    put(c, hx + 4, hy - 7, PAL["hood"])
    rect(c, hx + 2, hy - 6, hx + 4, hy - 6, PAL["hair"])     # mái tóc
    put(c, hx - 1, hy - 6, PAL["hair"])


def back(c, p, g):
    """Sau lưng: ống tên chéo + đuôi ngựa đỏ đung đưa theo tốc độ."""
    t, hip = g["top"], g["hip"]
    qx, qy = t[0] - 3, t[1] + 1
    line(c, qx + 1, qy + 6, qx - 2, qy - 2, PAL["quiver"], 2)
    put(c, qx - 3, qy - 3, PAL["feather"])
    put(c, qx - 2, qy - 4, PAL["feather"])
    hx, hy = g["head"]
    x, y = hx - 5, hy - 5
    for k in range(1, 6):
        wave = math.sin(p["phase"] + k * 0.8) * (0.4 + 0.8 * p["speed"])
        nx = hx - 5 - round(k * (0.3 + 0.6 * p["speed"]))
        ny = hy - 5 + round(k * (1 - 0.6 * p["speed"])) + round(wave)
        line(c, x, y, nx, ny, PAL["hair"] if k < 5 else PAL["hair_d"], 2)
        x, y = nx, ny
    _ = hip


def bow(c, p, g):
    """Cung gỗ dọc ở tay trước, lưng cung cong ra trước, dây cung sáng sát tay."""
    hx, hy = g["hand_front"]
    top, bot = hy - 7, min(hy + 7, mf.FLOOR - 2)
    prev = None
    for y in range(top, bot + 1):
        t = (y - hy) / 7.0
        x = hx + 1 + round(3 * (1 - t * t))
        if prev:
            line(c, prev[0], prev[1], x, y, PAL["wood"], 1)
        prev = (x, y)
        put(c, x + 1, y, PAL["wood_d"]) if abs(t) < 0.5 else None
    line(c, hx + 1, top, hx + 1, bot, PAL["string"], 1)


CHAR = {"pal": PAL, "body": "tunic", "head": head, "hair": hair, "neck": neck, "behind": back, "held": bow}



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
