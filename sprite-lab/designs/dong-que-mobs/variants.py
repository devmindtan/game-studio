#!/usr/bin/env python3
"""Quái Làng Hạc / Đồi sim (Thất Tinh Ấn): mỗi con 3 phương án để chọn (skill pixel-sprite bước 0, 2026-11-23).

Bù nhìn rơm (cọc tập, không di chuyển), Chuột đồi (nhanh, yếu), Bọ sim (chậm, cứng). Khác nhau ở silhouette và
cách di chuyển, không chỉ màu. Mỗi ô: 2 frame đứng + 4 frame di chuyển/nảy (bù nhìn: lắc khi trúng đòn).
Chạy: python3 sprite-lab/designs/dong-que-mobs/variants.py -> variants.png
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parents[2]
sys.path.insert(0, str(WS / "tools/gamekit/pipeline"))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from spritekit import Canvas  # noqa: E402

OUT = "#1b1726"
N = 32
FLOOR = 29


def px(c, x, y, col):
    c.pixel(int(x), int(y), col)


def box(c, x0, y0, x1, y1, col):
    c.rect(int(x0), int(y0), int(x1), int(y1), col)


def fin(c):
    c.outline(OUT)
    return c


# ---------- Bù nhìn rơm ----------
def dummy_a(t):  # A: bao rơm tròn trên cọc chữ thập, nón lá
    c = Canvas(N, N); s = [0, 1, 0, -1, 0, 1][t]
    box(c, 15, 18, 16, 28, "#7a5228")                       # cọc
    box(c, 9 + s, 15, 22 + s, 16, "#7a5228")                # tay ngang
    box(c, 11 + s, 9, 20 + s, 20, "#d9b45a"); box(c, 11 + s, 18, 20 + s, 20, "#b08a3a")
    box(c, 12 + s, 14, 19 + s, 14, "#8a2620")               # dây buộc
    for x in range(8, 24):                                  # nón lá
        y = 8 - (8 - abs(x - 16)) // 3
        box(c, x + s, y, x + s, 8, "#e0c88a")
    px(c, 14 + s, 11, OUT); px(c, 18 + s, 11, OUT)
    return fin(c)


def dummy_b(t):  # B: cọc gỗ mộc nhân (cột cao, ba tay gỗ ngắn)
    c = Canvas(N, N); s = [0, 0, 1, 0, -1, 0][t]
    box(c, 12 + s, 4, 19 + s, 28, "#8a5a36"); box(c, 12 + s, 4, 13 + s, 28, "#64401f")
    box(c, 19 + s, 10, 25 + s, 11, "#a8744a"); box(c, 19 + s, 16, 24 + s, 17, "#a8744a")
    box(c, 6 + s, 13, 12 + s, 14, "#a8744a")
    box(c, 12 + s, 22, 19 + s, 23, "#3a7866")
    return fin(c)


def dummy_c(t):  # C: bó rơm thấp có áo vải vá, đầu bí, đứng nghiêng
    c = Canvas(N, N); s = [0, 1, 1, 0, -1, -1][t]
    box(c, 15, 22, 16, 28, "#7a5228")
    box(c, 10 + s, 13, 21 + s, 23, "#5a6b8a"); box(c, 13 + s, 16, 15 + s, 18, "#c23b32")
    for k in range(4):
        px(c, 10 + s + k * 3, 24, "#d9b45a")
    box(c, 11 + s, 6, 20 + s, 12, "#d98a3a"); px(c, 15 + s, 5, "#3a7866"); px(c, 16 + s, 4, "#3a7866")
    px(c, 13 + s, 9, OUT); px(c, 18 + s, 9, OUT); box(c, 14 + s, 11, 17 + s, 11, OUT)
    return fin(c)


# ---------- Chuột đồi ----------
def rat_a(t):  # A: chuột nhỏ thấp, đuôi dài, chạy sát đất
    c = Canvas(N, N); b = [0, 0, -1, 0, 1, 0][t]; leg = t % 2
    box(c, 9, 22 + b, 21, 27 + b, "#8a6b55"); box(c, 20, 21 + b, 25, 26 + b, "#8a6b55")
    box(c, 10, 26 + b, 20, 27 + b, "#a88a70")
    px(c, 21, 19 + b, "#c99a8a"); px(c, 22, 20 + b, "#c99a8a"); px(c, 24, 23 + b, OUT); px(c, 26, 25 + b, "#d07a7a")
    for k in range(7):
        px(c, 8 - k, 24 + b - (k // 2) + (1 if k > 4 else 0), "#c99a8a")
    box(c, 11 + leg * 2, 28, 12 + leg * 2, 28, "#5a4636"); box(c, 18 - leg * 2, 28, 19 - leg * 2, 28, "#5a4636")
    return fin(c)


def rat_b(t):  # B: chuột đứng hai chân, to tai, cầm que (đi lạch bạch)
    c = Canvas(N, N); b = [0, 1, 0, 1, 0, 1][t]
    box(c, 12, 14 + b, 20, 26, "#9c8a78"); box(c, 13, 20 + b, 19, 25, "#c8b8a0")
    box(c, 13, 8 + b, 21, 14 + b, "#9c8a78"); box(c, 11, 5 + b, 14, 9 + b, "#d8a8a0"); box(c, 19, 5 + b, 22, 9 + b, "#d8a8a0")
    px(c, 18, 10 + b, OUT); px(c, 22, 12 + b, "#d07a7a")
    for k in range(9):
        px(c, 22, 12 + k + b, "#7a5228")
    box(c, 13 + (t % 2), 27, 15 + (t % 2), 28, "#5a4636"); box(c, 17 - (t % 2), 27, 19 - (t % 2), 28, "#5a4636")
    return fin(c)


def rat_c(t):  # C: chuột tròn béo nảy bóng (thân tròn, chân giấu), nhảy cóc
    c = Canvas(N, N); h = [0, 0, -3, -5, -3, 0][t]; sq = 1 if t in (0, 5) else 0
    cx, cy = 16, 22 + h
    for y in range(-6 + sq, 7):
        w = int((36 - y * y) ** 0.5 * 1.2) + sq
        box(c, cx - w, cy + y, cx + w, cy + y, "#7a6a5a")
    box(c, cx - 3, cy + 2, cx + 4, cy + 5, "#b8a890")
    box(c, cx - 4, cy - 9, cx - 2, cy - 6, "#d8a8a0"); box(c, cx + 2, cy - 9, cx + 4, cy - 6, "#d8a8a0")
    px(c, cx + 3, cy - 3, OUT); px(c, cx + 7, cy - 1, "#d07a7a")
    return fin(c)


# ---------- Bọ sim ----------
def beetle_a(t):  # A: bọ tròn mai tím bóng, sáu chân nhỏ, bò chậm
    c = Canvas(N, N); leg = t % 2
    for y in range(-6, 1):
        w = int((49 - y * y) ** 0.5 * 1.3)
        box(c, 16 - w, 25 + y, 16 + w, 25 + y, "#6b3f8f")
    box(c, 16, 19, 16, 25, "#4a2a66"); px(c, 12, 20, "#b088d0"); px(c, 13, 20, "#b088d0")
    box(c, 24, 21, 27, 25, "#2a2230"); px(c, 26, 22, "#e0b250")
    for k in range(3):
        px(c, 11 + k * 5 + leg, 27, "#2a2230"); px(c, 11 + k * 5 + leg, 28, "#2a2230")
    return fin(c)


def beetle_b(t):  # B: bọ cánh cứng có sừng cao, thân dài, mai sim chín đốm
    c = Canvas(N, N); leg = t % 2; s = [0, 0, 0, 1, 0, 0][t]
    box(c, 7, 19, 21, 26, "#4a2a66"); box(c, 7, 19, 21, 20, "#6b3f8f")
    for x, y in ((10, 22), (14, 23), (18, 22)):
        px(c, x, y, "#9a5ab8")
    box(c, 21, 20, 25, 25, "#2a2230")
    for k in range(6):
        px(c, 25 + k // 2, 19 - k + s, "#5a4a6e")
    px(c, 23, 22, "#e05050")
    for k in range(3):
        px(c, 9 + k * 5 - leg, 27, "#2a2230"); px(c, 8 + k * 5 - leg, 28, "#2a2230")
    return fin(c)


def beetle_c(t):  # C: bọ bay vo ve (cánh mở rung, bay lượn trên đất), bóng dưới đất
    c = Canvas(N, N); h = [0, -1, -2, -1, 0, -1][t]; wing = t % 2
    for x in range(10, 22):
        px(c, x, 28, "#2a2a36")
    box(c, 11, 14 + h, 21, 19 + h, "#6b3f8f"); box(c, 20, 15 + h, 23, 18 + h, "#2a2230"); px(c, 22, 16 + h, "#e0b250")
    if wing:
        box(c, 12, 8 + h, 17, 13 + h, "#c8d8f0")
    else:
        box(c, 9, 11 + h, 16, 13 + h, "#c8d8f0")
    return fin(c)


ROWS = [
    ("Bù nhìn rơm", [("A nón lá, chữ thập", dummy_a), ("B mộc nhân gỗ", dummy_b), ("C đầu bí, áo vá", dummy_c)]),
    ("Chuột đồi", [("A bò sát đất", rat_a), ("B đứng 2 chân cầm que", rat_b), ("C tròn nảy cóc", rat_c)]),
    ("Bọ sim", [("A mai tròn bò chậm", beetle_a), ("B có sừng, thân dài", beetle_b), ("C bay vo ve", beetle_c)]),
]


def main(scale=5):
    cell = N * scale
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 6 * scale)
    W = 3 * (6 * cell + cell // 2)
    H = len(ROWS) * (cell + 16 * scale)
    sheet = Image.new("RGBA", (W, H), (32, 34, 46, 255)); d = ImageDraw.Draw(sheet)
    y = 0
    for mob, variants in ROWS:
        for vi, (label, fn) in enumerate(variants):
            x0 = vi * (6 * cell + cell // 2)
            d.text((x0 + 6, y + 4), f"{mob} — {label}", fill=(230, 230, 240), font=font)
            for t in range(6):
                im = fn(t).img.resize((cell, cell), Image.NEAREST)
                sheet.alpha_composite(im, (x0 + t * cell, y + 10 * scale))
            d.line([(x0, y + 10 * scale + FLOOR * scale), (x0 + 6 * cell, y + 10 * scale + FLOOR * scale)], fill=(70, 74, 92))
        y += cell + 16 * scale
    sheet.save(HERE / "variants.png"); print(HERE / "variants.png")


if __name__ == "__main__":
    main()
