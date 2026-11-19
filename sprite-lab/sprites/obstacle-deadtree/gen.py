#!/usr/bin/env python3
"""Generator cho sprite "obstacle-deadtree" (Sprite Lab).

Sửa file này rồi:
  gamekit art run obstacle-deadtree              vẽ lại + kiểm tra metadata
  gamekit art lab obstacle-deadtree [sheet|move] thử: mọi animation cạnh nhau / điều khiển di chuyển
  gamekit art shot obstacle-deadtree [sheet|move] chụp ảnh để agent tự xem
  gamekit art promote obstacle-deadtree <game>   khi đạt: chép strip + json vào game

File sinh ra (cạnh gen.py, trong sprite-lab/sprites/obstacle-deadtree/):
  obstacle-deadtree_strip.png   mọi frame, trái sang phải (animation nối tiếp nhau)
  obstacle-deadtree.json        frame_size, ĐIỂM NEO, danh sách animation {name, start, frames, fps, loop}
  obstacle-deadtree.png         frame đầu (icon)
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

NAME = "obstacle-deadtree"
SIZE = 48
# Vật cản Đầm Lầy Độc (games/bach-ai design/obstacles.md): cây chết mục, cành trơ cong, rêu xanh độc,
# chân ngập nước đầm. Chỉ gốc chặn đường; neo giữa gốc trên đất.
ANCHOR = (24.0, 45.0)
HERE = Path(__file__).resolve().parent
OUT = HERE
PALETTE = {"o": "#14120c", "K": "#2e2a1e", "k": "#4a4232", "b": "#6a6048", "l": "#857a5c",
           "g": "#5a6a2e", "G": "#9fd04a", "w": "#3a4a30", "W": "#55704a"}


def idle(i: int) -> Canvas:
    c = Canvas(SIZE, SIZE)
    p = PALETTE
    c.ellipse(12, 41, 36, 47, p["w"])       # marsh water round the foot
    c.ellipse(15, 42, 30, 45, p["W"])
    c.polygon([(19, 45), (21, 16), (27, 16), (29, 45)], p["k"])   # trunk
    c.line(24, 18, 25, 44, p["b"])
    c.line(26, 20, 27, 40, p["l"])
    c.line(21, 22, 21, 43, p["K"])
    # bare twisted branches
    c.line(22, 22, 12, 12, p["k"], 3)
    c.line(12, 12, 8, 4, p["k"], 2)
    c.line(12, 12, 6, 14, p["k"], 2)
    c.line(26, 18, 34, 8, p["k"], 3)
    c.line(34, 8, 40, 6, p["k"], 2)
    c.line(34, 8, 33, 2, p["k"], 2)
    c.line(27, 28, 38, 22, p["k"], 2)
    c.line(38, 22, 42, 24, p["k"], 1)
    c.line(23, 16, 23, 8, p["k"], 2)
    # hollow knot and poison moss
    c.ellipse(22, 27, 25, 31, p["K"])
    for x, y in ((20, 36), (21, 38), (27, 33), (28, 34), (12, 12), (34, 9), (22, 21)):
        c.pixel(x, y, p["g"])
    for x, y in ((21, 37), (28, 33), (13, 12)):
        c.pixel(x, y, p["G"])
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
