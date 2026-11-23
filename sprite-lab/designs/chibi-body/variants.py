#!/usr/bin/env python3
"""Thân chibi chuẩn 64x64 (sprite-lab/BODY_PLAN.md bước 1): 3 phương án tỉ lệ để người dùng chọn, mỗi phương án
idle 2 + walk 9 (nhịp học từ LPC walk, tự vẽ). Chạy: python3 sprite-lab/designs/chibi-body/variants.py"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WS = HERE.parents[2]
sys.path.insert(0, str(WS / "tools/gamekit/pipeline"))
sys.path.insert(0, str(WS / "sprite-lab/lib"))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from chibi_body import PROPORTIONS, GROUND, skeleton, draw_bare  # noqa: E402

PAL = {"skin": "#f6caa8", "skin_d": "#d89c7c", "hair": "#c26a2a", "eye": "#1b1726", "cheek": "#f08a8a",
       "shirt": "#e8e2d0", "shorts": "#2f5f6e", "shoe": "#5a3d28", "shoe_d": "#3d2919", "outline": "#1b1726"}


def main(scale=3):
    cols = 2 + 1 + 9
    lab = 16
    sheet = Image.new("RGBA", (cols * 64 * scale, 3 * (64 * scale + lab * scale // 2)), (40, 62, 46, 255))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 6 * scale)
    y = 0
    for key, pr in PROPORTIONS.items():
        d.text((8, y + 4), f"{key}  {pr['name']}    idle 2  |  walk 9", fill=(235, 235, 240), font=font)
        y += lab * scale // 2
        frames = [("idle", i) for i in range(2)] + [None] + [("walk", i) for i in range(9)]
        for k, fr in enumerate(frames):
            if fr is None:
                continue
            im = draw_bare(skeleton(fr[0], fr[1], pr), pr, PAL).img.resize((64 * scale, 64 * scale), Image.NEAREST)
            d.line([(k * 64 * scale, y + GROUND * scale + scale), ((k + 1) * 64 * scale, y + GROUND * scale + scale)], fill=(70, 90, 74))
            sheet.alpha_composite(im, (k * 64 * scale, y))
        y += 64 * scale
    sheet.save(HERE / "variants.png")
    print(HERE / "variants.png")


if __name__ == "__main__":
    main()
