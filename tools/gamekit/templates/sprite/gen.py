#!/usr/bin/env python3
"""Generator cho sprite "__NAME__".

Sửa file này rồi chạy:  gamekit art run <game> __NAME__

File sinh ra:
  assets/sprites/custom/__NAME__/__NAME__.png        frame chính (Godot dùng)
  assets/sprites/custom/__NAME__/__NAME___strip.png  dải animation (nếu có nhiều frame)
  assets/source/sprites/__NAME__/preview.png          ảnh phóng to để agent xem
  assets/source/sprites/__NAME__/anim.gif             xem animation
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))

from spritekit import Canvas, gif, preview, strip  # noqa: E402

NAME = "__NAME__"
SIZE = __SIZE__

HERE = Path(__file__).resolve().parent          # assets/source/sprites/<name>
GAME = HERE.parents[3]                           # thư mục game
OUT = GAME / "assets/sprites/custom" / NAME      # PNG cho Godot

# Palette: giữ ít màu, đủ tối/sáng để đọc silhouette ở 1x.
PALETTE = {
    "o": "#2b1b0e",
    "d": "#8a5a1e",
    "m": "#ffd34d",
    "l": "#fff3b0",
}


def frame(i: int) -> Canvas:
    """Một frame. Thay bằng thiết kế thật của bạn.

    Cách nhanh nhất là vẽ bằng ASCII map:

        from spritekit import from_rows
        rows = [
            "..oo..",
            ".ommo.",
            "ommmmo",
            ".ommo.",
            "..oo..",
        ]
        c = from_rows(rows, PALETTE)

    Ở đây là hình tròn giữ chỗ để `gamekit art run` có kết quả ngay.
    """
    c = Canvas(SIZE, SIZE)
    pad = max(1, SIZE // 8)
    c.ellipse(pad, pad, SIZE - 1 - pad, SIZE - 1 - pad, PALETTE["m"], fill=True)
    c.ellipse(pad * 2, pad * 2, SIZE // 2, SIZE // 2, PALETTE["l"], fill=True)
    if i % 2:
        c.pixel(SIZE // 2, pad + 1, "#ffffff")
    c.outline(PALETTE["o"])
    return c


def main() -> None:
    frames = [frame(i) for i in range(4)]
    OUT.mkdir(parents=True, exist_ok=True)
    frames[0].save(OUT / f"{NAME}.png")
    strip(frames).save(OUT / f"{NAME}_strip.png")
    zoom = max(2, 256 // SIZE)
    preview(frames, HERE / "preview.png", scale=zoom)
    gif(frames, HERE / "anim.gif", fps=8, scale=max(1, zoom // 2))
    print(f"sprite:  {OUT / f'{NAME}.png'}")
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
