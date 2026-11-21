#!/usr/bin/env python3
"""Generator cho "archer": nữ xạ thủ nhìn nghiêng, quay phải (trái = lật) — phương án C trong
sprite-lab/designs/archer/variants.py (người dùng chọn 2026-11-21).

Cách cầm cung theo tham khảo LPC `body/bodies/female/shoot.png` + `weapon/ranged/bow/recurve/universal/shoot`:
tay trước nắm GIỮA thân cung, lưng cung về phía mục tiêu, dây cung phía người. Dáng luôn sẵn sàng: tay trước
duỗi ra trước ngang ngực, cung dựng, tay sau giữ hờ dây. Dấu hiệu: tóc xanh xám bím ngắn, áo xanh, giáp vai bạc,
cung bạc.

Chuẩn như swordsman: 48x48, neo (24, 44), ground=True, vẽ THEO LỚP (minifig.LAYERS) để mặc đồ;
idle 4, run 8, hurt 3, dash 5, death 5. Bắn tên là sprite hiệu ứng riêng (không vẽ vào thân).
Chạy:  gamekit art run archer  ·  thử: gamekit art shot archer sheet|move
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
from minifig import RUN_FEET, line, pose, put, rect  # noqa: E402
from sheet import export_layered  # noqa: E402

NAME = "archer"
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))
HALF = 7            # nửa chiều dài cung (cung cao 15 px, thân người ~26 px)

PAL = {
    "skin": "#f2d0b4", "skin_d": "#c99a80", "lip": "#a8505a", "eye": "#1b1726",
    "hair": "#4a4a6a", "hair_d": "#2e2e45", "hair_l": "#6e6e94",
    "tunic": "#3f5f9c", "tunic_d": "#2b4170", "tunic_l": "#6488c8",
    "sleeve": "#3f5f9c", "sleeve_d": "#2b4170", "belt": "#2b2b3a", "buckle": "#cfd6e0",
    "pants": "#2b2b3a", "pants_d": "#1e1e29", "boot": "#3a3448", "boot_d": "#26222f",
    "pad": "#b8c2d0", "pad_d": "#7c8698",
    "wood": "#dde3ec", "wood_d": "#8a94a6", "string": "#a6b0c0",
}


def head(c, p, g):
    """Mặt và mắt (lớp nền)."""
    hx, hy = g["head"]
    rect(c, hx - 3, hy - 6, hx + 4, hy, PAL["skin"])
    put(c, hx - 3, hy, PAL["skin_d"])
    mf.eyes(c, hx + 2, hy - 4, p["eyes"], PAL)
    put(c, hx + 3, hy - 1, PAL["lip"])


def hair(c, p, g):
    """Tóc ôm đầu, mái nghiêng theo tilt, bím ngắn rủ sau gáy (ô đầu)."""
    hx, hy = g["head"]
    tilt = p["tilt"]
    rect(c, hx - 4, hy - 8, hx + 4, hy - 7, PAL["hair"])
    rect(c, hx - 4, hy - 7, hx - 2, hy - 2, PAL["hair"])
    put(c, hx + 1 + tilt, hy - 8, PAL["hair_l"])
    sway = round(math.sin(p["phase"]) * p["speed"])
    for k in range(4):
        x = hx - 4 - (sway if k >= 2 else 0) - round(k * 0.4 * p["speed"])
        put(c, x, hy - 1 + k, PAL["hair"] if k % 2 == 0 else PAL["hair_d"])
        put(c, x - 1, hy - 1 + k, PAL["hair_d"] if k % 2 == 0 else PAL["hair"])


def pad(c, p, g):
    """Giáp vai bạc trên vai trước (lớp front)."""
    s = g["sh_front"]
    rect(c, s[0] - 1, s[1] - 1, s[0] + 2, s[1], PAL["pad"])
    put(c, s[0] - 1, s[1], PAL["pad_d"])


def _bow(c, cx, cy, facing_deg, depth, pull):
    """Cung nắm tại (cx, cy); facing_deg = hướng LƯNG cung (0 về trước); hai đầu lùi `depth` về phía người;
    dây nối hai đầu qua điểm `pull` (tay sau) hoặc thẳng nếu pull=None."""
    f = math.radians(facing_deg)
    fx, fy = math.cos(f), math.sin(f)
    ax, ay = -fy, fx
    pts = []
    for k in range(-HALF, HALF + 1):
        t = k / HALF
        back = depth * t * t
        x, y = cx + 0.5 + ax * k - fx * back, cy + 0.5 + ay * k - fy * back
        pts.append((x, min(y, mf.SOLE - 1.5)))               # không xuyên sàn
    for a, b in zip(pts, pts[1:]):
        line(c, a[0], a[1], b[0], b[1], PAL["wood"], 1)
    put(c, round(pts[0][0] - fx), round(pts[0][1] - fy), PAL["wood_d"])
    put(c, round(pts[-1][0] - fx), round(pts[-1][1] - fy), PAL["wood_d"])
    put(c, cx, cy, PAL["wood_d"])
    top, bot = pts[0], pts[-1]
    if pull:
        line(c, top[0], top[1], pull[0], pull[1], PAL["string"], 1)
        line(c, pull[0], pull[1], bot[0], bot[1], PAL["string"], 1)
    else:
        line(c, top[0], top[1], bot[0], bot[1], PAL["string"], 1)


def bow(c, p, g):
    """p["weapon"] = hướng lưng cung (0 = sẵn sàng về trước). Cung cong 4 px để dây (thẳng giữa hai đầu) tách
    khỏi thân cung một khe; cong 2 px thì dây dính sát thân cung, chỉ thấy khi cung xoay (bài học 2026-11-21)."""
    hx, hy = g["hand_front"]
    _bow(c, hx, hy, p["weapon"], 4, None)


CHAR = {"pal": PAL, "body": "tunic", "head": head, "hair": hair, "held": bow, "front": pad}


def frame(**kw):
    kw.setdefault("weapon", 0)
    return mf.draw_layers(CHAR, pose(**kw))


READY = ((3, 3), (7, 2))     # tay sau sát dây, tay trước duỗi ra trước


# --- animations: di chuyển và trạng thái (bắn tên là sprite hiệu ứng riêng) ----------------------

def idle(i):
    return frame(bob=[0, 0, 1, 0][i], lean=1, feet=((-4, 0), (3, 0)), hands=READY, phase=i * 1.1,
                 eyes="closed" if i == 3 else "open")


def run(i):
    (fdx, fl), (bdx, bl) = RUN_FEET[i]
    return frame(bob=[0, 1, 0, -1, 0, 1, 0, -1][i], lean=3, feet=((bdx, bl), (fdx, fl)), hands=READY,
                 phase=i * math.pi / 4, speed=1.0)


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-3, 4), (3, 5)), weapon=30,
              eyes="wince", flash=0.75, speed=0.5, tilt=-1),
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-3, 5), (3, 5)), weapon=30,
              eyes="wince", speed=0.3, phase=1.0, tilt=-1),
        frame(bob=0, lean=1, feet=((-4, 0), (3, 0)), hands=READY),
    ][i]


def dash(i):
    """Lướt: lấy đà, phóng, hai frame lướt (cung kéo ra sau như vật bị gió đẩy), thu về tư thế sẵn sàng."""
    return [
        frame(bob=2, lean=1, feet=((-4, 0), (3, 0)), hands=((2, 4), (5, 4)), weapon=20, speed=0.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-3, 4), (3, 4)), weapon=60, speed=1.0, phase=0.6),
        frame(bob=2, lean=3, feet=((-7, 2), (5, 0)), hands=((-4, 3), (2, 4)), weapon=70, speed=1.0, phase=1.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-3, 4), (3, 4)), weapon=60, speed=1.0, phase=2.2),
        frame(bob=1, lean=1, feet=((-4, 0), (3, 0)), hands=READY, speed=0.5, phase=3.0),
    ][i]


def death(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (2, 5)), weapon=40,
              eyes="x", flash=0.5, tilt=-1),
        frame(bob=3, lean=-1, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), weapon=80, eyes="x"),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), weapon=90, eyes="x", lie=0.4),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), weapon=90, eyes="x", lie=0.85),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), weapon=90, eyes="x", lie=1.0),
    ][i]


HB = {"shape": "rect", "center": [24.0, 44.0]}
ANIMATIONS = [
    ("idle", [idle(i) for i in range(4)], 5, True, {"durations_ms": [240, 160, 240, 120], "hitbox": {**HB, "active": [0, 3]}}),
    ("run", [run(i) for i in range(8)], 12, True, {"hitbox": {**HB, "active": [0, 7]}}),
    ("hurt", [hurt(i) for i in range(3)], 12, False, {"durations_ms": [90, 110, 120], "hitbox": {**HB, "active": [0, 2]}}),
    ("dash", [dash(i) for i in range(5)], 14, False, {"durations_ms": [60, 50, 70, 70, 90], "hitbox": {**HB, "active": [0, 4]}}),
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [120, 140, 110, 100, 400], "hitbox": {**HB, "active": [0, 4]}}),
]


def check_string_visible(strip_path, min_px=4):
    """Dây cung phải nhìn thấy trong MỌI frame của strip cuối (sau khi ghép lớp + viền).
    Bài học 2026-11-21: cung cong 2 px nên dây nằm sát thân cung, bị viền nuốt; chỉ hiện khi dash."""
    from PIL import Image
    im = Image.open(strip_path).convert("RGBA")
    rgb = lambda h: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))  # noqa: E731
    want, wood = rgb(PAL["string"]), {rgb(PAL["wood"]), rgb(PAL["wood_d"])}
    # frame nháy trắng (frame đầu hurt/death, flash > 0) đổi mọi màu: không kiểm
    skip, start = set(), 0
    for name, frames, *_ in ANIMATIONS:
        if name in ("hurt", "death"):
            skip.add(start)
        start += len(frames)
    bad = []
    for f in range(im.width // 48):
        if f in skip:
            continue
        fr = im.crop((f * 48, 0, f * 48 + 48, 48)).load()
        woods = [(x, y) for y in range(48) for x in range(48) if fr[x, y][3] and fr[x, y][:3] in wood]
        n = 0
        for y in range(48):
            for x in range(48):
                if fr[x, y][3] and fr[x, y][:3] == want and \
                        all(max(abs(x - wx), abs(y - wy)) >= 2 for wx, wy in woods):
                    n += 1      # có khe (>= 1 px) giữa dây và thân cung theo mọi hướng = mắt thấy hai nét
        if n < min_px:
            bad.append((f, n))
    if bad:
        raise SystemExit(f"dây cung không thấy ở frame (frame, số px): {bad}")


if __name__ == "__main__":
    export_layered(HERE, NAME, ANIMATIONS, anchor=ANCHOR, outline=mf.OUTLINE, ground=True, body="idle",
                   preview_scale=4, gif_scale=4)
    check_string_visible(HERE / f"{NAME}_strip.png")
    print(f"OK {NAME}")
