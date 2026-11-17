"""slam: the Ground Slam family seen from above (Bach Ai is a top-down arena).

One impact point; a heavy slam punches a jagged crater, throws angular rock
chips outward and rolls a broken shock ring across the ground. Earth DNA (see
the pixel-sprite skill): uneven, heavy, fractured, asymmetric — never the
symmetric ice rings of the frost family. Ground Slam is its own line, not a
copy of Earth Strike: Earth Strike is fault lines running out of the impact,
Ground Slam is the impact itself (crater + shock + thrown debris).

Tiers are evolution beats, each with a different silhouette:
  I   compact impact: small pit, one broken ring, a few chips.
  II  the ground splits: one long fault + secondary cracks, double shock ring.
  III a block of ground is punched up: square-shifted slab, shattered rim.
  IV  the shock becomes a landslide: a directional wave of dust and boulders.
  V   the ground collapses: wide caldera, a ring of upthrust pillars, magma.

10 frames, 14 fps, one shot: 0 impact · 1-2 shock and debris · 2-6 damage
frames (hitbox active) · 7-9 settle into crater, cracks, cooled chips.
Faint haze (alpha < 96) never counts for the hitbox (spritekit.fit_hitbox).
"""
from __future__ import annotations

import math
import random

from spritekit import Canvas, from_rows

ROCK = "#8a6a52"; ROCK_L = "#c79a6a"; ROCK_D = "#5a4335"; STRATA = "#6e503c"
CRACK = "#241a18"; SHADOW = "#171014"; DUST = "#c9ab82"; SAND = "#a9835e"
DUST_D = "#6b5236"; MAGMA = "#ff6a2a"; MAGMA_D = "#b8331a"; GLOW = "#ffd08a"
ASH = "#7c6a58"; SOIL = "#56402f"

CHUNK_PAL = {"L": ROCK_L, "M": ROCK, "D": ROCK_D, "S": STRATA}
CHUNKS = {
    0: [".LM.", "LMMD", ".LD."],
    1: ["..L..", ".LMM.", "LMSMD", "LMMDD", ".LDD."],
    2: [
        "...LL...",
        "..LMML..",
        ".LMMSMD.",
        "LMMSMMDD",
        "LMMMMMDD",
        ".LMMDDD.",
        "..LDDD..",
    ],
}
PUFF_PAL = {"L": DUST, "M": SAND, "D": DUST_D}
PUFFS = {
    0: [".LL..", "LLMML", ".MMD."],
    1: ["..LL...", ".LLLLM.", "LLMMMMD", ".MMMDD."],
    2: ["...LLL...", "..LLLLM..", ".LLMMMMD.", "LLMMMMMMD", ".MMMDDDD."],
}

# jagged crater outlines, not ellipses: earth breaks in blocks and chips
CALDERA = [
    (-1.0, 0.05), (-0.9, -0.35), (-0.65, -0.3), (-0.5, -0.6), (-0.2, -0.45),
    (0.05, -0.65), (0.35, -0.45), (0.6, -0.55), (0.9, -0.2), (0.85, 0.25),
    (0.55, 0.2), (0.4, 0.5), (0.1, 0.35), (-0.15, 0.55), (-0.45, 0.35),
    (-0.7, 0.5), (-0.9, 0.25),
]
BLOCK = [
    (-1.0, -0.55), (-0.8, -0.85), (-0.25, -0.8), (0.1, -1.0), (0.6, -0.85),
    (0.9, -0.5), (0.85, 0.2), (1.0, 0.5), (0.5, 0.7), (0.2, 0.95),
    (-0.3, 0.8), (-0.6, 1.0), (-0.9, 0.6), (-0.8, 0.2),
]

