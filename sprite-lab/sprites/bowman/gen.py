#!/usr/bin/env python3
"""bowman: the user's own archer (sprite-lab/sources/user/archer-2026-11-25.png, user 2026-11-25). Only animated and
recoloured: the drawing is cut into layers and moved by whole pixels, mirrored to face right. No helmet: the slots
are quiver, armour, bow, boots, gloves. The drawing is the default look; items recolour its pieces per tier.
Chạy: gamekit art run bowman
"""
import sys
from pathlib import Path


def _ws():
    for p in Path(__file__).resolve().parents:
        if (p / "tools/gamekit/pipeline/spritekit.py").exists():
            return p
    raise SystemExit("no workspace")


HERE = Path(__file__).resolve().parent
WS = _ws()
sys.path.insert(0, str(WS / "tools/gamekit/pipeline"))
sys.path.insert(0, str(HERE.parents[1] / "lib"))
from PIL import Image  # noqa: E402
from spritekit import Canvas  # noqa: E402
from sheet import export  # noqa: E402
from userart import check_connected  # noqa: E402
from spritekit import strip  # noqa: E402

SRC = WS / "sprite-lab/sources/user/archer-2026-11-25.png"
S = 48
CROP = (0, 0, 32, 30)
FEET_Y = 28
FLOOR = 44


LAYER_ORDER = ["quiver", "feet_back", "chest", "body", "arms_front", "weapon"]
SLOT_OF = {"quiver": "quiver", "chest": "chest", "feet_back": "feet", "weapon": "weapon", "arms_front": "arms"}
GREENS = {(0x91, 0x92, 0x5a), (0x7d, 0x7e, 0x4e), (0x5c, 0x5e, 0x39), (0x2c, 0x2c, 0x2c), (0xf3, 0xe8, 0xcf)}
BLACK = (0x08, 0x08, 0x0c)
QUIVER = {(0xb7, 0xb3, 0x9d), (0x95, 0x8f, 0x6f), (0x76, 0x72, 0x5f), (0xdf, 0xdc, 0xce), (0x4e, 0x31, 0x21)}   # not the ear


def _layer_of(x, y, rgb):
    """Layer of a pixel of the user's archer (left-facing crop)."""
    if y >= 25:
        return "feet_back"                                # boots (both legs below the armour)
    if x <= 11 and y >= 20:
        return "weapon"                                   # the bow and its string, low in the front hand
    if rgb in QUIVER and ((x >= 23 and 11 <= y <= 17) or (18 <= x <= 20 and 4 <= y <= 5)):
        return "quiver"                                   # the quiver's greys behind the shoulder, its fletchings
    if (x >= 22 and 20 <= y <= 24) or (11 <= x <= 13 and 21 <= y <= 23):
        return "arms_front"                               # the gloves on both hands
    if y >= 17 and (rgb in GREENS or rgb == BLACK or 12 <= x <= 21):
        return "chest"                                    # the green armour and belt
    return "body"                                         # hair, ears, face


def _group(layer, x, y=0):
    if layer == "feet_back":
        return "a" if x >= 14 else "b"                    # mirrored: the front leg is x >= 14
    if layer == "body" and y < 17 or layer == "quiver":
        return "hd"                                       # the head (and the quiver strapped behind it)
    return "ch"                                           # body, armour, gloves and the bow in the hand


def _parts():
    im = Image.open(SRC).convert("RGBA").crop(CROP)
    out = {k: Image.new("RGBA", im.size) for k in LAYER_ORDER}
    for y in range(im.height):
        for x in range(im.width):
            p = im.getpixel((x, y))
            if p[3]:
                out[_layer_of(x, y, p[:3])].putpixel((x, y), p)
    flip = Image.Transpose.FLIP_LEFT_RIGHT
    return {k: v.transpose(flip) for k, v in out.items()}


PARTS = _parts()
OX = 24 - 14            # after the mirror the legs are x 10..12 and 16..18: centre them on the anchor
OY = FLOOR - FEET_Y - 1


