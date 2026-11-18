"""hires: a denser copy of a pixel-art strip for sprites drawn big (skill effects).

    python3 hires.py <sprite_dir> [<sprite_dir> ...]   (gamekit hires <game> [names])

Writes <name>_strip_x4.png next to <name>_strip.png: Scale2x (EPX, A. Mazzoleni)
applied twice, which keeps hard pixel edges but rounds diagonals, and adds
"hires": 4 to <name>.json. SpriteSheet draws that texture at the same on-screen
size, so an effect scaled x5 shows 4x more pixels instead of 5 px blocks. Hit
boxes and anchors stay in the original pixel units.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

FACTOR = 4
MAX_TEXTURE = 16384   # Godot's texture width limit: long strips get x2, or none


def scale2x(img: Image.Image) -> Image.Image:
    """EPX: each pixel P becomes 4, taking a neighbour colour where two meet."""
    w, h = img.size
    src = img.load()
    out = Image.new("RGBA", (w * 2, h * 2))
    dst = out.load()

    def px(x, y):
        return src[min(max(x, 0), w - 1), min(max(y, 0), h - 1)]

    for y in range(h):
        for x in range(w):
            p = src[x, y]
            a, b, c, d = px(x, y - 1), px(x + 1, y), px(x - 1, y), px(x, y + 1)
            e0 = c if (c == a and c != d and a != b) else p
            e1 = a if (a == b and a != c and b != d) else p
            e2 = d if (d == c and d != b and c != a) else p
            e3 = b if (b == d and b != a and d != c) else p
            dst[2 * x, 2 * y] = e0
            dst[2 * x + 1, 2 * y] = e1
            dst[2 * x, 2 * y + 1] = e2
            dst[2 * x + 1, 2 * y + 1] = e3
    return out


def make(sprite_dir: Path) -> Path:
    name = sprite_dir.name
    strip = sprite_dir / f"{name}_strip.png"
    meta = sprite_dir / f"{name}.json"
    if not strip.exists() or not meta.exists():
        raise SystemExit(f"hires: {sprite_dir} has no {name}_strip.png / {name}.json")
    img = Image.open(strip).convert("RGBA")
    data = json.loads(meta.read_text())
    if data.get("layers"):   # a layered hero is composed at run time (worn items): no baked copy
        for old in sprite_dir.glob(f"{name}_strip_x*.png"):
            old.unlink()
        data.pop("hires", None)
        meta.write_text(json.dumps(data, indent=2) + "\n")
        return sprite_dir / f"{name}: layered, skipped"
    fw = int(data.get("frame_size", [img.width, img.height])[0])
    factor = FACTOR
    while factor > 1 and img.width * factor > MAX_TEXTURE:
        factor //= 2
    for old in sprite_dir.glob(f"{name}_strip_x*.png"):
        old.unlink()
    if factor == 1:
        data.pop("hires", None)
        meta.write_text(json.dumps(data, indent=2) + "\n")
        return sprite_dir / f"{name}: too long for a hires copy"
    big = Image.new("RGBA", (img.width * factor, img.height * factor))
    for x0 in range(0, img.width, fw):   # frame by frame: no colour bleeds from the next frame
        f = img.crop((x0, 0, x0 + fw, img.height))
        k = 1
        while k < factor:
            f = scale2x(f)
            k *= 2
        big.paste(f, (x0 * factor, 0))
    out = sprite_dir / f"{name}_strip_x{factor}.png"
    big.save(out)
    data["hires"] = factor
    meta.write_text(json.dumps(data, indent=2) + "\n")
    return out


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(make(Path(arg)))
