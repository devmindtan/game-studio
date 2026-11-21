#!/usr/bin/env python3
"""Nữ cung thủ: 3 phương án thiết kế để người dùng chọn (skill pixel-sprite bước 0, 2026-11-21).

Tham khảo tư thế: LPC `body/bodies/female/shoot.png` + `weapon/ranged/bow/recurve/universal/shoot` (hướng phải):
cung nằm ngang ở hông -> nâng lên -> tay trước duỗi ngang vai, cung dựng đứng, tay nắm GIỮA thân cung ->
tay sau kéo dây về má -> buông -> giữ. Lưng cung luôn quay về mục tiêu, dây cung phía người.

Ba phương án khác nhau ở silhouette, cách mang cung và nhịp chuyển động (không chỉ đổi màu):
  A "Trường cung"  : cung dài dựng đứng cạnh người, đứng thẳng điềm tĩnh, sải chạy dài nhún ít, áo choàng dài.
  B "Thợ săn"      : cung cong ngắn cầm ngang ở hông (như frame đầu LPC), dáng khom, chạy nảy gấp đôi, đuôi ngựa.
  C "Xạ thủ"       : luôn ở tư thế sẵn sàng: tay trước duỗi ra trước, cung dựng, tay sau giữ dây; chạy lao người.
Mỗi phương án: idle 4 + run 8 + 1 tư thế giương cung (chỉ để duyệt cách cầm). Chọn xong mới làm đủ animation
(idle/run/hurt/dash/death) thành sprite trong sprites/.
Chạy: python3 sprite-lab/designs/archer/variants.py  -> variants.png (x4) cạnh file này.
"""

import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parents[2]
sys.path.insert(0, str(WS / "tools/gamekit/pipeline"))
sys.path.insert(0, str(WS / "sprite-lab/lib"))

from PIL import Image, ImageDraw  # noqa: E402

import minifig as mf  # noqa: E402
from minifig import RUN_FEET, line, pose, put, rect  # noqa: E402


def bow(c, pal, cx, cy, facing_deg, half, depth, pull=None):
    """Cung có tay nắm ở (cx, cy). facing_deg: hướng LƯNG cung (0 = về trước/mục tiêu, 90 = xuống).
    Hai đầu cung lùi `depth` px về phía người; dây nối hai đầu, hoặc qua điểm `pull` khi đang kéo."""
    f = math.radians(facing_deg)
    fx, fy = math.cos(f), math.sin(f)
    ax, ay = -fy, fx                                    # trục thân cung, vuông góc hướng nhìn
    pts = []
    for k in range(-half, half + 1):
        t = k / half
        back = depth * t * t
        pts.append((cx + 0.5 + ax * k - fx * back, cy + 0.5 + ay * k - fy * back))
    for a, b in zip(pts, pts[1:]):
        line(c, a[0], a[1], b[0], b[1], pal["wood"], 1)
    put(c, round(pts[0][0] - fx), round(pts[0][1] - fy), pal["wood_d"])     # đầu cung cong ngược
    put(c, round(pts[-1][0] - fx), round(pts[-1][1] - fy), pal["wood_d"])
    put(c, cx, cy, pal["wood_d"])                                              # chỗ nắm
    top, bot = pts[0], pts[-1]
    if pull:
        line(c, top[0], top[1], pull[0], pull[1], pal["string"], 1)
        line(c, pull[0], pull[1], bot[0], bot[1], pal["string"], 1)
    else:
        line(c, top[0], top[1], bot[0], bot[1], pal["string"], 1)


def face(pal):
    def head(c, p, g):
        hx, hy = g["head"]
        rect(c, hx - 3, hy - 6, hx + 4, hy, pal["skin"])
        put(c, hx - 3, hy, pal["skin_d"])
        mf.eyes(c, hx + 2, hy - 4, p["eyes"], pal)
        put(c, hx + 3, hy - 1, pal["lip"])
    return head


# --- A: Trường cung -----------------------------------------------------------------------------
PA = {"skin": "#f0c4a0", "skin_d": "#c98f72", "lip": "#b8574a", "eye": "#1b1726",
      "hair": "#e3c06a", "hair_d": "#a8843f",
      "hood": "#3e6b48", "hood_d": "#29482f", "cloak": "#3e6b48", "cloak_d": "#29482f",
      "tunic": "#7a5a3a", "tunic_d": "#5a4129", "tunic_l": "#9c7650",
      "sleeve": "#3e6b48", "sleeve_d": "#29482f", "belt": "#4a3322", "buckle": "#d9b45a",
      "pants": "#4a4f5c", "pants_d": "#363a45", "boot": "#5a3d28", "boot_d": "#3d2919",
      "wood": "#c08a4a", "wood_d": "#7a5228", "string": "#d8d2c4"}


def a_hair(c, p, g):
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 7, PA["hood"])         # mũ trùm
    rect(c, hx - 5, hy - 7, hx - 2, hy, PA["hood"])
    put(c, hx + 4, hy - 7, PA["hood_d"])
    rect(c, hx + 1, hy - 6, hx + 4, hy - 6, PA["hair"])         # mái vàng lộ ra
    put(c, hx - 1, hy - 6, PA["hair"])


