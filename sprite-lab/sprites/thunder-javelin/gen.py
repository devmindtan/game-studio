#!/usr/bin/env python3
"""Generator cho sprite "thunder-javelin": giáo sét lao nhanh và giật nổ.

  fly     6 frame lặp: mũi sét thẳng, tia điện tỏa hai bên, đuôi sáng;
  impact  6 frame một lần: tia chớp nổ ra tứ phía rồi tắt dần.

Bay sang phải. Neo (14, 10) gần đầu giáo.

Chạy:  gamekit art run thunder-javelin
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip, write_anim_meta  # noqa: E402

NAME = "thunder-javelin"
W, H = 28, 20
CX, CY = 14, 10
ANCHOR = (float(CX), float(CY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
BOLT = "#f8ff9a"
BOLT_MID = "#ffd84a"
ELEC = "#8ad8ff"
ELEC_D = "#3a7bd5"


def p(c, x, y, col):
    c.pixel(x, y, col)


def glow(c, x, y, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(x - r, y - r, x + r, y + r, col)
    c.paste(ring)


def shaft(c, x, y, phase):
    # thân giáo sét: đường sáng ngang hơi gấp khúc
    zig = ((0, 0), (0, -1), (0, 0), (0, 1), (0, 0), (0, -1))[phase]
    pts = [(x - 10, y + 1), (x - 6, y - 1), (x - 2, y + zig[1]), (x + 4, y), (x + 8, y)]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], ELEC_D, 1)
    c.line(x - 8, y, x + 7, y + zig[1], BOLT_MID, 1)
    c.line(x - 4, y, x + 6, y, BOLT)
    c.rect(x + 5, y - 1, x + 7, y, CORE)
    p(c, x + 8, y, BOLT)
    # tua điện hai bên, đổi theo pha
    branches = [
        ((-5, -3), (-3, -1)), ((-2, 3), (0, 1)), ((2, -3), (4, -1)),
        ((-7, 2), (-5, 1)), ((1, 3), (3, 2)),
    ]
    for k, (a, b) in enumerate(branches):
        if (phase + k) % 2 == 0:
            c.line(x + a[0], y + a[1], x + b[0], y + b[1], ELEC if k % 2 else BOLT_MID)


def tail_sparks(c, x, y, phase):
    for k, (dx, dy) in enumerate(((-12, -2), (-13, 1), (-15, 0), (-11, 3), (-14, -3))):
        if (phase + k) % 3 != 2:
            p(c, x + dx, y + dy, CORE if k == 0 else BOLT_MID)


def fly(i):
    c = Canvas(W, H)
    glow(c, CX, CY, 5, "#8ad8ff18")
    shaft(c, CX, CY, i)
    tail_sparks(c, CX, CY, i)
    return c


def impact(i):
    c = Canvas(W, H)
    center = (CX, CY)
    x, y = center
    if i == 0:
        glow(c, x, y, 4, "#ffffff55")
        c.ellipse(x - 2, y - 2, x + 2, y + 2, CORE)
        for dx, dy in ((4, 0), (-4, 0), (0, 4), (0, -4), (3, 3), (-3, -3)):
            c.line(x, y, x + dx, y + dy, BOLT)
        return c
    if i == 1:
        c.ellipse(x - 3, y - 3, x + 3, y + 3, BOLT_MID)
        c.ellipse(x - 1, y - 1, x + 1, y + 1, CORE)
        rays = [(8, 0), (-8, 0), (0, 7), (0, -7), (6, 5), (-6, -5), (6, -5), (-6, 5)]
        for dx, dy in rays:
            c.line(x, y, x + dx, y + dy, BOLT)
            c.line(x + dx//2, y + dy//2, x + dx//2 + (1 if dy else 0), y + dy//2 - (1 if dx else 0), ELEC)
        return c
    if i == 2:
        c.ellipse(x - 2, y - 2, x + 2, y + 2, BOLT)
        rays = [(10, 0), (-10, 0), (0, 8), (0, -8), (7, 6), (-7, -6), (7, -6), (-7, 6)]
        for dx, dy in rays:
            c.line(x + dx//3, y + dy//3, x + dx, y + dy, BOLT_MID)
            p(c, x + dx, y + dy, ELEC)
        return c
    if i == 3:
        p(c, x, y, BOLT_MID)
        rays = [(11, 0), (-11, 0), (0, 9), (0, -9), (8, 6), (-8, -6), (8, -6), (-8, 6)]
        for dx, dy in rays:
            c.line(x + dx//2, y + dy//2, x + dx, y + dy, ELEC_D)
            p(c, x + dx, y + dy, ELEC)
        return c
    if i == 4:
        for dx, dy in [(11, 0), (-11, 0), (0, 9), (0, -9), (8, 7), (-8, -7), (8, -7), (-8, 7)]:
            p(c, x + dx, y + dy, ELEC_D)
            p(c, x + dx//2, y + dy//2, ELEC_D)
        return c
    for dx, dy in [(12, 0), (-12, 0), (0, 9), (9, 7), (-9, -7)]:
        p(c, x + dx, y + dy, ELEC_D)
    return c


ANIMATIONS = [
    ("fly", [fly(i) for i in range(6)], 16, True),
    ("impact", [impact(i) for i in range(6)], 15, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * W, len(ANIMATIONS) * H)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * H)
    preview([sheet], HERE / "preview.png", scale=6)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=6)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
