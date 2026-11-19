#!/usr/bin/env python3
"""Generator cho "wolf" (Sói Rừng): quái lao có báo trước của Rừng Âm U (Bách Ải 6A).

Chuẩn creature-v1 (sprite-lab/CREATURE_STANDARD.md), mô tả từng khung trong brief.json. Người dùng 2026-11-19:
bản cũ "đơ như tượng, chỉ có chân di chuyển". Bản này dựng từ bộ phận, mỗi khung một tư thế: hông và ngực
nhấp nhô lệch nhịp, đầu gật, đuôi vẫy trễ, lông gáy dựng dần khi gồng, hàm há/đớp.
Ngoại hình: sói thật (người dùng 2026-11-19: bản gai lưng "giống con quái vật"): tai nhọn to, mõm dài có khấc
trán, bờm lông cổ dựng khi gồng, đuôi xù, lông xám có yên lưng sẫm, má/bụng sáng, mắt hổ phách (lóe đỏ khi gồng).
Frame 48x32, quay phải, neo (24, 31) giữa chân trên đất. Chạy: gamekit art run wolf
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

from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = "wolf"
W, H = 48, 32
ANCHOR = (24.0, 31.0)
PAW_Y = 29                     # paws on this row; the outline adds the floor row 30
OUTLINE = "#0c0a10"
C = {"dark": "#3a3632", "fur": "#6e6860", "lit": "#9a948a", "tip": "#c8c2b6", "belly": "#d2ccbe",
     "saddle": "#4a4540", "mouth": "#a82830", "mouth_d": "#5a1418", "fang": "#f4ecdc", "eye": "#f0b030",
     "eye_hot": "#ff4a2a", "nose": "#141210"}


def clip(c):
    """Nothing below the paw row: thick strokes must not sink into the floor."""
    for yy in range(PAW_Y + 1, H):
        c.line(0, yy, W - 1, yy, (0, 0, 0, 0))
    return c


def ell(c, x, y, rx, ry, col):
    c.ellipse(round(x - rx), round(y - ry), round(x + rx), round(y + ry), col, fill=True)


def leg(c, jx, jy, paw_dx, lift, knee_dx, col, w=2, claw=True):
    kx, ky = jx + knee_dx, jy + (PAW_Y - jy) * 0.5
    px, py = jx + paw_dx, PAW_Y - lift
    c.line(round(jx), round(jy), round(kx), round(ky), col, w + 1)
    c.line(round(kx), round(ky), round(px), round(py), col, w)
    if claw and lift == 0:
        c.pixel(round(px) + 1, py, C["fang"])


def wolf(p):
    """p: pose dict (all optional): hip, chest (body dy), head_dx, head_dy, jaw (0..4), hackle (0..1),
    tail (deg up from straight back), legs [(paw_dx, lift, knee_dx) x4: back far, back near, front far,
    front near], dx (whole body), glow (eye flare), ears (0 back .. 2 pricked)."""
    c = Canvas(W, H)
    dx = p.get("dx", 0)
    hy, cy = 16 + p.get("hip", 0), 15 + p.get("chest", 0)   # body high: long legs under it
    hipx, chx = 15 + dx, 29 + dx
    legs = p.get("legs", [(-2, 0, 1), (0, 0, 1), (0, 0, 1), (2, 0, 1)])
    # far legs (darker, behind)
    leg(c, hipx - 1, hy + 2, legs[0][0], legs[0][1], legs[0][2], C["dark"], 2, False)
    leg(c, chx - 1, cy + 3, legs[2][0], legs[2][1], legs[2][2], C["dark"], 2, False)
    # tail: four segments, thick to thin, the tip lags (overlapping action)
    a0 = math.radians(180 - p.get("tail", 10))
    lag = math.radians(p.get("tail_lag", 12))
    x, y = hipx - 6, hy - 3
    for k, (ln, w) in enumerate(((3, 4), (3, 4), (3, 3), (2, 2))):   # bushy
        a = a0 + lag * k
        nx, ny = x + math.cos(a) * ln, y - math.sin(a) * ln
        c.line(round(x), round(y), round(nx), round(ny), C["fur"] if k < 3 else C["tip"], w)
        x, y = nx, ny
    c.pixel(round(x) - 1, round(y) - 1, C["tip"])
    # torso: hips, chest with a shoulder hump, joined
    ell(c, hipx, hy, 6, 3.5, C["fur"])                       # lean hips
    ell(c, chx, cy, 7, 4.5, C["fur"])                        # deep chest, shoulder hump
    c.polygon([(hipx, hy - 3), (chx, cy - 4), (chx - 2, cy + 4), (hipx + 2, hy + 2)], C["fur"])
    c.line(hipx + 3, hy + 3, chx - 3, cy + 4, C["belly"])      # tucked belly line
    ell(c, chx - 1, cy - 2, 4, 1.5, C["lit"])
    ell(c, hipx + 1, hy - 2, 3, 1, C["lit"])
    c.polygon([(hipx - 3, hy - 3), (chx - 2, cy - 4), (chx - 4, cy - 1), (hipx, hy - 1)], C["saddle"])   # dark saddle
    # neck ruff: a thick mane of fur at the shoulders; it rises in tufts when the wolf bristles
    hk = p.get("hackle", 0.15)
    for k, sx in enumerate(range(chx - 5, chx + 5)):
        base = cy - 4 + (1 if k < 2 else 0)
        h = round(1 + hk * (1.4 + (k * 5) % 3 * 0.5))
        c.line(sx, base, sx - 1 - round(h * 0.7), base - h, C["fur"] if k % 2 else C["lit"])   # tufts swept back
        if hk > 0.5 and k % 2 == 0:
            c.pixel(sx - 1 - round(h * 0.7), base - h, C["tip"])
    # near legs
    leg(c, hipx + 1, hy + 2, legs[1][0], legs[1][1], legs[1][2], C["fur"])
    leg(c, chx + 1, cy + 3, legs[3][0], legs[3][1], legs[3][2], C["fur"])
    # head: low and forward from the chest
    hx, hdy = chx + 8 + p.get("head_dx", 0), cy + 1 + p.get("head_dy", 0)
    c.polygon([(chx + 2, cy - 4), (hx - 1, hdy - 3), (hx, hdy + 2), (chx + 4, cy + 2)], C["fur"])   # neck
    ell(c, hx, hdy, 4.5, 3.5, C["fur"])
    ell(c, hx - 1, hdy - 2, 3, 1.2, C["lit"])
    ell(c, hx, hdy + 2, 3, 1.3, C["belly"])                  # pale cheek
    ears = p.get("ears", 1)
    # big pointed ears: pricked up when alert, laid back when snarling
    tipx, tipy = (hx - 1, hdy - 8) if ears >= 1 else (hx - 6, hdy - 5)
    c.polygon([(hx - 3, hdy - 2), (tipx, tipy), (hx + 1, hdy - 3)], C["fur"])
    c.line(hx - 2, hdy - 3, tipx, tipy + 2, C["dark"])           # inner ear
    c.pixel(tipx, tipy, C["dark"])
    # jaws: upper snout, lower jaw opens by `jaw`
    jaw = p.get("jaw", 1)
    c.polygon([(hx + 2, hdy - 2), (hx + 4, hdy - 1), (hx + 9, hdy), (hx + 2, hdy + 1)], C["fur"])   # muzzle with a stop
    c.line(hx + 4, hdy - 1, hx + 8, hdy, C["lit"])
    c.pixel(hx + 9, hdy, C["nose"])
    if jaw > 0:
        c.polygon([(hx + 2, hdy + 1), (hx + 7, hdy + 1), (hx + 2, hdy + 1 + jaw)], C["mouth"])
        c.pixel(hx + 3, hdy + 1 + max(0, jaw - 1), C["mouth_d"])
    c.polygon([(hx + 1, hdy + 1 + jaw), (hx + 6, hdy + 1 + jaw), (hx + 1, hdy + 3 + jaw)], C["dark"])    # lower jaw
    c.pixel(hx + 6, hdy + 1, C["fang"])                       # upper fang
    c.pixel(hx + 3, hdy + 1, C["fang"])
    if jaw > 1:
        c.pixel(hx + 5, hdy + jaw, C["fang"])                 # lower fang
    # eye: red, flares hot when it is about to strike
    c.pixel(hx + 2, hdy - 1, C["eye_hot"] if p.get("glow") else C["eye"])
    c.pixel(hx + 1, hdy - 2, C["dark"])                       # brow over the eye: a scowl
    c.pixel(hx + 2, hdy - 2, C["dark"])
    if p.get("glow"):
        c.pixel(hx + 3, hdy - 1, "#ff8a5a")
    return clip(c).outline(OUTLINE)


def flash(c, amount=0.7):
    px = c.img.load()
    for yy in range(c.height):
        for xx in range(c.width):
            r, g, b, a = px[xx, yy]
            if a and (r, g, b) != (0x0c, 0x0a, 0x10):
                px[xx, yy] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                              round(b + (255 - b) * amount), a)
    return c


def lying(dy=0, fade=0.0):
    """Fallen on its side: body low and long, legs sticking out forward, jaw slack."""
    c = Canvas(W, H)
    by = 25 + dy
    for k, x0 in enumerate((14, 17, 28, 31)):
        c.line(x0, by + 2, x0 + 5, PAW_Y, C["dark"] if k % 2 == 0 else C["fur"], 2)
    ell(c, 21, by, 13, 4, C["fur"])
    ell(c, 21, by - 2, 10, 1.5, C["lit"])
    c.line(8, by, 3, by + 2, C["fur"], 2)
    ell(c, 37, by + 1, 4, 3, C["fur"])
    c.polygon([(39, by), (45, by + 2), (39, by + 3)], C["fur"])
    c.pixel(44, by + 3, C["mouth"])
    c.line(37, by, 39, by, C["dark"])           # eye shut
    c = clip(c).outline(OUTLINE)
    if fade:
        px = c.img.load()
        for yy in range(c.height):
            for xx in range(c.width):
                if px[xx, yy][3] and (xx * 3 + yy) % 5 < round(fade * 5):
                    px[xx, yy] = (0, 0, 0, 0)
    return c


L = lambda *t: list(t)   # noqa: E731
# rotary gallop, 8 keys: hips and chest rock out of phase, head nods, tail lags (brief.json says each)
RUN = [
    dict(hip=0, chest=0, head_dy=0, tail=12, legs=L((-6, 1, -1), (-5, 0, -1), (6, 2, 2), (7, 1, 2))),
    dict(hip=0, chest=1, head_dy=1, tail=8, legs=L((-4, 2, 0), (-5, 1, -1), (6, 1, 2), (4, 0, 1))),
    dict(hip=-1, chest=2, head_dy=2, tail=2, legs=L((-1, 3, 1), (-3, 2, 0), (2, 0, 1), (0, 0, 0))),
    dict(hip=-1, chest=1, head_dy=1, tail=-4, legs=L((3, 2, 2), (1, 1, 1), (-1, 0, 0), (-3, 1, -1))),
    dict(hip=1, chest=-1, head_dy=0, tail=-8, legs=L((4, 0, 2), (2, 0, 1), (-5, 2, -1), (-3, 3, -1))),
    dict(hip=0, chest=-2, head_dy=-1, tail=-4, legs=L((0, 0, 1), (-2, 0, 0), (2, 3, 1), (4, 2, 2))),
    dict(hip=-1, chest=-2, head_dy=-2, tail=4, legs=L((-4, 1, -1), (-5, 0, -1), (5, 2, 2), (6, 1, 2))),
    dict(hip=-1, chest=-1, head_dy=-1, tail=10, legs=L((-6, 0, -1), (-6, 2, -1), (6, 2, 2), (7, 2, 2))),
]
STAND = L((-2, 0, 1), (0, 0, 1), (0, 0, 1), (2, 0, 1))
CROUCH = L((-3, 0, 3), (-1, 0, 3), (-1, 0, 3), (1, 0, 3))
ATTACK = [
    dict(head_dx=-1, head_dy=2, hackle=0.4, jaw=1, ears=2, tail=15, legs=STAND),
    dict(chest=1, head_dy=2, hackle=1.0, jaw=2, glow=True, ears=0, tail=30, tail_lag=4, legs=STAND),
    dict(hip=2, chest=3, head_dy=3, hackle=1.0, jaw=2, glow=True, ears=0, tail=35, tail_lag=2, legs=CROUCH),
    dict(hip=-2, chest=-3, head_dx=3, head_dy=-1, hackle=0.8, jaw=4, glow=True, ears=0, tail=10,
         legs=L((-7, 1, -1), (-7, 0, -1), (7, 2, 2), (8, 2, 2))),
    dict(hip=-1, chest=0, head_dx=3, head_dy=1, hackle=0.8, jaw=0, ears=0, tail=5,
         legs=L((-5, 0, -1), (-4, 0, 0), (5, 0, 2), (6, 0, 2))),
    dict(hip=0, chest=1, head_dx=1, hackle=0.6, jaw=1, ears=1, tail=8, legs=L((-3, 0, 0), (-1, 0, 1), (2, 0, 1), (3, 0, 1))),
    dict(hip=0, chest=1, head_dy=1, hackle=0.3, jaw=1, ears=1, tail=10, legs=STAND),
]
HURT = [
    dict(dx=-1, head_dx=-2, head_dy=-2, jaw=2, ears=0, hackle=0.5, tail=25, legs=STAND),
    dict(dx=-2, chest=-1, head_dx=-3, head_dy=-3, jaw=3, ears=0, hackle=0.6, tail=30, legs=L((-3, 0, 0), (-1, 0, 0), (-1, 1, 0), (1, 0, 1))),
    dict(dx=-1, head_dy=0, jaw=1, ears=1, hackle=0.3, tail=12, legs=STAND),
]

HB = {"shape": "rect", "center": [24.0, 31.0]}
ANIMATIONS = [
    ("move", [wolf({**p, "hackle": 0.3, "jaw": 1, "ears": 1}) for p in RUN], 12, True,
     {"durations_ms": [70, 80, 90, 80, 70, 80, 90, 80], "hitbox": {**HB, "active": [0, 7]}}),
    ("attack", [wolf(p) for p in ATTACK], 12, False,
     {"durations_ms": [120, 160, 220, 80, 120, 120, 140], "hitbox": {**HB, "active": [3, 4]}}),
    ("hurt", [flash(wolf(HURT[0])), wolf(HURT[1]), wolf(HURT[2])], 12, False,
     {"durations_ms": [70, 110, 120], "hitbox": {**HB, "active": [0, 2]}}),
    ("death", [flash(wolf(dict(head_dy=-3, head_dx=-1, jaw=3, ears=0, tail=30, hackle=0.6, legs=STAND)), 0.5),
               wolf(dict(hip=3, chest=4, head_dy=4, jaw=2, ears=0, tail=-10, hackle=0.3, legs=CROUCH)),
               lying(-1), lying(-2), lying(0), lying(0, 0.5)], 10, False,
     {"durations_ms": [100, 140, 110, 90, 260, 300], "hitbox": {**HB, "active": [0, 5]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, body="move", preview_scale=5, gif_scale=4)
    print(f"OK {NAME}")
