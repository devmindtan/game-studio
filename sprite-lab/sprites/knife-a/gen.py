"""Generator for "knife-a": the Sát thủ's thrown dagger (Phi dao), 2026-11-26. It is the user's own dagger, drawn beside
the assassin in sprite-lab/sources/user/assassin-2026-11-25.png, at double density (px_scale 0.5) and turned to each
flight direction (whole-pixel nearest rotation, no redraw). Anchor = the blade's tip.
Chạy: gamekit art run knife-a
"""
import json
import math
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

NAME = HERE.name
SIZE = 56
C = SIZE // 2
FPS = 12.0
SRC = WS / "sprite-lab/sources/user/assassin-2026-11-25.png"
PIECE = (28, 23, 42, 32)          # the dagger beside the figure
TIP = (29, 24)                    # its point (the handle end is at 40, 30)
SRC_ANGLE = math.degrees(math.atan2(24 - 30, 29 - 40)) % 360   # screen angle the drawn dagger points at
HB = {"shape": "rect", "center": [C, C], "active": [0, 0]}


def knife(direction):
    """One frame: the dagger pointing at screen angle [direction] (0 = right, 90 = down), tip on the centre."""
    piece = Image.open(SRC).convert("RGBA").crop(PIECE)
    piece = piece.resize((piece.width * 2, piece.height * 2), Image.NEAREST)
    big = Image.new("RGBA", (SIZE * 2, SIZE * 2))
    tx, ty = (TIP[0] - PIECE[0]) * 2, (TIP[1] - PIECE[1]) * 2
    big.alpha_composite(piece, (SIZE - tx, SIZE - ty))
    big = big.rotate(SRC_ANGLE - direction, resample=Image.NEAREST, center=(SIZE, SIZE))
    c = Canvas(SIZE, SIZE)
    c.img.alpha_composite(big.crop((C, C, C + SIZE, C + SIZE)))
    return c


DIRS = [("fly", 0), ("fly_right", 0), ("fly_left", 180), ("fly_up", 270), ("fly_down", 90)] + \
    [("fly_%03d" % round(k * 22.5), k * 22.5) for k in range(16)]
ANIM = [(n, [knife(d)], FPS, True, {"hitbox": dict(HB)}) for n, d in DIRS]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(float(C), float(C)), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