def frame(up=(0, 0), a=(0, 0), b=(0, 0), flash=False, gear=None, hd=(0, 0), wp=(0, 0), ch=(0, 0)):
    """One frame as {layer: Canvas}; gear maps a slot to a colour function (the item tier). up moves the whole upper
    body; hd / ch / wp add to the head, the body and the staff on top of it."""
    offs = {"a": a, "b": b, "hd": (up[0] + hd[0], up[1] + hd[1]), "ch": (up[0] + ch[0], up[1] + ch[1]),
            "wp": (up[0] + wp[0], up[1] + wp[1])}
    out = {}
    for k in LAYER_ORDER:
        fn = (gear or {}).get(SLOT_OF.get(k, ""))
        src = PARTS[k]
        if fn and k == "head" and getattr(fn, "extra", None):   # tier details on the hood (user 2026-11-25)
            src = src.copy()
            for (ex, ey, col) in fn.extra:
                src.putpixel((ex, ey), (*_rgb(col), 255))
        px = src.load()
        c = Canvas(S, S)
        for y in range(src.height):
            for x in range(src.width):
                p = px[x, y]
                if not p[3]:
                    continue
                dx, dy = offs[_group(k, x, y)]
                col = fn(p) if fn else p
                if flash:
                    col = (min(255, col[0] + 150), min(255, col[1] + 150), min(255, col[2] + 150), col[3])
                c.img.putpixel((OX + x + dx, OY + y + dy), col)
        out[k] = c
    return out


def flat(layers):
    c = Canvas(S, S)
    for k in LAYER_ORDER:
        c.img.alpha_composite(layers[k].img)
    return c


