"""burstfx: projectile impacts, earth eruption, holy column and lightning strike, drawn to
the fx_craft standard (double density, >= 12 frames, lead-in -> hit -> linger -> fade,
fxkit solids). Palettes per skill keep each element readable:
  impact_burst(pal): charge spark -> flash and rays -> energy blob with outlined shards
                     -> sparks and a ring linger -> fade        (arcane, solar, thunder, void, steel)
  earth_burst:       cracks run out -> rock pillars erupt in a ring -> dust -> crumble
  holy_column:       a glyph circle on the ground -> the beam slams down -> pillar shimmers -> fades up
  lightning_strike:  a crackling spark above -> the bolt hits with a flash -> crackle -> fade
"""

from __future__ import annotations

import math
import random

from spritekit import Canvas
from icefx import _disk, _fade, _p
import fxkit as fk

PALS = {
    # rim, mid, light, core, shard lit, shard dark, outline
    "arcane": ("#4a2a9a", "#7a5af0", "#7ef0ff", "#ffffff", "#c8f6ff", "#4a2a9a", "#1a1040"),
    "solar": ("#a8601a", "#ffb43a", "#ffe88a", "#fffbe0", "#fff2a8", "#c8802a", "#3a2008"),
    "thunder": ("#2a6ab0", "#ffe14a", "#fff8c0", "#ffffff", "#fff8c0", "#2a6ab0", "#101a40"),
    "void": ("#2a0a4a", "#8a2ad8", "#e05aff", "#ffd8ff", "#e8a0ff", "#3a0a6a", "#0a0418"),
    "steel": ("#5f7186", "#9fb3c8", "#e8f0f6", "#ffffff", "#f2f7fb", "#5f7186", "#1b1726"),
}
IMPACT_MS = [50, 45, 50, 55, 60, 70, 80, 90, 100, 110, 120, 130]


def impact_burst(tier, size, radius, pal, seed=21):
    rim, mid, light, core, lit, dark, outl = PALS[pal]
    cx = cy = size / 2
    radius = min(radius, size / 2 - 4)
    rng = random.Random(seed)
    shards = [(rng.uniform(0, math.tau), rng.uniform(0.6, 1.0)) for _ in range(6 + 2 * tier)]
    sparks = [(rng.uniform(0, math.tau), rng.uniform(0.5, 1.1)) for _ in range(10 + 3 * tier)]
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(size, size)
        if f == 0:
            fk.glow(c, cx, cy, radius * 0.25, [mid, light, core])
            fk.sparkle(c, int(cx), int(cy), 2 + tier, core, light)
        elif f == 1:
            fk.glow(c, cx, cy, radius * 0.55, [mid, light, core], density=0.9)
            fk.rays(c, cx, cy, radius * 0.35, radius, 8 + 2 * tier, light, core, rot=0.3, width=2)
        elif f < 5:
            t = (f - 1) / 3
            r = radius * (0.5 + 0.5 * t)
            fk.glow(c, cx, cy, r, [rim, mid, light, core], density=0.85 - 0.15 * t)
            lay = Canvas(size, size)
            for a, d in shards:
                fk.crystal(lay, cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6, a, (3 + tier) * d * (0.7 + 0.5 * t),
                           1.6 + tier * 0.2, lit, mid, dark, core)
            fk.stack(c, lay, outl)
            fk.ring_band(c, cx, cy, r + 2, [outl, rim, light])
            for a, d in sparks:
                rr = r * d + 3 * t
                fk.streak(c, cx + math.cos(a) * rr, cy + math.sin(a) * rr, math.cos(a), math.sin(a), 3, core, light)
        else:
            k = f - 5
            r = radius * (1.0 + 0.04 * k)
            fk.ring_band(c, cx, cy, r, [rim, mid])
            fk.glow(c, cx, cy, max(1, r * (0.35 - 0.04 * k)), [mid, light], density=0.6)
            for a, d in sparks:
                rr = r * d * (1 + 0.08 * k)
                if (k + int(a * 5)) % 3:
                    _p(c, cx + math.cos(a) * rr, cy + math.sin(a) * rr - k, light)
            if k % 2 == 0 and k < 4:
                fk.sparkle(c, int(cx + r * 0.4), int(cy - r * 0.3), 2, core, light)
            if k >= 1:
                _fade(c, min(0.95, 0.1 + 0.18 * k))
        out.append(c)
        masks.append(fk.mask_art(c, cx, cy, radius * 0.3 if f == 0 else radius * 0.6 if f == 1 else radius * (0.5 + 0.5 * (f - 1) / 3) + 3 if f < 5 else radius * 0.5))
    return fk.FxFrames(out, masks)


