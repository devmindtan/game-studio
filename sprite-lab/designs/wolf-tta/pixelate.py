#!/usr/bin/env python3
"""Chuyển ảnh sói người dùng gửi sang pixel art (ảnh tĩnh) — chạy bằng Pillow, local.

Quy trình:
  1. crop bỏ dải watermark Shutterstock ở cuối ảnh;
  2. tìm bounding box của con sói (mọi pixel không gần trắng);
  3. resize về 64 px ngang (NEAREST) giữ đúng tỉ lệ dáng gốc;
  4. map sang palette cố định 11 màu (cc-29 + afr-32, đã dùng cho Thất Tinh Ấn);
  5. nền trắng -> trong suốt, viền 1px, xuất bản raw 64x40 và bản phóng 8x.

Ảnh nguồn là ảnh stock có bản quyền -> KHÔNG commit vào repo; script nhận đường dẫn làm tham số.
Chạy: python3 sprite-lab/designs/wolf-tta/pixelate.py /tmp/opencode/wolf-source.png
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
OUT_DIR = Path('/tmp/opencode')

# 11 màu: nền trắng không dùng (trong suốt), phần còn lại lấy từ cc-29/afr-32 + khớp ảnh.
PALETTE = [
    (0xF2, 0xF0, 0xE5),  # 0 kem rất sáng (mõm/ngực)
    (0xE5, 0xCE, 0xB4),  # 1 kem bụng
    (0xB8, 0xB5, 0xB9),  # 2 xám nhạt
    (0xB2, 0x8B, 0x78),  # 3 nâu xám sáng
    (0x86, 0x81, 0x88),  # 4 xám trung
    (0x84, 0x70, 0x66),  # 5 nâu xám
    (0x69, 0x5B, 0x59),  # 6 nâu sậm
    (0x4F, 0x42, 0x40),  # 7 nâu rất sậm (chân dưới)
    (0x35, 0x2F, 0x2E),  # 8 gần đen
    (0x21, 0x21, 0x23),  # 9 viền
    (0xD3, 0xA0, 0x68),  # 10 hổ phách (mắt, nếu có)
]


def nearest(rgb):
    r, g, b = rgb[:3]
    best, bi = 10 ** 9, 0
    for i, (pr, pg, pb) in enumerate(PALETTE):
        d = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if d < best:
            best, bi = d, i
    return bi


def main(src: str, width: int = 64):
    src = Path(src)
    im = Image.open(src).convert('RGB')
    # 1) bỏ dải watermark: cắt phần dưới cùng (khoảng 12% chiều cao)
    im = im.crop((0, 0, im.width, int(im.height * 0.87)))
    # 2) bbox của sói: pixel không gần trắng
    px = im.load()
    xs, ys = [], []
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = px[x, y]
            if min(r, g, b) < 238:            # nền trắng/kem trắng bị loại
                xs.append(x); ys.append(y)
    if not xs:
        raise SystemExit('không tìm thấy con sói trong ảnh')
    box = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
    wolf = im.crop(box)
    # 3) scale giữ tỉ lệ
    h = round(wolf.height * width / wolf.width)
    small = wolf.resize((width, h), Image.Resampling.NEAREST)
    # 4) map palette + 5) nền trong suốt
    sp = small.load()
    out = Image.new('RGBA', small.size, (0, 0, 0, 0))
    op = out.load()
    for y in range(small.height):
        for x in range(small.width):
            r, g, b = sp[x, y]
            if min(r, g, b) > 238:            # nền trắng -> trong suốt
                continue
            idx = nearest((r, g, b))
            op[x, y] = (*PALETTE[idx], 255)
    # viền 1px ngoài silhouette (không làm mờ nền)
    alpha = out.getchannel('A')
    grown = alpha.filter(ImageFilter.MaxFilter(3))
    border = Image.new('RGBA', out.size, (0x21, 0x21, 0x23, 255))
    border.putalpha(grown)
    outlined = Image.alpha_composite(border, out)
    # dời ảnh để có mép viền không bị cắt
    final = Image.new('RGBA', (outlined.width + 2, outlined.height + 2), (0, 0, 0, 0))
    final.alpha_composite(outlined, (1, 1))

    raw = OUT_DIR / 'wolf-pixel.png'
    final.save(raw)
    scale = 8
    prev = Image.new('RGBA', (final.width * scale + 20, final.height * scale + 50), (18, 22, 30, 255))
    prev.alpha_composite(final.resize((final.width * scale, final.height * scale), Image.NEAREST), (10, 40))
    d = ImageDraw.Draw(prev)
    d.text((10, 10), f'Sói từ ảnh gốc · {final.width}x{final.height} · 11 màu', fill=(236, 210, 140))
    preview = OUT_DIR / 'wolf-pixel-preview.png'
    prev.save(preview)
    print('bbox', box, '->', final.size)
    print(raw)
    print(preview)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '/tmp/opencode/wolf-source.png')
