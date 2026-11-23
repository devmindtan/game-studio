"""Generator cho "arrow-c": mũi tên của Cung thủ, phương án C (tên lông xanh, vệt gió), 2026-11-23.
Vẽ thẳng từng hướng bay (lib/arrowfx.py), mật độ gấp đôi (px_scale 0.5), neo = đầu mũi tên.
Chạy: gamekit art run arrow-c
"""
import json
import sys
from pathlib import Path


def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
import arrowfx  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE = 56
C = SIZE / 2
FPS = 12.0
HB = {"shape": "rect", "center": [C, C], "active": [0, 3]}
DIRS = [("fly", 0), ("fly_right", 0), ("fly_left", 180), ("fly_up", 270), ("fly_down", 90)] + \
    [("fly_%03d" % round(k * 22.5), k * 22.5) for k in range(16)]
ANIM = [(n, arrowfx.arrow("c", SIZE, d), FPS, True, {"hitbox": dict(HB)}) for n, d in DIRS]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
