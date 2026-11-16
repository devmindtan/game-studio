#!/usr/bin/env python3
"""Generator cho sprite "gold-coin": đồng vàng quái rơi ra (Bách Ải). 8x8, xoay 4 frame (mặt, nghiêng, cạnh, nghiêng).

Neo (4, 4) tâm đồng xu. Animation: idle 4.  Chạy: gamekit art run gold-coin
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

PAL = {"o": "#6b4410", "m": "#f2c443", "l": "#fff2a8", "d": "#c08a1e"}
FRAMES = [
    ["..oooo..", ".ommmdo.", "omlmmmdo", "omlmdmdo", "ommmmmdo", "ommmmddo", ".oddddo.", "..oooo.."],
    ["...oo...", "..omdo..", ".omlmdo.", ".omldmo.", ".ommmdo.", ".ommddo.", "..oddo..", "...oo..."],
    ["...oo...", "...od...", "...ld...", "...md...", "...md...", "...md...", "...od...", "...oo..."],
    ["...oo...", "..odmo..", ".odmmlo.", ".omdlmo.", ".odmmmo.", ".oddmmo.", "..oddo..", "...oo..."],
]


def main() -> None:
    frames = [from_rows(rows, PAL) for rows in FRAMES]
    export(HERE, "gold-coin", [("idle", frames, 8, True, {})], anchor=(4.0, 4.0), preview_scale=16, gif_scale=8)
    print("ok")


if __name__ == "__main__":
    main()
