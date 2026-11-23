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
ICE = {"l": "#ffffff", "m": "#9ee0ff", "d": "#3f8fe0", "x": "#1f4f8a"}
BOLT = {"l": "#ffffff", "m": "#fff27a", "d": "#f2b64a", "x": "#a8661f"}
ARC = {"l": "#f4e0ff", "m": "#c38df5", "d": "#7a4ad8", "x": "#3a2070"}
VOID = {"l": "#e0b8ff", "m": "#7a3ab8", "d": "#3a1660", "x": "#14081e"}
LEAF = {"l": "#c8f07a", "m": "#5ab83a", "d": "#2a6a28"}
HEART = {"l": "#ffb0b0", "m": "#e0364a", "d": "#8a1a2a"}
FEATHER = {"l": "#ffffff", "m": "#d8e8f0", "d": "#8aa0b8"}
STONE = {"l": "#d8cfc0", "m": "#8a7e70", "d": "#4e463e"}


def new():
    return Canvas(S, S)


def done(c):
    return c.outline(OUTLINE)


def sword(c, hilt, tip, guard=3, grip=3):
    """A straight sword on ONE 45-degree axis from [hilt] (guard centre) to [tip], placed pixel by pixel:
    every part (blade, guard, grip) is two pixels thick with its second pixel on the SAME side (+x), so the
    blade comes out of the guard's middle (user 2026-11-20, twice: width-2 lines thickened each part on a
    different side and the blade sat off its handle). Only diagonal swords: tip - hilt must be (+-n, +-n)."""
    (hx, hy), (tx, ty) = hilt, tip
    n = abs(tx - hx)
    assert n == abs(ty - hy) and n > 0, "sword(): the axis must be exactly 45 degrees"
    dx, dy = (1 if tx > hx else -1), (1 if ty > hy else -1)

    def two(x, y, col, col2=None):
        c.pixel(x, y, col)
        c.pixel(x + 1, y, col2 or col)

    for k in range(1, n + 1):                              # blade: light edge + steel body
        two(hx + dx * k, hy + dy * k, STEEL["l"], STEEL["m"])
    c.pixel(tx + (1 if dx > 0 else 0), ty, STEEL["l"])
    for k in range(-guard, guard + 1):                     # guard: perpendicular through the hilt
        two(hx + dx * k, hy - dy * k, GOLD["m"], GOLD["d"])
    for k in range(1, grip + 1):                           # grip behind the hilt, pommel at its end
        two(hx - dx * k, hy - dy * k, WOOD["m"], WOOD["d"])
    two(hx - dx * (grip + 1), hy - dy * (grip + 1), GOLD["d"])


# --- knight skills -------------------------------------------------------------------------------------------

def blade_arc():
    """Chém kiếm: a short sword mid-swing leaving a wide white crescent."""
    c = new()
    c.ellipse(2, 3, 21, 22, WIND["d"], fill=False)          # the slash crescent, thick on the outside
    c.ellipse(3, 3, 20, 21, WIND["m"], fill=False)
    c.ellipse(4, 4, 19, 20, WIND["l"], fill=False)
    c.rect(9, 5, 23, 23, (0, 0, 0, 0))                       # keep only the left arc
    c.rect(4, 15, 23, 23, (0, 0, 0, 0))
    sword(c, (8, 15), (18, 5))
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


# --- mage skills ---------------------------------------------------------------------------------------------

def arcane_bolt():
    """Tia phép: a violet star-tipped bolt streaking up-right with a sparkle trail."""
    c = new()
    for k, (x, y) in enumerate(((3, 20), (6, 17), (9, 14))):
        c.rect(x, y, x + 2 - (k == 0), y + 2 - (k == 0), (ARC["d"], ARC["m"], ARC["m"])[k])
    c.polygon([(17, 2), (19, 8), (23, 9), (19, 11), (17, 17), (15, 11), (11, 9), (15, 8)], ARC["m"])
    c.polygon([(17, 5), (18, 8), (20, 9), (18, 10), (17, 13), (16, 10), (14, 9), (16, 8)], ARC["l"])
    c.pixel(17, 9, "#ffffff")
    c.line(10, 14, 14, 11, ARC["m"], 2)
    return done(c)


def fireball():
    """Cầu lửa: a round fireball with a hot core flying left-down, flames streaming behind."""
    c = new()
    c.polygon([(22, 1), (14, 6), (18, 9), (11, 10), (16, 14), (21, 9), (17, 7)], FIRE["d"])
    c.polygon([(20, 3), (14, 7), (16, 9), (12, 11), (16, 12)], FIRE["m"])
    c.ellipse(2, 9, 15, 22, FIRE["d"])
    c.ellipse(3, 10, 14, 21, FIRE["m"])
    c.ellipse(4, 12, 11, 19, FIRE["l"])
    c.ellipse(5, 13, 8, 16, "#ffffff")
    return done(c)


def frost_nova():
    """Băng nổ: a six-armed ice crystal bursting, shards flying out."""
    c = new()
    import math
    for k in range(6):
        a = k * math.pi / 3 + math.pi / 6
        x1, y1 = 12 + round(math.cos(a) * 10), 12 + round(math.sin(a) * 10)
        c.line(12, 12, x1, y1, ICE["d"], 3)
        c.line(12, 12, x1, y1, ICE["m"], 1)
        c.pixel(x1, y1, ICE["l"])
    c.ellipse(8, 8, 16, 16, ICE["m"])
    c.ellipse(9, 9, 14, 14, ICE["l"])
    return done(c)


