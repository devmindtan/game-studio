#!/usr/bin/env python3
"""Generator cho "swordsman-hd": bản nâng cấp của swordsman, thân ~40 px trong khung 64x64 (người dùng 2026-11-21:
nhân vật 26 px quá ít chỗ cho chi tiết so với boss). Vẽ bằng sprite-lab/lib/hdfig.py.

Giữ nhận diện và tư thế của swordsman (cùng tham số pose, cùng animation idle 4, run 8, hurt 3, dash 5, death 5;
cùng palette), thêm chi tiết: tóc 3 tông có mái và chỏm, mắt có ánh + lông mày, tai, mũi, miệng; khăn đỏ to có
nút và tua; áo 3 tông có cổ chữ V, thắt lưng khoá, vạt áo xếp nếp; tay/chân gập khuỷu/gối; ủng có cổ, mũi, đế;
kiếm 16 px: lưỡi 2 tông, chắn kiếm vàng, chuôi quấn, núm.
Neo (32, 60), ground=True, vẽ theo lớp như swordsman. Chạy: gamekit art run swordsman-hd
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
from minifig import line, pose, put, rect, run_pose  # noqa: E402
from sheet import export_layered  # noqa: E402

NAME = "swordsman-hd"
ANCHOR = (float(hd.ROOT_X), float(hd.FLOOR))
BLADE = 16

PAL = {
    "skin": "#f2c49b", "skin_d": "#c98d6b",
    "hair": "#7a3f22", "hair_d": "#552a17", "hair_l": "#a8603a",
    "scarf": "#d94a4a", "scarf_d": "#9c2f3b", "scarf_l": "#f07a6a",
    "tunic": "#3f7fbf", "tunic_d": "#2c5a8c", "tunic_l": "#68a6dd",
    "sleeve": "#3f7fbf", "sleeve_d": "#2c5a8c",
    "belt": "#6b4a2b", "buckle": "#e8b84a",
    "pants": "#2d3550", "pants_d": "#1f2438",
    "boot": "#5a3a26", "boot_d": "#3e2819", "boot_l": "#7a5236",
    "blade": "#e8f0f6", "blade_d": "#9fb3c8", "guard": "#e8b84a", "guard_d": "#a8802f",
    "grip": "#6b4a2b", "grip_l": "#8a6440",
    "eye": "#1b1726", "eye_l": "#ffffff",
}


def hair(c, p, g):
    """Tóc nâu đỏ: chỏm, gáy dài, mái lởm chởm trước trán, 3 chỏm nhọn nghiêng theo tilt (ô đầu)."""
    hx, hy = g["head"]
    t = p["tilt"]
    rect(c, hx - 5, hy - 13, hx + 5, hy - 10, PAL["hair"])
    rect(c, hx - 5, hy - 10, hx - 2, hy - 3, PAL["hair"])
    rect(c, hx - 5, hy - 9, hx - 5, hy - 3, PAL["hair_d"])
    rect(c, hx - 4, hy - 4, hx - 3, hy - 3, PAL["hair_d"])
    for k, x in enumerate(range(hx + 1, hx + 6)):                 # mái: răng cưa
        rect(c, x, hy - 10, x, hy - 9 - (k % 2), PAL["hair"])
    for sx, sy in ((-6, -12), (-3 + t, -15), (1 + t, -15), (4 + t, -14)):   # chỏm
        rect(c, hx + sx, hy + sy, hx + sx + 1, hy + sy + 1, PAL["hair"])
    for x in (hx - 1, hx, hx + 2):                                 # ánh tóc
        put(c, x, hy - 12, PAL["hair_l"])
    put(c, hx + 3, hy - 11, PAL["hair_l"])


def neck(c, p, g):
    """Nút khăn quanh cổ (ô ngực)."""
    t = g["top"]
    rect(c, t[0] - 5, t[1] - 1, t[0] + 4, t[1] + 1, PAL["scarf"])
    rect(c, t[0] - 5, t[1] + 1, t[0] + 4, t[1] + 1, PAL["scarf_d"])
    rect(c, t[0] - 1, t[1] - 1, t[0] + 2, t[1] - 1, PAL["scarf_l"])
    rect(c, t[0] + 2, t[1] + 1, t[0] + 3, t[1] + 3, PAL["scarf"])   # mối nút rủ trước ngực
    put(c, t[0] + 3, t[1] + 3, PAL["scarf_d"])


def scarf_tail(c, p, g):
    """Đuôi khăn sau lưng: dải 3 px gợn sóng, dài và cao hơn khi chạy, có tua ở đầu."""
    t = g["top"]
    length = 6 + round(6 * p["speed"])
    x, y = t[0] - 5, t[1]
    for k in range(1, length + 1):
        wave = math.sin(p["phase"] + k * 0.7) * (0.8 + 1.2 * p["speed"])
        nx = t[0] - 5 - k
        ny = t[1] + round(wave) - round(k * 0.4 * (1 - p["speed"])) * -1
        line(c, x, y, nx, ny, PAL["scarf"], 3)
        put(c, nx, ny + 1, PAL["scarf_d"])
        x, y = nx, ny
    for d in (-1, 1):                                              # tua
        put(c, x - 2, y + d, PAL["scarf_d"])


def _points_back(p):
    return math.cos(math.radians(p["weapon"])) < -0.2


def sword_behind(c, p, g):
    if _points_back(p):
        _sword(c, p, g)


def sword(c, p, g):
    if not _points_back(p):
        _sword(c, p, g)


def _sword(c, p, g):
    hx, hy = g["hand_front"]
    a = math.radians(hd.keep_above_floor(hx, hy, p["weapon"], BLADE))
    dx, dy = math.cos(a), math.sin(a)
    px, py = -dy, dx
    gx, gy = hx + 0.5, hy + 0.5
    line(c, gx - dx * 3, gy - dy * 3, gx, gy, PAL["grip"], 2)                 # chuôi
    put(c, gx - dx * 2, gy - dy * 2, PAL["grip_l"])                           # quấn chuôi
    put(c, gx - dx * 4, gy - dy * 4, PAL["guard"])                            # núm
    line(c, gx + dx + px * 2.5, gy + dy + py * 2.5, gx + dx - px * 2.5, gy + dy - py * 2.5, PAL["guard"], 2)
    put(c, gx + dx + px * 2.5, gy + dy + py * 2.5, PAL["guard_d"])
    line(c, gx + dx * 3, gy + dy * 3, gx + dx * BLADE, gy + dy * BLADE, PAL["blade"], 2)
    line(c, gx + dx * 3 + px, gy + dy * 3 + py, gx + dx * (BLADE - 1) + px, gy + dy * (BLADE - 1) + py,
         PAL["blade_d"], 1)                                                    # mép tối
    put(c, gx + dx * (BLADE + 1), gy + dy * (BLADE + 1), PAL["blade"])        # mũi nhọn


CHAR = {"pal": PAL, "head": None, "hair": hair, "neck": neck, "behind": scarf_tail,
        "held_back": sword_behind, "held": sword}


def frame(**kw):
    return hd.draw_layers(CHAR, pose(**kw))


SWORD = 35   # góc cầm kiếm cố định cho mọi tư thế đứng: chúc mũi xuống phía trước, không bị thân che

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


def check_blade_visible(min_px=16):   # >= nửa lưỡi (16 px x 2)
    """Lưỡi kiếm phải nhìn thấy trong mọi frame đứng của strip cuối (death nằm xuống: bỏ qua).
    Bài học 2026-11-21: run cầm kiếm chĩa ra sau (205°) nên lưỡi nằm ở lớp sau lưng, bị thân che hết."""
    from PIL import Image
    im = Image.open(HERE / f"{NAME}_strip.png").convert("RGBA")
    blade = {tuple(int(PAL[k][i:i + 2], 16) for i in (1, 3, 5)) for k in ("blade", "blade_d")}
    skip, start = set(), 0
    for name, frames, *_ in ANIMATIONS:
        if name == "death":
            skip.update(range(start, start + len(frames)))
        elif name == "hurt":
            skip.add(start)                                   # frame nháy trắng
        start += len(frames)
    bad = []
    for f in range(im.width // 64):
        if f in skip:
            continue
        n = sum(1 for px in im.crop((f * 64, 0, f * 64 + 64, 64)).getdata() if px[3] and px[:3] in blade)
        if n < min_px:
            bad.append((f, n))
    if bad:
        raise SystemExit(f"lưỡi kiếm bị che ở frame (frame, số px): {bad}")


if __name__ == "__main__":
    export_layered(HERE, NAME, ANIMATIONS, anchor=ANCHOR, outline=hd.OUTLINE, ground=True, body="idle",
                   preview_scale=3, gif_scale=3)
    check_blade_visible()
    print(f"OK {NAME}")
