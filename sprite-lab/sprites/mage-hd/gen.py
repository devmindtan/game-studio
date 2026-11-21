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
STAFF_UP = 22       # tay -> đỉnh thân trượng (trượng cao ngang người, chống từ sàn lên quá đầu)
STAFF_DOWN = 18     # tay -> đáy trượng (cắt bớt khi chạm sàn)
SLOPE = 3           # nghiêng về trước 1 cột mỗi 3 hàng: dốc 1:3 vẫn là đường pixel đều
STAFF = -90         # tư thế đứng: trượng dựng (nghiêng SLOPE); frame nằm dùng cùng góc rồi được xoay

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
    "magic": "#7ef0ff", "magic_mid": "#37b9e8", "magic_deep": "#8b5cf6", "core": "#effdff", "spark": "#b48cff",
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


def staff(c, p, g):
    """Trượng cao ngang người, nghiêng về trước dốc 1:3 (đường pixel đều), góc cố định ở mọi tư thế đứng.
    Thân gỗ 2 tông, chỗ cầm quấn da có 2 vòng vàng, đáy bọc kim loại; đầu trượng là hai chạc gỗ (màu gnarl)
    ôm viên pha lê hình thoi nhiều mặt có lõi sáng và đốm phép. p["weapon"] chỉ dùng ở frame nằm (xoay sẵn)."""
    hx, hy = g["hand_front"]
    top = None
    for k in range(-STAFF_DOWN, STAFF_UP + 1):
        y = hy - k
        x = hx + k // SLOPE
        if y > hd.SOLE - 1:
            continue
        if k <= -STAFF_DOWN + 1 or y >= hd.SOLE - 2:          # đáy bọc kim loại (2 px cuối)
            put(c, x, y, PAL["metal"])
            put(c, x + 1, y, PAL["metal_d"])
            continue
        col = PAL["wood"]
        if k in (-3, 3):
            col = PAL["ring"]                                  # vòng vàng
        elif -2 <= k <= 2:
            col = PAL["wrap"]                                  # quấn da chỗ cầm
        put(c, x, y, col)
        put(c, x + 1, y, PAL["wood_d"] if col == PAL["wood"] else col)
        top = (x, y)
    tx, ty = top

    def hp(dx, dy, col):
        """Pixel đầu trượng ở (dx, dy) so với đỉnh thân, nghiêng CÙNG dốc 1:SLOPE với thân (dy < 0 là lên)."""
        put(c, tx + dx + (-dy) // SLOPE, ty + dy, col)

    # hai chạc gỗ ôm pha lê
    for dx, dy in ((-1, -1), (-2, -2), (-3, -3), (-3, -4), (-3, -5), (-2, -7), (-1, -8)):
        hp(dx, dy, PAL["gnarl"])
    for dx, dy in ((2, -1), (3, -2), (4, -3), (4, -4), (4, -5), (3, -7), (2, -8)):
        hp(dx, dy, PAL["gnarl"])
    # quả cầu tròn 7x7 (tròn thì không cần nghiêng theo dốc): tâm đặt trên trục kéo dài của thân
    ox, oy = tx + 1 + 5 // SLOPE, ty - 5
    for dy in range(-3, 4):
        half = 2 if abs(dy) == 3 else 3
        for dx in range(-half, half + 1):
            if dx * dx + dy * dy > 11:
                continue
            col = PAL["magic_mid"]
            if dx + dy >= 3:
                col = PAL["magic_deep"]                         # bóng phía dưới-phải
            elif dx - dy >= 3 or (dx >= 1 and dy <= -1):
                col = PAL["magic"]                              # sáng phía trên-phải
            put(c, ox + dx, oy + dy, col)
    put(c, ox + 1, oy - 2, PAL["core"])
    put(c, ox + 2, oy - 1, PAL["core"])
    for dx, dy in ((-4, -11), (7, -9), (2, -16)):             # đốm phép (đặc, để ghép lớp khớp)
        hp(dx, dy, PAL["spark"])


def check_staff(min_gem=12):
    """Mọi frame đứng: thân trượng (wood + ring + wrap, cột trái nhất) là đường dốc 1:3 đều; quả cầu tròn 7x7 có tâm trên trục thân;
    quả cầu thấy được (>= min_gem px)."""
    from PIL import Image
    im = Image.open(HERE / f"{NAME}_strip.png").convert("RGBA")
    main = {hd._rgb(PAL[k]) for k in ("wood", "wrap", "ring")}
    gem = {hd._rgb(PAL[k]) for k in ("magic", "magic_mid", "magic_deep", "core")}
    bad = []
    for f in hd.standing_frames(ANIMATIONS):
        fr = im.crop((f * 64, 0, f * 64 + 64, 64)).load()
        rows = {}
        for y in range(64):
            xs = [x for x in range(64) if fr[x, y][3] and fr[x, y][:3] in main]
            if xs:
                rows[y] = [min(xs)]          # cột chính = pixel trái nhất (bên phải là cạnh tối/quấn)
        n_gem = sum(1 for y in range(64) for x in range(64) if fr[x, y][3] and fr[x, y][:3] in gem)
        # dốc đều kể cả khi tay che vài hàng: tồn tại pha phi và hằng c với x = c - (y + phi) // SLOPE
        ok = n_gem >= min_gem and len(rows) >= 10 and any(
            len({v[0] + (y + phi) // SLOPE for y, v in rows.items()}) == 1 for phi in range(SLOPE))
        if ok:
            # quả cầu tròn (khung bao vuông, mỗi hàng đối xứng quanh tâm) và tâm nằm trên trục kéo dài của thân
            # (bài học 2026-11-21: đầu vẽ lệch trục thân trông bị gãy)
            pts = [(x, y) for y in range(64) for x in range(64) if fr[x, y][3] and fr[x, y][:3] in gem]
            ys = [y for _, y in pts]
            bx = [x for x, _ in pts]
            by = ys
            w, h = max(bx) - min(bx) + 1, max(by) - min(by) + 1
            xc, yc = (max(bx) + min(bx)) / 2, (max(by) + min(by)) / 2
            phis = [phi for phi in range(SLOPE) if len({v[0] + (y + phi) // SLOPE for y, v in rows.items()}) == 1]
            axis = min(abs(xc - (rows[min(rows)][0] + (min(rows) + phi) // SLOPE - (yc + phi) / SLOPE))
                       for phi in phis) if phis else 99
            ok = w == h == 7 and axis <= 1.5
        if not ok:
            bad.append((f, n_gem))
    if bad:
        raise SystemExit(f"trượng không đều dốc 1:{SLOPE} hoặc mất pha lê ở frame (frame, px pha lê): {bad}")


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
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 3)),
              weapon=-135, eyes="x", flash=0.5, tilt=-1),
        frame(bob=3, lean=-1, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 6)), weapon=-135, eyes="x"),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 6)), weapon=-135, eyes="x", lie=0.4),
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