def lightning():
    """Sét đánh: a single bright bolt striking down from a dark cloud onto a spark."""
    c = new()
    c.ellipse(1, 1, 13, 8, STONE["d"]); c.ellipse(8, 0, 22, 8, STONE["m"]); c.ellipse(10, 1, 18, 5, STONE["l"])
    c.polygon([(12, 7), (16, 7), (13, 13), (17, 13), (9, 23), (11, 15), (7, 15)], BOLT["d"])
    c.polygon([(13, 8), (15, 8), (12, 14), (15, 14), (10, 21), (11, 15), (8, 15)], BOLT["m"])
    c.line(13, 9, 11, 13, BOLT["l"])
    return done(c)


def thunder_javelin():
    """Giáo sấm: a javelin of lightning, a gold spear tip, bolts crackling along the shaft."""
    c = new()
    c.line(2, 21, 16, 7, BOLT["x"], 2)
    c.line(3, 21, 16, 8, BOLT["d"])
    c.polygon([(15, 4), (21, 2), (19, 8), (17, 9), (14, 6)], BOLT["m"])
    c.polygon([(17, 4), (20, 3), (19, 6)], BOLT["l"])
    for (x, y) in ((6, 14), (10, 10)):
        c.line(x, y, x - 2, y - 3, BOLT["m"]); c.line(x - 2, y - 3, x, y - 4, BOLT["m"])
        c.line(x + 1, y + 2, x + 4, y + 3, BOLT["l"])
    return done(c)


def meteor():
    """Mưa thiên thạch: a burning rock diving down-left, a second smaller one behind."""
    c = new()
    c.polygon([(23, 0), (13, 7), (17, 12), (23, 5)], FIRE["d"])
    c.polygon([(22, 2), (15, 8), (17, 10)], FIRE["m"])
    c.ellipse(5, 6, 18, 19, STONE["d"])
    c.ellipse(6, 7, 17, 17, STONE["m"])
    c.ellipse(7, 8, 12, 12, STONE["l"])
    c.pixel(13, 13, FIRE["m"]); c.pixel(9, 15, FIRE["m"]); c.pixel(14, 10, FIRE["d"])
    c.line(15, 9, 17, 11, FIRE["l"])
    c.ellipse(2, 18, 6, 22, STONE["m"]); c.pixel(3, 19, STONE["l"])
    return done(c)


def void_orb():
    """Cầu hư không: a black orb with a violet rim, ringed by a tilted void halo."""
    c = new()
    c.ellipse(1, 9, 22, 15, VOID["m"], fill=False)
    c.ellipse(4, 4, 19, 19, VOID["m"])
    c.ellipse(5, 5, 18, 18, VOID["x"])
    c.ellipse(6, 6, 11, 10, VOID["d"])
    c.pixel(7, 7, VOID["l"])
    c.line(1, 12, 4, 13, VOID["l"]); c.line(19, 11, 22, 12, VOID["l"])
    c.rect(5, 13, 18, 13, VOID["m"])
    return done(c)


def blizzard():
    """Bão tuyết: a swirling ice storm, snowflakes and icicles whipping round."""
    c = new()
    c.ellipse(2, 2, 21, 21, ICE["d"], fill=False)
    c.ellipse(5, 5, 18, 18, ICE["m"], fill=False)
    c.rect(12, 1, 23, 10, (0, 0, 0, 0)); c.rect(1, 13, 10, 23, (0, 0, 0, 0))
    c.ellipse(9, 9, 14, 14, ICE["l"])
    for (x, y) in ((4, 4), (19, 19), (19, 5), (4, 18)):
        c.line(x - 1, y, x + 1, y, ICE["l"]); c.line(x, y - 1, x, y + 1, ICE["l"])
    c.polygon([(14, 2), (17, 2), (15, 8)], ICE["m"])
    c.polygon([(7, 16), (10, 22), (6, 22)], ICE["m"])
    return done(c)


def storm():
    """Bão sét: a heavy storm cloud loosing three bolts at once."""
    c = new()
    c.ellipse(0, 1, 10, 9, STONE["d"]); c.ellipse(6, 0, 18, 9, STONE["m"]); c.ellipse(13, 2, 23, 10, STONE["d"])
    c.ellipse(8, 1, 15, 5, STONE["l"])
    for x in (4, 11, 18):
        c.polygon([(x, 9), (x + 3, 9), (x + 1, 14), (x + 3, 14), (x - 1, 22), (x, 15), (x - 2, 15)], BOLT["m"])
        c.line(x + 1, 10, x, 14, BOLT["l"])
    return done(c)


# --- stat cards (no reuse of the HUD stat icons: each card shows what grants the stat) ----------------------

def back_slash():
    """Chém ngược: the hero's blade points right while a second slash arc cuts behind, to the left."""
    c = new()
    c.ellipse(0, 2, 12, 21, WIND["d"], fill=False)
    c.ellipse(1, 3, 12, 20, WIND["m"], fill=False)
    c.ellipse(2, 4, 12, 19, WIND["l"], fill=False)
    c.rect(7, 2, 12, 21, (0, 0, 0, 0))
    c.polygon([(3, 19), (8, 20), (4, 23)], WIND["l"])
    c.line(12, 12, 22, 12, STEEL["m"], 2); c.line(12, 11, 22, 11, STEEL["l"])
    c.rect(10, 8, 11, 15, GOLD["m"]); c.rect(7, 11, 9, 12, WOOD["m"])
    return done(c)