def a_cloak(c, p, g):
    t = g["top"]
    for k in range(14):
        back = round(k * (0.2 + 0.45 * p["speed"]))
        y = t[1] + k - round(k * 0.35 * p["speed"]) + round(math.sin(p["phase"] + k * 0.5) * 0.6 * p["speed"])
        x1 = t[0] - 2 - back
        rect(c, x1 - 3, y, x1, y, PA["cloak"] if k < 12 else PA["cloak_d"])
        put(c, x1 - 3, y, PA["cloak_d"])


def a_bow(c, p, g):
    hx, hy = g["hand_front"]
    if p["fx"] == "aim":
        bow(c, PA, hx, hy, 0, 9, 3, pull=g["hand_back"])
    else:
        bow(c, PA, hx, hy, 0, 9, 2)


A = {"pal": PA, "body": "tunic", "head": face(PA), "hair": a_hair, "behind": a_cloak, "held": a_bow}


def a_idle(i):   # đứng thẳng, cung dựng cạnh người; thở chậm
    return pose(bob=[0, 0, 1, 0][i], hands=((-2, 7), (4, 2)), phase=i * 0.8, eyes="closed" if i == 3 else "open")


def a_run(i):   # sải dài, nhún nhẹ, cung giữ thẳng đứng
    (fdx, fl), (bdx, bl) = RUN_FEET[i]
    return pose(bob=[0, 0, 0, -1, 0, 0, 0, -1][i], lean=1, feet=((bdx - 1, bl), (fdx + 1, fl)),
                hands=((-2 + fdx // 2, 6), (4, 2)), phase=i * math.pi / 4, speed=0.8)


def a_aim():
    return pose(hands=((2, 0), (8, 0)), fx="aim")


# --- B: Thợ săn ---------------------------------------------------------------------------------
PB = {"skin": "#d9a27a", "skin_d": "#a8735a", "lip": "#8a3b32", "eye": "#1b1726",
      "hair": "#2b1d1a", "hair_d": "#16100e", "fur": "#d8c8a8",
      "tunic": "#a8603a", "tunic_d": "#7a4128", "tunic_l": "#c98052",
      "sleeve": "#d9a27a", "sleeve_d": "#a8735a", "belt": "#3d2919", "buckle": "#c9c2b0",
      "pants": "#5a4a3a", "pants_d": "#3f3328", "boot": "#3d2919", "boot_d": "#2a1c12",
      "quiver": "#6a4429", "feather": "#e8e2d2",
      "wood": "#8a5a32", "wood_d": "#5a3a1f", "string": "#cfc6b4"}


def b_hair(c, p, g):
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 3, hy - 6, PB["hair"])
    rect(c, hx - 4, hy - 6, hx - 2, hy - 3, PB["hair"])
    put(c, hx + 4, hy - 6, PB["hair"])
    # đuôi ngựa buộc cao, bay theo nhịp nảy
    x, y = hx - 4, hy - 8
    for k in range(1, 6):
        nx = hx - 4 - round(k * (0.6 + 0.4 * p["speed"]))
        ny = hy - 8 + round(k * (0.9 - 0.7 * p["speed"])) + round(math.sin(p["phase"] + k) * p["speed"])
        line(c, x, y, nx, ny, PB["hair"] if k < 5 else PB["hair_d"], 2)
        x, y = nx, ny


def b_neck(c, p, g):
    t = g["top"]
    rect(c, t[0] - 3, t[1], t[0] + 3, t[1] + 1, PB["fur"])      # cổ lông thú


def b_quiver(c, p, g):
    h = g["hip"]
    line(c, h[0] - 3, h[1] - 1, h[0] - 6, h[1] - 7, PB["quiver"], 2)   # ống tên đeo hông, chéo ra sau
    put(c, h[0] - 7, h[1] - 8, PB["feather"])
    put(c, h[0] - 6, h[1] - 9, PB["feather"])


def b_bow(c, p, g):
    hx, hy = g["hand_front"]
    if p["fx"] == "aim":
        bow(c, PB, hx, hy, 0, 6, 2, pull=g["hand_back"])
    else:
        bow(c, PB, hx, hy, 90, 7, 4)                            # nằm ngang ở hông, lưng cung xuống đất, cong rõ


B = {"pal": PB, "body": "tunic", "head": face(PB), "hair": b_hair, "neck": b_neck, "behind": b_quiver,
     "held": b_bow}


def b_idle(i):   # khom, nhún tại chỗ nhanh như đang rình
    return pose(bob=[1, 2, 1, 2][i], lean=1, feet=((-4, 0), (4, 0)), hands=((-1, 6), (3, 7)), phase=i * 1.5,
                speed=0.2, eyes="closed" if i == 2 else "open")


def b_run(i):   # nảy gấp đôi, bước ngắn nhanh
    (fdx, fl), (bdx, bl) = RUN_FEET[i]
    return pose(bob=[1, 2, 0, -2, 1, 2, 0, -2][i], lean=2, feet=((bdx, bl + (1 if bl else 0)), (fdx, fl + (1 if fl else 0))),
                hands=((-2 - fdx // 2, 5), (3, 7)), phase=i * math.pi / 4, speed=1.0)


def b_aim():
    return pose(lean=1, bob=1, feet=((-4, 0), (4, 0)), hands=((2, 0), (7, 0)), fx="aim")


# --- C: Xạ thủ ----------------------------------------------------------------------------------
PC = {"skin": "#f2d0b4", "skin_d": "#c99a80", "lip": "#a8505a", "eye": "#1b1726",
      "hair": "#4a4a6a", "hair_d": "#2e2e45", "hair_l": "#6e6e94",
      "tunic": "#3f5f9c", "tunic_d": "#2b4170", "tunic_l": "#6488c8",
      "sleeve": "#3f5f9c", "sleeve_d": "#2b4170", "belt": "#2b2b3a", "buckle": "#cfd6e0",
      "pants": "#2b2b3a", "pants_d": "#1e1e29", "boot": "#2b2b3a", "boot_d": "#1e1e29",
      "pad": "#b8c2d0", "pad_d": "#7c8698",
      "wood": "#d0d6e0", "wood_d": "#7c8698", "string": "#9aa4b4"}


def c_hair(c, p, g):
    hx, hy = g["head"]
    rect(c, hx - 4, hy - 8, hx + 4, hy - 7, PC["hair"])
    rect(c, hx - 4, hy - 7, hx - 2, hy - 2, PC["hair"])
    put(c, hx + 1, hy - 8, PC["hair_l"])
    # bím tóc ngắn rủ sau gáy
    for k in range(4):
        put(c, hx - 4, hy - 1 + k, PC["hair"] if k % 2 == 0 else PC["hair_d"])
        put(c, hx - 5, hy - 1 + k, PC["hair_d"] if k % 2 == 0 else PC["hair"])


def c_pad(c, p, g):
    s = g["sh_front"]
    rect(c, s[0] - 1, s[1] - 1, s[0] + 2, s[1], PC["pad"])      # giáp vai kim loại (lớp front)
    put(c, s[0] - 1, s[1], PC["pad_d"])


def c_bow(c, p, g):
    hx, hy = g["hand_front"]
    hb = g["hand_back"]
    if p["fx"] == "aim":
        bow(c, PC, hx, hy, 0, 7, 3, pull=(hb[0], hb[1]))
    else:
        bow(c, PC, hx, hy, 0, 7, 2, pull=(hx - 3, hy))         # giữ dây hờ, sẵn sàng kéo


C = {"pal": PC, "body": "tunic", "head": face(PC), "hair": c_hair, "held": c_bow, "front": c_pad}


def c_idle(i):   # tay trước duỗi ra trước ngang ngực, cung dựng, tay sau sát dây
    return pose(bob=[0, 0, 1, 0][i], lean=1, feet=((-4, 0), (3, 0)), hands=((3, 3), (7, 2)),
                eyes="closed" if i == 3 else "open")


def c_run(i):   # lao người, chân sải, cung vẫn ở trước
    (fdx, fl), (bdx, bl) = RUN_FEET[i]
    return pose(bob=[0, 1, 0, -1, 0, 1, 0, -1][i], lean=3, feet=((bdx, bl), (fdx, fl)),
                hands=((3, 3), (7, 2)), phase=i * math.pi / 4, speed=1.0)


def c_aim():
    return pose(lean=1, feet=((-4, 0), (3, 0)), hands=((1, 0), (8, 0)), fx="aim")


VARIANTS = [
    ("A  Trường cung", A, a_idle, a_run, a_aim),
    ("B  Thợ săn", B, b_idle, b_run, b_aim),
    ("C  Xạ thủ", C, c_idle, c_run, c_aim),
]


def render(char, p):
    return mf.draw(char, p).img


def main(scale=4):
    cols = 4 + 1 + 8 + 1 + 1   # idle | gap | run | gap | aim
    label_h = 14
    W = cols * 48 * scale
    H = len(VARIANTS) * (48 * scale + label_h * scale // 2)
    sheet = Image.new("RGBA", (W, H), (32, 34, 46, 255))
    d = ImageDraw.Draw(sheet)
    from PIL import ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 7 * scale)
    y = 0
    for name, char, idle, run, aim in VARIANTS:
        d.text((8, y + 4), f"{name}    idle 4  |  run 8  |  giương cung (tham khảo LPC shoot)", fill=(230, 230, 240), font=font)
        y += label_h * scale // 2
        frames = [idle(i) for i in range(4)] + [None] + [run(i) for i in range(8)] + [None] + [aim()]
        for k, p in enumerate(frames):
            if p is None:
                continue
            im = render(char, p).resize((48 * scale, 48 * scale), Image.NEAREST)
            d.line([(k * 48 * scale, y + 44 * scale), ((k + 1) * 48 * scale, y + 44 * scale)], fill=(70, 74, 92))
            sheet.alpha_composite(im, (k * 48 * scale, y))
        y += 48 * scale
    out = HERE / "variants.png"
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
