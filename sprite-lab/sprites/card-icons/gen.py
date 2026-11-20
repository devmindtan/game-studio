#!/usr/bin/env python3
"""Generator cho "card-icons": icon thẻ 24x24 của Bách Ải (người dùng 2026-11-20: icon cũ 16 px nhỏ, chung chung,
trùng với icon chỉ số). Mỗi icon = một animation 1 frame tên trùng id thẻ; UiIcons đọc sheet này trước ui-icons.

Quy tắc (tham khảo các bộ 24x24 trên itch.io, ghi ở games/bach-ai/design/card-rarity.md "Icon thẻ"):
- một vật thể chính đọc được ở 1x + một hiệu ứng phụ; không viền khung, không chữ (khung do UI vẽ theo bậc);
- ánh sáng từ trên-trái: mặt sáng `l`, thân `m`, bóng `d`; viền tối 1 px quanh mọi thứ;
- mỗi hệ một bảng màu: thép, đất, thánh quang, gió, lửa, băng, sét, hư không.
Neo (12, 12) = tâm ô. Chạy: gamekit art run card-icons
"""

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

NAME = "card-icons"
S = 24
OUTLINE = "#14111c"

STEEL = {"l": "#f4f8ff", "m": "#b8c4d8", "d": "#6a7590", "x": "#3a4058"}
EARTH = {"l": "#e8b878", "m": "#a8703a", "d": "#6a4020", "x": "#3e2414"}
GOLD = {"l": "#fff4b0", "m": "#f2c14e", "d": "#c0801a", "x": "#7a4a10"}
HOLY = {"l": "#ffffff", "m": "#fff2a0", "d": "#f2c14e"}
WIND = {"l": "#ffffff", "m": "#bfeaff", "d": "#6fb7e0"}
FIRE = {"l": "#fff2a0", "m": "#ff9a2a", "d": "#d9361e", "x": "#7a1410"}
WOOD = {"m": "#8a5a2a", "d": "#5a3618"}
RED = {"l": "#ff9a8a", "m": "#e0402e", "d": "#8a1a18"}


def new():
    return Canvas(S, S)


def done(c):
    return c.outline(OUTLINE)


# --- knight skills -------------------------------------------------------------------------------------------

def blade_arc():
    """Chém kiếm: a short sword mid-swing leaving a wide white crescent."""
    c = new()
    c.ellipse(2, 3, 21, 22, WIND["d"], fill=False)          # the slash crescent, thick on the outside
    c.ellipse(3, 3, 20, 21, WIND["m"], fill=False)
    c.ellipse(4, 4, 19, 20, WIND["l"], fill=False)
    c.rect(9, 5, 23, 23, (0, 0, 0, 0))                       # keep only the left arc
    c.rect(4, 15, 23, 23, (0, 0, 0, 0))
    c.line(9, 15, 19, 5, STEEL["m"], 2)                      # blade
    c.line(10, 15, 19, 6, STEEL["l"])
    c.line(20, 4, 21, 3, STEEL["l"])
    c.line(6, 15, 11, 20, GOLD["m"], 2)                       # guard
    c.line(6, 18, 8, 20, WOOD["m"], 2)                        # grip
    c.pixel(5, 21, GOLD["d"]); c.pixel(6, 21, GOLD["d"])
    return done(c)


def whirlwind():
    """Lốc xoáy: a wind funnel, wide on top, two blades caught in its swirl."""
    c = new()
    rows = [(2, 20, 3), (4, 18, 6), (6, 16, 9), (8, 15, 12), (9, 14, 15), (10, 13, 18), (11, 12, 21)]
    for k, (x0, x1, y) in enumerate(rows):
        c.ellipse(x0, y - 1, x1 + 2, y + 1, (WIND["d"], WIND["m"])[k % 2])
        c.line(x0 + 1, y - 1, x1 - 3, y - 1, WIND["l"])
    c.line(1, 8, 6, 5, STEEL["m"], 2); c.line(1, 8, 6, 5, STEEL["l"])           # a blade flung left
    c.line(17, 15, 22, 12, STEEL["m"], 2); c.line(17, 15, 22, 12, STEEL["l"])   # and right
    return done(c)


def earth_strike():
    """Đất nứt: the ground splits, the crack glows, two rocks burst up out of it."""
    c = new()
    c.rect(0, 15, 23, 22, EARTH["m"])
    c.line(0, 15, 23, 15, EARTH["l"])
    c.rect(0, 21, 23, 22, EARTH["d"])
    c.polygon([(10, 15), (14, 15), (13, 17), (15, 19), (12, 22), (11, 19), (9, 17)], EARTH["x"])
    c.line(12, 16, 12, 20, FIRE["d"])
    c.polygon([(7, 6), (11, 4), (13, 8), (10, 11), (7, 10)], EARTH["m"])
    c.line(8, 6, 11, 5, EARTH["l"]); c.line(8, 7, 8, 9, EARTH["l"])
    c.polygon([(14, 2), (17, 1), (18, 4), (16, 6), (14, 5)], EARTH["d"])
    c.pixel(15, 2, EARTH["l"])
    c.pixel(6, 12, EARTH["d"]); c.pixel(18, 10, EARTH["d"])   # loose grit
    return done(c)