REACH = [0.0, 0.38, 0.62, 0.85, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
CRATER_SCALE = [0.55, 0.8, 1.0, 1.0, 1.0, 1.0, 1.0, 0.97, 0.93, 0.9]
RING_R = [0.0, 0.0, 0.62, 0.82, 1.0, 1.0, 0.96, 0.9, 0.0, 0.0]
RING_A = [0, 0, 250, 240, 225, 190, 130, 80, 0, 0]

_chunk_cache: dict[int, Canvas] = {}
_puff_cache: dict[int, Canvas] = {}


def _rgba(hex_col, alpha):
    s = hex_col.lstrip("#")
    r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    return (r, g, b, alpha)


def _paste_fade(c, art, x, y, alpha):
    img = art.img.copy()
    a = img.getchannel("A").point(lambda v: v * alpha // 255)
    img.putalpha(a)
    c.paste(img, int(x), int(y))


def _padded(art):
    """1px transparent margin so outline() has room for the border."""
    out = Canvas(art.width + 2, art.height + 2)
    out.paste(art, 1, 1)
    return out


def _chunk(size):
    if size not in _chunk_cache:
        _chunk_cache[size] = _padded(from_rows(CHUNKS[size], CHUNK_PAL)).outline(SHADOW)
    return _chunk_cache[size]


def _puff(size):
    if size not in _puff_cache:
        _puff_cache[size] = from_rows(PUFFS[size], PUFF_PAL)
    return _puff_cache[size]


def _arm(cx, cy, angle_deg, length, seed):
    """A jagged fault line stepping out along an angle, kinking sideways."""
    rng = random.Random(seed)
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    steps = max(3, int(length / 4))
    pts = [(cx, cy)]
    side = 1 if rng.random() < 0.5 else -1
    for k in range(1, steps + 1):
        r = length * k / steps
        off = side * rng.choice((1, 2, 2, 3)) * (0.4 if k == 1 else 1.0)
        side = -side if rng.random() < 0.7 else side
        pts.append((cx + ux * r + px * off, cy + uy * r + py * off))
    return pts


def _cut(pts, frac):
    if frac >= 1:
        return pts
    n = max(2, int(round(1 + (len(pts) - 1) * frac)))
    return pts[:n]


def _outline_pts(spec, frac, scale=1.0):
    size = spec["size"]
    cx = cy = size // 2
    rx, ry = spec["crater"]
    outline = BLOCK if spec["tier"] == 3 else CALDERA
    if spec["tier"] == 4:  # elongated behind the landslide direction
        rx *= 1.35
        ry *= 0.85
    return [(cx + dx * rx * frac * scale, cy + dy * ry * frac * scale) for dx, dy in outline]


def _scorch(c, spec, i):
    """A faint dark footprint under the whole effect (never part of the hitbox)."""
    if i < 1 or i > 8:
        return
    cx = cy = spec["size"] // 2
    r = spec["r"]
    a = 42 if i <= 5 else max(0, 42 - (i - 5) * 12)
    if a <= 0:
        return
    # follow the broken crater outline, widened — a regular ellipse reads as a UI drop shadow
    pts = _outline_pts(spec, 1.0, 1.28)
    c.polygon([(int(round(x + 1)), int(round(y + 2))) for x, y in pts], _rgba(SHADOW, a))


def _crater(c, spec, i):
    frac = CRATER_SCALE[i]
    cx = cy = spec["size"] // 2
    pts = _outline_pts(spec, frac)
    ints = [(int(round(x)), int(round(y))) for x, y in pts]

    # dark lip, then the exposed soil floor inset by ~18% so the rim stays black
    c.polygon(ints, CRACK)
    floor = _outline_pts(spec, frac, 0.82)
    c.polygon([(int(round(x)), int(round(y))) for x, y in floor], SOIL)
    # lit upper lip: a continuous highlight above the rim, not sprinkled pixels
    for k in range(0, len(pts), 1):
        x, y = pts[k]
        if y < cy - 0.1:
            c.pixel(round(x), round(y) - 1, ROCK_L)
    # strata in the floor and shadow along the lower inner wall
    if frac >= 0.8:
        for k in range(0, len(floor), 3):
            x, y = floor[k]
            if y < cy:
                c.pixel(round(x), round(y), STRATA)
        for k in range(1, len(floor), 2):
            x, y = floor[k]
            if y > cy + 0.1:
                c.pixel(round(x), round(y), SHADOW)

    if spec["tier"] == 3 and frac >= 0.8:
        # the block of ground itself is punched up inside the rim: slab face, lit top, dark walls
        slab = [(x, y - 3) for x, y in _outline_pts(spec, frac, 0.7)]
        c.polygon([(int(round(x)), int(round(y) + 3)) for x, y in slab], SHADOW)
        c.polygon([(int(round(x)), int(round(y))) for x, y in slab], ROCK)
        for k in range(len(slab)):
            x, y = slab[k]
            nxt = slab[(k + 1) % len(slab)]
            if y < cy - 3:
                c.line(round(x), round(y), round(nxt[0]), round(nxt[1]), ROCK_L)
                c.line(round(x), round(y) + 1, round(nxt[0]), round(nxt[1]) + 1, ROCK)
        for k in range(0, len(slab), 3):
            x, y = slab[k]
            if y > cy + 2:
                c.pixel(round(x), round(y), STRATA)

    if spec.get("magma") and 1 <= i <= 7:
        pool = min(3, spec["magma"])
        r = max(1, int(2 + pool))
        col = MAGMA if i <= 6 else MAGMA_D
        c.ellipse(cx - r, cy - max(1, r // 2), cx + r, cy + max(1, r // 2), col)
        if pool >= 3 and i <= 6:
            c.pixel(cx, cy, GLOW)


def _rim_dust(c, spec, i):
    """Ground dust kicked up against the crater lip — makes the pit sit in the ground."""
    if not 1 <= i <= 7 or spec["tier"] < 2:
        return
    size = spec["size"]
    cx = cy = size // 2
    pts = _outline_pts(spec, CRATER_SCALE[i])
    fade = 255 if i <= 5 else max(150, 255 - (i - 5) * 50)
    for k, (x, y) in enumerate(pts):
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        # clumps: some lip segments carry a thick collar, some none at all
        if (k * 7 + i) % 5 in (0, 1):
            continue
        c.pixel(round(x + ux * 1.3), round(y + uy * 0.7), _rgba(SAND, fade))
        if (k + i) % 2:
            c.pixel(round(x + ux * 2.4), round(y + uy * 1.3), _rgba(DUST_D, fade))


def _rim_rubble(c, spec, i):
    if i < 6:
        return
    cx = cy = spec["size"] // 2
    pts = _outline_pts(spec, CRATER_SCALE[i])
    for k in range(0, len(pts), 3):
        x, y = pts[k]
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy) or 1.0
        bx = int(round(x + dx / d * 1.5))
        by = int(round(y + dy / d * 0.9))
        c.rect(bx, by, bx + 2, by + 1, ROCK_D)
        c.pixel(bx, by, ROCK)
        c.pixel(bx + 1, by, ROCK_L)


def _cracks(c, spec, i):
    frac = REACH[i]
    if frac <= 0:
        return
    for n, (_angle, _length, width) in enumerate(spec["cracks"]):
        pts = _cut(spec["_arms"][n], frac)
        hot = spec.get("magma", 0) >= 2 and 2 <= i <= 6
        w = width if n == 0 else 1
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            c.line(int(round(x1 + 1)), int(round(y1 + 1)), int(round(x2 + 1)), int(round(y2 + 1)),
                   ROCK_L if i < 7 else STRATA, 1)
            c.line(int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)), CRACK, w)
            if hot and n < (1 if spec["magma"] == 2 else 3):
                c.line(int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2)), MAGMA, 1)


