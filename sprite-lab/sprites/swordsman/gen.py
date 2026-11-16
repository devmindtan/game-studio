#!/usr/bin/env python3
"""Side-facing pixel swordsman with the same animation set as mage."""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "swordsman"
W = H = 56
ANCHOR = (24.0, 54.0)
HERE = Path(__file__).resolve().parent

INK = "#171b2b"
ARMOR = "#416b91"
ARMOR_D = "#294760"
ARMOR_L = "#82b4d0"
STEEL = "#c8d9df"
STEEL_L = "#f3fbf7"
GOLD = "#e6b957"
SKIN = "#e8b58f"
HAIR = "#56352d"
SCARF = "#b84345"
SCARF_L = "#e56b5d"
PANTS = "#34344b"
BOOT = "#49352f"
FX = "#a9e9f2"


def line(c, a, b, color, width=1):
    c.line(a[0], a[1], b[0], b[1], color, width)


def fighter(i=0, *, bob=0, lean=0, sword="ready", legs="stand", hurt=False,
            scarf=0, slash=None, burst=False, fallen=False):
    c = Canvas(W, H)
    if fallen:
        c.ellipse(12, 38, 38, 47, ARMOR_D)
        c.ellipse(8, 34, 19, 43, SKIN)
        c.rect(8, 33, 17, 36, HAIR)
        line(c, (27, 44), (48, 44), STEEL, 2)
        line(c, (24, 42), (29, 46), GOLD, 2)
        c.outline(INK)
        return c

    # Rear leg and boots: exaggerated stride reads clearly when mirrored.
    poses = {
        "stand": ((18, 41, -1), (27, 41, 1)),
        "wide": ((11, 41, -1), (31, 41, 1)),
        "stride_a": ((10, 40, -1), (30, 41, 1)),
        "stride_b": ((17, 41, -1), (26, 39, 1)),
        "tuck": ((17, 36, 0), (27, 37, 0)),
        "kneel": ((14, 42, -1), (27, 42, 1)),
    }
    for x, y, toe in poses[legs]:
        x += lean
        y += bob
        c.rect(x + 1, y - 5, x + 3, y, PANTS)
        c.rect(x, y, x + 5, y + 3, BOOT)
        c.line(x, y + 3, x + 5, y + 3, INK)
        c.pixel(x + (5 if toe > 0 else 0), y, "#765349")

    # Cape/scarf trails behind the body, with small frame-to-frame motion.
    c.polygon([(18 + lean, 22 + bob), (10 + lean - scarf, 25 + bob),
               (7 + lean - scarf, 34 + bob), (16 + lean, 31 + bob)], SCARF)
    line(c, (15 + lean - scarf, 27 + bob), (9 + lean - scarf, 33 + bob), SCARF_L)

    # Compact steel cuirass, shoulder plate, belt and arm.
    c.polygon([(18 + lean, 22 + bob), (28 + lean, 22 + bob),
               (33 + lean, 28 + bob), (30 + lean, 38 + bob),
               (17 + lean, 38 + bob), (14 + lean, 29 + bob)], ARMOR)
    line(c, (18 + lean, 24 + bob), (27 + lean, 24 + bob), ARMOR_L, 2)
    line(c, (23 + lean, 26 + bob), (24 + lean, 35 + bob), ARMOR_D, 2)
    c.rect(16 + lean, 35 + bob, 31 + lean, 37 + bob, ARMOR_D)
    c.rect(23 + lean, 35 + bob, 26 + lean, 38 + bob, GOLD)
    c.polygon([(28 + lean, 23 + bob), (33 + lean, 25 + bob),
               (32 + lean, 30 + bob), (27 + lean, 29 + bob)], ARMOR_L)

    # Head, swept hair and readable profile.
    c.ellipse(19 + lean, 11 + bob, 29 + lean, 23 + bob, SKIN)
    c.polygon([(17 + lean, 16 + bob), (18 + lean, 10 + bob),
               (25 + lean, 8 + bob), (31 + lean, 12 + bob),
               (29 + lean, 15 + bob), (23 + lean, 13 + bob)], HAIR)
    c.pixel(29 + lean, 17 + bob, INK)
    c.pixel(30 + lean, 18 + bob, SKIN)
    c.line(19 + lean, 14 + bob, 27 + lean, 13 + bob, "#815247")

    # Sword positions share a stable hand/grip; attack moves the blade through a broad arc.
    hand = (32 + lean, 29 + bob)
    if sword == "ready":
        hilt, tip = (34 + lean, 31 + bob), (43 + lean, 8 + bob)
    elif sword == "wind":
        hilt, tip = (34 + lean, 31 + bob), (27 + lean, 8 + bob)
    elif sword == "high":
        hilt, tip = (35 + lean, 29 + bob), (45 + lean, 7 + bob)
    elif sword == "swing":
        hilt, tip = (34 + lean, 30 + bob), (49 + lean, 18 + bob)
    elif sword == "low":
        hilt, tip = (34 + lean, 31 + bob), (46 + lean, 35 + bob)
    else:  # skill thrust
        hilt, tip = (34 + lean, 29 + bob), (51 + lean, 22 + bob)
    line(c, hand, hilt, SKIN, 3)
    line(c, (hilt[0] - 3, hilt[1] + 2), (hilt[0] + 3, hilt[1] - 2), GOLD, 2)
    line(c, hilt, tip, STEEL, 3)
    line(c, (hilt[0] + 1, hilt[1]), (tip[0], tip[1]), STEEL_L)
    c.pixel(tip[0], tip[1], STEEL_L)
    if slash:
        # Short stepped crescent; clipped safely inside the generous frame.
        points = slash
        for a, b in zip(points, points[1:]):
            line(c, a, b, FX, 2)
        for x, y in points[::2]:
            c.pixel(x, y, STEEL_L)
    if burst:
        for x, y in ((48, 17), (51, 20), (48, 23), (45, 20), (53, 16), (53, 24)):
            c.pixel(x, y, STEEL_L if (x + y) % 2 else FX)
    if hurt:
        c.pixel(19 + lean, 18 + bob, "#fff4d7")
    c.outline(INK)
    return c


