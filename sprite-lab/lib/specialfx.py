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