STONE = ("#b8b0a0", "#8a8070", "#4a4038", "#e8e0d0")
DIRT = "#6a4a2a"
DIRT_D = "#3e2a18"
DUST = "#b89a70"
DUST_L = "#d8c09a"
EARTH_MS = [70, 60, 55, 55, 60, 70, 80, 90, 100, 110, 120, 130]


def earth_burst(tier, size, radius, seed=31):
    cx = cy = size / 2
    radius = min(radius, size / 2 - 6)
    rng = random.Random(seed)
    cracks = [(rng.uniform(0, math.tau), rng.uniform(0.6, 1.0)) for _ in range(6 + tier)]
    pillars = [(k * math.tau / (5 + tier) + rng.uniform(-0.2, 0.2), rng.uniform(0.35, 0.8)) for k in range(5 + tier)]
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(size, size)
        grow = min(1.0, (f + 1) / 3)
        for a, d in cracks:
            x1, y1 = cx + math.cos(a) * radius * d * grow, cy + math.sin(a) * radius * d * grow * 0.8
            c.line(int(cx), int(cy), int(x1), int(y1), DIRT_D, 2)
            c.line(int(cx), int(cy), int(x1), int(y1), DIRT)
        if f == 1:
            fk.glow(c, cx, cy, radius * 0.25, [DUST, DUST_L, "#fff2d0"])
        if 2 <= f <= 7:
            up = [0.5, 1.0, 1.0, 0.9, 0.7, 0.4][f - 2]
            lay = Canvas(size, size)
            for a, d in pillars:
                x, y = cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d * 0.8
                fk.crystal(lay, x, y + 3, -math.pi / 2 + (a % 0.5) - 0.25, (12 + tier * 3) * up, 4 + tier * 0.4, *STONE)
            fk.stack(c, lay, DIRT_D)
            if f <= 4:
                for a, d in pillars:
                    x, y = cx + math.cos(a) * radius * d, cy + math.sin(a) * radius * d * 0.8
                    fk.streak(c, x + rng.uniform(-3, 3), y - rng.uniform(4, 12), 0, -1, 3, DUST_L, DUST)
        if f >= 6:
            _disk(c, cx, cy - (f - 6), radius * 0.8, DUST, density=0.22 - 0.03 * (f - 6))
        if f >= 8:
            _fade(c, min(0.95, 0.1 + 0.2 * (f - 7)))
        out.append(c)
        masks.append(fk.mask_art(c, cx, cy, radius * 0.95))
    return fk.FxFrames(out, masks)


# the floor pool + sigil reach about 1.7x the shaft radius; the hit mask must
# cover the light the player sees, not just the narrow pillar (user 2026-11-18)
HOLY_HIT_MUL = 1.7