def sharpen():
    """Mài kiếm: a blade drawn across a whetstone, sparks flying."""
    c = new()
    c.rect(2, 16, 21, 21, STONE["m"]); c.line(2, 16, 21, 16, STONE["l"]); c.rect(2, 20, 21, 21, STONE["d"])
    sword(c, (7, 13), (16, 4))
    for (x, y) in ((13, 13), (16, 12), (18, 14), (15, 9)):
        c.pixel(x, y, BOLT["l"]); c.pixel(x + 1, y - 1, BOLT["m"])
    return done(c)


def haste():
    """Nhanh tay: an hourglass whose sand runs fast, speed lines beside it."""
    c = new()
    c.rect(6, 2, 17, 3, WOOD["m"]); c.rect(6, 20, 17, 21, WOOD["m"])
    c.polygon([(7, 4), (16, 4), (12, 11), (11, 11)], FEATHER["d"])
    c.polygon([(11, 12), (12, 12), (16, 19), (7, 19)], FEATHER["d"])
    c.polygon([(9, 5), (14, 5), (12, 9), (11, 9)], GOLD["m"])
    c.polygon([(11, 15), (12, 15), (15, 19), (8, 19)], GOLD["m"])
    c.line(11, 10, 11, 15, GOLD["l"])
    c.line(18, 8, 22, 8, WIND["m"]); c.line(19, 12, 23, 12, WIND["l"]); c.line(18, 16, 22, 16, WIND["m"])
    return done(c)


def reach():
    """Tầm với: a long spear reaching across the whole tile, a ring at its tip showing the reach."""
    c = new()
    c.line(2, 21, 17, 6, WOOD["m"], 2)
    c.polygon([(16, 4), (22, 1), (19, 7), (17, 8)], STEEL["m"]); c.line(17, 5, 21, 2, STEEL["l"])
    c.ellipse(14, 0, 23, 9, WIND["m"], fill=False)
    c.line(1, 18, 4, 21, WIND["m"])
    return done(c)


def vitality():
    """Sinh lực: a heart with a big green cross on it (more max hp), not the plain hp heart."""
    c = new()
    c.ellipse(2, 3, 12, 13, HEART["m"]); c.ellipse(11, 3, 21, 13, HEART["m"])
    c.polygon([(2, 9), (21, 9), (12, 21)], HEART["m"])
    c.ellipse(4, 5, 8, 8, HEART["l"])
    c.polygon([(12, 21), (21, 9), (19, 12)], HEART["d"])
    c.rect(14, 12, 23, 15, LEAF["d"]); c.rect(17, 9, 20, 18, LEAF["d"])
    c.rect(15, 13, 22, 14, LEAF["l"]); c.rect(18, 10, 19, 17, LEAF["l"])
    return done(c)


def swift():
    """Nhẹ chân: a white feather drifting, speed lines behind (lighter, faster)."""
    c = new()
    c.polygon([(20, 2), (23, 4), (13, 15), (6, 20), (9, 13)], FEATHER["m"])
    c.polygon([(20, 2), (22, 3), (14, 12), (10, 14)], FEATHER["l"])
    c.line(20, 3, 5, 21, FEATHER["d"])
    c.line(1, 8, 6, 8, WIND["m"]); c.line(0, 12, 5, 12, WIND["l"]); c.line(1, 16, 4, 16, WIND["m"])
    return done(c)


def magnet():
    """Nam châm: a horseshoe magnet with gems flying into it (not the HUD magnet alone)."""
    c = new()
    c.ellipse(2, 2, 16, 16, RED["m"], fill=False); c.ellipse(3, 3, 15, 15, RED["m"], fill=False)
    c.ellipse(4, 4, 14, 14, RED["l"], fill=False)
    c.rect(2, 9, 16, 16, (0, 0, 0, 0))
    c.rect(2, 9, 5, 15, RED["m"]); c.rect(13, 9, 16, 15, RED["m"])
    c.rect(2, 13, 5, 15, STEEL["l"]); c.rect(13, 13, 16, 15, STEEL["l"])
    for (x, y, col) in ((19, 18, ICE["m"]), (9, 20, ICE["m"]), (20, 10, ICE["l"])):
        c.polygon([(x, y - 2), (x + 2, y), (x, y + 2), (x - 2, y)], col)
    return done(c)


def regen():
    """Hồi phục: a sprouting leaf with green healing drops rising."""
    c = new()
    c.line(11, 22, 11, 12, WOOD["m"], 2)
    c.polygon([(11, 13), (3, 8), (2, 15), (7, 17)], LEAF["m"]); c.line(10, 13, 4, 10, LEAF["l"])
    c.polygon([(12, 11), (20, 5), (22, 12), (15, 15)], LEAF["d"]); c.line(13, 11, 19, 7, LEAF["m"])
    for (x, y) in ((6, 3), (16, 1), (19, 16)):
        c.polygon([(x, y), (x + 2, y + 3), (x, y + 4), (x - 2, y + 3)], LEAF["l"])
    return done(c)


def toughness():
    """Da thép: a riveted steel breastplate, an incoming arrow bouncing off it."""
    c = new()
    c.polygon([(4, 4), (19, 4), (19, 13), (12, 21), (4, 13)], STEEL["m"])
    c.polygon([(4, 4), (11, 4), (11, 20), (4, 13)], STEEL["l"])
    c.polygon([(12, 4), (19, 4), (19, 13), (12, 21)], STEEL["d"])
    for (x, y) in ((6, 6), (17, 6), (6, 12), (17, 12)):
        c.pixel(x, y, STEEL["x"])
    c.line(20, 1, 23, 4, WOOD["m"]); c.polygon([(18, 1), (21, 0), (20, 3)], STEEL["l"])
    return done(c)