def ground_slam():
    """Dậm đất: an armoured boot stamping down, a shockwave ring spreading at its sole."""
    c = new()
    c.ellipse(1, 16, 22, 22, EARTH["d"], fill=False)
    c.ellipse(3, 17, 20, 21, EARTH["m"], fill=False)
    c.rect(8, 2, 15, 12, STEEL["m"])                          # greave
    c.rect(8, 2, 9, 12, STEEL["l"])
    c.rect(14, 2, 15, 12, STEEL["d"])
    c.rect(7, 12, 19, 17, STEEL["m"])                         # boot
    c.rect(7, 12, 19, 12, STEEL["l"])
    c.rect(7, 16, 19, 17, STEEL["d"])
    c.line(4, 6, 6, 9, WIND["l"]); c.line(19, 6, 17, 9, WIND["l"])   # downward speed lines
    c.line(3, 10, 5, 12, WIND["m"]); c.line(20, 10, 18, 12, WIND["m"])
    return done(c)


def cleave_wave():
    """Sóng kiếm: a crescent of blue sword energy flying right, trailing streaks."""
    c = new()
    c.ellipse(4, 1, 21, 22, WIND["d"])
    c.ellipse(2, 1, 18, 22, (0, 0, 0, 0))
    c.ellipse(5, 2, 20, 21, WIND["m"], fill=False)
    c.ellipse(6, 3, 20, 20, WIND["l"], fill=False)
    c.ellipse(1, 3, 17, 20, (0, 0, 0, 0))
    for y, x0 in ((7, 2), (11, 0), (15, 2)):
        c.line(x0, y, x0 + 7, y, WIND["m"])
        c.line(x0 + 4, y, x0 + 7, y, WIND["l"])
    return done(c)


def holy_column():
    """Cột thánh quang: a pillar of light falling from a gold halo onto the ground."""
    c = new()
    c.rect(8, 4, 15, 21, HOLY["d"])
    c.rect(9, 4, 14, 21, HOLY["m"])
    c.rect(11, 4, 12, 21, HOLY["l"])
    c.ellipse(4, 1, 19, 6, GOLD["m"], fill=False)
    c.ellipse(5, 2, 18, 5, GOLD["l"], fill=False)
    c.ellipse(3, 19, 20, 23, HOLY["d"])
    c.ellipse(6, 20, 17, 22, HOLY["l"])
    for (x, y) in ((3, 10), (20, 13), (5, 15), (18, 8)):
        c.pixel(x, y, HOLY["l"]); c.pixel(x, y - 1, HOLY["m"]); c.pixel(x, y + 1, HOLY["m"])
    return done(c)


def dash():
    """Lướt: a figure-less burst: three red chevrons with motion streaks behind."""
    c = new()
    for k, x in enumerate((6, 11, 16)):
        col = (RED["d"], RED["m"], RED["l"])[k]
        c.polygon([(x, 5), (x + 4, 12), (x, 19), (x - 2, 19), (x + 2, 12), (x - 2, 5)], col)
    for y in (8, 12, 16):
        c.line(0, y, 3, y, WIND["m"])
    return done(c)


def earthquake():
    """Địa chấn: the ground breaks into tilted slabs with a glowing rift between them."""
    c = new()
    c.polygon([(0, 14), (10, 10), (11, 22), (0, 22)], EARTH["m"])
    c.line(0, 14, 10, 10, EARTH["l"])
    c.polygon([(13, 9), (23, 13), (23, 22), (12, 22)], EARTH["d"])
    c.line(13, 9, 23, 13, EARTH["m"])
    c.polygon([(10, 10), (13, 9), (12, 22), (11, 22)], FIRE["d"])
    c.line(11, 11, 11, 20, FIRE["m"]); c.pixel(12, 13, FIRE["l"]); c.pixel(11, 16, FIRE["l"])
    for (x, y) in ((5, 5), (17, 4), (11, 2)):
        c.rect(x, y, x + 2, y + 2, EARTH["m"]); c.pixel(x, y, EARTH["l"])
    return done(c)


def solar_ray():
    """Thái dương xạ: a blazing sun disc firing a long beam to the right."""
    c = new()
    c.rect(9, 10, 23, 13, HOLY["d"])
    c.rect(9, 11, 23, 12, HOLY["l"])
    for k in range(8):
        import math
        a = k * math.pi / 4
        c.line(7 + round(math.cos(a) * 4), 12 + round(math.sin(a) * 4),
               7 + round(math.cos(a) * 7), 12 + round(math.sin(a) * 7), GOLD["m"])
    c.ellipse(3, 8, 11, 16, GOLD["d"])
    c.ellipse(3, 8, 10, 15, GOLD["m"])
    c.ellipse(4, 9, 8, 13, GOLD["l"])
    return done(c)


def god_hammer():
    """Búa thần: a heavy gold-banded war hammer crackling with light."""
    c = new()
    c.line(12, 10, 12, 23, WOOD["m"], 2)
    c.line(12, 10, 12, 23, WOOD["d"])
    c.rect(3, 3, 20, 10, STEEL["m"])
    c.rect(3, 3, 20, 4, STEEL["l"])
    c.rect(3, 9, 20, 10, STEEL["d"])
    c.rect(10, 3, 14, 10, GOLD["m"])
    c.rect(10, 3, 14, 4, GOLD["l"])
    c.pixel(12, 6, RED["m"]); c.pixel(12, 7, RED["d"])
    c.line(1, 1, 3, 3, HOLY["m"]); c.line(22, 1, 20, 3, HOLY["m"]); c.line(21, 12, 19, 10, HOLY["m"])
    return done(c)


ICONS = {f.__name__: f for f in (blade_arc, whirlwind, earth_strike, ground_slam, cleave_wave, holy_column, dash,
                                 earthquake, solar_ray, god_hammer)}

if __name__ == "__main__":
    anims = [(n, [f()], 1, False, {}) for n, f in ICONS.items()]
    export(HERE, NAME, anims, anchor=(12.0, 12.0), preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
