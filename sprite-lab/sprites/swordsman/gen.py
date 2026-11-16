#!/usr/bin/env python3
"""Generator cho sprite "swordsman": kiếm sĩ nhìn nghiêng, quay phải, phong cách tối giản nhỏ gọn.

Frame 48x48, nhân vật cao khoảng 26 px, neo (24, 44) giữa hai bàn chân trên mặt đất (ground=True: mọi
frame không phải nhảy phải chạm đất, art run kiểm tra). Hình dựng từ tư thế bằng sprite-lab/lib/minifig.py.
Dấu hiệu nhận diện: khăn quàng đỏ bay theo chuyển động (chuyển động phụ), kiếm bạc chuôi vàng.

7 animation: idle 4, run 8, jump 4 (airborne), attack 5 (giữ frame không đều: lấy đà lâu, chém nhanh),
spell 6 (giơ kiếm tụ sức rồi đâm), hurt 3, death 5.
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

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402
import minifig as mf  # noqa: E402
from minifig import line, pose, put, rect, run_pose  # noqa: E402

NAME = "swordsman"
OUT = HERE
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


def head(c, p, g):
    hx, hy = g["head"]
    t = g["top"]
    # scarf knot round the neck, under the chin
    rect(c, t[0] - 3, t[1], t[0] + 3, t[1] + 1, PAL["scarf"])
    put(c, t[0] + 2, t[1] + 1, PAL["scarf_d"])
    # head block
    rect(c, hx - 3, hy - 6, hx + 4, hy, PAL["skin"])
    put(c, hx - 3, hy, PAL["skin_d"])
    # hair: cap, back of the head, three spikes that follow the tilt
    tilt = p["tilt"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 6, PAL["hair"])
    rect(c, hx - 4, hy - 6, hx - 2, hy - 2, PAL["hair"])
    put(c, hx + 4, hy - 6, PAL["hair"])                      # fringe over the brow
    for sx, sy in ((-5, -7), (-2 + tilt, -9), (1 + tilt, -9)):
        put(c, hx + sx, hy + sy, PAL["hair"])
    put(c, hx, hy - 8, PAL["hair_l"])
    put(c, hx + 1, hy - 8, PAL["hair_l"])
    mf.eyes(c, hx + 2, hy - 4, p["eyes"], PAL)


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


def fx(c, p, g):
    """Effects after the outline: slash arc, charge sparkle, thrust flash."""
    sx, sy = g["sh_front"]
    if p["fx"] == "slash":
        # arc from up-back to down-forward; t grows the visible part
        a0, a1 = -110, -110 + 160 * p["fx_t"]
        for r, col in ((13, (235, 250, 255, 230)), (12, (150, 220, 255, 150)), (11, (150, 220, 255, 70))):
            for deg in range(int(a0), int(a1) + 1, 3):
                rad = math.radians(deg)
                put(c, sx + math.cos(rad) * r, sy + math.sin(rad) * r, col)
    elif p["fx"] == "charge":
        hx, hy = g["hand_front"]
        a = math.radians(p["weapon"])
        tipx, tipy = hx + math.cos(a) * BLADE, hy + math.sin(a) * BLADE
        n = 2 + round(3 * p["fx_t"])
        for k in range(n):
            ang = k * 2 * math.pi / n + p["fx_t"] * 3
            put(c, tipx + math.cos(ang) * 3, tipy + math.sin(ang) * 3, (255, 240, 150, 220))
        put(c, tipx, tipy, (255, 255, 255, 255))
    elif p["fx"] == "thrust":
        hx, hy = g["hand_front"]
        for k in range(4, 16):
            alpha = 220 - k * 12
            put(c, hx + 2 + k, hy, (255, 245, 180, max(40, alpha)))
            if k % 3 == 0:
                put(c, hx + 2 + k, hy - 1, (255, 255, 255, max(40, alpha)))
                put(c, hx + 2 + k, hy + 1, (255, 255, 255, max(40, alpha)))


CHAR = {"pal": PAL, "body": "tunic", "head": head, "behind": scarf_tail, "held_back": sword_behind,
        "held": sword, "fx": fx}


def frame(**kw):
    return mf.draw(CHAR, pose(**kw))


# --- animations -------------------------------------------------------------------

def idle(i):
    bob = [0, 0, 1, 0][i]
    return frame(bob=bob, hands=((-2, 7), (3, 5)), weapon=20, phase=i * 1.2,
                 eyes="closed" if i == 3 else "open")


def run(i):
    p = run_pose(i, weapon=205 + 8 * math.sin(i * math.pi / 4))
    return mf.draw(CHAR, p)


def jump(i):
    return [
        frame(bob=2, feet=((-2, 0), (2, 0)), hands=((-3, 6), (3, 7)), weapon=60, tilt=-1),        # crouch
        frame(bob=-1, feet=((-2, 3), (2, 5)), hands=((-4, 2), (3, 1)), weapon=-40, tilt=1,
              speed=0.6, phase=1.0),                                                               # rise
        frame(bob=0, feet=((-3, 2), (3, 1)), hands=((-4, 4), (4, 3)), weapon=10, speed=0.8,
              phase=2.2),                                                                          # fall
        frame(bob=2, feet=((-4, 0), (4, 0)), hands=((-3, 6), (4, 6)), weapon=70, tilt=-1),        # land
    ][i]


ATTACK_MS = [140, 50, 60, 90, 150]   # long wind-up, fast swing, hold the hit, settle


def attack(i):
    return [
        frame(bob=1, lean=-1, feet=((-4, 0), (3, 0)), hands=((-3, 5), (-1, -3)), weapon=-120),
        frame(bob=0, lean=2, feet=((-4, 0), (4, 0)), hands=((-2, 6), (5, 0)), weapon=-25,
              fx="slash", fx_t=0.5),
        frame(bob=1, lean=3, feet=((-4, 0), (5, 0)), hands=((-2, 6), (6, 4)), weapon=40,
              fx="slash", fx_t=1.0),
        frame(bob=1, lean=2, feet=((-4, 0), (5, 0)), hands=((-2, 7), (4, 6)), weapon=80),
        frame(bob=0, lean=1, feet=((-3, 0), (3, 0)), hands=((-2, 7), (3, 5)), weapon=20),
    ][i]


SPELL_MS = [120, 120, 140, 60, 80, 160]


def spell(i):
    return [
        frame(bob=1, lean=-1, hands=((-3, 4), (1, -5)), weapon=-90, fx="charge", fx_t=0.2,
              head=(0, -1)),
        frame(bob=1, lean=-1, hands=((-3, 4), (1, -6)), weapon=-90, fx="charge", fx_t=0.6,
              head=(0, -1)),
        frame(bob=2, lean=-2, feet=((-5, 0), (3, 0)), hands=((-4, 5), (-1, 1)), weapon=-10,
              fx="charge", fx_t=1.0, eyes="closed"),
        frame(bob=0, lean=3, feet=((-5, 0), (6, 0)), hands=((-3, 6), (7, 2)), weapon=0,
              fx="thrust", speed=0.8, phase=2.0),
        frame(bob=0, lean=3, feet=((-5, 0), (6, 0)), hands=((-3, 6), (7, 2)), weapon=0,
              speed=0.5, phase=2.8),
        frame(bob=0, lean=1, feet=((-3, 0), (3, 0)), hands=((-2, 7), (3, 5)), weapon=20),
    ][i]


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


# (name, frames, fps, loop, extra)
ANIMATIONS = [
    ("idle", [idle(i) for i in range(4)], 5, True, {"durations_ms": [240, 160, 240, 120]}),
    ("run", [run(i) for i in range(8)], 12, True, {}),
    ("jump", [jump(i) for i in range(4)], 10, False, {"airborne": True,
                                                       "durations_ms": [80, 160, 160, 100]}),
    ("attack", [attack(i) for i in range(5)], 14, False, {"durations_ms": ATTACK_MS}),
    ("spell", [spell(i) for i in range(6)], 12, False, {"durations_ms": SPELL_MS}),
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
                    anchor=ANCHOR, ground=True, body="idle")
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")


if __name__ == "__main__":
    main()
