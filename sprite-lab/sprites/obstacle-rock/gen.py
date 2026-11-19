#!/usr/bin/env python3
"""Generator cho sprite "obstacle-rock" (Sprite Lab).

Sửa file này rồi:
  gamekit art run obstacle-rock              vẽ lại + kiểm tra metadata
  gamekit art lab obstacle-rock [sheet|move] thử: mọi animation cạnh nhau / điều khiển di chuyển
  gamekit art shot obstacle-rock [sheet|move] chụp ảnh để agent tự xem
  gamekit art promote obstacle-rock <game>   khi đạt: chép strip + json vào game

File sinh ra (cạnh gen.py, trong sprite-lab/sprites/obstacle-rock/):
  obstacle-rock_strip.png   mọi frame, trái sang phải (animation nối tiếp nhau)
  obstacle-rock.json        frame_size, ĐIỂM NEO, danh sách animation {name, start, frames, fps, loop}
  obstacle-rock.png         frame đầu (icon)
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

NAME = "obstacle-rock"
SIZE = 32
# Vật cản Đồng cỏ (games/bach-ai design/obstacles.md): tảng đá chặn đường, neo giữa chân đá trên đất.
ANCHOR = (16.0, 27.0)

HERE = Path(__file__).resolve().parent
OUT = HERE

PALETTE = {
    "o": "#1b1726",   # outline
    "D": "#4a4a58",   # shadow side
    "d": "#6a6a7a",
    "m": "#8a8a98",   # body
    "l": "#b4b4c0",   # lit top
    "w": "#d8d8e0",   # highlight
    "g": "#3f6136",   # moss (Đồng cỏ tuft colour)
    "G": "#5a8a46",
    "s": "#00000055", # ground shadow
}
from spritekit import from_rows  # noqa: E402

ROCK = [
    "..........oooooo..............",
    "........oowwllllooo...........",
    "......oowlllllllmmmoo.........",
    ".....owlllllmmmmmmmmmo........",
    "....owllllmmmmmmmmmdmmoooo....",
    "...olllmmmmmmmmmmddmmmlllloo..",
    "...olmmmmmmmmmmmdmmmmlllllmmo.",
    "..olmmmmmmGmmmmdmmmmmmmmmmmmo.",
    "..ommmmmGGgGmmdmmmmmmmmmmmmdo.",
    ".ommmmmGggggmmdmmmmmmmmmmmddo.",
    ".ommmmmmggmmmdmmmmmmmmmmmdddo.",
    ".odmmmmmmmmmmmmmmmmmmmmmdddDo.",
    ".oddmmmmmmmmmmmmmmmmmmddddDDo.",
    ".oDddddmmmmmmmmmmmmdddddDDDo..",
    "..oDDddddddddddddddddDDDDDo...",
    "...ooDDDDDDDDDDDDDDDDDDoooo...",
    ".....oooooooooooooooooo.......",
]


def idle(i: int) -> Canvas:
    c = Canvas(SIZE, SIZE)
    c.ellipse(3, 24, 28, 30, PALETTE["s"], fill=True)   # shadow on the ground
    rock = from_rows(ROCK, PALETTE)
    c.paste(rock, 1, 27 - rock.height + 1)
    return c


ANIMATIONS = [
    ("idle", [idle(0)], 1, True),
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
