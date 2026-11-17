"""16 flight directions for projectiles (user 2026-11-17: the thunder javelin had
only 4 directions, so a shot flying diagonally kept a flat sprite).

with_directions() puts every frame of a sprite into a larger square frame (the
anchor in its middle, so a diagonal sprite is not clipped) and adds 16 animations
fly_000 .. fly_337 (degrees, clockwise from right on screen), each a rotation of
fly_right about the anchor. Rotation is RotSprite-like: scale up x8 (nearest),
rotate (nearest), scale back down taking the most common colour of each 8x8 block,
so pixel edges stay clean instead of breaking up.
"""
from collections import Counter

from PIL import Image

from spritekit import Canvas

UP = 8
ANGLES = [round(k * 22.5) for k in range(16)]   # 0, 22, 45, 68 (rounded), ...


def _pad(c, anchor, size):
    out = Canvas(size, size)
    out.img.alpha_composite(c.img, (int(size // 2 - anchor[0]), int(size // 2 - anchor[1])))
    return out


def _rotsprite(c, deg):
    w, h = c.img.size
    big = c.img.resize((w * UP, h * UP), Image.Resampling.NEAREST)
    big = big.rotate(-deg, resample=Image.Resampling.NEAREST, center=(w * UP / 2, h * UP / 2))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = big.load()
    for y in range(h):
        for x in range(w):
            cols = Counter()
            for dy in range(UP):
                for dx in range(UP):
                    p = px[x * UP + dx, y * UP + dy]
                    if p[3] >= 128:
                        cols[p] += 1
            if cols and sum(cols.values()) >= UP * UP * 0.4:
                out.putpixel((x, y), cols.most_common(1)[0][0])
    nc = Canvas(w, h)
    nc.img = out
    return nc


def with_directions(animations, anchor, size):
    """animations: [(name, frames, fps, loop, ...)]. Returns (animations padded to
    size x size with fly_000..fly_337 added after fly_right, the new anchor)."""
    out = []
    right = None
    for a in animations:
        frames = [_pad(f, anchor, size) for f in a[1]]
        rest = tuple(a[2:])
        if len(rest) >= 3 and isinstance(rest[2], dict) and "hitbox" in rest[2]:
            hb = dict(rest[2]["hitbox"])
            hb["center"] = [hb["center"][0] - anchor[0] + size / 2, hb["center"][1] - anchor[1] + size / 2]
            rest = rest[:2] + (dict(rest[2], hitbox=hb),) + rest[3:]
        out.append((a[0], frames) + rest)
        if a[0] == "fly_right":
            right = (frames,) + tuple(a[2:])
    if right is not None:
        rest = right[1:]
        for deg in ANGLES:
            out.append(("fly_%03d" % deg, [_rotsprite(f, deg) for f in right[0]]) + rest)
    return out, (size / 2.0, size / 2.0)
