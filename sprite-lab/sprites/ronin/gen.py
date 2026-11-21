#!/usr/bin/env python3
"""Generator cho sprite "ronin": lãng khách kiếm sĩ nhìn nghiêng, quay phải (trái = lật), cùng chuẩn với "swordsman".

Ngoại hình chốt bằng concept AI: gamekit art concept ronin "..." -> concept/103.png (pixel hoá) + 103.json
(palette). Frame 48x48, neo (24, 44) giữa hai bàn chân, ground=True, vẽ THEO LỚP (minifig.LAYERS) để mặc đồ.
Dấu hiệu nhận diện (khác swordsman áo tunic xanh, khăn, kiếm ngắn): áo khoác dài xanh than tới gối, áo choàng
đỏ thẫm sau lưng bay theo tốc độ, búi tóc đen, kiếm dài thép.
Animation như swordsman: idle 4, run 8, hurt 3, dash 5, death 5 (đòn đánh là sprite hiệu ứng riêng).
Chạy:  gamekit art run ronin  ·  thử: gamekit art shot ronin sheet|move
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

NAME = "ronin"
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))
BLADE = 13          # blade length in px (body is ~26 px tall)

PAL = {   # từ concept/103.json (pixel hoá ảnh AI), chỉnh sáng/tối cho đủ ramp 3 bậc
    "skin": "#e7a986", "skin_d": "#b8765e",
    "hair": "#2f2730", "hair_l": "#523747",
    "cape": "#8e3636", "cape_d": "#5e2328", "cape_l": "#b4503f",
    "robe": "#46506a", "robe_d": "#323a4e", "robe_l": "#6c7894", "trim": "#323a4e",
    "sleeve": "#46506a", "sleeve_d": "#323a4e",
    "belt": "#644831", "buckle": "#b0b2b4",
    "pants": "#323746", "pants_d": "#23262f",
    "boot": "#7a4e34", "boot_d": "#4f3222",
    "blade": "#e2e6ea", "blade_d": "#8f9092", "guard": "#8f9092", "grip": "#523747",
    "eye": "#1b1726",
}


def neck(c, p, g):
    """Cổ áo choàng đỏ quanh vai (chest slot)."""
    t = g["top"]
    rect(c, t[0] - 3, t[1], t[0] + 2, t[1] + 1, PAL["cape"])
    put(c, t[0] + 2, t[1], PAL["cape_l"])
    put(c, t[0] - 3, t[1] + 1, PAL["cape_d"])


def head(c, p, g):
    """Face block and eyes (skin layer)."""
    hx, hy = g["head"]
    rect(c, hx - 3, hy - 6, hx + 4, hy, PAL["skin"])
    put(c, hx - 3, hy, PAL["skin_d"])
    mf.eyes(c, hx + 2, hy - 4, p["eyes"], PAL)


def hair(c, p, g):
    """Tóc đen ôm đầu + búi tó trên đỉnh, nghiêng theo tilt (head-gear slot)."""
    hx, hy = g["head"]
    tilt = p["tilt"]
    rect(c, hx - 4, hy - 7, hx + 3, hy - 6, PAL["hair"])
    rect(c, hx - 4, hy - 6, hx - 2, hy - 2, PAL["hair"])
    put(c, hx + 4, hy - 6, PAL["hair"])                      # tóc mái
    bx = hx - 1 + tilt
    rect(c, bx - 1, hy - 10, bx + 1, hy - 8, PAL["hair"])    # búi
    put(c, bx, hy - 10, PAL["hair_l"])
    put(c, bx - 1, hy - 8, PAL["cape"])                      # dây buộc đỏ


def cape(c, p, g):
    """Áo choàng sau lưng: từ vai rủ xuống gần gối, đứng yên thì buông, chạy thì bay ra sau và gợn sóng."""
    t = g["top"]
    length = 12 + round(2 * p["speed"])
    for k in range(length):
        back = round(k * (0.25 + 0.6 * p["speed"]))
        wave = round(math.sin(p["phase"] + k * 0.7) * 0.9 * p["speed"])
        x1 = t[0] - 1 - back                                 # mép trước (sát lưng)
        y = t[1] + k - round(k * 0.5 * p["speed"]) + wave
        w = 3 + min(3, k // 3)                               # rộng dần xuống dưới
        rect(c, x1 - w + 1, y, x1, y, PAL["cape"])
        put(c, x1 - w + 1, y, PAL["cape_d"])
        if k < 4:
            put(c, x1 - 1, y, PAL["cape_l"])                 # nếp sáng gần vai
        if k == length - 1:
            rect(c, x1 - w + 1, y, x1, y, PAL["cape_d"])


def _points_back(p):
    return math.cos(math.radians(p["weapon"])) < -0.2


def sword_behind(c, p, g):
    """A sword carried backwards is drawn behind the body, not across the chest."""
    if _points_back(p):
        _sword(c, p, g)


def sword(c, p, g):
    if not _points_back(p):
        _sword(c, p, g)


def _sword(c, p, g):
    hx, hy = g["hand_front"]
    a = math.radians(mf.keep_above_floor(hx, hy, p["weapon"], BLADE))  # never through the floor
    dx, dy = math.cos(a), math.sin(a)
    gx, gy = hx + 0.5, hy + 0.5
    line(c, gx - dx * 2, gy - dy * 2, gx, gy, PAL["grip"], 1)               # grip behind the hand
    px, py = -dy, dx                                                          # guard across the blade
    line(c, gx + dx + px * 1.5, gy + dy + py * 1.5, gx + dx - px * 1.5, gy + dy - py * 1.5, PAL["guard"], 1)
    line(c, gx + dx * 2, gy + dy * 2, gx + dx * BLADE, gy + dy * BLADE, PAL["blade"], 1)
    line(c, gx + dx * 2 + px, gy + dy * 2 + py, gx + dx * (BLADE - 2) + px, gy + dy * (BLADE - 2) + py,
         PAL["blade_d"], 1)


CHAR = {"pal": PAL, "body": "robe", "hem_up": 3, "head": head, "hair": hair, "neck": neck, "behind": cape,
        "held_back": sword_behind, "held": sword}


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
