#!/usr/bin/env python3
"""Generator cho sprite "arrow": mũi tên cơ bản của hệ cung.

  fly/fly_right  4 frame lặp: bay sang phải;
  fly_left       4 frame lặp: bay sang trái;
  fly_up         4 frame lặp: bay lên trên;
  fly_down       4 frame lặp: bay xuống dưới;
  impact         5 frame một lần: cắm vào mục tiêu và mảnh gỗ văng (hướng ngang).

4 hướng bay cho game top-down. Neo tại tâm mũi tên (sprite vuông 20x20).

Chạy:  gamekit art run arrow
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("no workspace")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "arrow"
S = 20
CX, CY = 10, 10
ANCHOR = (float(CX), float(CY))  # tâm sprite (ổn định cho mọi hướng)
HERE = Path(__file__).resolve().parent
OUT = HERE

WOOD = "#8a5a2e"; WOOD_D = "#563418"; STEEL = "#c5d4e6"; TIP = "#e8f4ff"; FEATHER = "#d94a4a"; FEATHER_D = "#8a2f2f"


def p(c, x, y, col):
    c.pixel(x, y, col)


def draw_arrow_dir(c, direction, wobble=0):
    # direction: 'right','left','up','down'
    if direction == "right":
        y = CY + wobble
        c.line(CX - 8, y, CX + 5, y, WOOD)
        c.line(CX - 8, y, CX + 4, y, WOOD_D)
        c.line(CX + 5, y, CX + 7, y, STEEL)
        p(c, CX + 8, y, TIP); p(c, CX + 7, y - 1, STEEL); p(c, CX + 7, y + 1, STEEL)
        c.line(CX - 8, y, CX - 6, y - 2, FEATHER); c.line(CX - 8, y, CX - 6, y + 2, FEATHER_D)
        p(c, CX - 9, y - 1, FEATHER); p(c, CX - 9, y + 1, FEATHER_D)
        return
    if direction == "left":
        y = CY + wobble
        c.line(CX - 5, y, CX + 8, y, WOOD)
        c.line(CX - 4, y, CX + 8, y, WOOD_D)
        c.line(CX - 7, y, CX - 5, y, STEEL)
        p(c, CX - 8, y, TIP); p(c, CX - 7, y - 1, STEEL); p(c, CX - 7, y + 1, STEEL)
        c.line(CX + 8, y, CX + 6, y - 2, FEATHER); c.line(CX + 8, y, CX + 6, y + 2, FEATHER_D)
        p(c, CX + 9, y - 1, FEATHER); p(c, CX + 9, y + 1, FEATHER_D)
        return
    if direction == "up":
        x = CX + wobble
        c.line(x, CY - 5, x, CY + 8, WOOD)
        c.line(x, CY - 4, x, CY + 8, WOOD_D)
        c.line(x, CY - 7, x, CY - 5, STEEL)
        p(c, x, CY - 8, TIP); p(c, x - 1, CY - 7, STEEL); p(c, x + 1, CY - 7, STEEL)
        c.line(x, CY + 8, x - 2, CY + 6, FEATHER); c.line(x, CY + 8, x + 2, CY + 6, FEATHER_D)
        p(c, x - 1, CY + 9, FEATHER); p(c, x + 1, CY + 9, FEATHER_D)
        return
    if direction == "down":
        x = CX + wobble
        c.line(x, CY - 8, x, CY + 5, WOOD)
        c.line(x, CY - 8, x, CY + 4, WOOD_D)
        c.line(x, CY + 5, x, CY + 7, STEEL)
        p(c, x, CY + 8, TIP); p(c, x - 1, CY + 7, STEEL); p(c, x + 1, CY + 7, STEEL)
        c.line(x, CY - 8, x - 2, CY - 6, FEATHER); c.line(x, CY - 8, x + 2, CY - 6, FEATHER_D)
        p(c, x - 1, CY - 9, FEATHER); p(c, x + 1, CY - 9, FEATHER_D)
        return


def fly(direction, i):
    c = Canvas(S, S)
    wobble = (0, -1, 0, 1)[i]
    # speed streak behind
    if direction == "right":
        for dx in (0, 2):
            if (i + dx) % 2 == 0: p(c, CX - 10 - dx, CY + wobble, WOOD_D)
    elif direction == "left":
        for dx in (0, 2):
            if (i + dx) % 2 == 0: p(c, CX + 10 + dx, CY + wobble, WOOD_D)
    elif direction == "up":
        for dy in (0, 2):
            if (i + dy) % 2 == 0: p(c, CX + wobble, CY + 10 + dy, WOOD_D)
    else:  # down
        for dy in (0, 2):
            if (i + dy) % 2 == 0: p(c, CX + wobble, CY - 10 - dy, WOOD_D)
    draw_arrow_dir(c, direction, wobble=wobble)
    return c


def impact(i):
    # impact ngang sang phải (tương thích), neo vẫn ở tâm
    c = Canvas(S, S)
    y = CY
    if i == 0:
        draw_arrow_dir(c, "right")
        p(c, CX + 9, y, TIP)
        return c
    if i == 1:
        c.line(CX - 8, y, CX + 4, y, WOOD); c.line(CX - 8, y, CX + 3, y, WOOD_D)
        c.line(CX + 4, y, CX + 6, y, STEEL)
        c.line(CX - 8, y, CX - 6, y - 2, FEATHER); c.line(CX - 8, y, CX - 6, y + 2, FEATHER_D)
        for dx, dy in ((7, -1), (7, 1), (8, 0)): p(c, CX + dx, y + dy, STEEL)
        return c
    y = CY + (1 if i == 2 else 0)
    c.line(CX - 8, y, CX + 4, y, WOOD); c.line(CX - 8, y, CX + 3, y, WOOD_D)
    c.line(CX + 4, y, CX + 6, y + (1 if i < 4 else 0), STEEL)
    c.line(CX - 8, y, CX - 6, y - 2, FEATHER); c.line(CX - 8, y, CX - 6, y + 2, FEATHER_D)
    if i == 2:
        for dx, dy in ((7, -2), (8, 1)): p(c, CX + dx, y + dy, WOOD_D)
    if i == 3:
        p(c, CX + 8, y - 1, WOOD_D)
    return c


def _rect(active):
    return {"shape": "rect", "center": [ANCHOR[0], ANCHOR[1]], "active": active}


ANIMATIONS = [
    {"name": "fly", "frames": [fly("right", i) for i in range(4)], "fps": 16, "loop": True, "hitbox": _rect([0, 3])},
    {"name": "fly_right", "frames": [fly("right", i) for i in range(4)], "fps": 16, "loop": True, "hitbox": _rect([0, 3])},
    {"name": "fly_left", "frames": [fly("left", i) for i in range(4)], "fps": 16, "loop": True, "hitbox": _rect([0, 3])},
    {"name": "fly_up", "frames": [fly("up", i) for i in range(4)], "fps": 16, "loop": True, "hitbox": _rect([0, 3])},
    {"name": "fly_down", "frames": [fly("down", i) for i in range(4)], "fps": 16, "loop": True, "hitbox": _rect([0, 3])},
    {"name": "impact", "frames": [impact(i) for i in range(5)], "fps": 14, "loop": False, "hitbox": _rect([0, 4])},
]


def main():
    flat = [f for a in ANIMATIONS for f in a["frames"]]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(a["frames"]) for a in ANIMATIONS)
    sheet = Canvas(cols * S, len(ANIMATIONS) * S)
    for r, a in enumerate(ANIMATIONS):
        sheet.paste(strip(a["frames"]), 0, r * S)
    preview([sheet], HERE / "preview.png", scale=6)
    for a in ANIMATIONS:
        gif(a["frames"], HERE / f"{a['name']}.gif", fps=a["fps"], scale=6)
    write_anim_meta(OUT / f"{NAME}.json", ANIMATIONS, anchor=ANCHOR)
    print(OUT / "preview.png")


if __name__ == "__main__":
    main()
