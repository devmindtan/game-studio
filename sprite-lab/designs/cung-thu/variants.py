#!/usr/bin/env python3
"""Cung thủ (class thứ 3 của Bách Ải, nội tại Mắt ưng): 3 phương án để người dùng chọn (pixel-sprite bước 0, 2026-11-23).

Tham khảo (2026-11-23, tìm web): Elthen "Royal Archer" 32x32 (idle/move/shoot), kiendko "Medieval Pixel Characters"
(idle 5 / run 10 / attack 9), pixollie "Archer Pixel Art" (idle 4 / walk 8).
  Học: cung là phần silhouette dễ đọc nhất; ống tên sau lưng cho biết vai trò ngay cả khi đứng yên; idle 4, run 8.
  Tránh: chép sheet nào; kiểu yêu tinh tai nhọn quen thuộc (thế giới game là mới).
  Quyết định: 3 phương án khác silhouette, vũ khí, dáng và nhịp; minifig 48x48 như Kiếm sĩ / Pháp sư.

  A "Thợ săn" : mũ trùm xanh lá, cung ngắn cầm dọc phía trước, ống tên sau lưng; chạy nảy nhẹ.
  B "Nỏ thủ"  : mũ da, khăn đỏ, nỏ cầm ngang hông; đứng vững, chạy chắc.
  C "Du hiệp" : tóc đuôi ngựa, áo chẽn sáng, cung dài vác chéo sau lưng (cao hơn người); sải dài, nghiêng người.
Mỗi phương án: idle 4 + run 8 + tư thế bắn.  Chạy: python3 sprite-lab/designs/cung-thu/variants.py
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parents[2]
sys.path.insert(0, str(WS / "tools/gamekit/pipeline"))
sys.path.insert(0, str(WS / "sprite-lab/lib"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import minifig as mf  # noqa: E402
from minifig import RUN_FEET, line, pose, put, rect  # noqa: E402


def face(pal):
    def head(c, p, g):
        hx, hy = g["head"]
        rect(c, hx - 3, hy - 6, hx + 4, hy, pal["skin"])
        put(c, hx - 3, hy, pal["skin_d"])
        mf.eyes(c, hx + 2, hy - 4, p["eyes"], pal)
    return head


def straight(c, x, y, dx, dy, n, col):
    """Straight item in integer steps (clean 0/45/90° angles only)."""
    for k in range(n):
        put(c, x + dx * k, y + dy * k, col)


# --- A: Thợ săn ------------------------------------------------------------------------------------
PA = {"skin": "#f0c4a0", "skin_d": "#c98f72", "eye": "#1b1726", "hair": "#6a4a2a",
      "tunic": "#4f7a3a", "tunic_d": "#36572a", "tunic_l": "#6f9a4e", "sleeve": "#4f7a3a", "sleeve_d": "#36572a",
      "belt": "#6a4a2a", "buckle": "#e0b250", "pants": "#6a5a44", "pants_d": "#4a3e2e",
      "boot": "#4a3222", "boot_d": "#2e1f15", "wood": "#a8743e", "wood_d": "#6e4a24", "string": "#e8e2d0",
      "quiver": "#7a4f2e", "feather": "#e8e2d0"}


def a_hood(c, p, g):   # mũ trùm nhọn đổ ra sau
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 6, PA["tunic"])
    rect(c, hx - 5, hy - 6, hx - 3, hy - 2, PA["tunic_d"])
    put(c, hx - 6, hy - 5, PA["tunic_d"])
    put(c, hx + 4, hy - 7, PA["tunic_l"])


def a_quiver(c, p, g):  # ống tên chéo sau lưng, đầu lông trắng
    sx, sy = g["hip"]
    for k in range(8):                        # leans back past the shoulder blade: visible behind the back
        put(c, sx - 5 - k // 3, sy - 1 - k, PA["quiver"])
        put(c, sx - 4 - k // 3, sy - 1 - k, PA["quiver"])
    for fx_, fy_ in ((-8, -10), (-7, -11), (-9, -11)):
        put(c, sx + fx_, sy + fy_, PA["feather"])


def a_bow(c, p, g):     # cung ngắn dọc phía trước tay; bắn: dây kéo về sau
    hx, hy = g["hand_front"]
    for k in range(-6, 7):
        put(c, hx + 1 + (2 if abs(k) < 3 else (1 if abs(k) < 5 else 0)), hy + k, PA["wood"])
    put(c, hx + 1, hy - 6, PA["wood_d"])
    put(c, hx + 1, hy + 6, PA["wood_d"])
    pull = 3 if p["fx"] == "shoot" else 0
    for k in range(-5, 6):
        put(c, hx + 1 - (pull * (5 - abs(k)) // 5), hy + k, PA["string"])
    if p["fx"] == "shoot":
        straight(c, hx - 2, hy, 1, 0, 9, PA["wood_d"])
        put(c, hx + 7, hy, "#d8e0ea")


A = {"pal": PA, "body": "tunic", "head": face(PA), "hair": a_hood, "behind": a_quiver, "held": a_bow}


def a_idle(i):
    return pose(bob=[0, 0, 1, 1][i], feet=((-3, 0), (4, 0)), hands=((-1, 6), (4, 3)), phase=i * 0.8,
                eyes="closed" if i == 3 else "open")


def a_run(i):
    return mf.run_pose(i, bob=[0, 1, -1, -2, 0, 1, -1, -2][i], hands=((-1, 5), (4, 3)))


def a_hit():
    return pose(lean=0, feet=((-5, 0), (4, 0)), hands=((0, 3), (6, 2)), fx="shoot")


# --- B: Nỏ thủ -----------------------------------------------------------------------------------
PB = {"skin": "#d9a77e", "skin_d": "#a8775a", "eye": "#1b1726", "hair": "#2a2230",
      "tunic": "#7a5a3a", "tunic_d": "#5a4028", "tunic_l": "#9a7650", "sleeve": "#5a4a3a", "sleeve_d": "#3e3226",
      "belt": "#2a2230", "buckle": "#c0c8d0", "pants": "#3b3a48", "pants_d": "#2a2a36",
      "boot": "#2a2230", "boot_d": "#1b1726", "wood": "#8a5a30", "wood_d": "#5a3a1e", "steel": "#c0c8d0",
      "scarf": "#c23b32", "cap": "#6a4a2a"}


def b_cap(c, p, g):   # mũ da tròn + khăn đỏ quanh cổ bay
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 4, hy - 6, PB["cap"])
    put(c, hx + 5, hy - 6, PB["cap"])
    for k in range(3):
        put(c, hx - 4 - k, hy + 1 + round(math.sin(p["phase"] + k) * p["speed"]), PB["scarf"])


def b_xbow(c, p, g):  # nỏ ngang hông: báng gỗ + cánh thép dọc ở đầu
    hx, hy = g["hand_front"]
    straight(c, hx - 4, hy, 1, 0, 10, PB["wood"])
    put(c, hx - 4, hy + 1, PB["wood_d"])
    for k in range(-3, 4):
        put(c, hx + 5, hy + k, PB["steel"])
    if p["fx"] == "shoot":
        straight(c, hx + 6, hy, 1, 0, 6, "#d8e0ea")


B = {"pal": PB, "body": "tunic", "head": face(PB), "hair": b_cap, "held": b_xbow}


def b_idle(i):
    return pose(bob=[1, 1, 2, 1][i], feet=((-5, 0), (5, 0)), hands=((1, 6), (4, 6)), phase=i * 0.8,
                eyes="closed" if i == 2 else "open")


def b_run(i):
    (fdx, fl), (bdx, bl) = RUN_FEET[i]
    return pose(bob=[1, 1, 0, 0, 1, 1, 0, 0][i], lean=1, feet=((bdx - 1, bl), (fdx + 1, fl)),
                hands=((1, 6), (4, 6)), phase=i * math.pi / 4, speed=0.9)


def b_hit():
    return pose(lean=-1, feet=((-6, 0), (4, 0)), hands=((2, 4), (5, 4)), fx="shoot")


# --- C: Du hiệp ----------------------------------------------------------------------------------
PC = {"skin": "#f0c4a0", "skin_d": "#c98f72", "eye": "#1b1726", "hair": "#c26a2a",
      "tunic": "#d8cfb0", "tunic_d": "#a89e80", "tunic_l": "#f0e8cc", "sleeve": "#2f5f6e", "sleeve_d": "#1f4050",
      "belt": "#2f5f6e", "buckle": "#e0b250", "pants": "#2f5f6e", "pants_d": "#1f4050",
      "boot": "#5a3d28", "boot_d": "#3d2919", "wood": "#c08a4a", "wood_d": "#7a5228", "string": "#e8e2d0"}


def c_hair(c, p, g):   # tóc đuôi ngựa cam, bay theo nhịp
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 6, PC["hair"])
    rect(c, hx - 4, hy - 6, hx - 3, hy - 4, PC["hair"])
    for k in range(4):
        put(c, hx - 5 - k, hy - 6 + k // 2 + round(math.sin(p["phase"] + k * 0.6) * p["speed"]), PC["hair"])


def c_longbow(c, p, g):  # cung dài vác chéo sau lưng; bắn: cầm dọc trước, cao hơn đầu
    if p["fx"] == "shoot":
        hx, hy = g["hand_front"]
        for k in range(-11, 12):
            put(c, hx + 1 + (2 if abs(k) < 5 else (1 if abs(k) < 9 else 0)), hy + k, PC["wood"])
        for k in range(-10, 11):
            put(c, hx - 3 + abs(k) * 4 // 10, hy + k, PC["string"])
        straight(c, hx - 4, hy, 1, 0, 12, PC["wood_d"])
    else:
        sx, sy = g["hip"]                     # slung on the back: nearly upright behind the shoulders
        for k in range(22):
            x = sx - 5 - (1 if 4 < k < 17 else 0)
            put(c, x, sy + 5 - k, PC["wood"])
            if 2 < k < 19:
                put(c, sx - 3, sy + 5 - k, PC["string"])
        put(c, sx - 5, sy + 5, PC["wood_d"])
        put(c, sx - 5, sy - 16, PC["wood_d"])


C = {"pal": PC, "body": "tunic", "head": face(PC), "hair": c_hair, "behind": c_longbow}


def c_idle(i):
    return pose(bob=[0, 0, 1, 1][i], lean=-1, feet=((-4, 0), (4, 0)), hands=((-2, 6), (3, 6)), phase=i * 0.8,
                eyes="closed" if i == 3 else "open")


def c_run(i):
    return mf.run_pose(i, bob=[1, 1, 1, 0, 1, 1, 1, 0][i], lean=2, hands=((-2, 5), (3, 5)))


def c_hit():
    return pose(lean=-1, feet=((-6, 0), (5, 0)), hands=((-1, 3), (7, 1)), fx="shoot")


VARIANTS = [
    ("A  Thợ săn (mũ trùm, cung ngắn, ống tên)", A, a_idle, a_run, a_hit),
    ("B  Nỏ thủ (mũ da, khăn đỏ, nỏ ngang hông)", B, b_idle, b_run, b_hit),
    ("C  Du hiệp (đuôi ngựa, cung dài sau lưng)", C, c_idle, c_run, c_hit),
]


def main(scale=4):
    cols = 4 + 1 + 8 + 1 + 1
    label_h = 14
    sheet = Image.new("RGBA", (cols * 48 * scale, len(VARIANTS) * (48 * scale + label_h * scale // 2)), (32, 34, 46, 255))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 7 * scale)
    y = 0
    for name, char, idle, run, hit in VARIANTS:
        d.text((8, y + 4), f"{name}    idle 4  |  run 8  |  ra đòn", fill=(230, 230, 240), font=font)
        y += label_h * scale // 2
        frames = [idle(i) for i in range(4)] + [None] + [run(i) for i in range(8)] + [None] + [hit()]
        for k, p in enumerate(frames):
            if p is None:
                continue
            im = mf.draw(char, p).img.resize((48 * scale, 48 * scale), Image.NEAREST)
            d.line([(k * 48 * scale, y + 44 * scale), ((k + 1) * 48 * scale, y + 44 * scale)], fill=(70, 74, 92))
            sheet.alpha_composite(im, (k * 48 * scale, y))
        y += 48 * scale
    sheet.save(HERE / "variants.png")
    print(HERE / "variants.png")


if __name__ == "__main__":
    main()
