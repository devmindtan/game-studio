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


def _ring(c, cx, cy, r, width, bands, a=255, squash=1.0):   # 2D (user 2026-11-22): round, not a 2.5D ellipse
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
        if f < 2:   # the trigger: a small see-through flash at the feet (scaled with the ring, a big one hid the hero)
            _flash(c, c0, c0 + 4, 3 + f * 2, 170)
        else:
            t = min(1.0, (f - 2) / 7.0)
            ease = 1 - (1 - t) ** 3                                     # fast out, slows to full reach
            r = 10 + (radius - 10) * ease
            fade = 255 if f < 10 else int(255 * (1 - (f - 10) / 6))
            width = max(2.0, 9 - 0.5 * max(0, f - 6))                  # thins as it slows
            _ring(c, c0, c0, r, width, [(255, 246, 210), GOLD, GOLD_D, EARTH], fade)
            _ring(c, c0, c0, r + 1.5, 1.5, [INK], fade)           # dark outer rim keeps it readable
            if f <= 4:                                                  # ground rays while it bursts (no centre flash)
                for i in range(10):
                    a = i * math.tau / 10 + f * 0.2
                    for s in range(int(r * 0.5), int(r * 0.85)):
                        _put(c, c0 + math.cos(a) * s, c0 + math.sin(a) * s, (255, 236, 170), 200)
            for i in range(9):                                          # shards thrown outward
                a = i * math.tau / 9 + 0.3
                d = r * (0.75 + 0.15 * (i % 3)) + (f - 2) * 1.5
                if d < radius + 6:
                    _shard(c, c0 + math.cos(a) * d, c0 + math.sin(a) * d,
                           a + f * 0.5, 3 + i % 2, STONE_L, STONE_D, fade)
            if 2 <= f <= 6:                                             # hit area: the disc the ring swept
                m.ellipse(int(c0 - r), int(c0 - r), int(c0 + r), int(c0 + r), "#ffffff", fill=True)
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
    sq = 1.0                                                               # 2D: a round sweep (user 2026-11-22)
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


FIRE_D = (150, 30, 20)
FIRE_R = (226, 70, 30)
FIRE_O = (255, 150, 40)
FIRE_Y = (255, 222, 90)
FIRE_W = (255, 250, 214)


def _flame(c, x, y, h, w, a=255):
    """One solid low flame standing on (x, y): dark red base, orange body, yellow tip, white core; a teardrop
    that narrows to its tip (no dots)."""
    for k in range(int(h) + 1):
        t = k / max(1.0, h)                                   # 0 at the base, 1 at the tip
        half = w * (1 - t) ** 0.8 * (0.7 + 0.3 * math.sin(math.pi * min(1.0, t * 1.6)))
        for s in range(-int(half), int(half) + 1):
            d = abs(s) / max(1.0, half)
            if t < 0.15 and d > 0.5:
                col = FIRE_D
            elif d > 0.75:
                col = FIRE_R
            elif t > 0.7 or d > 0.45:
                col = FIRE_O if t < 0.85 else FIRE_Y
            else:
                col = FIRE_Y if t > 0.35 else FIRE_W
            _put(c, x + s, y - k, col, a)


