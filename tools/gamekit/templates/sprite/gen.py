#!/usr/bin/env python3
"""Generator cho sprite "__NAME__" (Sprite Lab).

Sửa file này rồi:
  gamekit art run __NAME__              vẽ lại + kiểm tra metadata
  gamekit art lab __NAME__ [sheet|move] thử: mọi animation cạnh nhau / điều khiển di chuyển
  gamekit art shot __NAME__ [sheet|move] chụp ảnh để agent tự xem
  gamekit art promote __NAME__ <game>   khi đạt: chép strip + json vào game

File sinh ra (cạnh gen.py, trong sprite-lab/sprites/__NAME__/):
  __NAME___strip.png   mọi frame, trái sang phải (animation nối tiếp nhau)
  __NAME__.json        frame_size, ĐIỂM NEO, danh sách animation {name, start, frames, fps, loop}
  __NAME__.png         frame đầu (icon)
  preview.png          mỗi animation một hàng, phóng to có lưới (để agent đọc)
  <animation>.gif      xem chuyển động (cho người)

Tên animation mà lab và game hiểu: idle, walk/run/fly/move, jump, attack, spell, hurt, death.
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

NAME = "__NAME__"
SIZE = __SIZE__
# Điểm neo (pixel nguồn) rơi đúng vào vị trí của vật thể trong game: giữa hai bàn chân (nhân vật
# đứng trên đất), tâm thân (vật bay), đầu giọt mưa… None = tâm phần có hình (chỉ đúng khi hình
# đối xứng và khung bao không đổi giữa các frame). Ví dụ nhân vật: ANCHOR = (SIZE / 2, SIZE - 2).
ANCHOR = None

HERE = Path(__file__).resolve().parent  # sprite-lab/sprites/<name>
OUT = HERE

# Palette: giữ ít màu, đủ tối/sáng để đọc silhouette ở 1x.
PALETTE = {
    "o": "#2b1b0e",
    "d": "#8a5a1e",
    "m": "#ffd34d",
    "l": "#fff3b0",
}


def idle(i: int) -> Canvas:
    """Một frame của "idle". Thay bằng thiết kế thật; vẽ nhanh nhất bằng ASCII map:

        from spritekit import from_rows
        c = from_rows(["..oo..", ".ommo.", "ommmmo", ".ommo.", "..oo.."], PALETTE)

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


# (tên, frames, fps, loop). Thêm animation bằng cách thêm dòng: ("walk", [walk(i) for i in range(6)], 10, True)
ANIMATIONS = [
    ("idle", [idle(i) for i in range(4)], 6, True),
]


def main() -> None:
    flat = [f for _, frames, _, _ in ANIMATIONS for f in frames]
    strip(flat).save(OUT / f"{NAME}_strip.png")
    flat[0].save(OUT / f"{NAME}.png")
    # Preview: mỗi animation một hàng.
    cols = max(len(frames) for _, frames, _, _ in ANIMATIONS)
    sheet = Canvas(cols * SIZE, len(ANIMATIONS) * SIZE)
    for row, (_, frames, _, _) in enumerate(ANIMATIONS):
        sheet.paste(strip(frames), 0, row * SIZE)
    preview([sheet], HERE / "preview.png", scale=max(2, 256 // SIZE))
    for anim, frames, fps, _ in ANIMATIONS:
        gif(frames, HERE / f"{anim}.gif", fps=fps, scale=max(1, 128 // SIZE))
    write_anim_meta(OUT / f"{NAME}.json",
                    [{"name": n, "frames": f, "fps": fps, "loop": loop} for n, f, fps, loop in ANIMATIONS],
                    anchor=ANCHOR)
    print(f"strip:   {OUT / f'{NAME}_strip.png'}")
    print(f"preview: {HERE / 'preview.png'}")


if __name__ == "__main__":
    main()
