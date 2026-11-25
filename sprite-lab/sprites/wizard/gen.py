#!/usr/bin/env python3
"""wizard: the user's own mage (sprite-lab/sources/user/mage-2026-11-25.png, user 2026-11-25: "xử lí tiếp nhân vật
pháp sư"). Only animated: the drawing is cut into the upper body and two feet, mirrored to face right, moved by whole
pixels (no redrawing). Animations as the knight: idle 4, run 8, hurt 3, dash 5, death 5. Equipment layers come later
(the user's choice of slots). Chạy: gamekit art run wizard
"""
import sys
from pathlib import Path


def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(__file__).resolve().parent
WS = _ws()
sys.path.insert(0, str(WS / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from PIL import Image  # noqa: E402
from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402
from userart import check_connected  # noqa: E402

SRC = WS / "sprite-lab/sources/user/mage-2026-11-25.png"
S = 48
CROP = (0, 0, 32, 30)
FEET_Y = 29          # the lowest row of the feet (with their outline)
FLOOR = 44


def _group(x, y):
    """The two bottom rows are the feet with their own outline (outline pixels left in the upper body made the feet
    come apart when the body dipped); the staff foot (x <= 17) stays with the upper body."""
    if y >= 27 and x >= 18:   # rows 27-29
        return "a" if x < 22 else "b"
    return "up"


def _parts():
    im = Image.open(SRC).convert("RGBA").crop(CROP)
    out = {g: Image.new("RGBA", im.size) for g in ("up", "a", "b")}
    for y in range(im.height):
        for x in range(im.width):
            p = im.getpixel((x, y))
            if p[3]:
                out[_group(x, y)].putpixel((x, y), p)
    flip = Image.Transpose.FLIP_LEFT_RIGHT
    return {g: v.transpose(flip) for g, v in out.items()}


PARTS = _parts()
OX = 24 - 10            # after the mirror the feet are x 5..13: centre them on the anchor
OY = FLOOR - FEET_Y - 1


def frame(up=(0, 0), a=(0, 0), b=(0, 0), flash=False):
    c = Canvas(S, S)
    for g, (dx, dy) in (("b", b), ("a", a), ("up", up)):
        c.img.alpha_composite(PARTS[g], (OX + dx, OY + dy))
    if flash:
        px = c.img.load()
        for y in range(S):
            for x in range(S):
                r, gg, bb, al = px[x, y]
                if al:
                    px[x, y] = (min(255, r + 150), min(255, gg + 150), min(255, bb + 150), al)
    return c


def lying(c):
    img = c.img.rotate(90, expand=True)
    bbox = img.getbbox()
    out = Canvas(S, S)
    if bbox:
        w = bbox[2] - bbox[0]
        out.img.alpha_composite(img.crop(bbox), (max(0, min(S - w, 24 - w // 2)), FLOOR - (bbox[3] - bbox[1])))
    return out


IDLE = [frame(), frame(), frame(up=(0, 1)), frame(up=(0, 1))]
RUN = [frame(up=(0, 1), a=(1, 0), b=(-1, -1)), frame(a=(1, 0), b=(0, -1)), frame(a=(0, 0), b=(1, 0)),
       frame(a=(-1, 0), b=(1, 0)), frame(up=(0, 1), a=(-1, -1), b=(1, 0)), frame(a=(0, -1), b=(1, 0)),
       frame(a=(1, 0), b=(0, 0)), frame(a=(1, 0), b=(-1, 0))]
HURT = [frame(up=(-1, 0), flash=True), frame(up=(-1, 0)), frame()]
DASH = [frame(up=(0, 1)), frame(up=(2, 1), a=(2, 0), b=(-2, 0)), frame(up=(2, 1), a=(2, 0), b=(-2, -1)),
        frame(up=(2, 1), a=(2, 0), b=(-2, 0)), frame(up=(1, 0))]
DEATH = [frame(up=(-1, 0), flash=True), frame(up=(0, 1)), frame(up=(0, 1)), lying(frame(up=(0, 1))),
         lying(frame(up=(0, 1)))]
HB = {"shape": "rect", "center": [24.0, 30.0]}
ANIM = [("idle", IDLE, 5, True, {"durations_ms": [240, 160, 240, 160], "hitbox": dict(HB, active=[0, 3])}),
        ("run", RUN, 12, True, {"hitbox": dict(HB, active=[0, 7])}),
        ("hurt", HURT, 12, False, {"durations_ms": [90, 110, 120], "hitbox": dict(HB, active=[0, 2])}),
        ("dash", DASH, 14, False, {"durations_ms": [60, 50, 70, 70, 90], "hitbox": dict(HB, active=[0, 4])}),
        ("death", DEATH, 8, False, {"durations_ms": [120, 140, 140, 100, 400], "hitbox": dict(HB, active=[0, 4])})]

if __name__ == "__main__":
    check_connected(ANIM, "wizard")
    export(HERE, HERE.name, ANIM, anchor=(24.0, float(FLOOR)), ground=True, body="idle")
    print("OK", HERE.name)
