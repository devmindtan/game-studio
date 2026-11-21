#!/usr/bin/env python3
"""Generator cho sprite "whirlwind": xoáy chém AOE của hệ đại kiếm.

  spin    8 frame lặp: vòng chém xoay quanh người, vệt thép và gió bao tròn.

Neo (24, 24) tại tâm (sprite 48x48) để đặt quanh nhân vật.

Chạy:  gamekit art run whirlwind
"""

import json
import math
import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "whirlwind"
D = 2   # double density (px_scale 0.5), review 2026-11-21
SIZE = 48 * D
CX, CY = 24 * D, 24 * D
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
EDGE = "#e8f4ff"
STEEL = "#aabbd0"
WIND = "#cfe8ff"
WIND_D = "#7fa6c9"


def p(c, x, y, col):
    c.pixel(x, y, col)


def arc_stroke(c, cx, cy, r, a0, a1, col, step=4):
    a = a0
    while a <= a1:
        rad = math.radians(a)
        p(c, round(cx + math.cos(rad) * r), round(cy + math.sin(rad) * r), col)
        a += step


def blade(c, a_head, span, r0, r1):
    """A solid crescent blade of wind: filled between r0 and r1 over `span` degrees ending at a_head; the
    head (leading edge) is white-hot, the tail fades to steel blue (user 2026-11-21: the dotted arcs read as
    a faint blur)."""
    for y in range(SIZE):
        for x in range(SIZE):
            dx, dy = x + 0.5 - CX, y + 0.5 - CY
            r = math.hypot(dx, dy)
            if not (r0 <= r <= r1):
                continue
            a = math.degrees(math.atan2(dy, dx)) % 360
            back = (a_head - a) % 360          # degrees behind the head
            if back > span:
                continue
            t = back / span                    # 0 head .. 1 tail
            inner = r0 + (r1 - r0) * (t ** 0.7)        # thick at the head, a thin hook at the tail
            if r < inner:
                continue
            rim = r > r1 - 1.6 * D                         # the outer cutting edge catches the light
            if rim and t < 0.7:
                col = CORE
            elif t < 0.25:
                col = EDGE
            elif t < 0.6:
                col = WIND
            else:
                col = WIND_D
            p(c, x, y, col)


def spin(i):
    c = Canvas(SIZE, SIZE)
    base = i * 45
    for k in (0, 180):                        # two blades opposite each other
        blade(c, base + k + 120, 160, 9 * D, 20 * D)
    for k in (0, 180):                        # a thin outer gust trailing each blade
        arc = base + k + 60
        for d in range(0, 70, 1):
            rad = math.radians(arc - d)
            for w in range(D):
                p(c, round(CX + math.cos(rad) * (21.5 * D + w)), round(CY + math.sin(rad) * (21.5 * D + w)), WIND if d < 40 else WIND_D)
    return c.outline("#1b2a40")


ANIMATIONS = [
    ("spin", [spin(i) for i in range(8)], 14, True),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=4)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=4)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop,
                      # hit area measured from the solid pixels of every frame (spritekit.fit_hitbox)
                      "hitbox": {"shape": "circle", "center": list(ANCHOR), "active": [0, len(f) - 1]}}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    m = json.loads((OUT / f"{NAME}.json").read_text())
    m["px_scale"] = 1.0 / D
    (OUT / f"{NAME}.json").write_text(json.dumps(m, indent=2) + "\n")
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
