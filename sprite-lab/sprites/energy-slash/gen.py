#!/usr/bin/env python3
"""Generator cho sprite "energy-slash": vệt chém năng lượng (hiệu ứng, không phải nhân vật).

Tạo hoàn chỉnh trong Sprite Lab: 6 frame, anchor tâm, hitbox rect theo vùng chém.
Chạy: gamekit art run energy-slash
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
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from sheet import export  # noqa: E402
from spritekit import Canvas  # noqa: E402

NAME = HERE.name
SIZE = 64
C = SIZE / 2
FPS = 12.0

EDGE = (30, 40, 60, 255)
DARK = (20, 120, 150, 255)
MID = (80, 220, 235, 255)
BRIGHT = (180, 250, 255, 255)
CORE = (235, 255, 255, 255)
SPARK = (200, 255, 255, 220)


def draw_slash(t: float) -> Canvas:
    c = Canvas(SIZE, SIZE, (0, 0, 0, 0))
    px = c.img.load()
    r0, r1 = 14, 26
    sweep = 1.2
    angle_center = -0.2
    if t < 0.2:
        env = t / 0.2
    elif t < 0.7:
        env = 1.0
    else:
        env = max(0.0, 1.0 - (t - 0.7) / 0.3)
    thickness = 2.5 + 2.0 * env
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x - C - 4, y - C
            r = math.hypot(dx, dy)
            if r < r0 - 2 or r > r1 + 3:
                continue
            a = math.atan2(dy, dx)
            da = abs((a - angle_center + math.pi) % (2 * math.pi) - math.pi)
            if da > sweep:
                continue
            dr = abs(r - (r0 + r1) / 2)
            end_taper = 1.0 - (da / sweep) ** 1.5
            half = thickness * end_taper * env
            if dr > half + 1.5:
                continue
            if dr < half * 0.3:
                col = CORE if env > 0.5 else BRIGHT
            elif dr < half * 0.7:
                col = BRIGHT if env > 0.6 else MID
            elif dr < half:
                col = MID
            elif dr < half + 1.0:
                col = DARK
            else:
                col = EDGE
            aout = int(col[3] * env)
            if aout > px[x, y][3]:
                px[x, y] = (col[0], col[1], col[2], aout)
    if 0.15 < t < 0.85:
        for i in range(6):
            ang = angle_center - sweep + (2 * sweep) * (i / 5)
            rr = r1 - 1 + (i % 2)
            sx = int(round(C + 4 + math.cos(ang) * rr))
            sy = int(round(C + math.sin(ang) * rr))
            if 0 <= sx < SIZE and 0 <= sy < SIZE:
                px[sx, sy] = SPARK
    return c


ANIM = [("slash", [draw_slash(i / 5) for i in range(6)], FPS, False,
         {"hitbox": {"shape": "rect", "center": [C + 2, C], "active": [1, 4]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=4, gif_scale=4)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["hit_source"] = "estimated"
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
