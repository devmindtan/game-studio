#!/usr/bin/env python3
"""retaliate-shock — Phản chấn: a slow, readable counter-shockwave.

Replaces the old reused stomp burst (too quick to see). 16 frames / ~1.5 s:
  0-1   bright pulse at the hero (the hit that sets it off)
  2-6   the ring opens, cracks run out, dust and stones fly outward (hit frames)
  7-11  the ring reaches full reach and slows, debris settles
  12-15 the last motes dither away (0.95 s outro)

Double density (px_scale 0.5), 112x112, anchor at the centre, hit mask measured
from the art. Earth/dust palette from stormfx, gold highlight for the knight.
Art reference: internet step skipped (search HTTP 402); local palette + rules.
"""
import json
import math
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
import fxkit as fk  # noqa: E402
from spritekit import Canvas  # noqa: E402
from icefx import _p, _fade  # noqa: E402
from stormfx import DUST, DUST_L, DIRT, DIRT_D, STONE, STONE_L, _qnoise, _scuff  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
W = H = 112
C = W / 2
RADIUS = 52
TAU = math.tau

# 16 frames ~1.52 s; the hits end at 0.565 s and the outro is 0.95 s (rules)
MS = [75, 75, 75, 80, 80, 85, 95, 100, 105, 110, 115, 120, 100, 100, 100, 100]


def _crack(c, a, length, seed, hot):
    x, y = C, C
    steps = int(length)
    for s in range(steps):
        a += (_qnoise(s, seed, 7) - 0.5) * 0.28
        x += math.cos(a)
        y += math.sin(a) * 0.72
        col = DIRT_D if s < 3 else (DIRT if s % 3 else DUST)
        if hot and s >= 3:
            col = DUST_L if s % 2 else DUST
        _p(c, x, y, col)


def frame(i):
    c = Canvas(W, H)

    if i <= 1:
        fk.glow(c, C, C, RADIUS * (0.24 + 0.10 * i),
                [DIRT_D, DUST, DUST_L, "#fff2d0"], density=0.85)
        fk.rays(c, C, C, RADIUS * 0.20, RADIUS * (0.42 + 0.08 * i), 12, DUST_L, "#fff2d0", rot=0.2)
        fk.ring_band(c, C, C, RADIUS * (0.30 + 0.12 * i), [DIRT_D, DUST, DUST_L])
    else:
        p = min(1.0, (i - 2) / 7.0)
        rr = RADIUS * (0.28 + 0.72 * p)
        _scuff(c, C, C, rr * 0.92, 17 + i % 3, DUST, 0.13 if i < 12 else 0.09)

        for k in range(7):
            _crack(c, k * TAU / 7 + 0.25, rr * (0.55 + 0.25 * (k % 3)),
                   31 + k, hot=(i < 9))

        # a broken band with a dark underside reads as a wave, not a drawn circle
        n = max(70, int(TAU * rr * 2.3))
        for s in range(n):
            if _qnoise(s // 5, i // 2, 5) < 0.16:
                continue
            a = s * TAU / n
            wob = 0.95 + 0.09 * _qnoise(s, i, 11)
            x = C + math.cos(a) * rr * wob
            y = C + math.sin(a) * rr * wob
            _p(c, x, y + 1, DIRT_D)
            _p(c, x, y, DUST if s % 4 else DUST_L)
            if s % 3 == 0:
                _p(c, C + math.cos(a) * (rr * wob - 2),
                   C + math.sin(a) * (rr * wob - 2), DIRT)

        # dust puffs ride the wave, stones tumble just ahead of it
        for k in range(9):
            a = k * TAU / 9 + 0.2
            d = rr * (0.82 + 0.2 * _qnoise(k, i, 13))
            x, y = C + math.cos(a) * d, C + math.sin(a) * d
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if abs(dx) + abs(dy) > 1:
                        continue
                    if _qnoise(k * 7 + dx, i * 3 + dy, 19) < 0.42:
                        _p(c, x + dx, y + dy, DUST if dy <= 0 else DUST_L)
            if k % 2 == 0 and i < 12:
                lift = 5 * math.sin(math.pi * min(1.0, (i - 2) / 10))
                sx, sy = C + math.cos(a) * (d + 5), C + math.sin(a) * (d + 5) - lift
                _p(c, sx, sy, STONE_L)
                _p(c, sx + 1, sy, STONE)

    if i >= 12:
        _fade(c, min(0.95, 0.15 + 0.20 * (i - 11)))
    return c


frames = [frame(i) for i in range(16)]
masks = [fk.mask_art(f, C, C,
                     RADIUS * 0.35 if i < 2 else RADIUS * (0.28 + 0.72 * min(1.0, (i - 2) / 7.0)) + 4)
         for i, f in enumerate(frames)]
ANIM = [("shock", fk.FxFrames(frames, masks), 13, False,
         {"durations_ms": MS,
          "hitbox": {"shape": "circle", "center": [C, C], "active": [2, 6],
                     "radius": float(RADIUS), "inner": 0.0}})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=1, gif_scale=1)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
