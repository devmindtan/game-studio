#!/usr/bin/env python3
"""knight: the user's own knight (sprite-lab/sources/user/knight-2026-11-25.png, user 2026-11-25: "thay nhân vật kiếm
sĩ hiện tại"). The agent only animates it: every frame is the user's pixels, cut into parts and moved by whole pixels
(no redrawing, no smooth rotation). The drawing faces left; it is mirrored so the sheet faces right like the others.

Parts (in the original, left-facing 32x30 crop): left leg x17-19 y26-28, right foot x24-25 y28, everything else is
the upper body (helmet and plume, face, tunic, sword arm and sword, shield).
Animations: idle 4, run 8, hurt 3, dash 5, death 5 (the swordsman's set).
Chạy: gamekit art run knight  ·  thử: gamekit art shot knight sheet|move
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

SRC = WS / "sprite-lab/sources/user/knight-2026-11-25.png"
S = 48
CROP = (0, 0, 32, 30)
FEET_Y = 28            # lowest row of the feet in the crop
FLOOR = 44             # anchor y in the frame (like the swordsman)


def _parts():
    im = Image.open(SRC).convert("RGBA").crop(CROP)
    w, h = im.size
    left = Image.new("RGBA", im.size)
    right = Image.new("RGBA", im.size)
    upper = Image.new("RGBA", im.size)
    for y in range(h):
        for x in range(w):
            p = im.getpixel((x, y))
            if p[3] == 0:
                continue
            if 17 <= x <= 19 and 26 <= y <= 28:
                left.putpixel((x, y), p)
            elif 24 <= x <= 25 and y == 28:
                right.putpixel((x, y), p)
            else:
                upper.putpixel((x, y), p)
    flip = Image.Transpose.FLIP_LEFT_RIGHT       # face right like the other heroes; pixels unchanged
    return upper.transpose(flip), left.transpose(flip), right.transpose(flip)


UPPER, LEG_A, LEG_B = _parts()
# after the mirror the feet sit at x 6..14 of the 32-wide crop: centre the pair on the anchor
OX = 24 - 10
OY = FLOOR - FEET_Y - 1   # the feet row sits just above the anchor line


def frame(up=(0, 0), a=(0, 0), b=(0, 0), flash=False):
    """Compose one frame: upper body and each foot offset by whole pixels (dx, dy)."""
    c = Canvas(S, S)
    for part, (dx, dy) in ((LEG_B, b), (LEG_A, a), (UPPER, up)):
        c.img.alpha_composite(part, (OX + dx, OY + dy))
    if flash:
        px = c.img.load()
        for y in range(S):
            for x in range(S):
                r, g, bb, al = px[x, y]
                if al:
                    px[x, y] = (min(255, r + 150), min(255, g + 150), min(255, bb + 150), al)
    return c


def lying(c):
    img = c.img.rotate(90, expand=False)
    bbox = img.getbbox()
    out = Canvas(S, S)
    if bbox:
        out.img.alpha_composite(img, (0, FLOOR - bbox[3]))
    return out


IDLE = [frame(), frame(), frame(up=(0, 1)), frame(up=(0, 1))]
# run: feet alternate (lift 1, step 1). The body never rises off the 3 px legs (that left a gap, user 2026-11-25):
# it dips 1 px on the contact frames instead, overlapping the feet.
RUN = [frame(up=(0, 1), a=(1, 0), b=(-1, -1)), frame(up=(0, 0), a=(1, 0), b=(0, -1)),
       frame(up=(0, 0), a=(0, 0), b=(1, 0)), frame(up=(0, 0), a=(-1, 0), b=(1, 0)),
       frame(up=(0, 1), a=(-1, -1), b=(1, 0)), frame(up=(0, 0), a=(0, -1), b=(1, 0)),
       frame(up=(0, 0), a=(1, 0), b=(0, 0)), frame(up=(0, 0), a=(1, 0), b=(-1, 0))]
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
    check_connected(ANIM, "knight")
    export(HERE, HERE.name, ANIM, anchor=(24.0, float(FLOOR)), ground=True)
    print("OK", HERE.name)
