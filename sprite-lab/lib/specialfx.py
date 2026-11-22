"""Effects of the special cards moved from items (bach-ai design/special-fx-redesign.md, user 2026-11-22).

The old ones were thin 1 px dotted rings, or dithered speck clouds. Shared rules here: double density (the
sprite json gets px_scale 0.5), solid bands with a lit and a shaded side and a dark rim, a bright flash where a
thing hits, fades by thinning and alpha (never dither), no veil over an area.
"""
import math

from spritekit import Canvas
from fxkit import FxFrames

INK = (34, 22, 14)


def _put(c, x, y, col, a=255):
    x, y = int(round(x)), int(round(y))
    w, h = c.img.size
    if 0 <= x < w and 0 <= y < h:
        old = c.img.getpixel((x, y))
        if old[3] < a:
            c.img.putpixel((x, y), (col[0], col[1], col[2], a))


def _ring(c, cx, cy, r, width, bands, a=255, squash=0.62):
    """A solid flat ring [r - width, r]: bands = colours from the outer edge inward (lit -> shaded)."""
    w, h = c.img.size
    for y in range(max(0, int(cy - r * squash - 2)), min(h, int(cy + r * squash + 3))):
        for x in range(max(0, int(cx - r - 2)), min(w, int(cx + r + 3))):
            d = math.hypot(x - cx, (y - cy) / squash)
            if r - width <= d <= r:
                k = min(len(bands) - 1, int((r - d) / max(1.0, width) * len(bands)))
                _put(c, x, y, bands[k], a)


def _shard(c, x, y, ang, size, lit, dark, a=255):
    """A small rock shard: a lit face and a shaded face, a dark rim."""
    dx, dy = math.cos(ang), math.sin(ang)
    for t in range(-size, size + 1):
        for s in range(-max(1, size // 2), max(1, size // 2) + 1):
            px, py = x + dx * t - dy * s, y + dy * t + dx * s
            col = lit if s < 0 else dark
            if abs(t) == size:   # dark tips only: small shards stay lit, not outlines
                col = INK
            _put(c, px, py, col, a)


def _flash(c, cx, cy, r, a=255):
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r * 1.6), int(cx + r * 1.6) + 1):
            e = ((x - cx) / (r * 1.6)) ** 2 + ((y - cy) / r) ** 2
            if e <= 1.0:
                _put(c, x, y, (255, 255, 240) if e < 0.4 else (255, 232, 150), a)


STONE_L = (214, 196, 160)
STONE_D = (120, 100, 78)
GOLD = (255, 212, 96)
GOLD_D = (196, 132, 40)
EARTH = (150, 112, 70)


def retaliate_shock(size=112, radius=52, frames=16):
    """Phản chấn: the hit that sets it off flashes at the feet, a thick stone-gold shock ring opens (frames 2-6
    hit), shards fly out, the ring slows to full reach, then thins and fades."""
    c0 = size / 2
    out, masks = [], []
    for f in range(frames):
        c = Canvas(size, size)
        m = Canvas(size, size)
        if f < 2:                                                       # the trigger: a flash at the feet
            _flash(c, c0, c0, 6 + f * 4)
        else:
            t = min(1.0, (f - 2) / 7.0)
            ease = 1 - (1 - t) ** 3                                     # fast out, slows to full reach
            r = 10 + (radius - 10) * ease
            fade = 255 if f < 10 else int(255 * (1 - (f - 10) / 6))
            width = max(2.0, 9 - 0.5 * max(0, f - 6))                  # thins as it slows
            _ring(c, c0, c0, r, width, [(255, 246, 210), GOLD, GOLD_D, EARTH], fade)
            _ring(c, c0, c0, r + 1.5, 1.5, [INK], fade)           # dark outer rim keeps it readable
            if f <= 4:                                                  # ground flash and rays while it bursts
                _flash(c, c0, c0, 10 - f * 2, 230)
                for i in range(10):
                    a = i * math.tau / 10 + f * 0.2
                    for s in range(int(r * 0.5), int(r * 0.85)):
                        _put(c, c0 + math.cos(a) * s, c0 + math.sin(a) * s * 0.62, (255, 236, 170), 200)
            for i in range(9):                                          # shards thrown outward
                a = i * math.tau / 9 + 0.3
                d = r * (0.75 + 0.15 * (i % 3)) + (f - 2) * 1.5
                if d < radius + 6:
                    _shard(c, c0 + math.cos(a) * d, c0 + math.sin(a) * d * 0.62 - (8 - abs(f - 7)) * 0.8,
                           a + f * 0.5, 3 + i % 2, STONE_L, STONE_D, fade)
            if 2 <= f <= 6:                                             # hit area: the disc the ring swept
                m.ellipse(int(c0 - r), int(c0 - r * 0.62), int(c0 + r), int(c0 + r * 0.62), "#ffffff", fill=True)
        out.append(c)
        masks.append(m)
    return FxFrames(out, masks)


