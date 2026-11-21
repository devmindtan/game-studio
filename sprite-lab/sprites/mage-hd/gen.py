#!/usr/bin/env python3
"""Generator cho "mage-hd": bản nâng cấp của mage, thân ~40 px trong khung 64x64 (vẽ bằng lib/hdfig.py).

Giữ nhận diện của mage: mũ nhọn tím viền vàng gập ra sau, râu trắng, áo choàng tím dài, gậy gỗ với quả cầu xanh
phát sáng. Chi tiết thêm: mũ 3 tông có ngôi sao, dải vàng 2 hàng và vành rộng; râu dài tới ngực có lọn và
bóng; áo choàng dài chấm cổ ủng (hdfig robe_len="long") có viền tím nhạt; gậy thẳng đứng CỐ ĐỊNH (90°, đường
pixel sạch như kiếm của swordsman-hd), quả cầu 5x5 có lõi trắng và đốm sáng.
Animation như mage: idle 4, run 8, hurt 3, dash 5, death 5 (phép là sprite hiệu ứng riêng).
Neo (32, 60), ground=True, vẽ theo lớp. Chạy: gamekit art run mage-hd
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

NAME = "mage-hd"
ANCHOR = (float(hd.ROOT_X), float(hd.FLOOR))
TILT = math.degrees(math.atan(1 / 3))   # ~18.4°: đỉnh trượng ngả về trước, góc cố định ở mọi tư thế đứng
STAFF = -90                              # tư thế đứng; frame nằm đặt góc khác, độ xoay = weapon + 90 + TILT

PAL = {   # của mage, thêm bậc tối/sáng
    "hat": "#4a2a7a", "hat_d": "#301f58", "hat_l": "#6d47ad",
    "gold": "#f0cd72", "gold_d": "#a8802f",
    "robe": "#5b3a96", "robe_d": "#3a2370", "robe_l": "#8a63cc", "trim": "#c9a4f2",
    "tunic_l": "#8a63cc",
    "sleeve": "#5b3a96", "sleeve_d": "#3a2370",
    "belt": "#a8802f", "buckle": "#f0cd72",
    "skin": "#f3cea6", "skin_d": "#cf9c73",
    "hair_d": "#b8b5cf",
    "beard": "#eceaf5", "beard_d": "#b8b5cf",
    "wood": "#8a5a2e", "wood_d": "#563418", "gnarl": "#6e4424",
    "wrap": "#5a2f3a", "ring": "#e2bd5e", "metal": "#9aa6b8", "metal_d": "#5c6678",
    "boot": "#4a3157", "boot_d": "#2b1a33", "boot_l": "#6a4a7a",
    "pants": "#3a2a4a", "pants_d": "#241630",
    "magic": "#7ef0ff", "magic_mid": "#37b9e8", "magic_deep": "#3b6fd0", "core": "#effdff",
    "eye": "#140d20", "eye_l": "#ffffff",
}

# Mũ 17 cột, quay phải; cột 8 nằm giữa đầu, hàng cuối là vành. d bóng, h mũ, L viền sáng, G dải vàng,
# g bóng dải, s sao (thoi rỗng, không phải dấu +: dấu + trông như thánh giá).
# Frame nằm (lie) được xoay 90°: gậy -90° ở đó sẽ nằm ngang sau khi xoay.
HAT_KEYS = {"d": "hat_d", "h": "hat", "L": "hat_l", "G": "gold", "g": "gold_d", "s": "gold"}
HAT_REST = [
    "..dh.............",
    "...dh............",
    "....dhL..........",
    ".....dhL.........",
    ".....dhhL........",
    "....dhhhhL.......",
    "....dhhhhhL......",
    "...dhhhshhhL.....",
    "...dhhshshhhL....",
    "..dhhhhshhhhhL...",
    "..gGGGGGGGGGGGg..",
    "..gGGGGGGGGGGGg..",
    "ddhhhhhhhhhhhhhhL",
]
HAT_WIND = [
    "dh...............",
    ".ddh.............",
    "...ddhL..........",
    ".....dhL.........",
    ".....dhhL........",
    "....dhhhhL.......",
    "....dhhhhhL......",
    "...dhhhshhhL.....",
    "...dhhshshhhL....",
    "..dhhhhshhhhhL...",
    "..gGGGGGGGGGGGg..",
    "..gGGGGGGGGGGGg..",
    "ddhhhhhhhhhhhhhhL",
]


def beard(c, p, g):
    """Râu trắng từ má xuống ngực, nhọn dần, có lọn tối; đung đưa theo chuyển động (lớp nền, vẽ đè lên mặt)."""
    hx, hy = g["head"]
    sway = round(math.sin(p["phase"]) * 0.8 * p["speed"])
    rows = [(-1, 5), (-1, 5), (-1, 5), (0, 5), (0, 4), (1, 4), (1, 3), (2, 3)]
    for k, (x0, x1) in enumerate(rows):
        y = hy - 4 + k
        dx = sway if k > 3 else 0
        rect(c, hx + x0 + dx, y, hx + x1 + dx, y, PAL["beard"])
        if k > 1:
            put(c, hx + x0 + dx, y, PAL["beard_d"])
        if k in (3, 5):
            put(c, hx + 2 + dx, y, PAL["beard_d"])                           # lọn râu
    rect(c, hx + 2, hy - 4, hx + 4, hy - 4, PAL["beard_d"])                  # ria
    rect(c, hx - 4, hy - 9, hx - 3, hy - 3, PAL["beard_d"])                  # tóc bạc sau tai


def hat(c, p, g):
    """Mũ nhọn (ô đầu): bản đồ pixel, gió/lùi thì chóp bay ra sau."""
    hx, hy = g["head"]
    rows = HAT_WIND if (p["speed"] >= 0.5 or p["tilt"] < 0) else HAT_REST
    for r, row in enumerate(rows):
        y = hy - 10 - (len(rows) - 1 - r)
        for col, ch in enumerate(row):
            if ch != ".":
                put(c, hx - 8 + col, y, PAL[HAT_KEYS[ch]])


def staff_template():
    """Trượng vẽ MỘT LẦN thẳng đứng (11 x 42), điểm neo = chỗ tay cầm (5, 25). Từ trên xuống: quả cầu tròn 7x7
    (sáng trên-phải, bóng dưới-trái, đốm sáng), hai chạc gỗ ôm hai bên cầu, nối vào thân ở hàng 9; thân gỗ 2 tông;
    vòng vàng - quấn da - vòng vàng quanh chỗ cầm; đáy bọc kim loại."""
    from PIL import Image
    w, h = 11, 42
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    def px(x, y, key):
        img.putpixel((x, y), hd._rgb(PAL[key]) + (255,))

    cx, cy = 5, 4
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dx * dx + dy * dy > 11:
                continue
            key = "magic_mid"
            if dx - dy <= -3 or (dx <= -1 and dy >= 1):
                key = "magic_deep"
            elif dx - dy >= 2:
                key = "magic"
            px(cx + dx, cy + dy, key)
    px(cx + 1, cy - 2, "core")
    px(cx + 2, cy - 1, "core")
    for x, y in ((1, 2), (1, 3), (1, 4), (1, 5), (2, 6), (2, 7), (3, 8), (4, 8),   # chạc trái
                 (9, 2), (9, 3), (9, 4), (9, 5), (8, 6), (8, 7), (7, 8), (6, 8),   # chạc phải
                 (0, 1), (10, 1)):                                                 # mũi chạc cong ra
        px(x, y, "gnarl")
    for y in range(9, h):
        if y >= h - 2:
            px(5, y, "metal")
            px(6, y, "metal_d")
        elif y in (22, 28):
            px(5, y, "ring")
            px(6, y, "ring")
        elif 23 <= y <= 27:
            px(5, y, "wrap")
            px(6, y, "wrap")
        else:
            px(5, y, "wood")
            px(6, y, "wood_d")
    return img


STAFF_TPL = staff_template()
STAFF_ANCHOR = (5, 25)


def staff(c, p, g):
    """Đặt điểm neo của trượng vào bàn tay trước và xoay cả khối (hd.held_sprite)."""
    hd.held_sprite(c, STAFF_TPL, STAFF_ANCHOR, g["hand_front"], p["weapon"] + 90 + TILT)


def check_staff(min_orb=30):
    """Mọi frame đứng: lớp vũ khí là MỘT khối liền (không mảnh rời như đốm phép trôi, chạc rời quả cầu), quả cầu
    tròn (khung bao vuông 7x7) và thấy được (>= min_orb px trong ảnh cuối). Bài học 2026-11-21: trượng nắn tay
    từng phần (thân theo dốc, chạc kéo xéo, cầu thẳng) lệch nhau; giờ vẽ một lần rồi xoay quanh điểm neo."""
    from PIL import Image
    pieces = hd.weapon_pieces(HERE / "layers/weapon_strip.png", ANIMATIONS)
    im = Image.open(HERE / f"{NAME}_strip.png").convert("RGBA")
    orb = {hd._rgb(PAL[k]) for k in ("magic", "magic_mid", "magic_deep", "core")}
    bad = []
    for f in hd.standing_frames(ANIMATIONS):
        fr = im.crop((f * 64, 0, f * 64 + 64, 64)).load()
        pts = [(x, y) for y in range(64) for x in range(64) if fr[x, y][3] and fr[x, y][:3] in orb]
        if pts:
            w = max(x for x, _ in pts) - min(x for x, _ in pts) + 1
            h = max(y for _, y in pts) - min(y for _, y in pts) + 1
        else:
            w = h = 0
        if pieces[f] != 1 or len(pts) < min_orb or abs(w - h) > 1:
            bad.append((f, pieces[f], len(pts), (w, h)))
    if bad:
        raise SystemExit(f"trượng hỏng (frame, số mảnh, px cầu, khung cầu): {bad}")


CHAR = {"pal": PAL, "body": "robe", "robe_len": "long", "head": beard, "hair": hat, "held": staff}


def frame(**kw):
    return hd.draw_layers(CHAR, pose(**kw))


# --- animations: di chuyển và trạng thái (phép là sprite hiệu ứng riêng) --------------------------

def idle(i):
    return frame(bob=[0, 0, 1, 0][i], hands=((-2, 7), (6, 3)), weapon=STAFF, phase=i * 1.1,
                 eyes="closed" if i == 3 else "open")


def run(i):
    return hd.draw_layers(CHAR, run_pose(i, weapon=STAFF, hands=((-2, 6), (5, 3))))


def dash(i):
    return [
        frame(bob=2, lean=1, feet=((-4, 0), (3, 0)), hands=((-3, 5), (5, 4)), weapon=STAFF, speed=0.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-6, 4), (4, 4)), weapon=STAFF, speed=1.0, phase=0.6),
        frame(bob=2, lean=3, feet=((-7, 2), (5, 0)), hands=((-7, 3), (4, 4)), weapon=STAFF, speed=1.0, phase=1.4),
        frame(bob=2, lean=3, feet=((-6, 1), (5, 0)), hands=((-7, 4), (4, 4)), weapon=STAFF, speed=1.0, phase=2.2),
        frame(bob=1, lean=1, feet=((-3, 0), (3, 0)), hands=((-2, 6), (5, 3)), weapon=STAFF, speed=0.5, phase=3.0),
    ][i]


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (4, 3)),
              weapon=STAFF, eyes="wince", flash=0.75, speed=0.6, tilt=-1),
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 4), (4, 3)),
              weapon=STAFF, eyes="wince", speed=0.4, phase=1.0, tilt=-1),
        frame(bob=0, lean=0, hands=((-2, 7), (6, 3)), weapon=STAFF),
    ][i]


def death(i):
    # ngã ngửa: trượng ngả RA TRƯỚC, xa mặt (-135° ngả ra sau làm quả cầu đè lên mặt). Frame nằm (lie) được
    # xoay nguyên khối 90° ngược chiều kim đồng hồ: trượng dựng (-90°) trước khi xoay sẽ nằm dọc theo người.
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 3)),
              weapon=-30, eyes="x", flash=0.5, tilt=-1),
        frame(bob=3, lean=-1, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 6)), weapon=-30, eyes="x"),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 6)), weapon=-60, eyes="x", lie=0.4),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 6)), weapon=-90, eyes="x", lie=0.85),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 6)), weapon=-90, eyes="x", lie=1.0),
    ][i]


HB = {"shape": "rect", "center": [32.0, 60.0]}
ANIMATIONS = [
    ("idle", [idle(i) for i in range(4)], 5, True, {"durations_ms": [240, 160, 240, 120], "hitbox": {**HB, "active": [0, 3]}}),
    ("run", [run(i) for i in range(8)], 12, True, {"hitbox": {**HB, "active": [0, 7]}}),
    ("hurt", [hurt(i) for i in range(3)], 12, False, {"durations_ms": [90, 110, 120], "hitbox": {**HB, "active": [0, 2]}}),
    ("dash", [dash(i) for i in range(5)], 14, False, {"durations_ms": [60, 50, 70, 70, 90], "hitbox": {**HB, "active": [0, 4]}}),
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [120, 140, 110, 100, 400], "hitbox": {**HB, "active": [0, 4]}}),
]


if __name__ == "__main__":
    export_layered(HERE, NAME, ANIMATIONS, anchor=ANCHOR, outline=hd.OUTLINE, ground=True, body="idle",
                   preview_scale=3, gif_scale=3)
    check_staff()
    print(f"OK {NAME}")
