#!/usr/bin/env python3
"""chibi-base: the standard 64x64 chibi body, proportions B (user 2026-11-23), sprite-lab/BODY_PLAN.md step 1.
Bare body (skin, plain shirt and shorts) on lib/chibi_body joints: idle 2, walk 8, hurt 3, dash 4, shoot 13, slash 6, spell 7, death 6
(LPC rhythm and frame counts, our own drawing).
Every outfit layer is drawn on the same joints. Anchor: between the feet on the ground line.
Chạy: gamekit art run chibi-base  ·  thử: gamekit art shot chibi-base sheet|move
"""
import sys
from pathlib import Path


def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from sheet import export  # noqa: E402
import chibi_body as cb  # noqa: E402

PAL = {"skin": "#f6caa8", "skin_d": "#d89c7c", "hair": "#c26a2a", "eye": "#1b1726", "cheek": "#f08a8a",
       "shirt": "#e8e2d0", "shorts": "#2f5f6e", "shoe": "#5a3d28", "shoe_d": "#3d2919", "outline": "#1b1726"}
PR = cb.PROPORTIONS[cb.STANDARD]
HB = {"shape": "rect", "center": [32.0, 44.0]}


def frames(anim):
    out = []
    for i in range(cb.ANIMS[anim]):
        c = cb.draw_bare(cb.skeleton(anim, i, PR), PR, PAL)
        out.append(cb.lay_down(c) if cb.lying(anim, i) else c)
    return out


ANIM = [("idle", frames("idle"), 3, True, {"durations_ms": [500, 500], "hitbox": dict(HB, active=[0, 1])}),
        ("walk", frames("walk")[1:], 10, True, {"hitbox": dict(HB, active=[0, 7])}),   # frame 0 (stand) is idle
        ("hurt", frames("hurt"), 12, False, {"durations_ms": [90, 110, 120], "hitbox": dict(HB, active=[0, 2])}),
        ("dash", frames("dash"), 14, False, {"durations_ms": [60, 70, 70, 90], "hitbox": dict(HB, active=[0, 3])}),
        ("shoot", frames("shoot"), 14, False, {"hitbox": dict(HB, active=[0, 12])}),
        ("slash", frames("slash"), 12, False, {"hitbox": dict(HB, active=[0, 5])}),
        ("spell", frames("spellcast"), 10, False, {"hitbox": dict(HB, active=[0, 6])}),
        ("death", frames("death"), 8, False, {"durations_ms": [120, 120, 120, 120, 120, 500], "hitbox": dict(HB, active=[0, 5])})]

if __name__ == "__main__":
    export(HERE, HERE.name, ANIM, anchor=(float(cb.ROOT_X), float(cb.GROUND)), ground=True)
    print("OK", HERE.name)