def flame_ring(size=128, radius=52, frames=10, n=22):
    """Hoả y: a low ring of solid flames round the hero, flickering out of step, embers rising; frames ~ the
    card's 0.76 s cadence so back-to-back pulses read as one steady fire. Hit mask = the ring's disc."""
    import random
    c0 = size / 2
    sq = 1.0   # 2D (user 2026-11-22)
    out, masks = [], []
    for f in range(frames):
        rng = random.Random(f)
        c = Canvas(size, size)
        m = Canvas(size, size)
        a = 255 if 1 <= f <= frames - 2 else 200
        for k in range(int(radius * 7)):                      # a thin band of glowing coals joining the flames
            ang = k / (radius * 7) * math.tau
            x, y = c0 + math.cos(ang) * radius, c0 + math.sin(ang) * radius * sq
            hot = (k + f * 3) % 9 < 3
            _put(c, x, y, FIRE_O if hot else FIRE_R, a)
            _put(c, x, y + 1, FIRE_D, a)
        pts = sorted(((i * math.tau / n, i) for i in range(n)), key=lambda p: math.sin(p[0]))   # back flames first
        for ang, i in pts:
            x = c0 + math.cos(ang) * radius
            y = c0 + math.sin(ang) * radius * sq
            flick = 0.6 + 0.4 * abs(math.sin(f * 1.7 + i * 2.3))
            _flame(c, x, y, (16 + (i % 3) * 4) * flick, 5 + (i % 2), a)
        for e in range(6):                                    # embers drifting up
            ang = rng.uniform(0, math.tau)
            x = c0 + math.cos(ang) * radius * rng.uniform(0.8, 1.05)
            y = c0 + math.sin(ang) * radius * sq - 6 - rng.uniform(0, 10)
            _put(c, x, y, FIRE_Y, 220)
            _put(c, x, y + 1, FIRE_O, 160)
        m.ellipse(int(c0 - radius), int(c0 - radius * sq), int(c0 + radius), int(c0 + radius * sq), "#ffffff", fill=True)
        out.append(c)
        masks.append(m)
    return FxFrames(out, masks)


ICE_W = "#f4feff"
ICE_L = "#c8f6ff"
ICE_M = "#6fe0ff"
ICE_D = "#2a8fd6"
ICE_X = "#1c4f8a"


def ice_nova(size=144, radius=60, frames=13, n=18):
    """Băng ấn: frost swirls in at the feet (0-2), a ring of solid faceted ice spikes bursts up at the reach
    (3-7, the freeze), they stand, then shatter into shards flying out (8-12). Hit mask = the disc they ring."""
    import fxkit as fk
    c0 = size / 2
    sq = 1.0   # 2D (user 2026-11-22)
    out, masks = [], []
    for f in range(frames):
        c = Canvas(size, size)
        m = Canvas(size, size)
        if f < 3:                                                     # frost gathering at the feet
            for i in range(10):
                a = i * math.tau / 10 + f * 0.6
                rr = radius * (0.5 - f * 0.13)
                for s in range(6):
                    t = a + s * 0.06
                    _put(c, c0 + math.cos(t) * rr, c0 + math.sin(t) * rr * sq, (200, 246, 255), 200 - s * 25)
        elif f < 8:
            grow = min(1.0, (f - 2) / 2.0)
            for k in range(int(radius * 7)):                          # a frosted band joining the spikes
                a = k / (radius * 7) * math.tau
                x, y = c0 + math.cos(a) * radius, c0 + math.sin(a) * radius * sq
                for w, col in ((0, (244, 254, 255)), (1, (160, 226, 250)), (2, (90, 170, 220))):
                    _put(c, x, y + w, col, int(255 * grow))
            lay = Canvas(size, size)
            pts = sorted(((i * math.tau / n, i) for i in range(n)), key=lambda p: math.sin(p[0]))
            for ang, i in pts:                                        # back spikes first
                x = c0 + math.cos(ang) * radius
                y = c0 + math.sin(ang) * radius * sq
                h = (14 + (i % 3) * 5) * grow   # round ring: shorter spikes stay inside the frame
                lean = math.cos(ang) * 0.35
                fk.crystal(lay, x, y, -math.pi / 2 + lean, h, 5.5, ICE_L, ICE_M, ICE_D, ICE_W)
            fk.stack(c, lay, ICE_X)
            if f == 3:                                                # the freeze flash along the ring
                for k in range(int(radius * 6)):
                    a = k / (radius * 6) * math.tau
                    _put(c, c0 + math.cos(a) * radius, c0 + math.sin(a) * radius * sq, (244, 254, 255))
            m.ellipse(int(c0 - radius), int(c0 - radius * sq), int(c0 + radius), int(c0 + radius * sq), "#ffffff", fill=True)
        else:                                                         # shatter: shards fly outward and fade
            k = f - 8
            a_out = int(255 * (1 - k / 5))
            lay = Canvas(size, size)
            for i in range(n * 2):
                ang = i * math.tau / (n * 2) + 0.2
                d = radius + 4 + k * 6 + (i % 3) * 3
                x = c0 + math.cos(ang) * d
                y = c0 + math.sin(ang) * d * sq - (6 - k) * 1.5
                fk.crystal(lay, x, y, ang + k * 0.7, 5 - k * 0.6, 1.6, ICE_L, ICE_M, ICE_D, ICE_W)
            fk.stack(c, lay, ICE_X)
            px = c.img.load()
            for yy in range(size):
                for xx in range(size):
                    p = px[xx, yy]
                    if p[3]:
                        px[xx, yy] = (p[0], p[1], p[2], min(p[3], a_out))
        out.append(c)
        masks.append(m)
    return FxFrames(out, masks)


