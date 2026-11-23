"""Sóng kiếm (sword-wave) drawn per direction (bach-ai design/cleave-wave-redesign.md, user 2026-11-21).

The old wave rotated one crescent image 16 ways (dirs16), so diagonals broke up, and its 6 flight frames were
the same picture. Here every direction is drawn from geometry at double pixel density ("px_scale" 0.5):
a crescent air blade (white leading edge, sea-green body, deep back edge), 3 trailing bands that waver frame to
frame, wind specks peeling off the tips. Its own colour, so it never reads as Chém kiếm's steel slash.
Tiers (each a different silhouette, user 2026-11-23: II-IV looked the same): II an afterimage blade behind,
III a wide blue back band and longer hooked tips, IV two afterimages + serrated back edge + longer trail, V gold core
and two small side blades.
No veil over an area (pixel-sprite rule).
"""
import math

from spritekit import Canvas

S = 144                         # frame (double density: 72 px on screen at px_scale 0.5)
C = S / 2
EDGE = (250, 255, 252)
CORE = (190, 255, 236)
BODY = (88, 220, 196)
DEEP = (34, 140, 136)
SHADE = (18, 78, 84)
RIM3 = (120, 190, 255)
GOLD = (255, 214, 92)


def _put(c, x, y, col, a=255):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < S and 0 <= y < S:
        old = c.img.getpixel((x, y))
        if old[3] < a:
            c.img.putpixel((x, y), (col[0], col[1], col[2], a))


GHOST = {EDGE: (150, 235, 220), CORE: (110, 210, 192), BODY: (60, 170, 156), DEEP: (30, 110, 110),
         SHADE: (18, 70, 76), RIM3: (80, 140, 220), GOLD: (200, 170, 80)}


def _crescent(c, deg, tier, scale=1.0, shift=(0.0, 0.0), k=0, ghost=0):
    """The blade: outer arc radius R round a centre behind the anchor, inner arc offset further back, so the
    blade is thick in the middle and sharp at the tips. Colour by depth from the leading edge."""
    d = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
    R = 52.0 * scale
    back = 18.0 * scale
    thick = (13.0 + tier * 0.8) * scale
    ox, oy = C + shift[0] - d[0] * back, C + shift[1] - d[1] * back            # outer arc centre
    ix, iy = ox - d[0] * thick, oy - d[1] * thick                              # inner arc centre
    half = math.radians(66 + tier * 2 + (8 if tier >= 3 else 0))   # III+: longer, hooked tips
    lo = int(min(ox, ix) - R - 2)
    hi = int(max(ox, ix) + R + 2)
    loy = int(min(oy, iy) - R - 2)
    hiy = int(max(oy, iy) + R + 2)
    for y in range(max(0, loy), min(S, hiy)):
        for x in range(max(0, lo), min(S, hi)):
            dx, dy = x - ox, y - oy
            ro = math.hypot(dx, dy)
            if ro > R or ro < 1:
                continue
            ang = math.atan2(dy, dx) - math.radians(deg)
            ang = (ang + math.pi) % (2 * math.pi) - math.pi
            if abs(ang) > half:
                continue
            if math.hypot(x - ix, y - iy) < R:
                continue                                                      # inside the inner arc: cut out
            depth = R - ro                                                    # 0 at the leading edge
            span = 1.0 - abs(ang) / half                                      # 1 mid-blade, 0 at the tips
            if depth < 1.6:
                col = EDGE
            elif depth < 3.5 + span * (2 + (2 if tier >= 2 else 0)):   # II+: a thicker bright core
                col = CORE if (tier >= 2 or span > 0.3) else BODY
            elif depth < 7 + span * 4:
                col = BODY
            elif depth < 10 + span * 5:
                col = DEEP
            else:
                col = SHADE
            if tier >= 5 and 2.5 <= depth < 4.0 and span > 0.25:
                col = GOLD
            if tier >= 3 and col in (BODY, SHADE, DEEP) and depth >= 6.5 + span * 3:   # III+: a wide blue back band
                col = RIM3
            if tier >= 4 and depth >= 10.5 + span * 4 and int((ang * 40) % 5) < 2:   # IV+: notched back edge
                continue
            if ghost:
                _put(c, x, y, GHOST.get(col, col), 200 - ghost * 50)
            else:
                _put(c, x, y, col)