STEEL_L = (240, 246, 255)
STEEL = (178, 192, 214)
STEEL_D = (96, 108, 136)
GRIP = (110, 70, 40)
TRAIL = (255, 224, 120)


def _sword(c, cx, cy, ang, r0, r1, a=255):
    """A sword lying along the radius at angle [param ang]: grip near r0, point at r1, guard, 2 px blade with a
    lit edge and a shaded edge, gold guard, dark point."""
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    length = r1 - r0
    for k in range(int(length) + 1):
        t = r0 + k
        x, y = cx + dx * t, cy + dy * t
        if k < length * 0.22:                                              # grip
            _put(c, x, y, GRIP, a)
        elif k < length * 0.3:                                             # guard: a cross bar
            for s in range(-4, 5):
                _put(c, x + nx * s, y + ny * s, GOLD if abs(s) < 4 else GOLD_D, a)
        else:                                                              # blade, tapering to the point
            half = 2 if k < length * 0.85 else 1
            for s in range(-half, half + 1):
                col = STEEL_L if s < 0 else (STEEL if s == 0 else STEEL_D)
                _put(c, x + nx * s, y + ny * s, col, a)
    _put(c, cx + dx * r1, cy + dy * r1, INK, a)


def holy_blades(size=144, radius=60, frames=14, n=6):
    """Thánh kiếm: n bright swords point outward and sweep one turn round the hero, each leaving a gold arc
    trail; frames 3..9 hit (the ring they sweep); they flare and dissolve into rays at the end."""
    c0 = size / 2
    sq = 0.62                                                              # flat on the ground like the rings
    out, masks = [], []
    for f in range(frames):
        c = Canvas(size, size)
        m = Canvas(size, size)
        grow = min(1.0, (f + 1) / 3)                                       # 0-2: swords slide out from the hero
        turn = f / (frames - 4) * math.tau if f < frames - 3 else math.tau
        fade = 255 if f < frames - 3 else int(255 * (frames - f) / 4)
        for i in range(n):
            a0 = i * math.tau / n + turn
            if 1 <= f < frames - 3:                                        # gold trail behind each sword
                for s in range(48):                                         # a solid 3 px arc, fading back
                    ta = a0 - s * 0.012
                    rr = radius * grow * 0.92
                    al = int(240 * (1 - s / 48))
                    for w, col in ((0, (255, 246, 200)), (1, TRAIL), (2, GOLD)):
                        _put(c, c0 + math.cos(ta) * (rr - w), c0 + math.sin(ta) * (rr - w) * sq, col, al)
            if f < frames - 3:
                lay = Canvas(size, size)
                _sword(lay, c0, c0, a0, radius * grow * 0.35, radius * grow, fade)
                # squash the sword layer onto the ground plane
                img = lay.img
                for y in range(size):
                    for x in range(size):
                        p = img.getpixel((x, y))
                        if p[3]:
                            _put(c, x, c0 + (y - c0) * sq, p[:3], p[3])
            else:                                                          # outro: each sword flares into rays
                k = f - (frames - 3)
                x, y = c0 + math.cos(a0) * radius, c0 + math.sin(a0) * radius * sq
                for s in range(5 + k * 3):                                 # a gold 4-point flare
                    col = (255, 250, 220) if s < 3 else GOLD
                    for d in (-1, 1):
                        _put(c, x + d * s, y, col, fade)
                        _put(c, x, y + d * s * 0.6, col, fade)
                        if s < 3:
                            _put(c, x + d * s, y + 1, col, fade)
        if 3 <= f <= 9:
            m.ellipse(int(c0 - radius), int(c0 - radius * sq), int(c0 + radius), int(c0 + radius * sq), "#ffffff", fill=True)
        out.append(c)
        masks.append(m)
    return FxFrames(out, masks)


