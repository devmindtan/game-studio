#!/usr/bin/env python3
"""Generator cho sprite "swordsman": kiếm sĩ nhìn nghiêng, quay phải (trái = lật), phong cách tối giản nhỏ gọn.

Frame 48x48, nhân vật cao khoảng 26 px, neo (24, 44) giữa hai bàn chân trên mặt đất (ground=True: art run
kiểm tra mọi frame chạm đất). Hình dựng từ tư thế bằng sprite-lab/lib/minifig.py.
Dấu hiệu nhận diện: khăn quàng đỏ bay theo chuyển động, kiếm bạc chuôi vàng.

Bách Ải chỉ cần di chuyển hai hướng trái/phải; đòn đánh là sprite hiệu ứng riêng (sword-slash), nên nhân
vật chỉ có: idle 4, run 8, hurt 3, death 5.

Vẽ theo LỚP để mặc giáp sau này (minifig.LAYERS): cape_back (đuôi khăn), leg_*/boot_*, arm_*/hand_*,
torso, neck (nút khăn), head (da, mắt), hair, weapon_back/weapon (kiếm). Mỗi lớp ghi ra
layers/<lớp>_strip.png (không viền); swordsman_strip.png = các lớp ghép lại + viền, check_layers kiểm tra
trùng từng pixel. Đồ mặc sau này vẽ lại đúng lớp của ô trang bị bằng cùng các tư thế ở đây.
Chạy:  gamekit art run swordsman  ·  thử: gamekit art shot swordsman sheet|move
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

NAME = "swordsman"
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))
BLADE = 10          # blade length in px (body is ~26 px tall)

PAL = {
    "skin": "#f2c49b", "skin_d": "#c98d6b",
    "hair": "#7a3f22", "hair_l": "#a8603a",
    "scarf": "#d94a4a", "scarf_d": "#9c2f3b",
    "tunic": "#3f7fbf", "tunic_d": "#2c5a8c", "tunic_l": "#68a6dd",
    "sleeve": "#3f7fbf", "sleeve_d": "#2c5a8c",
    "belt": "#6b4a2b", "buckle": "#e8b84a",
    "pants": "#2d3550", "pants_d": "#1f2438",
    "boot": "#5a3a26", "boot_d": "#3e2819",
    "blade": "#e8f0f6", "blade_d": "#9fb3c8", "guard": "#e8b84a", "grip": "#6b4a2b",
    "eye": "#1b1726",
}


def neck(c, p, g):
    """Scarf knot round the neck, under the chin (chest slot)."""
    t = g["top"]
    rect(c, t[0] - 3, t[1], t[0] + 3, t[1] + 1, PAL["scarf"])
    put(c, t[0] + 2, t[1] + 1, PAL["scarf_d"])


def head(c, p, g):
    """Face block and eyes (skin layer)."""
    hx, hy = g["head"]
    rect(c, hx - 3, hy - 6, hx + 4, hy, PAL["skin"])
    put(c, hx - 3, hy, PAL["skin_d"])
    mf.eyes(c, hx + 2, hy - 4, p["eyes"], PAL)


def hair(c, p, g):
    """Cap, back of the head, three spikes that follow the tilt (head-gear slot)."""
    hx, hy = g["head"]
    tilt = p["tilt"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 6, PAL["hair"])
    rect(c, hx - 4, hy - 6, hx - 2, hy - 2, PAL["hair"])
    put(c, hx + 4, hy - 6, PAL["hair"])                      # fringe over the brow
    for sx, sy in ((-5, -7), (-2 + tilt, -9), (1 + tilt, -9)):
        put(c, hx + sx, hy + sy, PAL["hair"])
    put(c, hx, hy - 8, PAL["hair_l"])
    put(c, hx + 1, hy - 8, PAL["hair_l"])


def scarf_tail(c, p, g):
    """Behind the body: the scarf end trails back and waves, longer and higher when moving."""
    t = g["top"]
    length = 4 + round(4 * p["speed"])
    x, y = t[0] - 3, t[1] + 1
    for k in range(1, length + 1):
        wave = math.sin(p["phase"] + k * 0.9) * (0.6 + 0.9 * p["speed"])
        nx = t[0] - 3 - k
        ny = t[1] + 1 + round(wave) - round(k * 0.35 * (1 - p["speed"]))
        line(c, x, y, nx, ny, PAL["scarf"] if k < length else PAL["scarf_d"], 2)
        x, y = nx, ny


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


CHAR = {"pal": PAL, "body": "tunic", "head": head, "hair": hair, "neck": neck, "behind": scarf_tail,
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
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [120, 140, 110, 100, 400], "hitbox": {"shape":"rect","center":[24.0,44.0],"active":[0,4]}}),
]


if __name__ == "__main__":
    export_layered(HERE, NAME, ANIMATIONS, anchor=ANCHOR, outline=mf.OUTLINE, ground=True, body="idle",
                   preview_scale=4, gif_scale=4)
    print(f"OK {NAME}")
