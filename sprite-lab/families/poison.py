#!/usr/bin/env python3
"""Family generator for Độc vụ (poison-splash-i .. v and poison-pool-i .. v, design/rogue-kits.md, 2026-11-26).

poison-splash-<t>: a flask drops in, shatters and splashes (fx_craft: 12 frames, frame 0 the falling flask as the
lead-in, hits on frames 1-4 from a hit mask disk, then drops settle and fade over 0.5 s).
poison-pool-<t>: the pool left behind, a looping 6-frame bubbling puddle drawn under the monsters (the run sizes it to
the zone radius). Each tier: a wider splash, more bubbles; toxic green, violet, then gold-green.
Chạy: gamekit art run poison-splash-i ; gamekit art run poison-pool-i
"""
TIER_FILE = globals().get("TIER_FILE", __file__)
# tier: [splash radius, liquid (dark, mid, light), glass]
TIERS = {"i": [30, ("#1e4a1e", "#3a8a2a", "#8ae05a"), "#c8f0ff"], "ii": [33, ("#1e4a2a", "#2a9a4a", "#9af07a"), "#c8f0ff"],
         "iii": [36, ("#3a1660", "#7a3ab8", "#c38df5"), "#e0d0ff"], "iv": [39, ("#3a1660", "#9a4ad0", "#e0b8ff"), "#ffffff"],
         "v": [42, ("#3a4a10", "#8ab020", "#f0ff8a"), "#fff4b0"]}
import json
import math
import sys
from pathlib import Path


def _ws():
    for p in Path(TIER_FILE).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(TIER_FILE).resolve().parent
TIER = HERE.name.rsplit("-", 1)[1]
TN = "i ii iii iv v".split().index(TIER)
R, (D, M, L), GLASS = TIERS[TIER]
sys.path.insert(0, str(_ws() / "tools/gamekit/pipeline"))
sys.path.insert(0, str(Path(TIER_FILE).resolve().parents[2] / "lib"))
from spritekit import Canvas  # noqa: E402
from fxkit import FxFrames, mask_disk  # noqa: E402
from sheet import export  # noqa: E402

NAME = HERE.name
OUT = "#14111c"


def splash():
    S = 2 * R + 20
    C = S // 2
    out = []
    for f in range(12):
        c = Canvas(S, S)
        if f == 0:                                           # the flask, falling in
            c.ellipse(C - 4, C - 14, C + 4, C - 6, M)
            c.rect(C - 1, C - 18, C + 1, C - 14, GLASS)
            c.pixel(C - 2, C - 12, L)
        else:
            g = min(1.0, f / 4.0)
            r = R * g
            fade = f >= 8
            c.ellipse(int(C - r), int(C - r * 0.55), int(C + r), int(C + r * 0.55), D if fade else M)
            if not fade:
                c.ellipse(int(C - r * 0.6), int(C - r * 0.3), int(C + r * 0.6), int(C + r * 0.3), L)
            for k in range(6 + TN * 2):                       # droplets thrown out, then falling back
                a = k * math.tau / (6 + TN * 2) + 0.3
                d = r + 4 + (f if f < 6 else 12 - f) * 2
                if d < S // 2 - 2:
                    c.rect(int(C + math.cos(a) * d), int(C + math.sin(a) * d * 0.55) - 1,
                           int(C + math.cos(a) * d) + 1, int(C + math.sin(a) * d * 0.55), L if f < 6 else M)
            if f <= 3:                                        # glass shards
                for k in range(4):
                    a = k * math.tau / 4 + 0.8
                    c.pixel(int(C + math.cos(a) * (6 + f * 4)), int(C + math.sin(a) * (4 + f * 3)), GLASS)
            if f >= 10 and f % 2:
                c = Canvas(S, S)
        c.outline(OUT)
        out.append(c)
    masks = [mask_disk(S, S, C, C, R if 1 <= k <= 4 else 0) for k in range(12)]
    return S, FxFrames(out, masks), [("burst", None, 12.0, False, {"hitbox": {"shape": "circle", "center": [C, C], "active": [1, 4]}})]


def pool():
    S = 96
    C = S // 2
    out = []
    for f in range(6):
        c = Canvas(S, S)
        c.ellipse(4, C - 22, S - 4, C + 22, D)
        c.ellipse(10, C - 17, S - 10, C + 17, M)
        for k in range(4 + TN * 2):                           # bubbles rising and popping
            x = 14 + (k * 23 + TN * 7) % (S - 28)
            y = C - 10 + (k * 13) % 20
            ph = (f + k) % 6
            if ph < 4:
                c.ellipse(x - 1 - ph // 2, y - 1 - ph // 2, x + 1 + ph // 2, y + 1 + ph // 2, L, fill=ph < 2)
        c.outline(OUT)
        out.append(c)
    return S, out


if HERE.name.startswith("poison-splash"):
    S, FR, spec = splash()
    C = S / 2
    ANIM = [(spec[0][0], FR, spec[0][2], spec[0][3], spec[0][4])]
else:
    S, FR = pool()
    C = S / 2
    ANIM = [("loop", FR, 8.0, True, {})]

if __name__ == "__main__":
    export(HERE, NAME, ANIM, anchor=(C, C), preview_scale=2, gif_scale=2)
    meta = HERE / f"{NAME}.json"
    m = json.loads(meta.read_text())
    m["px_scale"] = 0.5
    meta.write_text(json.dumps(m, indent=2) + "\n")
    print("OK", NAME)