BOLT_W = (250, 252, 255)
BOLT_B = (150, 210, 255)
BOLT_D = (60, 110, 200)


def shock_rune(size=96, frames=10):
    """Lôi ấn at the hero: a lightning rune (a zigzag glyph in a diamond) rises over the head, flashes white, and
    throws sparks; anchor = the hero's body centre (the frame's centre)."""
    import random
    rng = random.Random(5)
    c0 = size / 2
    out = []
    for f in range(frames):
        c = Canvas(size, size)
        lift = -18 - min(f, 3) * 3
        a = 255 if f < frames - 3 else int(255 * (frames - f) / 4)
        cy = c0 + lift
        r = 9 + (2 if f == 3 else 0)
        for k in range(-r, r + 1):                                       # diamond frame, 2 px
            w = r - abs(k)
            for s in (-w, w):
                _put(c, c0 + s, cy + k, BOLT_B, a)
                _put(c, c0 + s + (1 if s < 0 else -1), cy + k, BOLT_D, a)
        for (x0, y0, x1, y1) in ((2, -6, -2, 0), (-2, 0, 2, 0), (2, 0, -2, 6)):   # the zigzag glyph
            for t in range(9):
                x = x0 + (x1 - x0) * t / 8
                y = y0 + (y1 - y0) * t / 8
                _put(c, c0 + x, cy + y, BOLT_W if f in (3, 4) else (255, 240, 150), a)
                _put(c, c0 + x + 1, cy + y, BOLT_B, a)
        if f in (3, 4, 5):                                               # the flash and sparks as it fires
            for i in range(8):
                ang = i * math.tau / 8 + f
                for s in range(r + 2, r + 6 + (f - 3) * 3):
                    _put(c, c0 + math.cos(ang) * s, cy + math.sin(ang) * s, BOLT_W if s < r + 5 else BOLT_B, a)
        for i in range(3):                                               # small sparks drifting up
            x = c0 + rng.uniform(-14, 14)
            y = cy + 10 - f * 2 - rng.uniform(0, 6)
            _put(c, x, y, BOLT_B, a // 2)
        out.append(c)
    return out


def shock_strike(w=48, h=112, frames=9):
    """Lôi ấn on a struck monster: a jagged bolt falls from above to its feet (anchor at the bottom centre),
    flashes, and its foot throws sparks; then the bolt thins and fades."""
    import random
    import boltfx
    out = []
    for f in range(frames):
        c = Canvas(w, h)
        rng = random.Random(11 + f // 2)
        x, foot = w / 2, h - 6
        if f == 0:                                                       # a thin warning spark at the top
            for y in range(4, 22):
                _put(c, x + (y % 3) - 1, y, BOLT_B, 200)
        elif f < frames - 2:
            boltfx.thin_bolt(c, x + rng.uniform(-4, 4), 2, x, foot, rng, 3, core="#fbfdff", glow="#8fd0ff")
            if f <= 3:                                                   # flash at the foot
                for yy in range(int(foot - 5), int(foot + 4)):
                    for xx in range(int(x - 10), int(x + 11)):
                        e = ((xx - x) / 10) ** 2 + ((yy - foot) / 4) ** 2
                        if e <= 1:
                            _put(c, xx, yy, BOLT_W if e < 0.4 else BOLT_B)
            for i in range(6):                                           # sparks at the foot
                ang = -math.pi * (0.1 + 0.8 * i / 5)
                s = 4 + f * 2
                _put(c, x + math.cos(ang) * s, foot + math.sin(ang) * s * 0.6, BOLT_W)
                _put(c, x + math.cos(ang) * (s + 1), foot + math.sin(ang) * (s + 1) * 0.6, BOLT_B)
        else:                                                            # outro: a fading line
            a = int(255 * (frames - f) / 3)
            for y in range(int(foot * 0.4), int(foot)):
                _put(c, x, y, BOLT_B, a)
        out.append(c)
    return out
