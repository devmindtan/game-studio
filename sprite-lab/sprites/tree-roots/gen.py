#!/usr/bin/env python3
"""Generator cho "tree-roots": rễ cây trồi lên dưới chân người chơi (đòn của boss Mộc Yêu, Bách Ải 6A).

Đất nứt, năm rễ gỗ cong nhọn đâm lên (vỏ sẫm, mặt sáng, đầu rêu), giữ một nhịp rồi rút xuống, đất vụn.
Game đặt vòng cảnh báo trước (Enemies._boss_tree) rồi vẽ sprite này khi rễ đâm. Frame 48x40, neo ở mặt đất
(24, 36). erupt 8 frame một lần.  Chạy: gamekit art run tree-roots
"""

import math
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402

NAME = "tree-roots"
W, H = 48, 40
ANCHOR = (24.0, 36.0)
GY = 35
OUTLINE = "#1a120c"
BARK_D, BARK, BARK_L = "#4a2e1a", "#6e4528", "#9a6a3e"
MOSS, MOSS_L = "#4a7a32", "#7ab04a"
DIRT, CRACK = "#5a4630", "#2a1e14"
# base x, full height, curl (+ right / - left)
ROOTS = [(11, 16, -1), (18, 24, 1), (24, 30, -1), (30, 22, 1), (37, 15, -1)]


def root(c, bx, h, curl, grow, moss=True):
    if h * grow < 2:
        return
    n = max(3, int(h * grow))
    pts = []
    for s in range(n + 1):
        t = s / n
        x = bx + curl * math.sin(t * math.pi * 0.9) * 4 * grow
        y = GY - h * grow * t
        pts.append((x, y, t))
    for (x0, y0, t0), (x1, y1, _) in zip(pts, pts[1:]):
        w = max(1, round(3.2 * (1 - t0)))
        c.line(round(x0), round(y0), round(x1), round(y1), BARK, w)
    for (x0, y0, t0), (x1, y1, _) in zip(pts, pts[1:]):   # lit edge on the curl side
        if t0 < 0.85:
            c.line(round(x0 - curl), round(y0), round(x1 - curl), round(y1), BARK_L)
    tip = pts[-1]
    if moss and grow > 0.6:
        c.pixel(round(tip[0]), round(tip[1]), MOSS_L)
        c.pixel(round(tip[0] + curl), round(tip[1] + 1), MOSS)


def ground(c, crack=True, dirt=0):
    c.line(6, GY, W - 7, GY, BARK_D)
    if crack:
        for x in (12, 19, 25, 31, 37):
            c.line(x, GY, x + 2, GY - 1, CRACK)
    for k in range(dirt):
        x = 8 + (k * 11) % 32
        c.pixel(x, GY - 2 - k % 3, DIRT)


def frame(i):
    c = Canvas(W, H)
    grow = [0.0, 0.35, 0.75, 1.0, 0.95, 0.9, 0.55, 0.2][i]
    ground(c, crack=True, dirt=[2, 5, 6, 4, 2, 1, 3, 5][i])
    for bx, h, curl in ROOTS:
        root(c, bx, h, curl, grow)
    return c.outline(OUTLINE)


HB = {"shape": "rect", "center": [24.0, 36.0]}
ANIMATIONS = [
    ("erupt", [frame(i) for i in range(8)], 12, False,
     {"durations_ms": [70, 60, 60, 120, 110, 100, 90, 110], "hitbox": {**HB, "active": [2, 5]}}),
]

if __name__ == "__main__":
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=False, body="erupt", preview_scale=6, gif_scale=4)
    print(f"OK {NAME}")