def extra_strike():
    """Thêm đòn: two blades side by side and a gold plus: one more hit."""
    c = new()
    for x in (5, 11):
        c.line(x, 2, x, 15, STEEL["m"], 2); c.line(x, 2, x, 15, STEEL["l"])
        c.rect(x - 2, 16, x + 2, 17, GOLD["m"]); c.rect(x, 18, x + 1, 21, WOOD["m"])
    c.rect(15, 9, 23, 12, GOLD["d"]); c.rect(18, 6, 20, 15, GOLD["d"])
    c.rect(16, 10, 22, 11, GOLD["l"]); c.rect(18, 7, 20, 14, GOLD["l"])
    return done(c)


def arcane_power():
    """Pháp lực: an open spellbook with a violet rune rising from its pages."""
    c = new()
    c.polygon([(1, 14), (11, 17), (11, 22), (1, 19)], ARC["d"])
    c.polygon([(12, 17), (22, 14), (22, 19), (12, 22)], ARC["d"])
    c.polygon([(2, 13), (11, 16), (11, 20), (2, 17)], FEATHER["m"])
    c.polygon([(12, 16), (21, 13), (21, 17), (12, 20)], FEATHER["l"])
    c.polygon([(11, 2), (15, 7), (11, 12), (7, 7)], ARC["m"])
    c.polygon([(11, 4), (13, 7), (11, 10), (9, 7)], ARC["l"])
    return done(c)


def quick_cast():
    """Niệm nhanh: a wand flicking a spark, a clock hand sweeping behind it."""
    c = new()
    c.ellipse(9, 1, 22, 14, ARC["d"], fill=False)
    c.line(15, 7, 15, 3, ARC["l"]); c.line(15, 7, 19, 9, ARC["m"])
    c.line(2, 21, 11, 12, WOOD["m"], 2)
    c.polygon([(11, 9), (14, 12), (11, 15), (8, 12)], BOLT["m"]); c.pixel(11, 12, BOLT["l"])
    return done(c)


def wide_magic():
    """Mở rộng: a magic circle with arrows pushing outward."""
    c = new()
    c.ellipse(5, 5, 18, 18, ARC["m"], fill=False)
    c.ellipse(8, 8, 15, 15, ARC["l"], fill=False)
    c.ellipse(10, 10, 13, 13, ARC["m"])
    for (pts) in ([(12, 0), (15, 3), (9, 3)], [(12, 23), (15, 20), (9, 20)], [(0, 12), (3, 9), (3, 15)], [(23, 12), (20, 9), (20, 15)]):
        c.polygon(pts, ARC["l"])
    return done(c)


def mana_shield():
    """Áo phép: a blue magic bubble with a rune shield inside."""
    c = new()
    c.ellipse(1, 1, 22, 22, ICE["d"], fill=False)
    c.ellipse(2, 2, 21, 21, ICE["m"], fill=False)
    c.line(5, 6, 8, 3, ICE["l"])
    c.polygon([(7, 7), (16, 7), (16, 13), (11, 18), (7, 13)], ARC["m"])
    c.polygon([(7, 7), (11, 7), (11, 17), (7, 13)], ARC["l"])
    c.pixel(11, 11, "#ffffff")
    return done(c)


def multicast():
    """Thêm phép: a violet spark splitting into three elemental orbs (fire, ice, lightning)."""
    c = new()
    c.polygon([(12, 9), (14, 12), (12, 15), (10, 12)], ARC["l"])
    for (x, y, col) in ((1, 14, FIRE), (8, 1, ICE), (15, 14, BOLT)):
        c.ellipse(x, y, x + 7, y + 7, col["d"]); c.ellipse(x, y, x + 6, y + 6, col["m"])
        c.ellipse(x + 1, y + 1, x + 3, y + 3, col["l"])
    c.pixel(9, 14, ARC["m"]); c.pixel(12, 8, ARC["m"]); c.pixel(15, 14, ARC["m"])
    return done(c)


# --- special cards (milestone rewards; each its own icon, user 2026-11-20) ---------------------------------

def sp_aegis_helm():
    """Thần hộ: a ghostly blue shield shimmering in front of a helmet."""
    c = new()
    c.ellipse(4, 2, 19, 15, STEEL["m"]); c.rect(4, 9, 19, 15, STEEL["m"]); c.ellipse(5, 3, 11, 8, STEEL["l"])
    c.rect(6, 10, 17, 11, STEEL["x"])
    c.polygon([(9, 12), (22, 12), (22, 18), (15, 23), (9, 18)], ICE["d"])
    c.polygon([(10, 13), (21, 13), (21, 18), (15, 22), (10, 18)], ICE["m"])
    c.line(11, 14, 14, 14, ICE["l"]); c.line(11, 15, 11, 17, ICE["l"])
    return done(c)


def sp_aegis_chest():
    """Phản chấn: a breastplate releasing a ring of force outward."""
    c = new()
    c.ellipse(0, 0, 23, 23, BOLT["d"], fill=False)
    c.ellipse(2, 2, 21, 21, BOLT["m"], fill=False)
    c.polygon([(6, 6), (17, 6), (17, 13), (12, 18), (6, 13)], STEEL["m"])
    c.polygon([(6, 6), (11, 6), (11, 17), (6, 13)], STEEL["l"])
    c.pixel(12, 10, BOLT["l"]); c.pixel(12, 11, BOLT["m"])
    return done(c)