HOLY_MS = [70, 60, 50, 45, 50, 55, 70, 80, 95, 110, 125, 140]
GOLD = ("#c08a2a", "#e8b23a", "#ffd96a", "#fff0b4", "#fffbe6", "#ffffff")
# per frame: strength of the light, how wide the ground flare is.  f0-1 a thread falls
# out of the sky, f2 it lands, f3-7 the pillar stands, f8-11 it lifts and fades.
HOLY_LEVEL = [0.55, 0.80, 0.92, 1.00, 0.98, 0.94, 0.88, 0.76, 0.56, 0.38, 0.22, 0.10]
HOLY_FLARE = [0.22, 0.45, 0.85, 1.00, 0.96, 0.92, 0.86, 0.70, 0.48, 0.30, 0.16, 0.08]


def _h01(x, y, salt):
    """A stable random 0..1 (integer hash with avalanche): the sparse spots of light
    scatter without a repeating grid, and a new salt makes them shimmer per frame."""
    h = (int(x) * 374761393 + int(y) * 668265263 + int(salt) * 1103515245) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return (h & 0xFFFF) / 65535.0


def _scatter(c, x, y, col, dens, salt=0):
    """One speckle of light, placed by the hash above (a Bayer grid reads as a plaid)."""
    if dens > 0 and _h01(x, y, salt) < dens:
        _p(c, x, y, col)


def _holy_ring(c, cx, cy, rx, ry, ramp, level, dash=None, rot=0.0):
    """The inlaid sigil on the ground: a one-pixel dashed ellipse, not a drawn hoop."""
    if level <= 0:
        return
    n = max(28, int(math.tau * max(rx, ry) * 2.0))
    for i in range(n):
        if dash and i % (dash[0] + dash[1]) < dash[1]:
            continue
        a = rot + i * math.tau / n
        x = int(round(cx + math.cos(a) * rx))
        y = int(round(cy + math.sin(a) * ry))
        col = ramp[3] if i % 8 == 0 else ramp[2]
        if level >= 0.75:
            _p(c, x, y, col)
        else:
            _scatter(c, x, y, col, level, salt=7)


def _holy_flare(c, cx, ground, rx, ramp, level, phase):
    """The light pooling on the ground: a wide flat ellipse, hot in the middle, with
    spokes running out along the floor and a rim that breaks into speckles."""
    if level <= 0 or rx <= 0:
        return
    ry = max(3.5, rx * 0.24)
    for y in range(int(ground - ry * 1.5), int(ground + ry * 1.5) + 1):
        for x in range(int(cx - rx * 1.28), int(cx + rx * 1.28) + 1):
            ex, ey = (x + 0.5 - cx) / rx, (y + 0.5 - ground) / ry
            d = math.hypot(ex, ey)
            if d > 1.26:
                continue
            spokes = 1.0 + 0.16 * math.cos(math.atan2(ey, ex) * 8 + phase)
            p = max(0.0, 1.0 - d) ** 1.1 * 1.5 * spokes * level
            if p >= 0.92:
                col = ramp[5]
            elif p >= 0.70:
                col = ramp[4]
            elif p >= 0.46:
                col = ramp[3]
            elif p >= 0.24:
                col = ramp[2]
            elif p >= 0.08:
                _scatter(c, x, y, ramp[1], (p - 0.06) * 3.4, salt=23 + int(phase * 2))
                continue
            else:
                continue
            _p(c, x, y, col)


