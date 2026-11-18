#!/usr/bin/env python3
"""Generator cho sprite "essence-pickup": Tinh hoa, nguyên liệu mở cây kỹ năng (Bách Ải), rơi từ quái
tinh anh và boss. Ngọn lửa linh hồn 12x12 tím hồng, lõi trắng: khác viên kinh nghiệm (pha lê xanh) và
đồng vàng ngay ở 1x. Tham khảo: các gói pickup pixel (soul/energy orb 12-16 px, lửa + điểm sáng).

Neo (5.5, 6.5) tâm ngọn lửa. Animation: idle 6 (lửa lay, điểm sáng chạy).  Chạy: gamekit art run essence-pickup
"""

import sys
from pathlib import Path


def _workspace() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools/gamekit/pipeline/spritekit.py").exists():
            return parent
    raise SystemExit("Không tìm thấy tools/gamekit/pipeline — chạy trong workspace game-studio")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_workspace() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))

from spritekit import from_rows  # noqa: E402
from sheet import export  # noqa: E402

PAL = {"o": "#3a1446", "d": "#8a2e9e", "m": "#d74fd6", "l": "#ff9cf0", "w": "#ffffff"}
FRAMES = [
    ["....o.......", "...odo......", "...odmo.....", "..odmmo.....", "..odmlmo....", ".odmllmmo...",
     ".odmlwlmo...", ".odmlllmo...", "..odmlmdo...", "...odmdo....", "....ooo.....", "............"],
    [".....o......", "....odo.....", "...odmo.....", "...odmmo....", "..odmlmo....", ".odmllmmo...",
     ".odmlwlmo...", ".odmlllmo...", "..odmlmdo...", "...odmdo....", "....ooo.....", "............"],
    ["......o.....", ".....odo....", "....odmo....", "...odmmo....", "..odmlmmo...", ".odmllmmo...",
     ".odmllwmo...", ".odmlllmo...", "..odmlmdo...", "...odmdo....", "....ooo.....", "............"],
    [".....o......", "....odo.....", "....odmo....", "...odmmo....", "..odmlmmo...", ".odmllmmo...",
     ".odmlwlmo...", ".odmlllmo...", "..odmlmdo...", "...odmdo....", "....ooo.....", "............"],
    ["....o.......", "...odo......", "...odmo.....", "..odmmo.....", "..odmlmo....", ".odmllmmo...",
     ".odwllmmo...", ".odmlllmo...", "..odmlmdo...", "...odmdo....", "....ooo.....", "............"],
    ["...o........", "...odo......", "..odmo......", "..odmmo.....", "..odmlmo....", ".odmllmmo...",
     ".odmlwlmo...", ".odmlllmo...", "..odmlmdo...", "...odmdo....", "....ooo.....", "............"],
]


def main() -> None:
    frames = [from_rows(rows, PAL) for rows in FRAMES]
    export(HERE, "essence-pickup", [("idle", frames, 8, True, {"hitbox": {"shape": "rect", "center": [4.5, 6.5], "active": [0, 5]}})],
           anchor=(4.5, 6.5), preview_scale=16, gif_scale=8)
    print("ok")


if __name__ == "__main__":
    main()