def sp_aegis_greaves():
    """Bàn thạch: a stone shell closing round the hero, cracks of orange light at its seams."""
    c = new()
    c.ellipse(2, 3, 21, 22, STONE["d"]); c.ellipse(3, 4, 20, 20, STONE["m"]); c.ellipse(5, 5, 11, 10, STONE["l"])
    c.line(12, 4, 10, 10, FIRE["m"]); c.line(10, 10, 14, 15, FIRE["m"]); c.line(14, 15, 11, 21, FIRE["d"])
    c.line(4, 13, 9, 12, STONE["d"]); c.line(15, 9, 20, 11, STONE["d"])
    return done(c)


def sp_aegis_gauntlets():
    """Huyết quyền: a clenched steel fist dripping a red blood drop (heal on kills)."""
    c = new()
    c.rect(5, 5, 16, 14, STEEL["m"]); c.rect(5, 5, 16, 6, STEEL["l"])
    for x in (7, 10, 13):
        c.line(x, 5, x, 9, STEEL["d"])
    c.rect(7, 14, 15, 19, STEEL["d"]); c.rect(3, 8, 5, 12, STEEL["m"])
    c.polygon([(19, 12), (22, 17), (19, 21), (16, 17)], HEART["m"]); c.pixel(18, 16, HEART["l"])
    return done(c)


def sp_aegis_boots():
    """Phong hành: a boot with a small wind wing at the heel (speed when hit)."""
    c = new()
    c.rect(7, 4, 13, 14, WOOD["m"]); c.rect(7, 4, 8, 14, EARTH["l"])
    c.rect(7, 14, 19, 18, WOOD["m"]); c.rect(7, 17, 19, 18, WOOD["d"])
    c.polygon([(6, 6), (1, 3), (2, 7), (0, 9), (4, 10), (6, 10)], WIND["l"])
    c.line(1, 6, 5, 8, WIND["d"])
    c.line(15, 20, 21, 20, WIND["m"]); c.line(17, 22, 23, 22, WIND["l"])
    return done(c)


def sp_aegis_blade():
    """Thánh kiếm: a holy sword pointing up inside a ring of light (pulses round the hero)."""
    c = new()
    c.ellipse(1, 3, 22, 22, HOLY["d"], fill=False)
    c.ellipse(2, 4, 21, 21, HOLY["m"], fill=False)
    c.line(11, 1, 11, 15, STEEL["l"], 2); c.line(12, 2, 12, 15, STEEL["m"])
    c.rect(7, 15, 16, 16, GOLD["m"]); c.rect(11, 17, 12, 21, WOOD["m"])
    return done(c)


def sp_star_hat():
    """Lôi ấn: a lightning seal: a gold circle sigil struck through by a bolt."""
    c = new()
    c.ellipse(2, 2, 21, 21, BOLT["x"], fill=False); c.ellipse(4, 4, 19, 19, BOLT["d"], fill=False)
    c.polygon([(13, 1), (16, 1), (12, 10), (16, 10), (8, 22), (10, 13), (6, 13)], BOLT["m"])
    c.line(14, 2, 11, 10, BOLT["l"])
    return done(c)


def sp_star_robe():
    """Tim bất diệt: a heart wrapped in gold wings (one second life)."""
    c = new()
    c.polygon([(9, 9), (0, 4), (2, 10), (0, 13), (6, 15)], GOLD["m"]); c.line(1, 6, 7, 10, GOLD["l"])
    c.polygon([(14, 9), (23, 4), (21, 10), (23, 13), (17, 15)], GOLD["m"]); c.line(22, 6, 16, 10, GOLD["l"])
    c.ellipse(6, 6, 12, 12, HEART["m"]); c.ellipse(11, 6, 17, 12, HEART["m"])
    c.polygon([(6, 10), (17, 10), (11, 19)], HEART["m"]); c.ellipse(7, 7, 9, 9, HEART["l"])
    return done(c)


def sp_star_pants():
    """Hoả y: a ring of fire burning round a point (an aura that burns nearby monsters)."""
    c = new()
    import math
    for k in range(8):
        a = k * math.pi / 4
        x, y = 12 + round(math.cos(a) * 8), 12 + round(math.sin(a) * 8)
        c.polygon([(x - 2, y + 2), (x, y - 3), (x + 2, y + 2)], FIRE["d"])
        c.polygon([(x - 1, y + 1), (x, y - 1), (x + 1, y + 1)], FIRE["l"])
    c.ellipse(5, 5, 18, 18, FIRE["m"], fill=False)
    c.ellipse(10, 10, 13, 13, FIRE["l"])
    return done(c)


def sp_star_bracer():
    """Băng ấn: an ice seal: a frozen hexagon sigil with a snowflake core."""
    c = new()
    c.polygon([(12, 1), (21, 6), (21, 17), (12, 22), (3, 17), (3, 6)], ICE["d"])
    c.polygon([(12, 3), (19, 7), (19, 16), (12, 20), (5, 16), (5, 7)], ICE["m"])
    c.line(12, 6, 12, 17, ICE["l"]); c.line(7, 9, 17, 14, ICE["l"]); c.line(7, 14, 17, 9, ICE["l"])
    c.ellipse(10, 10, 14, 14, "#ffffff")
    return done(c)