def _holy_shaft(c, cx, ground, hw0, ramp, level, phase, y_top=0.0, hscale=1.0,
                off_extra=0.0):
    """One pillar of light: a white core, pale middle, gold rim and a speckled halo,
    straight at the sides and flaring where it meets the ground. Near the top of the
    frame the light cools and stops, so a visible end never looks cut; [y_top] lifts
    the foot of the light as it dies and [off_extra] draws a companion ray."""
    for y in range(int(y_top), int(ground)):
        t = y / max(1.0, ground)
        w = hw0 * (0.94 + 0.06 * t)
        if t > 0.84:                                  # the foot of the pillar spreads
            w *= 1.0 + 0.26 * ((t - 0.84) / 0.16) ** 1.5
        foot = max(0.0, (t - 0.92) / 0.08)            # then gathers back into the impact
        if foot > 0:
            w *= 1.0 - 0.60 * foot ** 1.4
        w = w * hscale + 0.8 * math.sin(y * 0.037 + phase)
        off = off_extra + 1.2 * math.sin(y * 0.047 + phase * 0.7)
        # near the top of the sprite the light narrows, cools and stops: a visible end
        # looks like the beam fading into the sky, never like a cut at the frame edge
        sky = max(0.0, min(1.0, (y - y_top) / 110.0))
        w *= 0.62 + 0.38 * sky
        lvl = level * (0.18 + 0.82 * sky)
        if lvl <= 0.06:
            continue
        cool = int((1.0 - sky) * 2.2)
        for x in range(int(math.floor(cx + off - w * 1.9)),
                       int(math.ceil(cx + off + w * 1.9)) + 1):
            d = abs(x + 0.5 - cx - off)
            if foot > 0:
                # the rim ends higher than the middle, with a ragged edge: the
                # pillar flows into the sigil instead of ending on a flat line
                edge = d / max(0.1, w)
                end = ground - edge * edge * 9 * foot - 2.5 * _h01(x, 29, 31) * edge * foot
                if y >= end:
                    continue
            if d <= w * 0.26:
                band = 5
            elif d <= w * 0.52:
                band = 4
            elif d <= w * 0.78:
                band = 3
            elif d <= w:
                band = 2
            else:
                k = d / w - 1.0
                if k < 0.55:
                    _scatter(c, x, y, ramp[2] if k < 0.3 else ramp[1],
                             0.38 * lvl * (1.0 - k / 0.55), salt=11 + int(phase * 3))
                elif k < 0.95:
                    _scatter(c, x, y, ramp[1], 0.18 * lvl * (1.0 - (k - 0.55) / 0.40),
                             salt=13 + int(phase * 3))
                continue
            # the last stretch at the top frays into specks, so a visible end reads as
            # light breaking up in the air instead of a straight line at the frame edge
            if sky < 0.30 and _h01(x, y, 17) > sky / 0.30:
                continue
            _p(c, x, y, ramp[max(1, band - int((1.0 - lvl) * 2.4) - cool)])


