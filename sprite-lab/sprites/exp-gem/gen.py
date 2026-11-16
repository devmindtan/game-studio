#!/usr/bin/env python3
"""Generator cho sprite "exp-gem": viên kinh nghiệm quái rơi ra (Bách Ải). Pha lê xanh lam 8x8, lấp lánh.

Neo (4, 4) tâm viên. Animation: idle 4 (một điểm sáng chạy qua mặt viên).  Chạy: gamekit art run exp-gem
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

PAL = {"o": "#1b3a6b", "m": "#4aa3ff", "l": "#a8dcff", "d": "#2a6cc2", "w": "#ffffff"}
FRAMES = [
    ["...o....", "..oLo...", ".omlmo..", "omlmmmo.", ".odmdo..", "..odo...", "...o....", "........"],
    ["...o....", "..olo...", ".owlmo..", "omlmmmo.", ".odmdo..", "..odo...", "...o....", "........"],
    ["...o....", "..olo...", ".omlmo..", "omlwmmo.", ".odmdo..", "..odo...", "...o....", "........"],
    ["...o....", "..olo...", ".omlmo..", "omlmmmo.", ".odmwo..", "..odo...", "...o....", "........"],
]


def main() -> None:
    pal = dict(PAL, L=PAL["l"])
    frames = [from_rows(rows, pal) for rows in FRAMES]
    export(HERE, "exp-gem", [("idle", frames, 8, True, {"durations_ms": [400, 80, 80, 80], "hitbox": {"shape":"rect","center":[3.5,3.5],"active":[0,3]}})],
           anchor=(3.5, 3.5), preview_scale=16, gif_scale=8)
    print("ok")


if __name__ == "__main__":
    main()
