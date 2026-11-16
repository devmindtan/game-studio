#!/usr/bin/env python3
"""Generator cho sprite "haste-rune": hiệu ứng buff tăng tốc cho pháp sư.

  cast  5 frame một lần: ký tự tốc độ bùng lên từ đất;
  loop  8 frame lặp: vòng rune xoay, vệt gió và mũi tên năng lượng bay lên;
  end   5 frame một lần: ánh sáng tan và rơi xuống.

Neo (16, 26) gần đáy chân (sprite 32x32), để hào quang bao quanh người.

Chạy:  gamekit art run haste-rune
"""

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

NAME = "haste-rune"
SIZE = 32
CX, GY = 16, 26  # neo gần chân
ANCHOR = (float(CX), float(GY))
HERE = Path(__file__).resolve().parent
OUT = HERE

CORE = "#ffffff"
LIME = "#c8ff66"
GREEN = "#6ee06e"
TEAL = "#2fbfa0"
DARK = "#1f6b4f"
FADE = "#6ee06e55"


def p(c, x, y, col):
    c.pixel(x, y, col)


def glow(c, x, y, r, col):
    ring = Canvas(c.width, c.height)
    ring.ellipse(x - r, y - r, x + r, y + r, col)
    c.paste(ring)


def base_ring(c, phase, r=10, alpha=True):
    # vòng rune dưới chân, hơi méo phối cảnh (ellipse dẹt)
    y = GY
    if alpha:
        ring = Canvas(c.width, c.height)
        ring.ellipse(CX - r, y - 3, CX + r, y + 3, "#6ee06e22")
        c.paste(ring)
    c.ellipse(CX - r, y - 3, CX + r, y + 3, TEAL, fill=False)
    c.ellipse(CX - r + 2, y - 2, CX + r - 2, y + 2, DARK, fill=False)
    # ký tự rune xoay quanh vòng
    for k in range(6):
        a = math.radians(phase * 30 + k * 60)
        x = round(CX + math.cos(a) * r)
        yy = round(y + math.sin(a) * 3)
        p(c, x, yy, CORE if (k + phase) % 3 == 0 else LIME)
        p(c, x + (1 if math.cos(a) > 0 else -1), yy, GREEN)


def up_arrow(c, x, y, col):
    p(c, x, y - 2, col); p(c, x, y - 1, col); p(c, x, y, col)
    p(c, x - 1, y - 1, col); p(c, x + 1, y - 1, col)


def wind_lines(c, phase):
    # vệt gió bay lên hai bên
    for k, (bx, by) in enumerate(((CX - 8, GY - 6), (CX + 8, GY - 8), (CX - 5, GY - 14), (CX + 6, GY - 12))):
        off = (phase + k * 2) % 6
        yy = by - off
        if 4 <= yy <= GY - 1:
            c.line(bx, yy, bx, yy + 3, TEAL if k % 2 else GREEN)
            if yy - 1 >= 4:
                p(c, bx, yy - 1, LIME)


def cast(i):
    c = Canvas(SIZE, SIZE)
    if i == 0:
        glow(c, CX, GY, 3, "#c8ff6633")
        c.ellipse(CX - 3, GY - 1, CX + 3, GY + 1, TEAL)
        p(c, CX, GY, CORE)
        return c
    r = 3 + i * 2
    base_ring(c, i, r=r, alpha=True)
    for k in range(i + 1):
        y = GY - 4 - k * 3
        if y > 3:
            up_arrow(c, CX - 4 + (k % 2) * 8, y, LIME if k % 2 == 0 else GREEN)
    return c


def loop(i):
    c = Canvas(SIZE, SIZE)
    glow(c, CX, GY - 8, 6, "#6ee06e18")
    base_ring(c, i, r=10, alpha=True)
    wind_lines(c, i)
    # mũi tên năng lượng bay lên, lặp dọc
    for k in range(3):
        y = GY - 5 - ((i * 2 + k * 6) % 18)
        x = CX - 6 + (k % 3) * 6
        if 4 <= y <= GY - 2:
            up_arrow(c, x, y, CORE if k == 1 else LIME)
    # hạt sáng
    for k, (dx, dy) in enumerate(((-10, -10), (10, -14), (0, -18))):
        yy = dy - (i % 4)
        if (i + k) % 3 != 2 and GY + yy > 3:
            p(c, CX + dx, GY + yy, CORE)
    return c


def end(i):
    c = Canvas(SIZE, SIZE)
    r = 10 - i
    if r > 2:
        c.ellipse(CX - r, GY - 3, CX + r, GY + 3, TEAL if i < 3 else DARK, fill=False)
    # hạt rơi xuống và mờ
    for k, (dx, dy0) in enumerate(((-8, -12), (8, -16), (-4, -8), (5, -20), (0, -14))):
        y = dy0 + i * 3
        if GY + y < GY + 1:
            p(c, CX + dx, GY + y, GREEN if i < 2 else TEAL if i < 4 else DARK)
    if i <= 1:
        glow(c, CX, GY, 4 - i, FADE)
    return c


ANIMATIONS = [
    ("cast", [cast(i) for i in range(5)], 14, False),
    ("loop", [loop(i) for i in range(8)], 12, True),
    ("end", [end(i) for i in range(5)], 12, False),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=5)
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=5)
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop}
                     for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
