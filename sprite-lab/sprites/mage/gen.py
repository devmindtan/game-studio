#!/usr/bin/env python3
"""Generator cho sprite "mage": pháp sư nhìn nghiêng, quay phải, phong cách tối giản nhỏ gọn.

Frame 48x48, nhân vật cao khoảng 30 px tính cả mũ nhọn, neo (24, 44) giữa hai bàn chân trên mặt đất
(ground=True: mọi frame không phải nhảy phải chạm đất). Hình dựng từ tư thế bằng sprite-lab/lib/minifig.py,
áo choàng dài thay cho áo + quần. Dấu hiệu nhận diện: mũ nhọn tím viền vàng gập ra sau, râu trắng, gậy gỗ
với quả cầu xanh phát sáng.

Giữ từ bản trước: bảng màu, và chiêu "spell" theo nhịp nạp → căng → đẩy gậy → chớp ở đầu gậy → thu về.
Viên đạn bay (lúc bay, lúc nổ) là sprite riêng "arcane-bolt".

Bách Ải (2026-11-17): vẽ THEO LỚP trang bị như kiếm sĩ (mũ = ô đầu; áo choàng = ô ngực; tay; ủng = ô chân;
gậy = vũ khí; mặt và râu là lớp nền), chỉ di chuyển và trạng thái: idle 4, run 8, hurt 3, dash 5, death 5.
Phép là sprite hiệu ứng riêng (arcane-bolt, fireball…). Bản cũ có jump/attack/spell nằm trong lịch sử git.
Chạy:  gamekit art run mage  ·  thử: gamekit art shot mage sheet|move
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

NAME = "mage"
OUT = HERE
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))
STAFF_UP = 11       # hand -> orb
STAFF_DOWN = 6      # hand -> butt

# Bảng màu từ bản trước (đọc silhouette ở 1x, không gradient).
PAL = {
    "hat": "#4a2a7a", "hat_d": "#301f58", "hat_l": "#6d47ad",
    "gold": "#f0cd72", "gold_d": "#a8802f",
    "robe": "#5b3a96", "robe_d": "#3a2370", "robe_l": "#8a63cc", "trim": "#c9a4f2",
    "sleeve": "#5b3a96", "sleeve_d": "#3a2370",
    "belt": "#a8802f",
    "skin": "#f3cea6", "skin_d": "#cf9c73",
    "beard": "#eceaf5", "beard_d": "#b8b5cf",
    "wood": "#8a5a2e", "wood_d": "#563418",
    "boot": "#4a3157", "boot_d": "#2b1a33",
    "pants": "#241630", "pants_d": "#241630",
    "magic": "#7ef0ff", "magic_mid": "#37b9e8", "magic_deep": "#8b5cf6", "core": "#ffffff",
    "eye": "#140d20",
}


# Hat pixel maps, 13 wide, facing right: d shade (back), h hat, L lit edge (front), G gold band,
# g band shade, s star. Same brim and band in both, only the cone/tip changes.
HAT_KEYS = {"d": "hat_d", "h": "hat", "L": "hat_l", "G": "gold", "g": "gold_d", "s": "gold"}
HAT_REST = [
    "..dh.........",
    "...dh........",
    "....dhL......",
    "....dhhL.....",
    "...dhhhhL....",
    "...dhhshhL...",
    "..dhhhhhhhL..",
    "..gGGGGGGGGg.",
    "ddhhhhhhhhhhL",
]
HAT_WIND = [
    ".............",
    "dh...........",
    ".ddhh........",
    "..ddhhL......",
    "...dhhhhL....",
    "...dhhshhL...",
    "..dhhhhhhhL..",
    "..gGGGGGGGGg.",
    "ddhhhhhhhhhhL",
]


def head(c, p, g):
    hx, hy = g["head"]
    tilt = p["tilt"]
    # face in the shade of the brim
    rect(c, hx - 2, hy - 5, hx + 3, hy - 1, PAL["skin"])
    put(c, hx + 4, hy - 3, PAL["skin"])                      # nose
    put(c, hx - 2, hy - 5, PAL["skin_d"])
    rect(c, hx - 3, hy - 4, hx - 3, hy - 1, PAL["beard_d"])  # hair tuft behind the ear
    mf.eyes(c, hx + 2, hy - 4, p["eyes"], PAL)
    # beard: from the cheeks to a point on the chest, swaying with the robe
    sway = round(math.sin(p["phase"]) * 0.8 * p["speed"])
    for k, (x0, x1) in enumerate(((-1, 3), (-1, 3), (0, 3), (0, 2), (1, 2))):
        y = hy - 2 + k
        rect(c, hx + x0 + (sway if k > 2 else 0), y, hx + x1 + (sway if k > 2 else 0), y, PAL["beard"])
    put(c, hx - 1, hy, PAL["beard_d"])


def hat(c, p, g):
    """The hat (head slot: equipment can replace it); the face and beard stay in the body."""
    hx, hy = g["head"]
    # hat: hand-drawn pixel map (the outline is added around it). Column 6 sits on the
    # head's centre, the last row is the brim. "rest" when still; "wind" when moving
    # fast or recoiling: the tip is blown further back.
    rows = HAT_WIND if (p["speed"] >= 0.5 or p["tilt"] < 0) else HAT_REST
    for r, row in enumerate(rows):
        y = hy - 6 - (len(rows) - 1 - r)
        for col, ch in enumerate(row):
            if ch != ".":
                put(c, hx - 6 + col, y, PAL[HAT_KEYS[ch]])


def _staff_ends(p, g):
    hx, hy = g["hand_front"]
    up = mf.keep_above_floor(hx, hy, p["weapon"] + 180, STAFF_DOWN) - 180   # butt stays above the floor
    a = math.radians(up)
    dx, dy = math.cos(a), math.sin(a)
    top = (hx + 0.5 + dx * STAFF_UP, hy + 0.5 + dy * STAFF_UP)
    butt = (hx + 0.5 - dx * STAFF_DOWN, hy + 0.5 - dy * STAFF_DOWN)
    return top, butt


def staff(c, p, g):
    top, butt = _staff_ends(p, g)
    line(c, butt[0], butt[1], top[0], top[1], PAL["wood"], 1)
    line(c, butt[0] + 1, butt[1], top[0] + 1, top[1], PAL["wood_d"], 1)
    # orb: 3x3 with a bright core, ring of mid blue
    ox, oy = round(top[0]), round(top[1]) - 1
    rect(c, ox - 1, oy - 1, ox + 1, oy + 1, PAL["magic_mid"])
    put(c, ox, oy, PAL["magic"])
    put(c, ox - 1, oy - 1, PAL["core"])
    # soft glow round the orb (part of the weapon layer: layered heroes have no fx pass)
    for deg in range(0, 360, 30):
        rad = math.radians(deg)
        put(c, ox + math.cos(rad) * 2.6, oy + math.sin(rad) * 2.6, (126, 240, 255, 70))


CHAR = {"pal": PAL, "body": "robe", "head": head, "hair": hat, "held": staff}


def frame(**kw):
    return mf.draw_layers(CHAR, pose(**kw))


# --- animations: movement and state only (spells are effect sprites) ------------------
# (staff angle: direction hand -> orb; -90 = straight up)

def idle(i):
    return frame(bob=[0, 0, 1, 0][i], hands=((-2, 7), (6, 3)), weapon=-88, phase=i * 1.1,
                 eyes="closed" if i == 3 else "open")


def run(i):
    return mf.draw_layers(CHAR, run_pose(i, weapon=-62))


def dash(i):
    """Dash (dash skill): wind-up, launch, two glide frames, recover; staff trails back."""
    return [
        frame(bob=2, lean=1, feet=((-4, 0), (3, 0)), hands=((-3, 5), (2, 4)), weapon=-130, speed=0.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-6, 4), (-1, 4)), weapon=-160, speed=1.0, phase=0.6),
        frame(bob=2, lean=3, feet=((-7, 2), (5, 0)), hands=((-7, 3), (-2, 4)), weapon=-165, speed=1.0, phase=1.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-7, 4), (-2, 4)), weapon=-162, speed=1.0, phase=2.2),
        frame(bob=1, lean=1, feet=((-3, 0), (3, 0)), hands=((-2, 6), (5, 3)), weapon=-80, speed=0.5, phase=3.0),
    ][i]


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 3)),
              weapon=-50, eyes="wince", flash=0.75, speed=0.6, tilt=-1),
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 4), (4, 3)),
              weapon=-45, eyes="wince", speed=0.4, phase=1.0, tilt=-1),
        frame(bob=0, lean=0, hands=((-2, 7), (6, 3)), weapon=-88),
    ][i]


def death(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 3)),
              weapon=-120, eyes="x", flash=0.5, tilt=-1),
        frame(bob=3, lean=-1, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 6)), weapon=-130, eyes="x"),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 6)), weapon=-150, eyes="x",
              lie=0.4),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 6)), weapon=-170, eyes="x",
              lie=0.85),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 6)), weapon=-170, eyes="x",
              lie=1.0),
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