BLOOD_D = (110, 10, 24)
BLOOD = (196, 28, 44)
BLOOD_L = (246, 92, 98)
BLOOD_W = (255, 214, 214)

FIST = [   # a clenched fist seen from the front: four fingers (dark gaps), the thumb across, the wrist below
    ".kkkkkkkkkk.",
    "kwlkwlkwlkwk",
    "kllkllkllklk",
    "krrkrrkrrkrk",
    "kkkkkkkkkkrk",
    "klllllllllrk",
    "krrrrrrrrrrk",
    ".krrrrrrrrk.",
    "..krrrrrrk..",
    "..krrrrrrk..",
    "..kkkkkkkk..",
]


def _blood_drop(c, x, y, r, a=255):
    """A solid blood drop: round body, a point on top, a lit highlight."""
    for yy in range(int(-r * 2), int(r) + 1):
        for xx in range(int(-r), int(r) + 1):
            if yy >= 0:
                inside = xx * xx + yy * yy <= r * r
            else:
                inside = abs(xx) <= r * (1 + yy / (2 * r)) + 0.3
            if inside:
                col = BLOOD_D if (xx > r * 0.4 or yy > r * 0.6) else BLOOD
                if xx < -r * 0.2 and -r * 0.6 < yy < r * 0.2:
                    col = BLOOD_L
                _put(c, x + xx, y + yy, col, a)


def blood_fist(size=112, frames=13):
    """Huyết quyền: blood drops fly in from all round (0-4), gather into a glowing crimson fist at the hero (5-8)
    with a ring of light, then red heal crosses rise as it fades (9-12). Drawn at the hero (no area)."""
    c0 = size / 2
    out = []
    for f in range(frames):
        c = Canvas(size, size)
        if f < 5:
            t = f / 4
            for i in range(8):
                a = i * math.tau / 8 + 0.3
                d = 30 * (1 - t) + 4
                _blood_drop(c, c0 + math.cos(a) * d, c0 - 36 + math.sin(a) * d, 3)   # gather above the head
        else:
            k = f - 5
            fade = 255 if f < frames - 3 else int(255 * (frames - f) / 4)
            sc = 3
            fy = int(c0 - 36 - len(FIST) * sc / 2 - min(k, 3) * 2)   # above the head (user 2026-11-22); whole pixels
            fx = int(c0 - len(FIST[0]) * sc / 2)
            keys = {"k": (60, 6, 14), "r": BLOOD, "l": BLOOD_L, "w": BLOOD_W}
            for ry, row in enumerate(FIST):
                for rx, ch in enumerate(row):
                    if ch != ".":
                        for dy in range(sc):
                            for dx in range(sc):
                                _put(c, fx + rx * sc + dx, fy + ry * sc + dy, keys[ch], fade)
            # the ring after the fist: _put keeps the first colour, so it sits behind the fist
            if k <= 3:                                               # ring of light bursting out
                rr = 12 + k * 5
                for s in range(int(rr * 7)):
                    a = s / (rr * 7) * math.tau
                    for w, col in ((0, BLOOD_W), (1, BLOOD_L), (2, BLOOD)):
                        _put(c, c0 + math.cos(a) * (rr - w), c0 - 36 + math.sin(a) * (rr - w), col, 255 - k * 50)
            if f >= 8:                                               # heal crosses rising
                for i in range(3):
                    x = c0 - 18 + i * 18
                    y = c0 - 50 - (f - 8) * 4 - (i % 2) * 6
                    for d in range(-3, 4):
                        _put(c, x + d, y, BLOOD_L, fade)
                        _put(c, x, y + d, BLOOD_L, fade)
                    _put(c, x, y, BLOOD_W, fade)
        out.append(c)
    return out


