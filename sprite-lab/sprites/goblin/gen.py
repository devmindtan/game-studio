#!/usr/bin/env python3
"""Generator cho sprite "goblin": quái vùng 1 (Bách Ải), goblin da xanh lá, tai nhọn, áo da, dao găm.

Frame 48x48 dựng bằng sprite-lab/lib/minifig.py (cùng tỉ lệ với swordsman/mage), neo (24, 44) trên đất
(ground=True). Hành vi trong game: "charge" (dừng, lấy đà, lao tới). Đầu/mặt/tai vẽ bằng bản đồ pixel tay.
Animation: move 8 (chạy lom khom), attack 4 (lấy đà → lao đâm → giữ → thu), hurt 2, death 5.
Chạy: gamekit art run goblin
"""

import math
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

import minifig as mf  # noqa: E402
from minifig import line, pose, put, run_pose  # noqa: E402
from sheet import export  # noqa: E402

NAME = "goblin"
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))
BLADE = 6

PAL = {
    "skin": "#7cc75b", "skin_d": "#4f8f3a",
    "tunic": "#7a5230", "tunic_d": "#5a3a20", "tunic_l": "#9a6c42",
    "sleeve": "#7cc75b", "sleeve_d": "#4f8f3a",          # bare green arms
    "belt": "#3e2a18", "buckle": "#c9a24a",
    "pants": "#4a3424", "pants_d": "#33241a",
    "boot": "#2e2218", "boot_d": "#211810",
    "blade": "#d8dde6", "blade_d": "#8f99a8", "grip": "#5a3a20",
    "eye": "#f6e05e", "pupil": "#1b1726", "tooth": "#f2efe0",
}
# Head 10 wide, facing right: s skin, d shade, e eye (yellow), p pupil, t tooth, n nose. Column 4 = head centre.
HEAD = [
    "...ssss...",
    "..ssssss..",
    ".ssssssss.",
    "dsssssepsn",
    "dsssssssss",
    ".ssssssts.",
    "..dssss...",
]
EAR = [  # long pointed ear, swept back (left of the head)
    "dd....",
    ".dsd..",
    "..dss.",
    "...ds.",
]
KEYS = {"s": "skin", "d": "skin_d", "e": "eye", "p": "pupil", "t": "tooth", "n": "skin_d"}


def head(c, p, g):
    hx, hy = g["head"]
    top = hy - len(HEAD) + 1
    for r, row in enumerate(EAR):
        for col, ch in enumerate(row):
            if ch != ".":
                put(c, hx - 9 + col, top + 1 + r, PAL[KEYS[ch]])
    for r, row in enumerate(HEAD):
        for col, ch in enumerate(row):
            if ch == ".":
                continue
            key = KEYS[ch]
            if p["eyes"] in ("closed", "wince", "x") and ch in "ep":
                key = "pupil" if (ch == "e" and p["eyes"] != "closed") else "skin_d"
            put(c, hx - 4 + col, top + r, PAL[key])


def dagger(c, p, g):
    hx, hy = g["hand_front"]
    a = math.radians(mf.keep_above_floor(hx, hy, p["weapon"], BLADE))
    dx, dy = math.cos(a), math.sin(a)
    gx, gy = hx + 0.5, hy + 0.5
    line(c, gx - dx, gy - dy, gx, gy, PAL["grip"], 1)
    line(c, gx + dx, gy + dy, gx + dx * BLADE, gy + dy * BLADE, PAL["blade"], 1)
    put(c, gx + dx * 2 - dy, gy + dy * 2 + dx, PAL["blade_d"])


def fx(c, p, g):
    if p["fx"] == "lunge":  # speed lines behind
        hx, hy = g["hip"]
        for k, y in enumerate((hy - 8, hy - 4, hy)):
            for x in range(hx - 14 + k, hx - 8 + k):
                put(c, x, y, (230, 230, 240, 120))


CHAR = {"pal": PAL, "body": "tunic", "head": head, "held": dagger, "fx": fx}


def frame(**kw):
    return mf.draw(CHAR, pose(**kw))


def move(i):
    return mf.draw(CHAR, run_pose(i, lean=2, weapon=30))   # hunched, dagger forward


def attack(i):
    return [
        frame(bob=2, lean=-1, feet=((-4, 0), (2, 0)), hands=((-3, 5), (-2, 3)), weapon=200),   # wind-up
        frame(bob=0, lean=4, feet=((-5, 0), (6, 0)), hands=((-3, 6), (7, 1)), weapon=0, fx="lunge",
              speed=1.0),
        frame(bob=1, lean=4, feet=((-5, 0), (6, 0)), hands=((-3, 6), (7, 2)), weapon=5),
        frame(bob=0, lean=2, hands=((-2, 7), (3, 5)), weapon=30),
    ][i]


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 4)), weapon=200,
              eyes="wince", flash=0.75),
        frame(bob=1, lean=-1, hands=((-3, 5), (2, 5)), weapon=40, eyes="wince"),
    ][i]


def death(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), (1, 4)), weapon=200,
              eyes="x", flash=0.5),
        frame(bob=3, lean=-1, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), weapon=40, eyes="x"),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), weapon=40, eyes="x", lie=0.4),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), weapon=40, eyes="x", lie=0.85),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), weapon=40, eyes="x", lie=1.0),
    ][i]


ANIMATIONS = [
    ("move", [move(i) for i in range(8)], 12, True, {}),
    ("attack", [attack(i) for i in range(4)], 10, False, {"durations_ms": [260, 90, 120, 140]}),
    ("hurt", [hurt(i) for i in range(2)], 12, False, {"durations_ms": [80, 120]}),
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [100, 120, 100, 100, 300]}),
]


def main() -> None:
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, preview_scale=4, body="move")
    print(f"strip: {HERE / f'{NAME}_strip.png'}")


if __name__ == "__main__":
    main()
