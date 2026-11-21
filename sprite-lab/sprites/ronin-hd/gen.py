#!/usr/bin/env python3
"""Generator cho "ronin-hd": bản nâng cấp của ronin, thân ~40 px trong khung 64x64 (vẽ bằng lib/hdfig.py).

Giữ nhận diện của ronin (concept/103 cũ): áo khoác dài xanh than tới gối, áo choàng đỏ thẫm sau lưng bay theo
tốc độ, búi tóc đen buộc dây đỏ, kiếm dài thép. Chi tiết thêm: búi tóc có ánh + dây buộc, tóc mai; cổ áo choàng
có nếp; áo choàng rộng dần có 2 nếp gấp và gấu tối; áo khoác 3 tông, vạt trước mở, đai vải rủ; kiếm 16 px bám
lưới ở góc cố định 45° (như swordsman-hd). Animation và tư thế như swordsman-hd.
Neo (32, 60), ground=True, vẽ theo lớp. Chạy: gamekit art run ronin-hd
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

import hdfig as hd  # noqa: E402
from minifig import pose, put, rect, run_pose  # noqa: E402
from sheet import export_layered  # noqa: E402

NAME = "ronin-hd"
ANCHOR = (float(hd.ROOT_X), float(hd.FLOOR))
BLADE = 16          # 11 bước chéo: dài hơn thì chạm sàn khi tay thấp, kiếm bị xoay khỏi 45°

PAL = {   # của ronin, thêm bậc tối/sáng cho bản chi tiết
    "skin": "#e7a986", "skin_d": "#b8765e",
    "hair": "#2f2730", "hair_d": "#1d171e", "hair_l": "#5a4560",
    "cape": "#8e3636", "cape_d": "#5e2328", "cape_l": "#b4503f",
    "robe": "#46506a", "robe_d": "#323a4e", "robe_l": "#6c7894", "trim": "#2a3042",
    "tunic_l": "#6c7894",
    "sleeve": "#46506a", "sleeve_d": "#323a4e",
    "belt": "#644831", "buckle": "#b0b2b4",
    "pants": "#323746", "pants_d": "#23262f",
    "boot": "#7a4e34", "boot_d": "#4f3222", "boot_l": "#9a6644",
    "blade": "#e2e6ea", "blade_d": "#8f9092", "guard": "#8f9092", "guard_d": "#5f6064",
    "grip": "#523747", "grip_l": "#8e3636",
    "eye": "#1b1726", "eye_l": "#ffffff",
}


def hair(c, p, g):
    """Tóc đen ôm đầu, tóc mai, búi tó trên đỉnh có dây buộc đỏ, nghiêng theo tilt (ô đầu)."""
    hx, hy = g["head"]
    t = p["tilt"]
    rect(c, hx - 5, hy - 12, hx + 5, hy - 10, PAL["hair"])
    rect(c, hx - 5, hy - 10, hx - 2, hy - 2, PAL["hair"])
    rect(c, hx - 5, hy - 9, hx - 5, hy - 2, PAL["hair_d"])
    rect(c, hx + 2, hy - 10, hx + 5, hy - 10, PAL["hair"])                # mái gọn
    put(c, hx - 1, hy - 3, PAL["hair"])                                     # tóc mai
    put(c, hx - 1, hy - 2, PAL["hair_d"])
    for x in (hx - 2, hx, hx + 2):
        put(c, x, hy - 12, PAL["hair_l"])
    bx = hx - 1 + t                                                          # búi tròn (bo góc)
    rect(c, bx - 1, hy - 16, bx + 1, hy - 16, PAL["hair"])
    rect(c, bx - 2, hy - 15, bx + 2, hy - 14, PAL["hair"])
    put(c, bx - 2, hy - 14, PAL["hair_d"])
    put(c, bx, hy - 16, PAL["hair_l"])
    put(c, bx + 1, hy - 15, PAL["hair_l"])
    rect(c, bx - 1, hy - 13, bx + 1, hy - 13, PAL["cape"])                  # dây buộc đỏ
    put(c, bx - 2, hy - 13, PAL["cape_d"])
    put(c, bx - 3, hy - 12, PAL["cape_d"])                                  # đuôi dây buộc


def neck(c, p, g):
    """Cổ áo choàng đỏ quanh vai, có nếp (ô ngực)."""
    t = g["top"]
    rect(c, t[0] - 6, t[1] - 1, t[0] + 3, t[1] + 2, PAL["cape"])
    rect(c, t[0] - 6, t[1] + 2, t[0] + 3, t[1] + 2, PAL["cape_d"])
    rect(c, t[0] - 2, t[1] - 1, t[0] + 2, t[1] - 1, PAL["cape_l"])
    put(c, t[0] - 3, t[1], PAL["cape_d"])                                   # nếp
    put(c, t[0], t[1] + 1, PAL["cape_d"])


def cape(c, p, g):
    """Áo choàng đỏ sau lưng: từ vai rủ tới gối, rộng dần, 2 nếp gấp dọc, gấu tối; chạy thì bay ra sau, gợn."""
    t = g["top"]
    length = 18 + round(3 * p["speed"])
    for k in range(length):
        back = round(k * (0.25 + 0.6 * p["speed"]))
        wave = round(math.sin(p["phase"] + k * 0.6) * 1.2 * p["speed"])
        x1 = t[0] - 2 - back
        y = t[1] + k - round(k * 0.5 * p["speed"]) + wave
        w = 4 + min(5, k // 3)
        rect(c, x1 - w + 1, y, x1, y, PAL["cape"])
        put(c, x1 - w + 1, y, PAL["cape_d"])
        if k > 3:
            put(c, x1 - w // 2, y, PAL["cape_d"])                              # nếp gấp
        if k < 6:
            put(c, x1 - 1, y, PAL["cape_l"])                                   # ánh gần vai
        if k >= length - 2:
            rect(c, x1 - w + 1, y, x1, y, PAL["cape_d"])                       # gấu


def _points_back(p):
    return math.cos(math.radians(p["weapon"])) < -0.2


def sword_behind(c, p, g):
    if _points_back(p):
        _sword(c, p, g)


def sword(c, p, g):
    if not _points_back(p):
        _sword(c, p, g)


def _sword(c, p, g):
    hd.grid_sword(c, g["hand_front"], p["weapon"], BLADE, PAL)


CHAR = {"pal": PAL, "body": "robe", "head": None, "hair": hair, "neck": neck, "behind": cape,
        "held_back": sword_behind, "held": sword}


def frame(**kw):
    return hd.draw_layers(CHAR, pose(**kw))


SWORD = 45   # góc cầm kiếm cố định (bội số 45°: đường pixel sạch) cho mọi tư thế đứng: chúc mũi xuống phía trước, không bị thân che

# --- animations: movement and state only (attacks are effect sprites) -------------

def idle(i):
    bob = [0, 0, 1, 0][i]
    return frame(bob=bob, hands=((-2, 7), (3, 5)), weapon=SWORD, phase=i * 1.2,
                 eyes="closed" if i == 3 else "open")


def run(i):
    """Chạy: kiếm giữ nguyên góc SWORD, chỉ đi theo tay (người dùng 2026-11-21: kiếm không cần tự chuyển động)."""
    return hd.draw_layers(CHAR, run_pose(i, weapon=SWORD))


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 4)),
              weapon=SWORD, eyes="wince", flash=0.75, speed=0.5),
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 4), (1, 5)),
              weapon=SWORD, eyes="wince", speed=0.3, phase=1.0),
        frame(bob=0, lean=0, hands=((-2, 7), (3, 5)), weapon=SWORD),
    ][i]


def dash(i):
    """Dash (2026-11-17, for the dash skill): wind-up, launch, two glide frames, recover.
    Feet stay on the floor (ground=True); the body leans hard, arms and sword trail back,
    the scarf flies out at full speed."""
    return [
        frame(bob=2, lean=1, feet=((-4, 0), (3, 0)), hands=((-3, 5), (3, 5)), weapon=SWORD, speed=0.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-6, 4), (-1, 5)), weapon=SWORD, speed=1.0, phase=0.6),
        frame(bob=2, lean=3, feet=((-7, 2), (5, 0)), hands=((-7, 3), (-2, 4)), weapon=SWORD, speed=1.0, phase=1.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-7, 4), (-2, 5)), weapon=SWORD, speed=1.0, phase=2.2),
        frame(bob=1, lean=1, feet=((-3, 0), (3, 0)), hands=((-2, 6), (3, 5)), weapon=SWORD, speed=0.5, phase=3.0),
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
    ("idle", [idle(i) for i in range(4)], 5, True, {"durations_ms": [240, 160, 240, 120], "hitbox": {"shape":"rect","center":[32.0,60.0],"active":[0,3]}}),
    ("run", [run(i) for i in range(8)], 12, True, {"hitbox": {"shape":"rect","center":[32.0,60.0],"active":[0,7]}}),
    ("hurt", [hurt(i) for i in range(3)], 12, False, {"durations_ms": [90, 110, 120], "hitbox": {"shape":"rect","center":[32.0,60.0],"active":[0,2]}}),
    ("dash", [dash(i) for i in range(5)], 14, False, {"durations_ms": [60, 50, 70, 70, 90], "hitbox": {"shape":"rect","center":[32.0,60.0],"active":[0,4]}}),
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [120, 140, 110, 100, 400], "hitbox": {"shape":"rect","center":[32.0,60.0],"active":[0,4]}}),
]


if __name__ == "__main__":
    export_layered(HERE, NAME, ANIMATIONS, anchor=ANCHOR, outline=hd.OUTLINE, ground=True, body="idle",
                   preview_scale=3, gif_scale=3)
    hd.check_blade(HERE / f"{NAME}_strip.png", ANIMATIONS, PAL, BLADE, angle=SWORD)
    print(f"OK {NAME}")
