#!/usr/bin/env python3
"""Generator cho "gold-goblin" (Yêu Tinh Vàng): quái sự kiện bỏ chạy, rơi vàng (Bách Ải 6B, design/events.md).

Người dùng 2026-11-20: không cầm dao; một tên đạo tặc vác bọc tiền rồi chạy. Cùng khung người (minifig) với
"goblin" nhưng: da vàng kim, khăn bịt mắt tím của kẻ trộm, áo tím sẫm, một BỌC TIỀN to vác sau vai (tay trước
nắm miệng bọc trên vai), đồng vàng lấp ló miệng bọc. move = chạy chồm người, bọc nảy theo nhịp; attack = ôm
chặt bọc ngoái lại (nó không đánh); hurt = rung, vàng văng; death = ngã, bọc rơi, tiền tung toé.
json ghi "variant_of": "goblin" để test chuẩn quái coi nó là biến thể của yêu tinh.
Chạy: gamekit art run gold-goblin
"""

import json
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

import minifig as mf  # noqa: E402
from minifig import pose, put, run_pose  # noqa: E402
from sheet import export  # noqa: E402

NAME = "gold-goblin"
ANCHOR = (float(mf.ROOT_X), float(mf.FLOOR))

PAL = {
    "skin": "#ffd04a", "skin_d": "#c88c1e",
    "tunic": "#5a2870", "tunic_d": "#3c184c", "tunic_l": "#824696",
    "sleeve": "#ffd04a", "sleeve_d": "#c88c1e",
    "belt": "#2a1a30", "buckle": "#fff0a0",
    "pants": "#3a2a40", "pants_d": "#281c2e",
    "boot": "#2e2218", "boot_d": "#211810",
    "eye": "#ffffff", "pupil": "#1b1726", "tooth": "#f2efe0", "mask": "#7a3ab8", "mask_d": "#4a1e74",
    "sack": "#b8865a", "sack_d": "#7a5230", "sack_l": "#dcb07e", "rope": "#5a3a20",
    "coin": "#ffd84a", "coin_l": "#fff6b0", "coin_d": "#c0801a",
}
# Head 10 wide, facing right; m = the thief's mask band across the eyes (eye still shows through it).
HEAD = [
    "...ssss...",
    "..ssssss..",
    ".mmmmmmmm.",
    "dmmmmmepmn",
    "dsssssssss",
    ".ssssssts.",
    "..dssss...",
]
EAR = ["dd....", ".dsd..", "..dss.", "...ds."]
KEYS = {"s": "skin", "d": "skin_d", "e": "eye", "p": "pupil", "t": "tooth", "n": "skin_d", "m": "mask"}


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
                key = "pupil" if (ch == "e" and p["eyes"] != "closed") else "mask_d"
            put(c, hx - 4 + col, top + r, PAL[key])
    # the mask's knot tails flutter behind the head
    k = int(p.get("phase", 0) * 2) % 2
    put(c, hx - 6, top + 2 + k, PAL["mask_d"]); put(c, hx - 7, top + 3 - k, PAL["mask"])


def coin(c, x, y):
    put(c, x, y, PAL["coin"]); put(c, x + 1, y, PAL["coin_d"]); put(c, x, y - 1, PAL["coin_l"])


def sack(c, p, g):
    """The loot bag slung over the back shoulder; the front hand holds its neck on the shoulder."""
    if p.get("drop") is not None:      # death: the bag lies on the floor, coins spilt round it
        x, y = int(p["drop"][0]), int(p["drop"][1])
        for yy in range(y - 7, y + 1):
            for xx in range(x - 6, x + 6):
                if ((xx - x) / 6.0) ** 2 + ((yy - (y - 3)) / 4.0) ** 2 <= 1.0:
                    put(c, xx, yy, PAL["sack_d"] if yy > y - 2 else PAL["sack"])
        for k, (dx, dy) in enumerate(p.get("spill", [])):
            coin(c, x + dx, y + dy)
        return
    sx, sy = g["sh_back"]
    bob = int(p.get("sack_bob", 0))
    cx, cy = sx - 5, sy - 6 + bob            # bag centre, up and behind the shoulder
    for yy in range(cy - 6, cy + 6):
        for xx in range(cx - 6, cx + 6):
            d = ((xx - cx) / 6.0) ** 2 + ((yy - cy) / 5.6) ** 2
            if d <= 1.0:
                col = PAL["sack_l"] if (xx < cx - 1 and yy < cy - 1) else (PAL["sack_d"] if (xx > cx + 2 or yy > cy + 3) else PAL["sack"])
                put(c, xx, yy, col)
    for yy in (cy - 1, cy + 2):              # burlap stitching
        put(c, cx - 2, yy, PAL["sack_d"]); put(c, cx + 1, yy + 1, PAL["sack_d"])
    # the tied neck runs forward to the front hand on the shoulder; coins peep out of it
    nx, ny = cx + 6, cy - 2
    hx, hy = g["hand_front"]
    for t in range(0, 5):
        put(c, round(nx + (hx - nx) * t / 4), round(ny + (hy - ny) * t / 4), PAL["rope"])
    coin(c, nx - 1, ny - 1); coin(c, nx + 1, ny - 2)
    if p.get("glint"):
        put(c, nx, ny - 3, PAL["coin_l"])
    for k, (dx, dy) in enumerate(p.get("spill", [])):   # coins flying out (hurt)
        coin(c, cx + dx, cy + dy)


