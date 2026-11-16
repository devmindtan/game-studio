#!/usr/bin/env python3
"""Generator cho sprite "mage": pháp sư nhìn nghiêng, quay phải, frame 48x56.

Một sheet gồm 7 animation (đứng yên, chạy, nhảy, đánh thường, chiêu thức, trúng
đòn, chết); mỗi animation chiếm một đoạn liên tiếp trên dải ngang, số frame, fps
và loop ghi trong mage.json. Điểm neo = giữa hai bàn chân, đúng mặt đất.
Vùng vẽ 48x48, cộng 8px phía trên để mũ không bị cắt khi nhảy (frame 48x56).

Chạy:  gamekit art run mage
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "mage"
W = 48
ART_H = 48          # vùng vẽ: đất ở y=44, outline chạm y=45
TOP_PAD = 8         # chừa chỗ phía trên cho mũ khi nhảy
FRAME_H = ART_H + TOP_PAD
ANCHOR = (24.0, 45.0 + TOP_PAD)  # giữa hai bàn chân, đúng mặt đất của frame
HERE = Path(__file__).resolve().parent
OUT = HERE  # sprite-lab/sprites/<name>/: strip + json next to gen.py

# Palette phẳng, tương phản: đọc silhouette ở 1x, không gradient.
DARK = "#160f22"      # outline
HAT = "#4a2a7a"       # mũ
HAT_D = "#33205c"     # mũ, mặt tối
HAT_L = "#6b45a8"     # mũ, mặt sáng
GOLD = "#e8c76a"      # sao trên mũ, khoá đai
ROBE = "#5b3a96"      # áo choàng
ROBE_D = "#3b2470"    # áo, mặt tối
ROBE_L = "#7d58bd"    # áo, mặt sáng
TRIM = "#b48ce0"      # viền áo
SKIN = "#f0c9a0"
SKIN_D = "#c99870"
BEARD = "#e6e6f0"
BEARD_D = "#b9b9cf"
WOOD = "#8a5a2e"
WOOD_D = "#5a3a1c"
BOOT = "#2a1a2e"
ORB = "#7ef0ff"
ORB_RIM = "#2f7f96"
ORB_CORE = "#ffffff"
GLOW = ("#3ac8e080", "#3ac8e04c", "#3ac8e026")


# --- hình học cơ bản ----------------------------------------------------------

def p(c, x, y, col):
    c.rect(x, y, x, y, col)


def robe_edges(y, body_dy, hem_dy, lean, spread):
    """Hai mép áo tại hàng y, áo là hình thang hơi loe ở gấu."""
    top_y, hem_y = 26 + body_dy, 42 + hem_dy
    t = (y - top_y) / max(1, hem_y - top_y)
    half = 6 + t * (10 + spread - 6)
    cx = 24 + lean * (1 - t)
    return round(cx - half), round(cx + half)


def pad(c):
    """Đặt hình đã vẽ vào frame cao hơn, chừa TOP_PAD phía trên."""
    out = Canvas(W, FRAME_H)
    out.paste(c, 0, TOP_PAD)
    return out


def draw_staff(c, base, top):
    bx, by = base
    tx, ty = top
    c.line(bx, by, tx, ty, WOOD, 2)
    c.line(bx + 1, by, tx + 1, ty, WOOD_D, 1)
    # đốt gỗ
    steps = max(abs(by - ty) // 9, 1)
    for k in range(1, steps):
        t = k / steps
        x = round(bx + (tx - bx) * t)
        y = round(by + (ty - by) * t)
        c.rect(x - 1, y, x + 1, y, WOOD_D)


def draw_boots(c, legs, hem_y):
    y0 = hem_y
    if legs == "stand":
        boxes = [(18, y0, 22, y0 + 2), (26, y0, 30, y0 + 2)]
    elif legs == "stride_r":  # chân phải (nhìn nghiêng) bước tới, thò ra ngoài gấu
        boxes = [(11, y0, 17, y0 + 2), (29, y0 - 1, 35, y0 + 2)]
    elif legs == "stride_l":
        boxes = [(13, y0 - 1, 19, y0 + 2), (31, y0, 37, y0 + 2)]
    elif legs == "tuck":  # nhảy: hai chân co lên
        boxes = [(19, y0 - 3, 23, y0), (25, y0 - 3, 29, y0)]
    else:  # wide: chân dạng ra (hạ cánh, quỵ)
        boxes = [(13, y0, 18, y0 + 2), (30, y0, 35, y0 + 2)]
    for x0, y0b, x1, y1 in boxes:
        c.rect(x0, y0b, x1, y1, BOOT)
        c.rect(x0, y1, x1, y1, DARK)  # đế giày


def draw_robe(c, body_dy, hem_dy, lean, spread):
    top_y, hem_y = 26 + body_dy, 42 + hem_dy
    for y in range(top_y, hem_y + 1):
        x0, x1 = robe_edges(y, body_dy, hem_dy, lean, spread)
        c.line(x0, y, x1, y, ROBE)
        c.line(x1 - 2, y, x1, y, ROBE_D)          # khối tối bên phải
        if y <= hem_y - 6:
            c.line(x0 + 1, y, x0 + 1, y, ROBE_L)  # nếp sáng bên trái
    # gấu áo
    for y in (hem_y - 1, hem_y):
        x0, x1 = robe_edges(y, body_dy, hem_dy, lean, spread)
        c.line(x0, y, x1, y, TRIM)
    # đai lưng + khoá
    for y in (32 + body_dy, 33 + body_dy):
        x0, x1 = robe_edges(y, body_dy, hem_dy, lean, spread)
        c.line(x0, y, x1, y, ROBE_D)
    c.rect(23 + lean, 32 + body_dy, 25 + lean, 33 + body_dy, GOLD)


def draw_arm(c, side, body_dy, lean, reach=(0, 0)):
    """Tay áo; reach là điểm tay vươn tới (tay phải cầm gậy)."""
    if side == "left":
        c.polygon([(19 + lean, 27 + body_dy), (14 + lean, 33 + body_dy),
                   (15 + lean, 37 + body_dy), (21 + lean, 31 + body_dy)], ROBE_D)
        c.rect(14 + lean, 37 + body_dy, 15 + lean, 38 + body_dy, SKIN)
    else:
        hx, hy = reach if reach != (0, 0) else (35 + lean, 33 + body_dy)
        c.polygon([(29 + lean, 27 + body_dy), (hx + 1, hy - 3),
                   (hx, hy + 2), (29 + lean, 31 + body_dy)], ROBE)
        c.rect(hx - 1, hy, hx, hy + 1, SKIN)


def draw_head(c, body_dy, lean, head=(0, 0), eyes="open"):
    dx = lean + head[0]
    dy = body_dy + head[1]
    c.rect(20 + dx, 15 + dy, 28 + dx, 22 + dy, SKIN)
    c.rect(19 + dx, 19 + dy, 19 + dx, 20 + dy, SKIN_D)   # tai
    p(c, 29 + dx, 19 + dy, SKIN_D)                        # mũi
    if eyes == "open":
        p(c, 26 + dx, 18 + dy, DARK)
        c.line(25 + dx, 17 + dy, 26 + dx, 17 + dy, SKIN_D)  # lông mày
    elif eyes == "shut":
        c.line(25 + dx, 19 + dy, 27 + dx, 19 + dy, DARK)
    else:  # hurt: mắt nhắm nghiền
        c.line(25 + dx, 18 + dy, 27 + dx, 20 + dy, DARK)
        c.line(27 + dx, 18 + dy, 25 + dx, 20 + dy, DARK)
    # râu + tóc
    c.rect(19 + dx, 17 + dy, 19 + dx, 20 + dy, BEARD)
    c.rect(20 + dx, 20 + dy, 28 + dx, 21 + dy, BEARD)
    c.polygon([(19 + dx, 21 + dy), (29 + dx, 21 + dy),
               (27 + dx, 26 + dy), (22 + dx, 26 + dy)], BEARD)
    c.line(22 + dx, 24 + dy, 26 + dx, 24 + dy, BEARD_D)
    c.line(22 + dx, 26 + dy, 27 + dx, 26 + dy, BEARD_D)
    c.line(20 + dx, 23 + dy, 21 + dx, 23 + dy, BEARD_D)


def draw_hat(c, body_dy, lean, tilt=(0, 0)):
    """Mũ nhọn; tilt[0] nghiêng ngọn, tilt[1] nhấc cả mũ."""
    dx = lean + tilt[0]
    dy = body_dy + tilt[1]
    c.rect(14 + dx, 12 + dy, 35 + dx, 14 + dy, HAT)
    c.rect(16 + dx, 12 + dy, 33 + dx, 12 + dy, HAT_L)
    c.rect(18 + dx, 10 + dy, 33 + dx, 11 + dy, TRIM)
    base_y, tip_y = 10 + dy, 1 + dy
    for y in range(tip_y, base_y):
        t = (base_y - y) / (base_y - tip_y)
        left = 18 + dx + t * (13 + tilt[0] * 0.5)
        right = 33 + dx + t * (-2 + tilt[0] * 0.5)
        c.line(round(left), y, round(right), y, HAT)
        c.line(round(right) - 1, y, round(right), y, HAT_D)
    sx, sy = 25 + dx, 6 + dy
    for ox, oy in ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2)):
        p(c, sx + ox, sy + oy, GOLD)


def draw_orb(c, pos, radius, glow=0, cores=1):
    x, y = pos
    if glow:
        g = Canvas(W, ART_H)
        for k in range(min(glow, len(GLOW))):
            r = radius + 2 + k
            g.ellipse(x - r, y - r, x + r, y + r, GLOW[k])
        c.paste(g)
    c.ellipse(x - radius, y - radius, x + radius, y + radius, ORB_RIM)
    c.ellipse(x - radius + 1, y - radius + 1, x + radius - 1, y + radius - 1, ORB)
    p(c, x, y - 1, ORB_CORE)
    if cores > 1:
        p(c, x - 1, y, ORB_CORE)


def pose(*, body_dy=0, hem_dy=0, lean=0, spread=0, legs="stand", staff=None,
         staff_base=None, orb_r=2, glow=0, hat=(0, 0), head=(0, 0),
         eyes="open", reach=(0, 0), bolt=0, sparks=(), dust=False, flash=False):
    """Một frame đầy đủ. Toạ độ gốc: chân ở y=42..44, neo (24, 45)."""
    c = Canvas(W, ART_H)
    hem_y = 42 + hem_dy
    if staff is None:
        top = (36 + lean, 8 + body_dy)
    else:
        top = (staff[0], staff[1] + body_dy)
    base = staff_base if staff_base else (36, 44)
    draw_staff(c, base, top)
    draw_boots(c, legs, hem_y)
    draw_robe(c, body_dy, hem_dy, lean, spread)
    draw_arm(c, "left", body_dy, lean)
    draw_arm(c, "right", body_dy, lean, reach)
    draw_head(c, body_dy, lean, head, eyes)
    draw_hat(c, body_dy, lean, hat)
    c.outline(DARK)

    orb = (top[0], top[1] - 2)
    draw_orb(c, orb, orb_r, glow)
    if bolt:
        for k in range(bolt):
            x = orb[0] + 4 + k
            if x < W - 1:
                c.rect(x, orb[1] - 1, x + 1, orb[1], ORB_CORE if k % 2 == 0 else ORB)
    for sx, sy in sparks:
        p(c, orb[0] + sx, orb[1] + sy, ORB_CORE)
    if dust:
        for x, y in ((16, 44), (19, 44), (28, 44), (31, 44)):
            p(c, x, y, TRIM)
    if flash:
        for y in range(ART_H):
            for x in range(W):
                r, g, b, a = c.img.getpixel((x, y))
                if a:
                    c.img.putpixel((x, y), (255, 255, 255, a))
    return pad(c)


# --- animation ----------------------------------------------------------------

def idle(i):
    return pose(
        body_dy=(0, 0, 1, 0)[i],
        hat=((0, 0), (1, 0), (1, 0), (0, 0))[i],
        glow=(0, 1, 2, 1)[i],
        eyes="shut" if i == 2 else "open",
    )


def run(i):
    legs = ("stride_r", "stride_l", "stride_r", "stride_r", "stride_l", "stride_r")[i]
    return pose(
        body_dy=(0, 1, 1, 0, 1, 1)[i],
        lean=1,
        spread=1,
        legs=legs,
        hat=((0, 1), (1, 0), (1, 1), (0, 1), (1, 0), (1, 1))[i],
        staff=(37 + (i % 3), 10),
        glow=1,
    )


def jump(i):
    if i == 0:  # nhún
        return pose(body_dy=2, hem_dy=1, spread=2, legs="wide", glow=1, hat=(0, 1),
                    staff=(36, 10), staff_base=(36, 42))
    if i == 1:  # bật lên
        return pose(body_dy=-2, hem_dy=-2, spread=1, legs="tuck", glow=2,
                    staff=(35, 9), staff_base=(35, 37), hat=(-1, -1))
    if i == 2:  # đỉnh
        return pose(body_dy=-5, hem_dy=-5, spread=2, legs="tuck", glow=2,
                    staff=(34, 10), staff_base=(34, 34), hat=(-1, -1))
    return pose(body_dy=1, hem_dy=1, spread=2, legs="wide", glow=1,
                staff=(36, 10), staff_base=(36, 41), dust=True)


def attack(i):
    if i == 0:  # lấy đà, kéo gậy về sau
        return pose(lean=-1, staff=(32, 11), orb_r=2, glow=1, hat=(1, 0),
                    reach=(33, 31))
    if i == 1:  # nạp
        return pose(staff=(35, 12), orb_r=3, glow=2, hat=(1, 1),
                    reach=(34, 30))
    if i == 2:  # đẩy tới, bắn tia
        return pose(lean=2, staff=(43, 15), orb_r=3, glow=3, hat=(2, 1),
                    reach=(35, 32), bolt=1)
    if i == 3:  # tia bay
        return pose(lean=1, staff=(42, 16), orb_r=2, glow=1, hat=(1, 0),
                    reach=(35, 33), bolt=6)
    return pose(lean=0, staff=(38, 11), orb_r=2, glow=1, reach=(35, 33))


def spell(i):
    if i == 0:  # giơ gậy
        return pose(lean=-1, staff=(35, 6), orb_r=2, glow=1, hat=(0, -1),
                    reach=(34, 30))
    if i == 1:
        return pose(lean=-1, staff=(35, 4), orb_r=3, glow=2, hat=(0, -1),
                    reach=(34, 29), sparks=((-5, 3), (5, 4)))
    if i == 2:
        return pose(lean=-1, staff=(36, 4), orb_r=4, glow=3, hat=(0, -1),
                    reach=(34, 29), sparks=((-7, 5), (7, 5), (0, -7)))
    if i == 3:
        return pose(lean=-2, staff=(36, 4), orb_r=5, glow=3, hat=(-1, -1),
                    reach=(34, 29), sparks=((-8, 6), (8, 6), (-6, -6), (6, -6)))
    if i == 4:  # xả
        return pose(lean=0, staff=(37, 6), orb_r=3, glow=2, hat=(1, 0),
                    reach=(35, 31), bolt=8, sparks=((0, -6), (7, 5)))
    return pose(lean=0, staff=(37, 9), orb_r=2, glow=1, reach=(35, 33))


def hurt(i):
    if i == 0:  # choáng, nháy trắng
        return pose(lean=-2, staff=(33, 10), glow=0, hat=(-2, 0), eyes="hurt",
                    head=(0, 1), flash=True)
    if i == 1:
        return pose(lean=-2, staff=(33, 11), glow=0, hat=(-2, 0), eyes="hurt",
                    head=(-1, 1), reach=(33, 34))
    return pose(lean=-1, staff=(34, 10), glow=0, hat=(-1, 0), eyes="shut",
                head=(0, 1))


def death(i):
    if i == 0:  # loạng choạng
        return pose(lean=-2, staff=(33, 10), glow=1, hat=(-2, 0),
                    eyes="hurt", head=(-1, 1))
    if i == 1:  # khuỵu
        return pose(body_dy=4, lean=-1, spread=3, legs="wide", staff=(33, 12),
                    glow=0, hat=(-3, 1), eyes="shut", head=(0, 2))
    if i == 2:  # quỳ, đầu cúi
        return pose(body_dy=7, lean=-1, spread=4, legs="wide", staff=(32, 14),
                    glow=0, hat=(-4, 1), eyes="shut", head=(0, 2))
    return heap(i == 4)


def heap(dust):
    """Đống áo choàng, mũ và gậy nằm trên đất sau khi gục."""
    c = Canvas(W, ART_H)
    c.ellipse(13, 33, 36, 44, ROBE)
    for y in range(39, 45):
        c.line(13, y, 36, y, ROBE)
    c.line(13, 44, 36, 44, TRIM)
    c.line(33, 34, 36, 44, ROBE_D)
    c.line(17, 35, 22, 44, ROBE_L)
    # giày thò ra khỏi đống áo
    c.rect(9, 41, 14, 44, BOOT)
    c.rect(9, 44, 14, 44, DARK)
    # đầu gục sang trái, mũ lăn ra
    c.ellipse(15, 30, 23, 39, SKIN)
    c.polygon([(17, 35), (22, 35), (21, 39), (18, 39)], BEARD)
    c.line(18, 34, 19, 34, DARK)  # mắt nhắm
    c.ellipse(5, 36, 15, 40, HAT)
    c.polygon([(7, 38), (1, 33), (12, 37)], HAT)
    c.line(6, 36, 12, 36, TRIM)
    # gậy nằm ngang
    c.line(34, 43, 43, 43, WOOD, 2)
    c.line(34, 44, 43, 44, WOOD_D, 1)
    c.outline(DARK)
    draw_orb(c, (44, 41), 2, 0)
    if dust:
        for x, y in ((11, 44), (14, 44), (37, 44), (41, 44)):
            p(c, x, y, TRIM)
    return pad(c)


ANIMATIONS = [
    ("idle", [idle(i) for i in range(4)], 6, True),
    ("run", [run(i) for i in range(6)], 12, True),
    ("jump", [jump(i) for i in range(4)], 10, False),
    ("attack", [attack(i) for i in range(5)], 12, False),
    ("spell", [spell(i) for i in range(6)], 10, False),
    ("hurt", [hurt(i) for i in range(3)], 12, False),
    ("death", [death(i) for i in range(5)], 8, False),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    flat = []
    for _, frames, _, _ in ANIMATIONS:
        flat.extend(frames)
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")

    # Preview: mỗi animation một hàng, để agent nhìn cả 7 trạng thái một lúc.
    columns = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(columns * W, len(ANIMATIONS) * FRAME_H)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * FRAME_H)
    preview([sheet], HERE / "preview.png", scale=3)

    for anim_name, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim_name}.gif", fps=fps, scale=4)

    write_anim_meta(
        OUT / f"{NAME}.json",
        [{"name": name, "frames": frames, "fps": fps, "loop": loop}
         for name, frames, fps, loop in ANIMATIONS],
        anchor=ANCHOR,
    )
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
