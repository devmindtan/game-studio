#!/usr/bin/env python3
"""Generator cho sprite "obstacle-tree" (Sprite Lab).

Sửa file này rồi:
  gamekit art run obstacle-tree              vẽ lại + kiểm tra metadata
  gamekit art lab obstacle-tree [sheet|move] thử: mọi animation cạnh nhau / điều khiển di chuyển
  gamekit art shot obstacle-tree [sheet|move] chụp ảnh để agent tự xem
  gamekit art promote obstacle-tree <game>   khi đạt: chép strip + json vào game

File sinh ra (cạnh gen.py, trong sprite-lab/sprites/obstacle-tree/):
  obstacle-tree_strip.png   mọi frame, trái sang phải (animation nối tiếp nhau)
  obstacle-tree.json        frame_size, ĐIỂM NEO, danh sách animation {name, start, frames, fps, loop}
  obstacle-tree.png         frame đầu (icon)
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

NAME = "obstacle-tree"
SIZE = 48
# Vật cản Rừng Âm U (games/bach-ai design/obstacles.md): cây cổ thụ, tán tròn ba tầng, rễ bám đất.
# Chỉ gốc cây chặn đường (game dùng bán kính gốc); neo giữa gốc trên đất.
ANCHOR = (24.0, 45.0)
HERE = Path(__file__).resolve().parent
OUT = HERE
PALETTE = {"o": "#10160f", "K": "#3a2618", "k": "#5a3a22", "b": "#7a5230",
           "D": "#173823", "d": "#22492c", "m": "#2f5a3e", "l": "#3f7a4e", "w": "#5e9a62"}


def idle(i: int) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = PALETTE
    # trunk with roots
    c.polygon([(20, 46), (21, 28), (27, 28), (28, 46)], p["k"])
    c.polygon([(16, 46), (20, 41), (22, 46)], p["k"])
    c.polygon([(26, 46), (28, 41), (33, 46)], p["k"])
    c.line(25, 30, 26, 45, p["b"])
    c.line(22, 32, 22, 44, p["K"])
    # canopy: dark base, mid, lit top-left, a few leaf highlights
    c.ellipse(4, 10, 44, 34, p["D"])
    c.ellipse(6, 6, 40, 28, p["d"])
    c.ellipse(9, 2, 36, 22, p["m"])
    c.ellipse(11, 3, 27, 15, p["l"])
    for x, y in ((14, 6), (18, 4), (13, 10), (30, 9), (22, 7)):
        c.pixel(x, y, p["w"])
        c.pixel(x + 1, y, p["w"])
    for x, y in ((8, 26), (38, 24), (20, 30), (31, 29)):   # leaf clumps hanging under the canopy
        c.ellipse(x - 3, y - 2, x + 3, y + 2, p["D"])
    c.outline(p["o"])
    return c


ANIMATIONS = [("idle", [idle(0)], 1, True)]


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
