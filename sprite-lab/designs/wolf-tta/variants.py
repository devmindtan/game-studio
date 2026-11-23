#!/usr/bin/env python3
"""Sói xám cho Thất Tinh Ấn — 3 phương án TĨNH để người dùng chọn (skill pixel-sprite bước 0).

Tái dùng bộ vẽ đã có trong lab: sprite-lab/sprites/wolf/gen.py (Sói Rừng, creature-v1, đã promote sang
bach-ai). Không sửa/ghi đè sprite đó — chỉ import hàm wolf(pose) để render 3 dáng tĩnh, rồi đổi tạm palette
trong bộ nhớ cho sát ảnh tham chiếu (xám-nâu, ngực/bụng kem, chân dưới sậm, mắt hổ phách thay vì đỏ).

Tham chiếu 2026-11-23 (tra web thật):
  - Zivatar, "2D Wolf animation assets" (itch.io, trang công khai): sói pixel 4 biến thể màu,
    idle 9 / walk 11 khung; dấu nhận diện = tai nhọn, mõm dài, bờm cổ, đuôi xù, lông xám-nâu, bụng sáng.
  - Slynyrd, Pixelblog 25 "Motion Cycles": đi 4 chân = hông/ngực nhấp nhô lệch nhịp, đầu gật, đuôi trễ.
  - Ảnh người dùng gửi: chỉ học giải phẫu/dáng đi; KHÔNG chép pixel hay watermark (ảnh stock có bản quyền).
  Học: thân thon, mõm dài, ngực sáng tách lưng xám, đuôi xù.
  Tránh: gai lưng/tím hóa (bài học skill: "giống quái vật"), chép pixel ảnh stock.
  Quyết định: 3 dáng KHÁC NHAU bằng pose có sẵn (sải / gồng / rình), cùng palette 10 màu để đồng nhất.

Chạy: python3 sprite-lab/designs/wolf-tta/variants.py -> variants.png (6x, nearest)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
WS = HERE.parents[2]
sys.path.insert(0, str(WS / "tools/gamekit/pipeline"))
sys.path.insert(0, str(WS / "sprite-lab/lib"))

SRC = WS / "sprite-lab/sprites/wolf/gen.py"
spec = importlib.util.spec_from_file_location("wolf_gen", SRC)
wg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wg)

W, H = wg.W, wg.H
FLOOR = wg.PAW_Y + 2
ORIGINAL = dict(wg.C)

# Cùng một palette nền tảng cho cả 3 phương án; chỉ đổi "eye" cho bản thường (không đỏ lóe).
BASE = {
    **ORIGINAL,
    "dark": "#352f2e", "fur": "#6e6860", "lit": "#9a948a", "tip": "#c8c2b6",
    "belly": "#e5ceb4", "saddle": "#4a4540", "eye": "#f0b030",
    "mouth": "#4a2420", "mouth_d": "#2a1210",
}


def render(pose, palette):
    wg.C.clear()
    wg.C.update(palette)
    return wg.wolf(pose).img


def variant_a():
    """Sải dài: dáng đi giữa nhịp, đầu hơi gật, đuôi ngang — gần ảnh tham chiếu nhất."""
    return render({**wg.RUN[0], "hackle": 0.2, "jaw": 0, "ears": 1}, BASE)


def variant_b():
    """Gáy dựng: lông cổ dựng, tai cụp, mõm dữ hơn — cùng loài, dáng rõ khác A."""
    return render({**wg.ATTACK[1], "glow": False}, BASE)


def variant_c():
    """Rình thấp: ngực hạ, đầu sát đất, đuôi rủ — silhouette thấp khác hẳn."""
    return render({**wg.ATTACK[2], "glow": False, "jaw": 1}, BASE)


VARIANTS = [
    ("A · Sói sải dài", variant_a, "dáng đi ngang, đầu gật nhẹ, ngực kem, đuôi xù"),
    ("B · Sói gáy dựng", variant_b, "lông cổ dựng, tai cụp, dữ nhưng vẫn là sói"),
    ("C · Sói rình", variant_c, "thân hạ, đầu sát đất, đuôi rủ"),
]


def main(scale=6):
    sheet = Image.new("RGBA", (W * scale + 20, (H * scale + 44) * len(VARIANTS)), (18, 22, 30, 255))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except OSError:
        font = small = ImageFont.load_default()
    for row, (name, fn, note) in enumerate(VARIANTS):
        y0 = row * (H * scale + 44)
        d.text((10, y0 + 4), name, fill=(236, 210, 140), font=font)
        d.text((10, y0 + 21), note, fill=(150, 200, 180), font=small)
        sheet.alpha_composite(fn().resize((W * scale, H * scale), Image.NEAREST), (10, y0 + 38))
        d.line([(10, y0 + 38 + FLOOR * scale), (10 + W * scale, y0 + 38 + FLOOR * scale)],
               fill=(70, 74, 92), width=1)
    out = HERE / "variants.png"
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
