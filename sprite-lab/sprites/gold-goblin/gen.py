#!/usr/bin/env python3
"""Generator cho "gold-goblin" (Yêu Tinh Vàng): quái sự kiện bỏ chạy, rơi vàng (Bách Ải 6B, design/events.md).

Cùng mọi khung của "goblin", đổi bảng màu: da vàng kim, áo tím sẫm như kẻ trộm, khóa thắt lưng sáng. Nhuộm
màu trong game không biến xanh thành vàng được, nên đây là sprite riêng (giống king-slime-rage).
json ghi "variant_of": "goblin" để test chuẩn quái coi nó là biến thể của yêu tinh (chờ nâng cấp cùng yêu tinh).
Chạy: gamekit art run gold-goblin
"""

import json
import shutil
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "goblin"
# goblin colour -> gold goblin colour
SWAP = {
    (124, 199, 91): (255, 208, 74), (79, 143, 58): (200, 140, 30),     # skin -> gold
    (190, 227, 173): (255, 240, 160), (222, 241, 214): (255, 250, 210),  # skin lights -> pale gold
    (122, 82, 48): (90, 40, 110), (90, 58, 32): (60, 24, 76), (154, 108, 66): (130, 70, 150),  # tunic -> thief purple
    (201, 162, 74): (255, 255, 200),                                     # buckle glints
}


def swap(path_in, path_out):
    im = Image.open(path_in).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in SWAP:
                px[x, y] = (*SWAP[(r, g, b)], a)
    im.save(path_out)


if __name__ == "__main__":
    swap(SRC / "goblin_strip.png", HERE / "gold-goblin_strip.png")
    swap(SRC / "goblin.png", HERE / "gold-goblin.png")
    swap(SRC / "preview.png", HERE / "preview.png")
    meta = json.loads((SRC / "goblin.json").read_text())
    meta["variant_of"] = "goblin"
    (HERE / "gold-goblin.json").write_text(json.dumps(meta, indent=2) + "\n")
    for gif in SRC.glob("*.gif"):
        shutil.copy(gif, HERE / gif.name)   # look only; the strip is the source the game reads
    print("OK gold-goblin")
    sys.exit(0)
