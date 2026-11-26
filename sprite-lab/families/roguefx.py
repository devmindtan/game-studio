#!/usr/bin/env python3
"""Family generator for the archer / assassin skill bursts (lib/roguefx.py, 2026-11-26). Each sprite folder's gen.py
runs this file with its own __file__; SPRITES maps the folder name to [drawing, frame size, hit radius, active].
Chạy: gamekit art run <tên>
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
SPRITES = {"arrow-rain": ["arrow_rain", 112, 40, [3, 7]], "thorn-trap": ["thorn_trap", 96, 32, [4, 7]],
           "thorn-trap-i": ["thorn_trap", 80, 28, [4, 7]], "thorn-trap-ii": ["thorn_trap", 88, 30, [4, 7]],
           "thorn-trap-iii": ["thorn_trap", 96, 32, [4, 7]], "thorn-trap-iv": ["thorn_trap", 96, 34, [4, 7]],
           "thorn-trap-v": ["thorn_trap", 104, 36, [4, 7]],
           "hawk-dive": ["hawk_dive", 112, 28, [4, 6]], "smoke-bomb": ["smoke_bomb", 112, 44, [1, 5]],
           "blade-ring": ["blade_ring", 128, 50, [2, 7]], "shadow-strike": ["shadow_strike", 80, 26, [2, 5]],
           # Kết liễu's look-only burst (the kill is made by Enemies), one per tier
           # tiers of the kept skills (design/rogue-kits.md step 12): [drawing, size, radius, active, tier]
           **{f"arrow-rain-{t}": ["arrow_rain", 112 + k * 4, 36 + k * 2, [3, 7], k] for k, t in enumerate(["i", "ii", "iii", "iv", "v"])},
           **{f"smoke-bomb-{t}": ["smoke_bomb", 104 + k * 6, 40 + k * 3, [1, 5], k] for k, t in enumerate(["i", "ii", "iii", "iv", "v"])},
           **{f"shadow-strike-{t}": ["shadow_strike", 72 + k * 4, 24 + k * 2, [2, 5], k] for k, t in enumerate(["i", "ii", "iii", "iv", "v"])},
           "execute-i": ["execute_burst", 64, 20, [1, 4]], "execute-ii": ["execute_burst", 72, 22, [1, 4]],
           "execute-iii": ["execute_burst", 72, 24, [1, 4]], "execute-iv": ["execute_burst", 80, 26, [1, 4]],
           "execute-v": ["execute_burst", 80, 28, [1, 4]]}
import json
import sys
from pathlib import Path


def _ws():
    for p in Path(TIER_FILE).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(TIER_FILE).resolve().parent
_V = SPRITES[HERE.name]
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(TIER_FILE).resolve().parents[2] / "lib"))
import roguefx  # noqa: E402
from fxkit import FxFrames, mask_disk  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
SIZE, RADIUS = _V[1], _V[2]
C = SIZE / 2
_FRAMES = getattr(roguefx, _V[0])(SIZE, RADIUS, *_V[4:])   # a 5th entry is the tier (0..4) for tiered drawings
# the damaging core is a disk of RADIUS on the active frames (rule hitbox / fx_craft: measured from a hit mask)
_MASKS = [mask_disk(SIZE, SIZE, C, C, RADIUS if _V[3][0] <= k <= _V[3][1] else 0) for k in range(len(_FRAMES))]
ANIM = [("burst", FxFrames(_FRAMES, _MASKS), 12, False, {"hitbox": {"shape": "circle", "center": [C, C], "active": _V[3]}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