def holy_column(tier, w, h, ground, radius, seed=41):
    cx = w / 2
    rng = random.Random(seed)
    ramp = GOLD
    hw0 = radius * (0.60 + 0.04 * tier)
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    motes = [(rng.uniform(-1.0, 1.0), rng.uniform(0.0, 1.0), rng.uniform(0.7, 1.4))
             for _ in range(8 + 2 * tier)]
    sparks = [(rng.uniform(-1.0, 1.0), rng.uniform(0.5, 1.1),
               rng.uniform(0.06, 0.20)) for _ in range(5 + tier)]
    gx, gy = radius * 1.32, radius * 0.40
    for f in range(12):
        c = Canvas(w, h)
        level, flare = HOLY_LEVEL[f], HOLY_FLARE[f]
        phase = 0.9 * f

        # the sigil: the mark the light lands on, then the scorch it leaves behind
        ring = (0.30 + 0.35 * f) if f <= 2 else (0.30 if f >= 9 else 0.0)
        _holy_ring(c, cx, ground, gx, gy, ramp, ring, dash=(7, 5), rot=f * 0.05)
        if ring > 0.5:
            _holy_ring(c, cx, ground, gx * 0.66, gy * 0.66, ramp, ring * 0.7,
                       dash=(2, 7), rot=-f * 0.08)
        if tier >= 2 and ring > 0:
            _holy_ring(c, cx, ground, gx * 1.22, gy * 1.22, ramp, ring * 0.5,
                       dash=(2, 10), rot=f * 0.03)
        _holy_flare(c, cx, ground, min(radius * (1.20 + 0.80 * flare), w * 0.40 - 4),
                    ramp, flare * 0.95, phase)

        # f0-1: a thread of light falls out of the sky and touches the ground
        if f <= 1:
            drop = ground * (0.58 if f == 0 else 1.0)
            x = cx
            for y in range(0, int(drop)):
                x = cx + 1.6 * math.sin(y * 0.09 + f * 1.9)
                if _h01(int(x), y, 3) < 0.55 + 0.45 * (y / max(1.0, drop)):
                    _p(c, x, y, ramp[5] if y > drop * 0.7 else ramp[4])
            tx, ty = int(x), int(drop) - 1
            if f == 0:
                fk.sparkle(c, tx, ty, 2, ramp[5], ramp[3])
            else:
                fk.sparkle(c, tx, ty, 3, ramp[5], ramp[4])
                fk.rays(c, tx, ty, 3, radius * 0.5, 8, ramp[4], ramp[5])

        # the pillar itself (f2: still narrowing into place, f8+: the foot lifts)
        if f >= 2:
            y_top = ground * 0.10 * max(0, f - 8)
            _holy_shaft(c, cx, ground, hw0 * (0.72 + 0.28 * min(1.0, level)), ramp,
                        level, phase, y_top=y_top)
            # gold filaments drifting down inside the shaft give the light some grain
            for i in range(3 + tier // 2):
                fx = (i - (2 + tier // 2) / 2.0) / max(1.0, 2 + tier // 2) * 1.5
                top = 0.0
                for y in range(int(top), int(ground) - 4):
                    if y > ground - 5 - 9 * max(0.0, (y / ground - 0.92) / 0.08):
                        continue
                    x = cx + fx * hw0 * (0.9 + 0.1 * math.sin(y * 0.05 + i))
                    x += math.sin(y * 0.09 + phase + i * 2.1) * 1.2
                    if _h01(int(x), y, 41 + i) < 0.16 + 0.34 * level * (y / ground):
                        _p(c, x, y, ramp[3])
            if tier >= 5 and level > 0.6:
                # the top tier keeps a crown of sparks turning around the foot
                for k in range(6):
                    a = k * math.tau / 6 + f * 0.14
                    fk.sparkle(c, int(cx + math.cos(a) * gx * 1.05),
                               int(ground + math.sin(a) * gy * 1.05), 1, ramp[5], ramp[3])
            if f >= 7:
                # as the shaft lifts it gathers into a bright knot at the impact:
                # the ending reads as light being absorbed by the ground, not a cut
                k = (f - 7) / 4.0
                kr = max(2, int(radius * (0.22 - 0.10 * k)))
                _disk(c, cx, ground, kr, ramp[2], density=0.75 - 0.40 * k)
                _disk(c, cx, ground, max(1, kr // 2), ramp[4], density=0.80 - 0.35 * k)

        # impact: a ring of light runs out over the floor, rays flare, sparks fly
        if 2 <= f <= 6:
            k = (f - 2) / 4.0
            rr = radius * (1.15 + 0.85 * k)
            rx, ry = rr, rr * 0.34
            n = max(30, int(math.tau * rx * 1.5))
            for i in range(n):
                a = i * math.tau / n
                x = int(round(cx + math.cos(a) * rx))
                y = int(round(ground + math.sin(a) * ry))
                col = ramp[3] if f <= 4 else ramp[2]
                if _h01(x, y, 51) < 1.0 - 0.55 * k:
                    _p(c, x, y, col)
        if 2 <= f <= 4:
            fk.rays(c, cx, ground, radius * 0.55, radius * (1.30 - 0.13 * (f - 2)),
                    9 + 2 * tier, ramp[2], ramp[4], rot=0.2 + f * 0.1)
        if 2 <= f <= 9:
            for i, (dx, sp, up) in enumerate(sparks):
                age = (f - 2) + i * 0.3
                if f > 4 and i % 2:
                    continue
                x = cx + dx * radius * (0.35 + 0.9 * age * (0.4 + up))
                y = ground - 3 - sp * 34.0 * age + 260.0 * age * age * up
                if y < 2 or y > ground - 2:
                    continue
                fk.streak(c, x, y, dx * 0.7, -1.4, 3, ramp[4], ramp[2])

        # motes of light rising through the pillar
        if f >= 2 and level > 0.3:
            rise = (f - 2) * 9.0
            for i, (dx, my, sp) in enumerate(motes):
                y = ground - ((my * ground * 0.92 + rise * sp) % (ground * 0.92))
                x = cx + dx * hw0 * (1.6 + 0.5 * math.sin(f * 0.5 + i))
                x += math.sin(f * 0.7 + i * 2) * 1.4
                if _h01(int(x), int(y), 31) < 0.10 + 0.55 * level:
                    fk.streak(c, x, y, math.sin(f * 0.4 + i) * 0.5, -1.5,
                              2 + i % 2, ramp[3], ramp[2])

        out.append(c)
        masks.append(fk.mask_art(c, cx, ground, radius * HOLY_HIT_MUL))
    return fk.FxFrames(out, masks)


BOLT_MS = [70, 70, 50, 50, 55, 60, 80, 90, 100, 110, 120, 130]


def lightning_strike(tier, w, h, ground, radius, seed=51):
    cx = w / 2
    rng = random.Random(seed)
    out = []
    masks = []   # hit masks: the damaging core (spritekit measures the hitbox from these)
    for f in range(12):
        c = Canvas(w, h)
        if f < 2:   # a crackling spark gathers at the top, a mark on the ground
            fk.sparkle(c, int(cx + rng.uniform(-3, 3)), 6 + f * 2, 3 + tier, "#fff8c0", "#9ad0ff")
            fk.ring_band(c, cx, ground, radius * (0.4 + 0.2 * f), ["#2a6ab0", "#9ad0ff"])
        elif f < 6:
            lay = Canvas(w, h)
            x0 = cx + rng.uniform(-6, 6)
            pts = [(x0, 0)]
            segs = 9
            for k in range(1, segs):
                pts.append((cx + rng.uniform(-8, 8) * (1 - k / segs), ground * k / segs))
            pts.append((cx, ground))
            for (a, b), (x1, y1) in zip(pts, pts[1:]):
                lay.line(int(a), int(b), int(x1), int(y1), "#9ad0ff", 4 + tier // 2)
                lay.line(int(a), int(b), int(x1), int(y1), "#fff8c0", 2)
            if tier >= 3:   # side forks
                for k in (3, 5):
                    a, b = pts[k]
                    lay.line(int(a), int(b), int(a + rng.choice((-1, 1)) * 10), int(b + 8), "#fff8c0", 1)
            fk.stack(c, lay, "#101a40")
            fk.glow(c, cx, ground, radius * (0.7 if f == 2 else 0.5), ["#2a6ab0", "#9ad0ff", "#fff8c0", "#ffffff"], density=0.85)
            fk.rays(c, cx, ground, radius * 0.3, radius, 8 + tier, "#fff8c0", "#ffffff", rot=f * 0.4, width=2 if f == 2 else 1)
        else:
            k = f - 6
            for s in range(6 + tier):
                a = s * 1.3 + k * 0.8
                r = radius * (0.3 + 0.12 * k) * (0.6 + (s % 3) * 0.2)
                fk.streak(c, cx + math.cos(a) * r, ground + math.sin(a) * r * 0.6, math.cos(a), math.sin(a), 3, "#c8f0ff", "#2a6ab0")
            if k < 3:
                fk.sparkle(c, int(cx), int(ground), 3 - k, "#ffffff", "#9ad0ff")
            if k >= 1:
                _fade(c, min(0.95, 0.1 + 0.18 * k))
        out.append(c)
        masks.append(fk.mask_art(c, cx, ground, radius * 0.75 if 2 <= f <= 3 else 0))
    return fk.FxFrames(out, masks)