def sp_star_shoes():
    """Lưu tinh: a shooting star with a long glittering tail (a speed rune on kills)."""
    c = new()
    c.polygon([(2, 22), (14, 9), (16, 12)], ARC["d"]); c.polygon([(4, 21), (14, 10), (15, 11)], ARC["l"])
    c.polygon([(17, 1), (19, 6), (23, 7), (19, 9), (17, 14), (15, 9), (11, 7), (15, 6)], BOLT["m"])
    c.polygon([(17, 4), (18, 6), (20, 7), (18, 8), (17, 11), (16, 8), (14, 7), (16, 6)], BOLT["l"])
    c.pixel(6, 14, ARC["l"]); c.pixel(10, 20, ARC["m"])
    return done(c)


def sp_star_staff():
    """Vĩnh cửu: an infinity loop of violet light (every cooldown resets)."""
    c = new()
    c.ellipse(1, 6, 12, 17, ARC["d"], fill=False); c.ellipse(2, 7, 11, 16, ARC["m"], fill=False)
    c.ellipse(11, 6, 22, 17, ARC["d"], fill=False); c.ellipse(12, 7, 21, 16, ARC["m"], fill=False)
    c.line(4, 8, 7, 7, ARC["l"]); c.line(16, 15, 19, 15, ARC["l"])
    c.pixel(11, 11, "#ffffff"); c.pixel(12, 12, "#ffffff")
    return done(c)


# --- lobby / menu icons (nav_*, user 2026-11-20: the lobby buttons get their own icon set) -------------------

def nav_character():
    """Nhân vật: a knight's helmet bust with a red plume."""
    c = new()
    c.polygon([(12, 1), (16, 2), (18, 5), (13, 4)], RED["m"])
    c.ellipse(5, 4, 18, 17, STEEL["m"]); c.rect(5, 11, 18, 18, STEEL["m"])
    c.ellipse(6, 5, 11, 9, STEEL["l"]); c.rect(16, 6, 18, 18, STEEL["d"])
    c.rect(7, 11, 16, 12, STEEL["x"]); c.line(11, 13, 11, 17, STEEL["d"])
    c.polygon([(2, 19), (21, 19), (23, 23), (0, 23)], RED["d"])
    return done(c)


def nav_deck():
    """Bộ thẻ: three cards fanned out, the front one gold-framed."""
    c = new()
    for k, (pts, col) in enumerate((([(1, 6), (9, 3), (13, 17), (5, 20)], ARC["d"]),
                                    ([(6, 3), (14, 2), (16, 17), (8, 18)], ICE["d"]))):
        c.polygon(pts, col)
    c.rect(10, 4, 20, 20, GOLD["d"]); c.rect(11, 5, 19, 19, "#2a2438")
    c.polygon([(15, 8), (18, 12), (15, 16), (12, 12)], GOLD["m"]); c.pixel(14, 11, GOLD["l"])
    return done(c)


def nav_gacha():
    """Gacha: a glowing crystal orb on a gold stand, sparkles round it."""
    c = new()
    c.ellipse(4, 2, 19, 17, ARC["d"]); c.ellipse(5, 3, 18, 16, ARC["m"]); c.ellipse(7, 5, 11, 9, ARC["l"])
    c.pixel(8, 6, "#ffffff")
    c.polygon([(6, 17), (17, 17), (19, 22), (4, 22)], GOLD["m"]); c.line(5, 21, 18, 21, GOLD["d"])
    for (x, y) in ((1, 3), (21, 6), (20, 1)):
        c.pixel(x, y, BOLT["l"])
    return done(c)


def nav_missions():
    """Nhiệm vụ: a parchment scroll with a green tick."""
    c = new()
    c.rect(4, 3, 18, 20, "#e8d8b0"); c.rect(4, 3, 5, 20, "#c8b080")
    c.rect(3, 1, 19, 3, "#b8905a"); c.rect(3, 20, 19, 22, "#b8905a")
    for y in (7, 10, 13):
        c.line(7, y, 12, y, "#8a7050")
    c.line(12, 15, 15, 18, LEAF["d"], 2); c.line(15, 18, 21, 10, LEAF["d"], 2)
    c.line(13, 15, 15, 17, LEAF["l"]); c.line(15, 17, 20, 11, LEAF["l"])
    return done(c)


def nav_settings():
    """Cài đặt: a steel cog."""
    c = new()
    import math
    for k in range(8):
        a = k * math.pi / 4
        x, y = 12 + round(math.cos(a) * 9), 12 + round(math.sin(a) * 9)
        c.rect(x - 2, y - 2, x + 1, y + 1, STEEL["m"])
    c.ellipse(4, 4, 19, 19, STEEL["m"]); c.ellipse(5, 5, 12, 12, STEEL["l"])
    c.ellipse(9, 9, 14, 14, "#2a2438")
    return done(c)


def nav_title():
    """Menu chính: a little house (home)."""
    c = new()
    c.polygon([(12, 2), (23, 11), (1, 11)], RED["m"]); c.line(12, 2, 1, 11, RED["l"])
    c.rect(4, 11, 19, 21, "#e8d8b0"); c.rect(4, 11, 5, 21, "#c8b080")
    c.rect(10, 14, 14, 21, WOOD["m"]); c.pixel(13, 17, GOLD["m"])
    return done(c)


def nav_tree():
    """Cây kỹ năng: a small tree whose branches end in glowing nodes."""
    c = new()
    c.line(11, 22, 11, 12, WOOD["m"], 3)
    c.line(11, 13, 5, 7, WOOD["m"], 2); c.line(12, 13, 18, 7, WOOD["m"], 2); c.line(11, 12, 11, 4, WOOD["m"], 2)
    for (x, y, col) in ((4, 6, LEAF), (18, 6, LEAF), (11, 3, GOLD)):
        c.ellipse(x - 3, y - 3, x + 3, y + 3, col["d"]); c.ellipse(x - 2, y - 2, x + 1, y + 1, col["l"])
    c.rect(6, 21, 17, 22, EARTH["d"])
    return done(c)