def fx(c, p, g):
    if p.get("fx") == "dust":                 # little dust kicks behind the running feet
        x, y = g["foot_back"]
        put(c, x - 3, y, (230, 220, 190, 150)); put(c, x - 5, y - 1, (230, 220, 190, 110))


CHAR = {"pal": PAL, "body": "tunic", "head": head, "held": sack, "fx": fx}
HOLD = (-1, -4)   # the front hand up on the shoulder, gripping the bag's neck


def move(i):
    p = run_pose(i, lean=3, hands=((-3, 5), HOLD), fx="dust" if i % 4 == 0 else None)
    p["sack_bob"] = (0, 1, 1, 0, 0, 1, 1, 0)[i]   # the bag bounces with the stride
    p["glint"] = i in (2, 6)
    return mf.draw(CHAR, p)


def frame(**kw):
    extra = {k: kw.pop(k) for k in ("sack_bob", "glint", "spill", "drop") if k in kw}
    p = pose(**kw)
    p.update(extra)
    if p.get("drop") is None:
        return mf.draw(CHAR, p)
    # death: the dropped bag lies on the floor in its own outlined layer UNDER the body, so the body's
    # "lie" rotation does not carry it away (it vanished in frames 3-4 otherwise)
    bag = mf.Canvas(mf.W, mf.H)
    sack(bag, p, None)
    bag.outline(mf.OUTLINE if hasattr(mf, "OUTLINE") else "#14111c")
    body = mf.draw({**CHAR, "held": None}, {**p, "drop": None, "spill": []})
    bag.img.alpha_composite(body.img)
    return bag


def attack(i):
    # it never fights: hugs the bag and glances back over its shoulder
    return [
        frame(bob=1, lean=-1, hands=((-2, 4), HOLD), head=(-1, 0), sack_bob=1),
        frame(bob=2, lean=-2, hands=((-1, 3), HOLD), head=(-2, 0), sack_bob=1, glint=True),
        frame(bob=2, lean=-2, hands=((-1, 3), HOLD), head=(-2, 0), sack_bob=2),
        frame(bob=1, lean=1, hands=((-2, 5), HOLD), sack_bob=0),
    ][i]


def hurt(i):
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), HOLD), eyes="wince",
              flash=0.75, sack_bob=-1, spill=[(-3, -8), (2, -9)]),
        frame(bob=1, lean=-1, hands=((-3, 5), HOLD), eyes="wince", sack_bob=1, spill=[(-6, -11), (4, -12)]),
    ][i]


SPILL = [(-8, 0), (-5, -2), (-2, 0), (3, -1), (6, 0), (8, -2), (0, -3)]


def death(i):
    floor = (int(mf.ROOT_X) + 12, int(mf.SOLE))   # in front of the body: the lying body covers the left
    return [
        frame(bob=1, lean=-2, head=(-1, 0), feet=((-4, 0), (2, 0)), hands=((-4, 3), HOLD), eyes="x", flash=0.5,
              spill=[(-3, -9), (3, -10)]),
        frame(bob=3, lean=-1, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), eyes="x", drop=floor, spill=SPILL[:3]),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (2, 7)), eyes="x", lie=0.4, drop=floor, spill=SPILL[:5]),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), eyes="x", lie=0.85, drop=floor, spill=SPILL),
        frame(bob=3, lean=-2, feet=((-3, 0), (3, 0)), hands=((-3, 6), (3, 7)), eyes="x", lie=1.0, drop=floor, spill=SPILL),
    ][i]


HB = {"shape": "rect", "center": [24.0, 44.0]}
ANIMATIONS = [
    ("move", [move(i) for i in range(8)], 14, True, {"hitbox": {**HB, "active": [0, 7]}}),
    ("attack", [attack(i) for i in range(4)], 8, False, {"durations_ms": [160, 200, 200, 140], "hitbox": {**HB, "active": [0, 3]}}),
    ("hurt", [hurt(i) for i in range(2)], 12, False, {"durations_ms": [80, 120], "hitbox": {**HB, "active": [0, 1]}}),
    ("death", [death(i) for i in range(5)], 8, False, {"durations_ms": [100, 120, 100, 100, 300], "hitbox": {**HB, "active": [0, 4]}}),
]


def main() -> None:
    export(HERE, NAME, ANIMATIONS, anchor=ANCHOR, ground=True, preview_scale=4, body="move")
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["variant_of"] = "goblin"
    meta.write_text(json.dumps(m, indent=2))
    print(f"strip: {HERE / f'{NAME}_strip.png'}")


if __name__ == "__main__":
    main()
