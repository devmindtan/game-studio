#!/usr/bin/env python3
"""Generator cho sprite "mage": pháp sư nhìn nghiêng, quay phải, phong cách tối giản nhỏ gọn.

Frame 48x48, nhân vật cao khoảng 30 px tính cả mũ nhọn, neo (24, 44) giữa hai bàn chân trên mặt đất
(ground=True: mọi frame không phải nhảy phải chạm đất). Hình dựng từ tư thế bằng sprite-lab/lib/minifig.py,
áo choàng dài thay cho áo + quần. Dấu hiệu nhận diện: mũ nhọn tím viền vàng gập ra sau, râu trắng, gậy gỗ
với quả cầu xanh phát sáng.

Giữ từ bản trước: bảng màu, và chiêu "spell" theo nhịp nạp → căng → đẩy gậy → chớp ở đầu gậy → thu về.
Viên đạn bay (lúc bay, lúc nổ) là sprite riêng "arcane-bolt".

7 animation: idle 4, run 8, jump 4 (airborne), attack 5 (vung gậy), spell 7, hurt 3, death 5.
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

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402
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


def fx(c, p, g):
    """After the outline: orb glow, charge sparks, muzzle flash, swing arc."""
    top, _ = _staff_ends(p, g)
    ox, oy = round(top[0]), round(top[1]) - 1
    t = p["fx_t"]
    if p["fx"] in ("glow", "charge", "muzzle"):
        radius = {"glow": 2 + t, "charge": 3 + 2 * t, "muzzle": 4 + 2 * t}[p["fx"]]
        for r in range(2, int(radius) + 1):
            alpha = int(90 - 60 * (r - 2) / max(1, radius - 1))
            for deg in range(0, 360, 20):
                rad = math.radians(deg)
                put(c, ox + math.cos(rad) * r, oy + math.sin(rad) * r, (126, 240, 255, max(20, alpha)))
    if p["fx"] == "charge":
        for k in range(2 + round(4 * t)):
            ang = k * 1.9 + t * 4
            d = 7 - 3 * t
            put(c, ox + math.cos(ang) * d, oy + math.sin(ang) * d,
                (139, 92, 246, 230) if k % 2 else (126, 240, 255, 230))
    if p["fx"] == "muzzle":
        for k in range(1, 7):  # short beam forward from the orb
            put(c, ox + 1 + k, oy, (255, 255, 255, 240 - k * 25))
            if k < 4:
                put(c, ox + 1 + k, oy - 1, (126, 240, 255, 200 - k * 40))
                put(c, ox + 1 + k, oy + 1, (126, 240, 255, 200 - k * 40))
        for dx, dy in ((0, -3), (2, -2), (0, 3), (2, 2)):
            put(c, ox + dx, oy + dy, (255, 255, 255, 220))
    if p["fx"] == "swing":
        sx, sy = g["sh_front"]
        a0, a1 = -120, -120 + 130 * t
        for deg in range(int(a0), int(a1) + 1, 3):
            rad = math.radians(deg)
            for r, col in ((14, (126, 240, 255, 210)), (13, (139, 92, 246, 120))):
                put(c, sx + math.cos(rad) * r, sy + math.sin(rad) * r, col)


CHAR = {"pal": PAL, "body": "robe", "head": head, "held": staff, "fx": fx}


def frame(**kw):
    return mf.draw(CHAR, pose(**kw))


# --- animations (staff angle: direction hand -> orb; -90 = straight up) -----------------

def idle(i):
    return frame(bob=[0, 0, 1, 0][i], hands=((-2, 7), (6, 3)), weapon=-88, phase=i * 1.1,
                 fx="glow", fx_t=[0.3, 0.6, 0.3, 0.0][i], eyes="closed" if i == 3 else "open")


def run(i):
    p = run_pose(i, weapon=-62, fx="glow", fx_t=0.2)
    return mf.draw(CHAR, p)


def jump(i):
    return [
        frame(bob=2, feet=((-2, 0), (2, 0)), hands=((-3, 6), (3, 6)), weapon=-80, tilt=1),        # crouch
        frame(bob=-1, feet=((-2, 3), (2, 5)), hands=((-4, 2), (3, 1)), weapon=-100, tilt=-1,
              speed=0.7, phase=1.0, fx="glow", fx_t=0.6),                                         # rise
        frame(bob=0, feet=((-3, 2), (3, 1)), hands=((-4, 4), (4, 3)), weapon=-70, speed=0.8,
              phase=2.0),                                                                         # fall
        frame(bob=2, feet=((-4, 0), (4, 0)), hands=((-3, 6), (4, 5)), weapon=-75, tilt=1),       # land
    ][i]


ATTACK_MS = [150, 50, 70, 90, 150]


def attack(i):
    return [
        frame(bob=1, lean=-1, feet=((-4, 0), (3, 0)), hands=((-3, 5), (-1, 1)), weapon=-135, tilt=-1),
        frame(bob=0, lean=2, feet=((-4, 0), (4, 0)), hands=((-2, 6), (4, 1)), weapon=-55,
              fx="swing", fx_t=0.6),
        frame(bob=1, lean=3, feet=((-4, 0), (5, 0)), hands=((-2, 6), (6, 3)), weapon=-5,
              fx="swing", fx_t=1.0),
        frame(bob=1, lean=2, feet=((-4, 0), (5, 0)), hands=((-2, 7), (5, 4)), weapon=-20,
              fx="glow", fx_t=0.8),
        frame(bob=0, lean=1, feet=((-3, 0), (3, 0)), hands=((-2, 7), (6, 3)), weapon=-88),
    ][i]


SPELL_MS = [120, 120, 160, 60, 80, 120, 140]


def spell(i):
    """Charge -> tension -> push the staff -> flash at the orb (the bolt leaves) -> recover."""
    return [
        frame(bob=0, lean=-1, hands=((-3, 4), (2, 1)), weapon=-95, fx="charge", fx_t=0.2,
              eyes="closed"),
        frame(bob=-1, lean=-1, hands=((-4, 3), (2, -1)), weapon=-100, fx="charge", fx_t=0.6,
              eyes="closed", speed=0.3, phase=0.8),
        frame(bob=-1, lean=-2, feet=((-4, 0), (3, 0)), hands=((-4, 3), (1, -1)), weapon=-105,
              fx="charge", fx_t=1.0, speed=0.6, phase=1.6),
        frame(bob=1, lean=3, feet=((-5, 0), (5, 0)), hands=((-3, 6), (7, 1)), weapon=-25,
              fx="muzzle", fx_t=1.0, speed=0.6, phase=2.4),
        frame(bob=1, lean=3, feet=((-5, 0), (5, 0)), hands=((-3, 6), (7, 1)), weapon=-25,
              fx="muzzle", fx_t=0.3, speed=0.4, phase=3.0),
        frame(bob=0, lean=1, feet=((-4, 0), (4, 0)), hands=((-2, 6), (4, 3)), weapon=-55,
              fx="glow", fx_t=0.6),
        frame(bob=0, lean=0, hands=((-2, 7), (6, 3)), weapon=-88, fx="glow", fx_t=0.3),
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


# (name, frames, fps, loop, extra)
ANIMATIONS = [
    ("idle", [idle(i) for i in range(4)], 5, True, {"durations_ms": [240, 160, 240, 120]}),
    ("run", [run(i) for i in range(8)], 12, True, {}),
    ("jump", [jump(i) for i in range(4)], 10, False, {"airborne": True,
                                                       "durations_ms": [80, 160, 160, 100]}),
    ("attack", [attack(i) for i in range(5)], 14, False, {"durations_ms": ATTACK_MS}),
    ("spell", [spell(i) for i in range(7)], 12, False, {"durations_ms": SPELL_MS}),
    ("hurt", [hurt(i) for i in range(3)], 12, False, {"durations_ms": [90, 110, 120]}),
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [120, 140, 110, 100, 400]}),
]


def main() -> None:
    flat = [f for _, frames, _, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _, _ in ANIMATIONS)
    sheet = Canvas(cols * mf.W, len(ANIMATIONS) * mf.H)
    for row, (_, frames, _, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * mf.H)
    preview([sheet], HERE / "preview.png", scale=4, grid_lines=False)
    for name, frames, fps, _, _ in ANIMATIONS:
        gif(frames, HERE / f"{name}.gif", fps=fps, scale=4)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop, **extra}
                     for n, f, fps, loop, extra in ANIMATIONS],
                    anchor=ANCHOR, ground=True)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")


if __name__ == "__main__":
    main()