def nav_equipment():
    """Trang bị: a breastplate and a sword crossed behind it."""
    c = new()
    sword(c, (6, 17), (18, 5))
    c.polygon([(8, 6), (21, 6), (21, 15), (14, 22), (8, 15)], STEEL["m"])
    c.polygon([(8, 6), (14, 6), (14, 21), (8, 15)], STEEL["l"])
    c.pixel(17, 10, RED["m"])
    return done(c)


def nav_stages():
    """Chọn ải: a red flag planted on a hill (the next stage)."""
    c = new()
    c.ellipse(0, 15, 23, 30, LEAF["d"]); c.ellipse(3, 16, 14, 22, LEAF["m"])
    c.line(10, 2, 10, 17, WOOD["d"], 2)
    c.polygon([(11, 2), (21, 5), (11, 9)], RED["m"]); c.line(12, 3, 18, 5, RED["l"])
    return done(c)



# --- region events (end-of-run damage table, design/region-events-plan.md) ------------------------------------

def ev_tornado():
    """Lốc cỏ: a grass-green funnel, wide at the top, leaves whipping round it."""
    c = new()
    for i, (y, w) in enumerate(((3, 9), (7, 7), (11, 5), (15, 4), (19, 2))):
        c.rect(12 - w, y, 12 + w - 1, y + 2, LEAF["m"] if i % 2 == 0 else LEAF["d"])
        c.line(12 - w, y, 12 - w + 2, y, LEAF["l"])
    c.rect(11, 22, 12, 23, LEAF["d"])
    c.polygon([(1, 10), (4, 9), (3, 12)], LEAF["l"]); c.polygon([(20, 16), (23, 15), (22, 18)], LEAF["l"])
    return done(c)


def ev_falling_tree():
    """Cây đổ: a tree trunk tipping over to the right, its crown crashing down."""
    c = new()
    c.rect(1, 20, 22, 22, EARTH["d"])
    c.line(4, 19, 14, 9, WOOD["m"], 3); c.line(4, 18, 13, 9, WOOD["d"])
    c.ellipse(11, 2, 23, 14, LEAF["d"]); c.ellipse(13, 3, 20, 9, LEAF["m"]); c.pixel(15, 4, LEAF["l"])
    c.line(1, 15, 3, 13, STONE["l"]); c.line(6, 22, 9, 20, STONE["l"])
    return done(c)


def ev_poison_tide():
    """Nước độc dâng: a green poison pool swelling up, bubbles on top, a rising arrow."""
    c = new()
    c.ellipse(1, 12, 22, 22, LEAF["d"]); c.ellipse(3, 13, 20, 20, "#7ad04a"); c.ellipse(5, 14, 12, 17, LEAF["l"])
    for (x, y, r) in ((6, 8, 2), (15, 5, 3), (19, 10, 1)):
        c.ellipse(x - r, y - r, x + r, y + r, "#9ae05a", fill=False)
    c.polygon([(11, 1), (14, 5), (8, 5)], GOLD["m"]); c.rect(10, 5, 12, 10, GOLD["m"])
    return done(c)


# --- Cung thủ (design/archer.md, 2026-11-23) -------------------------------------------------------------------

def _arrow(c, x0, y0, x1, y1, shaft=None, head=None):
    """An arrow from tail (x0, y0) to head (x1, y1) on a 45-degree axis: wood shaft, steel head, white fletching."""
    dx, dy = (1 if x1 > x0 else -1), (1 if y1 > y0 else -1)
    c.line(x0, y0, x1, y1, (shaft or WOOD)["m"], 1)
    c.line(x0 + 1, y0, x1, y1 - dy, (shaft or WOOD)["d"], 1)
    h = head or STEEL
    c.polygon([(x1 + dx, y1 + dy), (x1 - 3 * dx, y1), (x1, y1 - 3 * dy)], h["m"])
    c.pixel(x1, y1, h["l"])
    for k in range(3):
        c.pixel(x0 + dx * k - dx, y0 + dy * k + dy, FEATHER["l"])
        c.pixel(x0 + dx * k + dx, y0 + dy * k - dy, FEATHER["m"])


def quick_arrow():
    """Tên nhanh: one arrow flying up-right with two speed lines."""
    c = new()
    _arrow(c, 3, 20, 19, 4)
    c.line(2, 14, 7, 9, WIND["m"], 1)
    c.line(9, 22, 14, 17, WIND["m"], 1)
    return done(c)


def steady_hand():
    """Tay vững: a drawn bow, string pulled tight, arrow nocked and level."""
    c = new()
    c.ellipse(6, 2, 22, 22, WOOD["m"], fill=False)
    c.rect(4, 0, 13, 24, (0, 0, 0, 0))
    c.line(14, 3, 8, 12, FEATHER["l"], 1)
    c.line(8, 12, 14, 21, FEATHER["l"], 1)
    c.line(6, 12, 21, 12, WOOD["d"], 1)
    c.polygon([(23, 12), (19, 9), (19, 15)], STEEL["m"])
    c.pixel(22, 12, STEEL["l"])
    return done(c)