def _ring(c, spec, i):
    r = RING_R[i] * spec["r"]
    alpha = RING_A[i]
    if r <= 0 or alpha <= 0:
        return
    cx = cy = spec["size"] // 2
    ry = r * (0.72 if spec["tier"] < 4 else 0.62)
    gaps = spec["gaps"]
    width = 2
    tier = spec["tier"]
    settled = alpha < 150
    top_col = ASH if settled else ROCK_L
    body_col = ASH if settled else DUST
    foot_col = STRATA if settled else SAND
    for deg in range(0, 360, 2):
        d = deg % 360
        if any(a <= d <= b for a, b in gaps):
            continue
        if tier == 4:  # landslide: only the leading crescent is a shock front
            wave = spec["wave"]
            diff = abs((d - wave + 180) % 360 - 180)
            if diff > 85:
                continue
            if diff > 55 and (i + deg // 6) % 3 == 0:
                continue
        # taper toward the torn ends instead of cutting the band off square
        edge = min((min((d - a) % 360, (b - d) % 360) for a, b in gaps), default=360)
        lump = 0.5 + 0.5 * math.sin(deg * 0.37 + spec["seed"] * 1.7)
        w_k = width if edge > 10 else (1 if edge > 3 else 0)
        if w_k == 0:
            continue
        if lump < 0.28:
            w_k = max(1, w_k - 1)
        rad = math.radians(deg)
        wob = 1.1 * math.sin(deg * 0.19 + spec["seed"])
        x = cx + math.cos(rad) * (r + wob)
        y = cy + math.sin(rad) * (ry + wob * 0.4)
        tone = body_col if lump > 0.4 else SAND
        # a rolling dust ridge: torn crest here and there, body, dark foot, contact shadow
        if edge > 6 and lump > 0.55:
            c.pixel(round(x), round(y) - 1, _rgba(top_col, alpha))
        for k in range(w_k):
            c.pixel(round(x), round(y + k), _rgba(tone, alpha))
        if lump > 0.3:
            c.pixel(round(x), round(y + w_k), _rgba(foot_col, alpha))
        c.pixel(round(x), round(y + w_k + 1), _rgba(SHADOW, 130 if settled else 95))
def _puffs(c, spec, i):
    cx = cy = spec["size"] // 2
    for _angle, dist, size, delay in spec["puffs"]:
        if i < delay or i > 8:
            continue
        p = min(1.0, (i - delay) / 6.0)
        fade = 185 if i <= 7 else max(0, 185 - (i - 7) * 70)
        if fade <= 0:
            continue
        a = math.radians(_angle)
        rr = (dist + 0.25 * p) * spec["r"]
        x = cx + math.cos(a) * rr
        y = cy + math.sin(a) * rr * 0.62
        grown = size + (1 if p > 0.5 and size < 2 else 0)
        art = _puff(grown)
        _paste_fade(c, art, x - art.width / 2, y - art.height / 2, fade)


def _streaks(c, spec, i):
    """Short force lines at the impact frames: the blow, not a soft cloud."""
    if i > 3:
        return
    cx = cy = spec["size"] // 2
    rng = random.Random(spec["seed"] + i)
    n = 6 + spec["tier"]
    for k in range(n):
        a = rng.uniform(0, 2 * math.pi)
        r0 = spec["r"] * (0.25 + 0.1 * i)
        r1 = r0 + spec["r"] * (0.32 if i < 2 else 0.2)
        for t in range(int(r1 - r0)):
            f = (r0 + t) / r1
            col = GLOW if (i == 0 and k % 2 and f < 0.6) else (DUST if f < 0.55 else SAND)
            c.pixel(round(cx + math.cos(a) * (r0 + t)),
                    round(cy + math.sin(a) * (r0 + t) * 0.62), col)


def _chunks(c, spec, i):
    cx = cy = spec["size"] // 2
    for _angle, d0, d1, hmax, size, delay in spec["chips"]:
        if i < delay or i > 9:
            continue
        p = min(1.0, (i - delay) / 4.0)
        a = math.radians(_angle)
        dist = (max(d0, 0.4) + (d1 - max(d0, 0.4)) * p) * spec["r"]
        h = hmax * math.sin(math.pi * p) * (0.6 if p >= 1 else 1.0)
        x = cx + math.cos(a) * dist
        y = cy + math.sin(a) * dist * 0.62
        ground_y = y
        draw_y = y - h
        # cast shadow on the ground (faint, not part of the hitbox)
        c.ellipse(x - 2, ground_y + 1, x + 2, ground_y + 2, _rgba(SHADOW, 60))
        art = _chunk(size)
        if i >= 8:
            _paste_fade(c, art, x - art.width / 2, ground_y - art.height / 2, 190)
        else:
            _paste_fade(c, art, x - art.width / 2, draw_y - art.height / 2, 255)


def _pillars(c, spec, i):
    if spec["tier"] < 5 or i < 2:
        return
    cx = cy = spec["size"] // 2
    for _angle, dist, h, w in spec["pillars"]:
        rise = min(1.0, (i - 1) / 4.0)
        hh = max(2, int(h * rise))
        a = math.radians(_angle)
        x = int(round(cx + math.cos(a) * dist * spec["r"]))
        ground = int(round(cy + math.sin(a) * dist * spec["r"] * 0.62))
        top = ground - hh
        c.ellipse(x - w - 1, ground - 1, x + w + 1, ground + 2, _rgba(SHADOW, 110))
        c.rect(x - w, top, x + w, ground, SHADOW)
        c.rect(x - w + 1, top + 1, x + w - 1, ground, ROCK)
        c.rect(x - w + 1, top + 1, x - w + 2, ground, ROCK_L)
        c.rect(x + w - 2, top + 1, x + w - 1, ground, ROCK_D)
        # jagged cap
        cap = [(x - w - 1, top), (x - w + 2, top - 2), (x, top - 3), (x + w - 2, top - 2), (x + w + 1, top)]
        c.polygon([(int(px), int(py)) for px, py in cap], ROCK_D)
        c.line(x - w + 1, top - 1, x, top - 2, ROCK_L)
        c.line(x, top - 2, x + w - 1, top - 1, ROCK_L)
        if spec.get("magma") and i <= 6:
            c.pixel(x, ground - 1, GLOW)


def _flash(c, spec, i):
    if i > 2:
        return
    cx = cy = spec["size"] // 2
    r = (8 if spec["tier"] >= 4 else 6) - i * 2
    c.ellipse(cx - r, cy - r // 2, cx + r, cy + r // 2, GLOW)
    c.ellipse(cx - max(1, r // 2), cy - max(1, r // 3), cx + max(1, r // 2), cy + max(1, r // 3), "#fff9e6")
    for deg in range(0, 360, 45):
        a = math.radians(deg)
        for k in range(3, r + 4):
            c.pixel(round(cx + math.cos(a) * k), round(cy + math.sin(a) * k * 0.6),
                    GLOW if k < r + 2 else MAGMA_D)


def _embers(c, spec, i):
    if not spec.get("embers") or not 2 <= i <= 7:
        return
    rng = random.Random(spec["seed"] + i)
    cx = cy = spec["size"] // 2
    for _ in range(6 if spec["tier"] >= 5 else 3):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(0.25, 0.8) * spec["r"]
        c.pixel(int(cx + math.cos(a) * r), int(cy + math.sin(a) * r * 0.62 - (i - 2)),
                GLOW if rng.random() < 0.5 else MAGMA)


def frames(spec):
    """All 10 frames of one Ground Slam tier.

    spec: size, tier 1..5, seed, crater (rx, ry), cracks [(angle, len, width)],
    chips [(angle, d0, d1, hmax, size, delay)], puffs [(angle, dist, size, delay)],
    gaps/gaps2 (ring gaps), magma 0..3, wave (degrees, tier IV), pillars,
    embers. All distances are fractions of r.
    """
    size = spec["size"]
    cx = cy = size // 2
    spec["r"] = size / 2 - 4
    spec["_arms"] = [_arm(cx, cy, a, spec["r"] * l, spec["seed"] + n)
                     for n, (a, l, _w) in enumerate(spec["cracks"])]
    spec.setdefault("gaps", ((30, 50),))
    spec.setdefault("gaps2", ((120, 140), (260, 280)))
    out = []
    for i in range(10):
        c = Canvas(size, size)
        _scorch(c, spec, i)
        _crater(c, spec, i)
        _rim_dust(c, spec, i)
        _rim_rubble(c, spec, i)
        _cracks(c, spec, i)
        _flash(c, spec, i)
        _streaks(c, spec, i)
        _ring(c, spec, i)
        _chunks(c, spec, i)
        _pillars(c, spec, i)
        _puffs(c, spec, i)
        _embers(c, spec, i)
        out.append(c)
    return out