WIND_W = (236, 255, 248)
WIND_L = (150, 236, 214)
WIND = (70, 190, 170)
WIND_D = (30, 120, 116)
LEAF = (150, 210, 90)
LEAF_D = (80, 140, 50)


def wind_ribbons(size=112, frames=12, n=3):
    """Phong hành: three solid wind ribbons (white edge, sea-green body, dark tail) curl round the hero's feet and
    stream off behind, leaves whirling with them; the speed rune's look. Drawn at the hero."""
    c0 = size / 2
    out = []
    for f in range(frames):
        c = Canvas(size, size)
        fade = 255 if f < frames - 3 else int(255 * (frames - f) / 4)
        for i in range(n):
            base = i * math.tau / n + f * 0.45
            rr = 30 + 6 * math.sin(f * 0.5 + i)
            for s in range(56):                                   # the ribbon: a thick arc fading to its tail
                t = base - s * 0.028
                x = c0 + math.cos(t) * rr
                y = c0 + math.sin(t) * rr   # 2D: round the body (user 2026-11-22)
                w = max(1, 5 - s // 12)
                a = int(fade * (1 - s / 56) ** 0.6)
                for k in range(w):
                    col = WIND_W if k == 0 else (WIND_L if k < 2 else (WIND if k < 4 else WIND_D))
                    _put(c, x, y + k, col, a)
        for i in range(4):                                        # leaves
            t = i * math.tau / 4 + f * 0.6
            x = c0 + math.cos(t) * 36
            y = c0 + math.sin(t) * 36
            for dx, dy, col in ((0, 0, LEAF), (1, 0, LEAF), (0, 1, LEAF_D), (1, 1, LEAF_D), (2, 0, LEAF)):
                _put(c, x + dx, y + dy, col, fade)
        out.append(c)
    return out


STAR_W = (255, 252, 230)
STAR_Y = (255, 224, 110)
STAR_O = (240, 160, 60)


def shooting_stars(size=112, frames=12, n=3):
    """Lưu tinh: three small shooting stars orbit the hero with solid gold trails, then flare (the speed rune's
    look on a kill streak). Drawn at the hero."""
    c0 = size / 2
    out = []
    for f in range(frames):
        c = Canvas(size, size)
        fade = 255 if f < frames - 3 else int(255 * (frames - f) / 4)
        for i in range(n):
            base = i * math.tau / n + f * 0.55
            rr = 34
            for s in range(30):                                   # trail
                t = base - s * 0.035
                x = c0 + math.cos(t) * rr
                y = c0 + math.sin(t) * rr
                a = int(fade * (1 - s / 30))
                col = STAR_W if s < 4 else (STAR_Y if s < 16 else STAR_O)
                for k in range(3 if s < 12 else (2 if s < 22 else 1)):
                    _put(c, x, y + k - 1, col if k == 1 else STAR_O, a)
            x = c0 + math.cos(base) * rr
            y = c0 + math.sin(base) * rr
            big = 6 if f >= frames - 4 else 4                     # the star: a solid diamond with 4 rays
            for dy in range(-3, 4):
                for dx in range(-3 + abs(dy), 4 - abs(dy)):
                    _put(c, x + dx, y + dy, STAR_W if abs(dx) + abs(dy) < 2 else STAR_Y, fade)
            for d in range(4, big + 2):
                for q in ((d, 0), (-d, 0), (0, d), (0, -d)):
                    _put(c, x + q[0], y + q[1], STAR_Y, fade)
        out.append(c)
    return out


HEART_D = (150, 30, 70)
HEART = (232, 72, 120)
HEART_L = (255, 160, 190)
HEART_W = (255, 236, 244)


def _heart(c, cx, cy, r, crack=0, a=255):
    """A solid heart (lit upper left, dark rim); crack > 0 opens a jagged split down the middle."""
    for y in range(int(-r * 1.1), int(r * 1.2) + 1):
        for x in range(int(-r * 1.2), int(r * 1.2) + 1):
            nx, ny = x / r, -y / r
            v = (nx * nx + ny * ny - 1) ** 3 - nx * nx * ny ** 3
            if v <= 0:
                if crack and abs(x - (2 if (y // 3) % 2 else -2) * (crack / 3)) < crack * 0.6:
                    continue
                edge = (nx * nx + ny * ny - 1) ** 3 - nx * nx * ny ** 3 > -0.02
                col = HEART_D if edge else (HEART_L if (nx < -0.2 and ny > 0.1) else HEART)
                if nx < -0.35 and 0.25 < ny < 0.55:
                    col = HEART_W
                _put(c, cx + x, cy + y, col, a)


def revive_heart(size=112, frames=14):
    """Tim bất diệt: a heart appears and beats (0-3), cracks and bursts (4-6) into a short column of light (6-9),
    white feathers drift down while it fades (8-13). Drawn at the hero."""
    c0 = size / 2
    out = []
    for f in range(frames):
        c = Canvas(size, size)
        fade = 255 if f < frames - 4 else int(255 * (frames - f) / 5)
        if f < 4:
            _heart(c, c0, c0 - 36, 9 + (2 if f % 2 else 0))
        elif f < 7:
            k = f - 3
            _heart(c, c0 - k * 3, c0 - 36 + k, 9, crack=k * 2)          # the two halves part
            for i in range(8):
                ang = i * math.tau / 8
                for s in range(6, 10 + k * 4):
                    _put(c, c0 + math.cos(ang) * s, c0 - 36 + math.sin(ang) * s, HEART_L, 220)
        if 5 <= f < 11:                                                  # a short column of light
            w = 7 - abs(f - 7) * 1.5
            for y in range(int(c0 - 54), int(c0 + 20)):
                for x in range(int(c0 - w), int(c0 + w) + 1):
                    d = abs(x - c0) / max(1.0, w)
                    _put(c, x, y, HEART_W if d < 0.4 else (HEART_L if d < 0.8 else HEART), fade if d < 0.8 else int(fade * 0.7))
        if f >= 7:                                                       # feathers drifting down
            for i in range(5):
                x = c0 - 24 + i * 12 + math.sin(f * 0.8 + i) * 3
                y = c0 - 50 + (f - 7) * 6 + (i % 2) * 8
                for k in range(5):
                    _put(c, x + k * 0.6, y + k, (250, 250, 255), fade)
                    _put(c, x + k * 0.6 + 1, y + k, (200, 206, 224), fade)
        out.append(c)
    return out


SAND = (240, 200, 110)
SAND_D = (190, 140, 60)
GLASS = (210, 236, 255)
FRAME = (150, 100, 40)
FRAME_L = (230, 180, 90)
TIME_B = (140, 200, 255)


def hourglass(size=112, frames=14):
    """Vĩnh cửu: a glowing hourglass appears over the hero, its sand runs down (0-6), it flips (7-8) and bursts
    into a ring of blue light: every cooldown is reset (9-13). Drawn at the hero."""
    c0 = size / 2
    out = []
    for f in range(frames):
        c = Canvas(size, size)
        fade = 255 if f < frames - 3 else int(255 * (frames - f) / 4)
        cx, cy = c0, c0 - 38   # above the head (anchor = the body centre)
        if f < 9:
            flip = f in (7, 8)
            h, w = 14, 10
            for y in range(-h, h + 1):                                   # the glass: two cones meeting at the waist
                half = 1 + (w - 1) * abs(y) / h
                for x in range(int(-half), int(half) + 1):
                    top = y < 0
                    level = f / 7                                       # sand left in the top bulb
                    filled = (top and abs(y) / h < (1 - level) * 0.9 + 0.05) if not flip else (not top and abs(y) / h < 0.9)
                    filled = filled or (not top and not flip and abs(y) / h > 1 - level * 0.85)
                    if abs(x) >= half - 0.8:
                        col = (120, 170, 210)
                    else:
                        col = (SAND if not flip else SAND_D) if filled else GLASS
                    _put(c, cx + x, cy + (-y if flip else y), col, fade)
            if not flip and f < 7:                                       # the falling stream
                for y in range(0, h):
                    if (y + f) % 2 == 0:
                        _put(c, cx, cy + y, SAND, fade)
            for x in range(-w - 2, w + 3):                               # wooden caps
                for dy, col in ((0, FRAME_L), (1, FRAME)):
                    _put(c, cx + x, cy - h - 2 + dy, col, fade)
                    _put(c, cx + x, cy + h + 1 + dy, col, fade)
        else:                                                            # the burst: a ring of blue light
            k = f - 9
            rr = 10 + k * 9
            for s in range(int(rr * 7)):
                ang = s / (rr * 7) * math.tau
                for wdt, col in ((0, (240, 250, 255)), (1, TIME_B), (2, (80, 140, 220))):
                    _put(c, c0 + math.cos(ang) * (rr - wdt), c0 + math.sin(ang) * (rr - wdt), col, fade)
            for i in range(6):
                ang = i * math.tau / 6 + k
                x, y = c0 + math.cos(ang) * rr, c0 + math.sin(ang) * rr
                for d in range(-3, 4):
                    _put(c, x + d, y, SAND, fade)
                    _put(c, x, y + d, SAND, fade)
        out.append(c)
    return out


# --- buff auras, 2D (user 2026-11-22: no 2.5D ground ellipses / front-back orbits) -----------------------------
AURA_FEET = (48, 88)      # anchor: the hero's feet (the run draws auras at player_pos)
AURA_BODY = (48, 68)      # the hero's body centre: ~20 world px above the feet (measured on the run shot)


def haste_ring(size=96, frames=8):
    """Rune tốc độ: a round ring of gold speed chevrons turning round the hero's body (loop)."""
    cx, cy = AURA_BODY
    out = []
    for f in range(frames):
        c = Canvas(size, size)
        for i in range(6):
            a = i * math.tau / 6 + f * math.tau / 24
            x, y = cx + math.cos(a) * 22, cy + math.sin(a) * 22
            tx, ty = -math.sin(a), math.cos(a)                       # chevron points along the turn
            for k in range(-4, 5):
                for w, col in ((0, STAR_W), (1, STAR_Y), (2, STAR_O)):
                    bx = x - tx * abs(k) * 0.9 + (math.cos(a) * k * 0.5)
                    by = y - ty * abs(k) * 0.9 + (math.sin(a) * k * 0.5)
                    _put(c, bx - tx * w, by - ty * w, col, 230)
        for s in range(int(22 * 7)):                                  # a faint broken track
            a = s / (22 * 7) * math.tau
            if (s + f * 2) % 14 < 9:
                _put(c, cx + math.cos(a) * 22, cy + math.sin(a) * 22, STAR_O, 120)
        out.append(c)
    return out


SHIELD_L = (236, 226, 190)
SHIELD = (196, 170, 110)
SHIELD_D = (120, 96, 52)
SHIELD_G = (255, 214, 92)


def _small_shield(c, x, y, a=255):
    rows = ["kkkkkkk", "klwllgk", "kllgllk", "kllgllk", ".kllgk.", "..kmk..", "...k..."]
    keys = {"k": (60, 40, 20), "l": SHIELD_L, "w": (255, 255, 240), "g": SHIELD_G, "m": SHIELD}
    for ry, row in enumerate(rows):
        for rx, ch in enumerate(row):
            if ch != ".":
                _put(c, x - 3 + rx, y - 3 + ry, keys[ch], a)


def aegis_orbit(size=96, form=4, loop=8, n=3):
    """Thần hộ: three small gold shields orbit the hero's body on one round path (2D, one layer; the old 3D orbit
    split into front/back halves). Returns (form frames, loop frames)."""
    cx, cy = AURA_BODY
    def frame(r, ang0, a):
        c = Canvas(size, size)
        for s in range(int(r * 7)):                                   # the orbit track, faint gold
            t = s / (r * 7) * math.tau
            if s % 6 < 4:
                _put(c, cx + math.cos(t) * r, cy + math.sin(t) * r, SHIELD_G, int(a * 0.45))
        for i in range(n):
            t = ang0 + i * math.tau / n
            _small_shield(c, cx + math.cos(t) * r, cy + math.sin(t) * r, a)
        return c
    forms = [frame(8 + 22 * (k + 1) / form, k * 0.4, int(255 * (k + 1) / form)) for k in range(form)]
    loops = [frame(30, form * 0.4 + k * math.tau / (n * loop), 255) for k in range(loop)]
    return forms, loops