def _trail(c, deg, tier, k):
    """Three thin bands behind the blade, fading and wavering frame to frame (the wave's speed)."""
    d = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
    n = (-d[1], d[0])
    bands = 3 + (1 if tier >= 4 else 0)
    for b in range(bands):
        length = 26 + b * 5 + (10 if tier >= 4 else 0)
        off = (b - (bands - 1) / 2) * 13
        wob = math.sin(k * 1.3 + b * 2.1) * 4
        start = -14 + abs(off) * 0.35 + (k + b) % 3 * 2   # from the blade's back edge, flickering
        for t in range(int(length)):
            if (t + k + b) % 3 == 2:
                continue                                                      # broken streak, not a solid bar
            a = int(255 * (1 - t / length) ** 0.7)
            x = C - d[0] * (start + t) + n[0] * (off + wob * t / length)
            y = C - d[1] * (start + t) + n[1] * (off + wob * t / length)
            col = CORE if t < length * 0.25 else (BODY if t < length * 0.6 else DEEP)
            _put(c, x, y, col, a)
            _put(c, x + n[0], y + n[1], col, a // 2)


def _specks(c, deg, tier, k):
    """Wind specks peeling off both tips and drifting back."""
    d = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
    n = (-d[1], d[0])
    count = 3 + tier
    for i in range(count):
        side = 1 if i % 2 == 0 else -1
        t = ((k * 0.17 + i * 0.29) % 1.0)
        along = 4 - t * 40
        out = side * (40 + t * 8 + (i % 3) * 3)
        x = C + d[0] * along + n[0] * out
        y = C + d[1] * along + n[1] * out
        col = EDGE if t < 0.35 else CORE
        a = int(255 * (1 - t * 0.6))
        for ddx, ddy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            _put(c, x + ddx, y + ddy, col, a)
        if tier >= 4 and t < 0.5:
            _put(c, x + 2, y, col, int(200 * (1 - t)))


def fly_frame(deg, tier, k):
    c = Canvas(S, S)
    _trail(c, deg, tier, k)
    d0 = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
    echoes = 0 if tier <= 1 else (1 if tier <= 3 else 2)        # II-III: one afterimage, IV-V: two
    for e in range(echoes, 0, -1):
        _crescent(c, deg, min(tier, 2), scale=1.0 - 0.1 * e, shift=(-d0[0] * 13 * e, -d0[1] * 13 * e), k=k, ghost=e)
    _crescent(c, deg, tier, k=k)
    if tier >= 5:                                                             # two small side blades
        d = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
        n = (-d[1], d[0])
        for side in (1, -1):
            _crescent(c, deg, 3, scale=0.40, shift=(n[0] * side * 34 - d[0] * 30, n[1] * side * 34 - d[1] * 30), k=k)
    _specks(c, deg, tier, k)
    if k % 3 == 0:                                                            # a glint runs along the edge
        d = (math.cos(math.radians(deg)), math.sin(math.radians(deg)))
        n = (-d[1], d[0])
        g = ((k // 3) * 2 - 1) * 20
        for r in range(-2, 3):
            _put(c, C + d[0] * 32 + n[0] * (g + r), C + d[1] * 32 + n[1] * (g + r), EDGE)
    return c


def impact_frame(tier, k):
    """The blade bursts into shards and specks (5 frames), drawn facing right; the game plays it in place."""
    c = Canvas(S, S)
    for i in range(10 + tier * 2):
        a = -1.3 + i * 2.6 / (9 + tier * 2)
        r = 26 + k * 9 + (i % 3) * 4
        x, y = C + math.cos(a) * r, C + math.sin(a) * r
        col = EDGE if k < 2 else (CORE if k < 3 else BODY)
        alpha = int(255 * (1 - k / 5))
        for j in range(5 - k):
            for w in (0, 1):
                _put(c, x - math.cos(a) * j * 2 + w, y - math.sin(a) * j * 2, col, alpha)
    if k < 3:   # the blade's flash, splitting outward
        for ang in range(-60, 61, 2):
            r = 30 + k * 6
            for w in range(3 - k):
                _put(c, C + math.cos(math.radians(ang)) * (r + w), C + math.sin(math.radians(ang)) * (r + w),
                     EDGE if w == 0 else CORE, 255 - k * 70)
    return c


ANGLES = [round(k * 22.5) for k in range(16)]


def animations(tier):
    """[(name, frames, fps, loop, extra)]: fly_000 .. fly_338, 6 frames each."""
    out = []
    for deg in ANGLES:
        frames = [fly_frame(deg, tier, k) for k in range(6)]
        out.append(("fly_%03d" % deg, frames, 14, True, {"hitbox": {"shape": "rect", "center": [C, C], "active": [0, 5]}}))
    # no "impact": a wave pierces, the game plays impacts only for shots (and fx_craft would ask a full
    # area effect of it); impact_frame stays for a future hit spark
    return out