def idle(i):
    return fighter(i, bob=(0, 0, 1, 1, 0, 0)[i], scarf=(0, 1, 1, 0, -1, 0)[i])


def run(i):
    return fighter(i, bob=(0, -1, 0, -1, 0, -1, 0, 1)[i], lean=1,
                   scarf=(2, 3, 4, 2, 1, 3, 4, 2)[i],
                   legs=("stride_a", "stride_b", "stride_a", "stride_b",
                         "stride_a", "stride_b", "stride_a", "stride_b")[i],
                   sword="low" if i % 2 else "ready")


def jump(i):
    return fighter(i, bob=(1, -2, -5, -2, 0)[i],
                   legs=("wide", "tuck", "tuck", "wide", "wide")[i],
                   scarf=(0, 2, 3, 2, 0)[i], sword=("wind", "high", "high", "swing", "ready")[i])


def attack(i):
    return fighter(i, bob=(1, 0, -1, 1, 0)[i], lean=(-2, -1, 2, 2, 0)[i],
                   scarf=(1, 2, 3, 2, 0)[i],
                   sword=("wind", "high", "swing", "low", "ready")[i],
                   slash=( [(32, 12), (39, 10), (46, 12), (51, 17)] if i == 2 else
                           [(35, 14), (42, 12), (48, 15)] if i == 3 else None))


def spell(i):
    # Signature skill: a two-handed forward lunge with an energy-edged thrust.
    return fighter(i, bob=(0, -1, -2, 0, 0)[i], lean=(-1, -2, -3, 1, 0)[i],
                   legs=("stand", "wide", "wide", "wide", "stand")[i],
                   scarf=(0, 1, 3, 3, 0)[i],
                   sword=("wind", "high", "thrust", "thrust", "ready")[i],
                   slash=( [(39, 20), (43, 17), (48, 18), (53, 21), (49, 25)] if i in (2, 3) else None),
                   burst=i == 3)


def hurt(i):
    return fighter(i, bob=1, lean=(-3, -2, -1)[i], hurt=True,
                   scarf=(-2, -1, 0)[i], sword=("low", "low", "ready")[i])


def death(i):
    if i < 3:
        return fighter(i, bob=(1, 3, 5)[i], lean=(-3, -2, -2)[i],
                       legs=("wide", "kneel", "kneel")[i], scarf=(-1, -2, -2)[i],
                       sword=("low", "low", "ready")[i])
    return fighter(i, fallen=True)


ANIMATIONS = [
    ("idle", [idle(i) for i in range(6)], 8, True),
    ("run", [run(i) for i in range(8)], 12, True),
    ("jump", [jump(i) for i in range(5)], 10, False),
    ("attack", [attack(i) for i in range(5)], 14, False),
    ("spell", [spell(i) for i in range(5)], 12, False),
    ("hurt", [hurt(i) for i in range(3)], 12, False),
    ("death", [death(i) for i in range(5)], 8, False),
]


def main():
    flat = [frame for _, frames, _, _ in ANIMATIONS for frame in frames]
    strip(flat).save(HERE / f"{NAME}_strip.png")
    flat[0].save(HERE / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * W, len(ANIMATIONS) * H)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * H)
    preview([sheet], HERE / "preview.png", scale=3)
    for name, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{name}.gif", fps=fps, scale=4)
    write_anim_meta(HERE / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS], anchor=ANCHOR)
    print(f"strip: {HERE / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