def sharp_arrows():
    """Tên sắc: a big steel arrowhead with a gleam."""
    c = new()
    c.polygon([(12, 1), (21, 14), (14, 12), (14, 22), (10, 22), (10, 12), (3, 14)], STEEL["d"])
    c.polygon([(12, 3), (18, 12), (12, 10)], STEEL["l"])
    c.polygon([(12, 3), (6, 12), (12, 10)], STEEL["m"])
    c.rect(10, 13, 13, 21, WOOD["m"])
    c.pixel(17, 4, "#ffffff")
    c.pixel(18, 3, "#ffffff")
    return done(c)


def extra_arrow():
    """Thêm tên: two arrows side by side and a gold plus."""
    c = new()
    _arrow(c, 2, 20, 14, 8)
    _arrow(c, 8, 22, 20, 10)
    c.rect(17, 1, 18, 8, GOLD["m"])
    c.rect(14, 4, 21, 5, GOLD["m"])
    return done(c)


def sp_ranger_boots():
    """Gió đuổi (hit: speed rune): a light boot with wind lines behind."""
    c = new()
    c.polygon([(10, 3), (16, 3), (16, 15), (22, 18), (22, 21), (9, 21)], LEAF["d"])
    c.polygon([(11, 4), (15, 4), (15, 15), (20, 18), (11, 18)], LEAF["m"])
    c.rect(9, 19, 22, 21, EARTH["d"])
    for y, x0 in ((7, 2), (12, 1), (17, 3)):
        c.line(x0, y, x0 + 5, y, WIND["m"], 1)
    return done(c)


def sp_ranger_gloves():
    """Nhịp săn (kills heal): a leather bracer and a small heart."""
    c = new()
    c.rect(4, 9, 15, 20, EARTH["m"])
    c.rect(4, 9, 15, 11, EARTH["d"])
    c.rect(4, 17, 15, 18, EARTH["d"])
    c.ellipse(13, 2, 18, 7, HEART["m"])
    c.ellipse(17, 2, 22, 7, HEART["m"])
    c.polygon([(13, 5), (22, 5), (17, 11)], HEART["m"])
    c.pixel(15, 3, HEART["l"])
    return done(c)


def sp_ranger_cloak():
    """Áo lá (shield): a leaf-green hooded cloak shaped like a shield."""
    c = new()
    c.polygon([(12, 1), (21, 6), (19, 18), (12, 23), (5, 18), (3, 6)], LEAF["d"])
    c.polygon([(12, 3), (19, 7), (17, 17), (12, 21), (7, 17), (5, 7)], LEAF["m"])
    c.line(12, 4, 12, 20, LEAF["d"], 1)
    c.ellipse(9, 6, 15, 11, LEAF["l"])
    return done(c)


def sp_ranger_ring():
    """Vòng tên (pulse): a ring with four arrowheads pointing out."""
    c = new()
    c.ellipse(5, 5, 18, 18, GOLD["d"], fill=False)
    c.ellipse(6, 6, 17, 17, GOLD["m"], fill=False)
    for pts in (((12, 0), (9, 4), (15, 4)), ((12, 23), (9, 19), (15, 19)), ((0, 12), (4, 9), (4, 15)), ((23, 12), (19, 9), (19, 15))):
        c.polygon(list(pts), STEEL["m"])
    return done(c)


def sp_ranger_hood():
    """Tên sấm (chain shock): an arrow wrapped by a lightning bolt."""
    c = new()
    _arrow(c, 3, 21, 18, 6)
    c.polygon([(14, 1), (8, 11), (12, 11), (8, 20), (17, 8), (13, 8), (17, 1)], BOLT["m"])
    c.line(14, 2, 10, 10, BOLT["l"], 1)
    return done(c)


def sp_ranger_bow():
    """Mắt thần (reset cooldowns): a hawk's golden eye."""
    c = new()
    c.polygon([(1, 12), (8, 5), (16, 5), (23, 12), (16, 19), (8, 19)], GOLD["d"])
    c.polygon([(3, 12), (9, 7), (15, 7), (21, 12), (15, 17), (9, 17)], GOLD["l"])
    c.ellipse(8, 7, 16, 17, GOLD["m"])
    c.ellipse(10, 9, 14, 15, OUTLINE)
    c.pixel(13, 10, "#ffffff")
    return done(c)


ICONS = {f.__name__: f for f in (blade_arc, whirlwind, earth_strike, ground_slam, cleave_wave, holy_column, dash,
                                 earthquake, solar_ray, god_hammer, arcane_bolt, fireball, frost_nova, lightning,
                                 thunder_javelin, meteor, void_orb, blizzard, storm, back_slash, sharpen, haste, reach,
                                 vitality, swift, magnet, regen, toughness, extra_strike, arcane_power, quick_cast,
                                 wide_magic, mana_shield, multicast, sp_aegis_helm, sp_aegis_chest, sp_aegis_greaves,
                                 sp_aegis_gauntlets, sp_aegis_boots, sp_aegis_blade, sp_star_hat, sp_star_robe,
                                 sp_star_pants, sp_star_bracer, sp_star_shoes, sp_star_staff, nav_character, nav_deck,
                                 nav_gacha, nav_missions, nav_settings, nav_title, nav_tree, nav_equipment, nav_stages, ev_tornado, ev_falling_tree,
                                 ev_poison_tide, quick_arrow, steady_hand, sharp_arrows, extra_arrow, sp_ranger_boots,
                                 sp_ranger_gloves, sp_ranger_cloak, sp_ranger_ring, sp_ranger_hood, sp_ranger_bow)}

if __name__ == "__main__":
    anims = [(n, [f()], 1, False, {}) for n, f in ICONS.items()]
    export(HERE, NAME, anims, anchor=(12.0, 12.0), preview_scale=8, gif_scale=4)
    print(f"OK {NAME}")
