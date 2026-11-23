#!/usr/bin/env python3
"""Võ sinh (nhân vật chính Thất Tinh Ấn): 3 phương án để người dùng chọn (skill pixel-sprite bước 0, 2026-11-23).

Tham khảo (2026-11-23, tìm web): sheet võ sinh nhìn ngang (Summer Engine "Fighter Sheet" áo trắng đai đỏ),
Luizmelo "Fantasy Martial Characters 3" (idle 4 / run 8), Slynyrd Pixelblog 53 "Punches and Kicks".
  Học: võ phục + đai màu là silhouette nhận diện; idle 4, run 8; xoay hông đưa người về thế ngang khi ra đòn.
  Tránh: chép bất kỳ sheet nào; tóc dựng/hào quang vàng kiểu truyện tranh nổi tiếng (thế giới của game là mới).
  Quyết định: 3 phương án khác silhouette, vũ khí, dáng và nhịp — chọn xong mới làm đủ animation.

  A "Quyền"  : tay không, áo võ ngắn tay + đai đỏ dài bay, thế thủ hai nắm tay trước ngực, chạy nảy nhanh.
  B "Côn"    : áo nâu dài tay, khăn quấn đầu, côn dài vác chéo 45° sau lưng; đứng thấp vững, chạy sải dài nặng.
  C "Kiếm"   : áo dài xẻ tà, búi tóc cao, kiếm ngắn cầm ngược dọc theo tay sau; đứng nghiêng người, chạy lướt thấp.
Mỗi phương án: idle 4 + run 8 + 1 tư thế ra đòn.  Chạy: python3 sprite-lab/designs/vo-sinh/variants.py
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


# --- A: Quyền ------------------------------------------------------------------------------------
PA = {"skin": "#f0c4a0", "skin_d": "#c98f72", "eye": "#1b1726", "hair": "#2a2230",
      "tunic": "#ece6d6", "tunic_d": "#bdb5a2", "tunic_l": "#ffffff", "sleeve": "#f0c4a0", "sleeve_d": "#c98f72",
      "belt": "#c23b32", "buckle": "#c23b32", "pants": "#ece6d6", "pants_d": "#bdb5a2",
      "boot": "#2a2230", "boot_d": "#1b1726"}


def a_hair(c, p, g):
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 6, PA["hair"])
    rect(c, hx - 4, hy - 6, hx - 2, hy - 3, PA["hair"])
    put(c, hx + 4, hy - 7, PA["hair"])


def a_belt(c, p, g):   # đai đỏ: hai đuôi bay sau hông
    hip = g["hip"]
    for k in range(5):
        y = hip[1] - 2 + round(k * 0.25 * (1 - p["speed"])) + round(math.sin(p["phase"] + k * 0.7) * 0.6 * p["speed"])
        put(c, hip[0] - 4 - k, y, "#c23b32" if k < 4 else "#8a2620")


A = {"pal": PA, "body": "tunic", "head": face(PA), "hair": a_hair, "behind": a_belt}


def a_idle(i):   # thế thủ, nảy nhẹ trên mũi chân
    return pose(bob=[0, 1, 1, 0][i], feet=((-4, 0), (4, 0)), hands=((3, 3), (5, 2)), phase=i * 0.8,
                eyes="closed" if i == 3 else "open")


def a_run(i):
    return mf.run_pose(i, bob=[0, 1, -1, -2, 0, 1, -1, -2][i], hands=((2, 3), (4, 3)))


def a_hit():     # đấm thẳng, xoay hông
    return pose(lean=2, feet=((-6, 0), (5, 0)), hands=((-1, 4), (10, 0)))


# --- B: Côn ---------------------------------------------------------------------------------------
PB = {"skin": "#d9a77e", "skin_d": "#a8775a", "eye": "#1b1726", "hair": "#3a2a20",
      "tunic": "#8a5a36", "tunic_d": "#64401f", "tunic_l": "#a8744a", "sleeve": "#8a5a36", "sleeve_d": "#64401f",
      "belt": "#3a7866", "buckle": "#e0b250", "pants": "#3b3a48", "pants_d": "#2a2a36",
      "boot": "#5a3d28", "boot_d": "#3d2919", "wood": "#c08a4a", "wood_d": "#7a5228", "wrap": "#3a7866"}


def b_hair(c, p, g):   # khăn quấn đầu ngọc, đuôi khăn
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 4, hy - 6, PB["wrap"])
    put(c, hx - 5, hy - 6, PB["wrap"])
    put(c, hx - 6, hy - 5 + round(math.sin(p["phase"]) * p["speed"]), PB["wrap"])


def b_staff(c, p, g):  # côn vác chéo 45° sau lưng, tay trước nắm
    hx, hy = g["hand_front"]
    if p["fx"] == "strike":
        straight(c, hx - 4, hy, 1, 0, 18, PB["wood"])           # đâm ngang
        put(c, hx + 13, hy, PB["wood_d"])
    else:
        straight(c, hx + 3, hy + 3, -1, -1, 17, PB["wood"])     # vác chéo 45° qua vai, ra sau lưng
        put(c, hx - 13, hy - 13, PB["wood_d"])


B = {"pal": PB, "body": "tunic", "head": face(PB), "hair": b_hair, "held_back": b_staff}


def b_idle(i):   # đứng thấp, chân rộng, thở chậm
    return pose(bob=[1, 1, 2, 1][i], feet=((-5, 0), (5, 0)), hands=((-2, 7), (3, 4)), phase=i * 0.8,
                eyes="closed" if i == 2 else "open")


def b_run(i):    # sải dài, nặng
    (fdx, fl), (bdx, bl) = RUN_FEET[i]
    return pose(bob=[1, 1, 0, 0, 1, 1, 0, 0][i], lean=1, feet=((bdx - 1, bl), (fdx + 1, fl)),
                hands=((-2 + fdx // 2, 6), (3, 4)), phase=i * math.pi / 4, speed=0.9)


def b_hit():
    return pose(lean=2, feet=((-6, 0), (5, 0)), hands=((2, 2), (7, 2)), fx="strike")


# --- C: Kiếm --------------------------------------------------------------------------------------
PC = {"skin": "#f0c4a0", "skin_d": "#c98f72", "eye": "#1b1726", "hair": "#1e1a28",
      "robe": "#2f4f6e", "robe_d": "#1f3550", "robe_l": "#4a7096", "trim": "#e0b250", "belt": "#e0b250",
      "sleeve": "#2f4f6e", "sleeve_d": "#1f3550", "pants": "#d8d0c0", "pants_d": "#a8a090",
      "boot": "#2a2230", "boot_d": "#1b1726", "steel": "#d8e0ea", "steel_d": "#8a96a8", "hilt": "#7a3b2e"}


def c_hair(c, p, g):   # búi tóc cao + dải buộc
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 6, PC["hair"])
    rect(c, hx - 4, hy - 6, hx - 3, hy - 4, PC["hair"])
    rect(c, hx - 2, hy - 11, hx, hy - 9, PC["hair"])
    put(c, hx - 3, hy - 10 + round(math.sin(p["phase"]) * p["speed"]), "#c23b32")


def c_sword(c, p, g):  # kiếm cầm ngược dọc tay sau (lưỡi chĩa lên sau cẳng tay) / chém ngang khi ra đòn
    if p["fx"] == "slash":
        hx, hy = g["hand_front"]
        put(c, hx, hy, PC["hilt"])
        straight(c, hx + 1, hy, 1, 0, 10, PC["steel"])
        put(c, hx + 1, hy + 1, PC["steel_d"])
    else:
        hx, hy = g["hand_back"]
        put(c, hx, hy + 1, PC["hilt"])
        straight(c, hx, hy, 0, -1, 10, PC["steel"])
        put(c, hx + 1, hy - 1, PC["steel_d"])


C = {"pal": PC, "body": "robe", "hem_up": 3, "head": face(PC), "hair": c_hair, "held": c_sword}


def c_idle(i):   # nghiêng người, tay sau ôm kiếm
    return pose(bob=[0, 0, 1, 1][i], lean=-1, feet=((-3, 0), (4, 0)), hands=((-1, 5), (3, 7)), phase=i * 0.8,
                eyes="closed" if i == 3 else "open")


def c_run(i):    # lướt thấp, đầu đổ về trước, ít nảy
    return mf.run_pose(i, bob=[1, 1, 1, 0, 1, 1, 1, 0][i], lean=2, hands=((-1, 4), (3, 6)))


def c_hit():
    return pose(lean=2, feet=((-6, 0), (5, 0)), hands=((-3, 5), (7, 1)), fx="slash")


VARIANTS = [
    ("A  Quyền (tay không, đai đỏ)", A, a_idle, a_run, a_hit),
    ("B  Côn (gậy dài, khăn quấn)", B, b_idle, b_run, b_hit),
    ("C  Kiếm (áo dài, búi tóc, kiếm ngắn)", C, c_idle, c_run, c_hit),
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