def lying(layers):
    whole = flat(layers).img.rotate(90, expand=True)
    bbox = whole.getbbox()
    if not bbox:
        return layers
    w = bbox[2] - bbox[0]
    x0, y0 = max(0, min(S - w, 24 - w // 2)), FLOOR - (bbox[3] - bbox[1])
    out = {}
    for k, c in layers.items():
        n = Canvas(S, S)
        n.img.alpha_composite(c.img.rotate(90, expand=True).crop(bbox), (x0, y0))
        out[k] = n
    return out


def anims(gear=None):
    f = lambda **kw: frame(gear=gear, **kw)  # noqa: E731
    # idle: breathe (body dips, the head nods a beat later). The staff never moves apart from the hand holding it
    # (user 2026-11-25: a staff swayed on its own slid out of the hand); it moves with the body
    idle = [f(), f(hd=(0, 1)), f(up=(0, 1)), f(hd=(0, 1))]
    # run (user 2026-11-25: the old gait looked bad, the head slid on its own): head locked to the body, the body dips
    # on each contact, the legs swap with the back foot lifted on the passing frames
    run = [f(up=(0, 1), a=(1, 0), b=(-1, 0)),
           f(up=(0, 1), a=(0, 0), b=(-1, -1)),
           f(a=(0, 0), b=(0, -1)),
           f(a=(-1, 0), b=(1, -1)),
           f(up=(0, 1), a=(-1, 0), b=(1, 0)),
           f(up=(0, 1), a=(-1, -1), b=(0, 0)),
           f(a=(0, -1), b=(0, 0)),
           f(a=(1, -1), b=(-1, 0))]
    hurt = [f(up=(-1, 0), flash=True, hd=(-1, 0)), f(up=(-1, 0), hd=(-1, 1)), f(hd=(0, 1))]
    dash = [f(up=(0, 1), hd=(0, 1)), f(up=(2, 1), a=(2, 0), b=(-2, 0), hd=(1, 0)),
            f(up=(2, 1), a=(2, 0), b=(-2, -1), hd=(1, 0)),
            f(up=(2, 1), a=(2, 0), b=(-2, 0), hd=(1, 0)), f(up=(1, 0))]
    death = [f(up=(-1, 0), flash=True), f(up=(0, 1)), f(up=(0, 1)), lying(f(up=(0, 1))), lying(f(up=(0, 1)))]
    hb = {"shape": "rect", "center": [24.0, 30.0]}
    return [("idle", idle, 5, True, {"durations_ms": [240, 160, 240, 160], "hitbox": dict(hb, active=[0, 3])}),
            ("run", run, 12, True, {"hitbox": dict(hb, active=[0, 7])}),
            ("hurt", hurt, 12, False, {"durations_ms": [90, 110, 120], "hitbox": dict(hb, active=[0, 2])}),
            ("dash", dash, 14, False, {"durations_ms": [60, 50, 70, 70, 90], "hitbox": dict(hb, active=[0, 4])}),
            ("death", death, 8, False, {"durations_ms": [120, 140, 140, 100, 400], "hitbox": dict(hb, active=[0, 4])})]


# --- equipment tiers: the user's layers recoloured with the mage item icons' ramps (gear-icons PAL "mage") -------
# archer tiers (the drawing's moss green is the default): leather, forest, shadow, sun
TIERS = {
    "leather": {"d": "#3e2819", "m": "#6b4a2b", "l": "#9a6e40", "h": "#c79a62", "c": "#d8cfb0", "C": "#8e8670",
                "b": "#6b4a2b", "B": "#4a321c", "g": "#e8e2d0", "G": "#ffffff"},
    "forest": {"d": "#123d2a", "m": "#1f6b45", "l": "#3fa060", "h": "#8ed890", "c": "#e8f0f6", "C": "#9fb3c8",
               "b": "#5a3a26", "B": "#3e2819", "g": "#bfe6ff", "G": "#ffffff"},
    "shadow": {"d": "#1a1426", "m": "#33284a", "l": "#5a4878", "h": "#9a86c0", "c": "#c38df5", "C": "#7b4bb0",
               "b": "#2a1a30", "B": "#160d1c", "g": "#ffb3f0", "G": "#ffffff"},
    "sun": {"d": "#8a5a1a", "m": "#d49a2a", "l": "#f2c14e", "h": "#fff2a8", "c": "#ffffff", "C": "#e8f0f6",
            "b": "#e8f0f6", "B": "#9fb3c8", "g": "#fff2a8", "G": "#ffffff"},
}
TIER_ORDER = ["leather", "forest", "shadow", "sun"]
ITEMS = {"quiver": ["leather_quiver", "forest_quiver", "shadow_quiver", "sun_quiver"],
         "chest": ["leather_armor", "forest_armor", "shadow_armor", "sun_armor"],
         "weapon": ["hunting_bow", "forest_bow", "shadow_bow", "sun_bow"],
         "feet": ["leather_boots", "forest_boots", "shadow_boots", "sun_boots"],
         "arms": ["leather_gloves", "forest_gloves", "shadow_gloves", "sun_gloves"]}


def _rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


# details on the hood surface, mirrored-crop coords (frame x - 14, y - 14): pixels inside the hood, so no outline
# changes. void: a small violet gem; star: two gold stars.
HOOD_EXTRA = {"cloth": [], "arcane": [],
              "void": [(9, 8, "#e05aff")],
              "star": [(7, 7, "#fff2a8"), (10, 8, "#fff2a8"), (11, 8, "#d9a63a")]}


def recolour(tier):
    """Greens / greys (armour, quiver, bow wood, gloves, boots) by brightness to the tier ramp; the bow string and the
    belt's pale cloth to the trim; outlines stay."""
    t = {k: _rgb(v) for k, v in TIERS[tier].items()}
    ramp = [t["d"], t["m"], t["l"], t["h"]]

    def fn(p):
        r, g, b, a = p
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if (r, g, b) == BLACK or lum < 25:
            return p
        if lum > 225:                                     # string, pale belt cloth
            return (*t["c"], a)
        if r > g + 40:                                    # skin-like browns stay (gloves' bare fingers)
            return p
        return (*ramp[min(3, int(lum / 58))], a)

    fn.extra = []
    return fn


def write_layers(anim_list, names, folder):
    folder.mkdir(parents=True, exist_ok=True)
    every = [fr for _, frames, *_ in anim_list for fr in frames]
    for k in names:
        strip([fr[k] for fr in every]).save(folder / f"{k}_strip.png")


KNIGHT_BOOTS = ["iron_boots", "steel_boots", "dragon_boots", "aegis_boots"]
PIECES = {"bow": (34, 7, 41, 28)}


def _quiver_icon(src):
    """The quiver's grey pixels and the outline touching them (fletchings and tube), x4."""
    def is_q(x, y):
        p = src.getpixel((x, y))
        return p[3] and p[:3] in QUIVER and ((x >= 23 and 11 <= y <= 17) or (18 <= x <= 20 and 4 <= y <= 5))
    im = Image.new("RGBA", (12, 16))
    for y in range(3, 18):
        for x in range(17, 29):
            p = src.getpixel((x, y))
            near = any(is_q(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if p[3] and (is_q(x, y) or (near and p[:3] == BLACK)):
                im.putpixel((x - 17, y - 3), p)
    im = im.crop(im.getbbox())
    k = max(1, min(20 // im.width, 20 // im.height))
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


def write_icons(folder):
    """Bow from the user's loose bow; quiver, armour, gloves cropped from the drawing; boots shared with the knight
    (user 2026-11-25: shoes are too small, same picture, own name)."""
    folder.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert("RGBA")
    up = lambda im, k: im.resize((im.width * k, im.height * k), Image.NEAREST)  # noqa: E731
    art = {"weapon": src.crop(PIECES["bow"]), "quiver": _quiver_icon(src),
           "chest": up(src.crop((12, 18, 22, 25)), 2), "arms": up(src.crop((22, 20, 25, 25)), 3)}
    for slot, items in ITEMS.items():
        for tier, item in zip(TIER_ORDER, items):
            if slot == "feet":
                knight = HERE.parent / "knight" / "icons" / f"{KNIGHT_BOOTS[TIER_ORDER.index(tier)]}.png"
                Image.open(knight).save(folder / f"{item}.png")
                continue
            if slot in ("quiver", "arms"):   # drawn properly (user 2026-11-25), in the tier's colours
                import drawnicons
                (drawnicons.quiver if slot == "quiver" else drawnicons.gloves)(TIERS[tier]).save(folder / f"{item}.png")
                continue
            fn = recolour(tier)
            im = art[slot]
            col = Image.new("RGBA", im.size)
            for yy in range(im.height):
                for xx in range(im.width):
                    p = im.getpixel((xx, yy))
                    if p[3]:
                        col.putpixel((xx, yy), fn(p))
            c = Image.new("RGBA", (24, 24))
            c.alpha_composite(col, ((24 - im.width) // 2, (24 - im.height) // 2))
            c.save(folder / f"{item}.png")


if __name__ == "__main__":
    import json
    base = anims()
    flat_anims = [(n, [flat(fr) for fr in frames], fps, loop, extra) for n, frames, fps, loop, extra in base]
    check_connected(flat_anims, "bowman")
    export(HERE, HERE.name, flat_anims, anchor=(24.0, float(FLOOR)), ground=True, body="idle")
    write_layers(base, LAYER_ORDER, HERE / "layers")
    meta_path = HERE / f"{HERE.name}.json"
    meta = json.loads(meta_path.read_text())
    meta["layers"] = list(LAYER_ORDER)
    meta["outline"] = "none"          # the user's drawing has its own outline
    meta["slots"] = {slot: [k for k, s in SLOT_OF.items() if s == slot] for slot in ITEMS}
    meta["base"] = ["body"]
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    for slot, items in ITEMS.items():
        for tier, item in zip(TIER_ORDER, items):
            sets = anims({slot: recolour(tier)})
            check_connected([(n, [flat(fr) for fr in frames], *r) for n, frames, *r in sets], f"bowman {item}")
            write_layers(sets, meta["slots"][slot], HERE / "gear" / item)
    write_icons(HERE / "icons")
    print("OK", HERE.name, "+ 20 items + icons")
