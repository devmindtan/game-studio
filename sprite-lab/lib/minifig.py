"""minifig: compact side-view characters for the Sprite Lab (style: minimal, chunky,
Celeste / Shovel Knight-like), drawn from numeric poses so proportions stay the
same in every frame and every animation.

A pose is a dict; every key has a default (see POSE). Coordinates are pixels in
a 48x48 frame, facing right; the floor is FLOOR (feet's last row is FLOOR - 1),
so the sprite's anchor is (ROOT_X, FLOOR) and `write_anim_meta(..., ground=True)`
can check that grounded frames touch the floor.

A character is a dict of palette + part painters:
    {"pal": {...}, "body": "tunic" | "robe", "head": painter, "behind": painter,
     "held": painter, "front": painter, "fx": painter}
Painters get (canvas, pose, geometry) and draw extra parts; "fx" runs after the
outline, for glows / slashes / sparks that must not be outlined.

Layers (for equipment): draw_layers() paints the figure split by EQUIPMENT SLOT
(SLOTS: head, chest, arms, legs, weapon; BASE: the face, never replaced), without outline, in LAYERS z order;
compose() + outline gives exactly what draw() returns. A slot that wraps around
the body has a back and a front part (the back arm is under the torso, the front
arm over it), but it is one slot: an armour piece replaces all its parts, drawn
with the same poses, and the game composes and outlines the result.
Character keys: "head" -> body (face), "hair" -> head, "neck" + tunic/robe -> chest,
"behind" -> chest_back, "held_back" -> weapon_back, "held" -> weapon, "front".

Used by sprite-lab/sprites/swordsman/gen.py and sprite-lab/sprites/mage/gen.py.
"""
from __future__ import annotations

import math

from spritekit import Canvas, color

W = H = 48
FLOOR = 44          # the outline under the boots is row 43 (lowest opaque row)
SOLE = FLOOR - 2    # boots' last coloured row; the 1 px outline goes below it
ROOT_X = 24         # between the feet; the anchor x
HIP_Y = 36          # hip height when standing
OUTLINE = "#1b1726"

POSE = {
    "bob": 0,            # upper body down (+) / up (-), feet unaffected
    "lean": 0,           # head + shoulders forward (+) / back (-)
    "hip": (0, 0),       # hip offset from (ROOT_X, HIP_Y)
    "feet": ((-3, 0), (3, 0)),   # (back, front): (dx from ROOT_X, lift above floor)
    "hands": ((-3, 7), (4, 7)),  # (back, front): offset from the shoulders
    "eyes": "open",      # open | closed | wince | x
    "head": (0, 0),      # extra head offset (look up/down, recoil)
    "tilt": 0,           # hat / hair tilt, -1 back .. +1 forward
    "phase": 0.0,        # secondary motion (scarf, cape, hem), radians
    "speed": 0.0,        # 0 standing .. 1 running: how far cloth trails
    "lie": 0.0,          # 0 upright .. 1 lying on the back (death)
    "flash": 0.0,        # 0..1 white hit flash over the whole figure
    "weapon": 45,        # held weapon angle in degrees: 0 forward, 90 down, -90 up, 180 back
    "fx": "",            # effect drawn after the outline (character-specific name)
    "fx_t": 0.0,         # effect progress 0..1
}


def pose(**kw):
    p = dict(POSE)
    for k in kw:
        if k not in POSE:
            raise KeyError(f"unknown pose key {k!r}")
    p.update(kw)
    return p


# --- pixel helpers ----------------------------------------------------------

def put(c: Canvas, x, y, col):
    c.pixel(int(round(x)), int(round(y)), col)


def line(c: Canvas, x0, y0, x1, y1, col, width=1):
    """Bresenham line with a square brush (crisp, no anti-aliasing)."""
    x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        for ox in range(width):
            for oy in range(width):
                c.pixel(x0 + ox - width // 2, y0 + oy - width // 2, col)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def rect(c: Canvas, x0, y0, x1, y1, col):
    c.rect(int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1)), col)


def blob(c: Canvas, x0, y0, x1, y1, col):
    """Rectangle with the four corner pixels cut: reads as a rounded block."""
    x0, y0, x1, y1 = (int(round(v)) for v in (x0, y0, x1, y1))
    c.rect(x0, y0, x1, y1, col)
    for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        c.img.putpixel((x, y), (0, 0, 0, 0)) if 0 <= x < c.width and 0 <= y < c.height else None


# --- geometry -----------------------------------------------------------------

def geometry(p):
    """Key points of the body for a pose (all ints, facing right)."""
    hx, hy = p["hip"]
    hip = (ROOT_X + hx, HIP_Y + hy + p["bob"])
    top = (hip[0] + p["lean"], hip[1] - 8)                    # top of the torso
    sh_back = (top[0] - 2, top[1] + 1)
    sh_front = (top[0] + 1, top[1] + 1)
    (bfx, bfl), (ffx, ffl) = p["feet"]
    foot_back = (ROOT_X + bfx, SOLE - bfl)
    foot_front = (ROOT_X + ffx, SOLE - ffl)
    (bhx, bhy), (fhx, fhy) = p["hands"]
    hand_back = (sh_back[0] + bhx, sh_back[1] + bhy)
    hand_front = (sh_front[0] + fhx, sh_front[1] + fhy)
    hdx, hdy = p["head"]
    head = (top[0] + hdx, top[1] - 1 + hdy)                  # bottom-centre of the head
    return {"hip": hip, "top": top, "sh_back": sh_back, "sh_front": sh_front,
            "foot_back": foot_back, "foot_front": foot_front,
            "hand_back": hand_back, "hand_front": hand_front, "head": head}


# --- body parts -----------------------------------------------------------------

def leg(c, hip, foot, pal, back, boot_c=None):
    """Trouser leg on c, boot on boot_c (default: the same canvas)."""
    pants = pal["pants_d"] if back else pal["pants"]
    boot = pal["boot_d"] if back else pal["boot"]
    knee_y = min(foot[1] - 2, hip[1] + 2)
    line(c, hip[0], hip[1], foot[0], knee_y, pants, 2)
    line(c, foot[0], knee_y, foot[0], foot[1] - 1, pants, 2)
    rect(boot_c or c, foot[0] - 1, foot[1] - 1, foot[0] + 2, foot[1], boot)   # boot, toe forward


def arm(c, shoulder, hand, pal, back, hand_c=None):
    """Sleeve on c, hand on hand_c (default: the same canvas)."""
    sleeve = pal["sleeve_d"] if back else pal["sleeve"]
    line(c, shoulder[0], shoulder[1], hand[0], hand[1], sleeve, 2)
    skin = pal["skin_d"] if back else pal["skin"]
    rect(hand_c or c, hand[0], hand[1], hand[0] + 1, hand[1] + 1, skin)


def tunic(c, g, pal):
    hip, top = g["hip"], g["top"]
    # torso leans with the shoulders: draw row by row between hip and top
    rows = hip[1] - top[1]
    for i in range(rows + 1):
        y = top[1] + i
        x = round(top[0] + (hip[0] - top[0]) * i / max(1, rows))
        c.rect(x - 3, y, x + 3, y, color(pal["tunic"]))
        c.pixel(x + 3, y, pal["tunic_l"])              # lit front edge
        c.pixel(x - 3, y, pal["tunic_d"])              # shaded back edge
    bx = round(hip[0] + (top[0] - hip[0]) * 0.2)
    c.rect(bx - 3, hip[1] - 2, bx + 3, hip[1] - 2, color(pal["belt"]))   # belt
    c.pixel(bx + 1, hip[1] - 2, pal["buckle"])


def robe(c, g, p, pal, hem_up=0):
    """Long robe from shoulders to just above the floor; the hem flares and sways.
    hem_up lifts the hem so trousers show above the boots."""
    hip, top = g["hip"], g["top"]
    hem_y = SOLE - 2 - hem_up
    sway = round(math.sin(p["phase"]) * 1.5 * (0.4 + p["speed"]))
    for y in range(top[1], hem_y + 1):
        t = (y - top[1]) / max(1, hem_y - top[1])
        cx = round(top[0] + (hip[0] - top[0]) * min(1.0, t * 1.4)) + round(sway * t * t)
        half = 3 + round(t * (3 + 1.5 * p["speed"]))
        c.rect(cx - half, y, cx + half, y, color(pal["robe"]))
        c.pixel(cx + half, y, pal["robe_l"])
        c.pixel(cx - half, y, pal["robe_d"])
        if y == hem_y:
            c.rect(cx - half, y, cx + half, y, color(pal["trim"]))
    c.rect(top[0] - 3, hip[1] - 3, top[0] + 3, hip[1] - 3, color(pal["belt"]))  # sash


def eyes(c, x, y, kind, pal):
    e = pal.get("eye", OUTLINE)
    if kind == "open":
        put(c, x, y, e)
        put(c, x, y + 1, e)
    elif kind == "closed":
        put(c, x, y + 1, e)
        put(c, x - 1, y + 1, e)
    elif kind == "wince":
        put(c, x, y, e)
        put(c, x - 1, y + 1, e)
        put(c, x, y + 2, e)
    elif kind == "x":
        put(c, x - 1, y, e)
        put(c, x, y + 1, e)
        put(c, x - 1, y + 2, e)
        put(c, x + 1, y, e)
        put(c, x + 1, y + 2, e)


# --- the figure -------------------------------------------------------------------

# Z order, back to front. BASE is the bare figure under everything (not a slot);
# the equipment slots group the rest (see SLOTS).
LAYERS = ["chest_back", "legs_back", "feet_back", "arms_back", "weapon_back", "chest", "legs_front",
          "feet_front", "body", "head", "weapon", "arms_front", "front"]
BASE = ["body"]                               # the bare figure (face, eyes, skin): never replaced
SLOTS = {
    "head": ["head"],                         # hair / helmet
    "chest": ["chest_back", "chest"],         # cape or scarf tail behind; tunic, robe, collar
    "arms": ["arms_back", "arms_front"],      # sleeves and hands (gloves, gauntlets)
    "legs": ["legs_back", "legs_front"],      # trousers / greaves (Quần)
    "feet": ["feet_back", "feet_front"],      # boots / shoes (Giày), split from the legs 2026-11-18
    "weapon": ["weapon_back", "weapon"],      # held behind the body / in front
}


def draw_layers(char, p):
    """The character in pose p split by equipment slot (no outline, no fx), as a
    dict in LAYERS order. compose() of it, outlined, is draw() without fx."""
    pal = char["pal"]
    L = {name: Canvas(W, H) for name in LAYERS}
    g = geometry(p)
    tunic_body = char.get("body", "tunic") == "tunic"
    if char.get("behind"):
        char["behind"](L["chest_back"], p, g)
    if tunic_body:
        leg(L["legs_back"], g["hip"], g["foot_back"], pal, back=True, boot_c=L["feet_back"])
    else:  # robe: only boots show under the hem
        b = g["foot_back"]
        rect(L["feet_back"], b[0] - 1, b[1] - 1, b[0] + 2, b[1], pal["boot_d"])
    arm(L["arms_back"], g["sh_back"], g["hand_back"], pal, back=True)
    if char.get("held_back"):
        char["held_back"](L["weapon_back"], p, g)
    if tunic_body:
        tunic(L["chest"], g, pal)
        leg(L["legs_front"], g["hip"], g["foot_front"], pal, back=False, boot_c=L["feet_front"])
    else:
        f = g["foot_front"]   # under the robe: with the back boot, below the chest
        rect(L["feet_back"], f[0] - 1, f[1] - 1, f[0] + 2, f[1], pal["boot"])
        up = char.get("hem_up", 0)
        if up:   # trousers between the hem and the boots (legs slot, Quần)
            for foot, layer, key in ((g["foot_back"], "legs_back", "pants_d"), (f, "legs_front", "pants")):
                rect(L[layer], foot[0], foot[1] - 2 - up, foot[0] + 1, foot[1] - 2, pal[key])   # 2 px: the legs stay apart
        robe(L["chest"], g, p, pal, up)
    if char.get("neck"):     # collar / scarf knot: part of the chest slot, above the legs
        char["neck"](L["chest"], p, g)
    char["head"](L["body"], p, g)
    if char.get("hair"):
        char["hair"](L["head"], p, g)
    if char.get("held"):
        char["held"](L["weapon"], p, g)
    arm(L["arms_front"], g["sh_front"], g["hand_front"], pal, back=False)
    if char.get("front"):
        char["front"](L["front"], p, g)
    if p["lie"]:
        L = _lie_layers(L, p["lie"])
    if p["flash"]:  # before the outline: the figure goes pale, its outline stays dark
        for c in L.values():
            _flash(c, p["flash"])
    return L


def compose(layers) -> Canvas:
    """Layers (dict in z order, or list of canvases) stacked into one canvas."""
    out = Canvas(W, H)
    for c in (layers.values() if isinstance(layers, dict) else layers):
        out.img.alpha_composite(c.img)
    return out


def draw(char, p) -> Canvas:
    """One frame: the character in pose p, outlined, effects on top."""
    c = compose(draw_layers(char, p))
    c.outline(OUTLINE)
    if char.get("fx"):
        char["fx"](c, p, geometry(p))
    return c


def _lie_layers(layers, amount):
    """_lie for every layer with one shared shift (from the whole figure)."""
    from PIL import Image
    angle = 90 * amount
    rotated = {k: c.img.rotate(angle, resample=Image.NEAREST, center=(ROOT_X, FLOOR - 1))
               for k, c in layers.items()}
    whole = Canvas(W, H)
    for img in rotated.values():
        whole.img.alpha_composite(img)
    bb = whole.img.getchannel("A").getbbox()
    shift = (FLOOR - 1) - bb[3] if bb else 0
    out = {}
    for k, img in rotated.items():
        moved = Canvas(W, H)
        moved.img.alpha_composite(img, (0, shift) if shift >= 0 else (0, 0),
                                  (0, 0) if shift >= 0 else (0, -shift))
        out[k] = moved
    return out


def _lie(c: Canvas, amount: float) -> Canvas:
    """Rotate the figure back about its feet (death): 0 upright .. 1 flat on the back."""
    from PIL import Image
    angle = 90 * amount
    rotated = c.img.rotate(angle, resample=Image.NEAREST, center=(ROOT_X, FLOOR - 1))
    out = Canvas(W, H)
    out.img = rotated
    bb = rotated.getchannel("A").getbbox()
    if bb:  # rest on the floor, leaving the bottom row for the outline
        shift = (FLOOR - 1) - bb[3]
        moved = Canvas(W, H)
        moved.img.alpha_composite(rotated, (0, shift) if shift >= 0 else (0, 0),
                                  (0, 0) if shift >= 0 else (0, -shift))
        out = moved
    return out


def _flash(c: Canvas, amount: float):
    px = c.img.load()
    for y in range(c.height):
        for x in range(c.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (round(r + (255 - r) * amount), round(g + (255 - g) * amount),
                            round(b + (255 - b) * amount), a)


def keep_above_floor(x, y, angle, length, margin=2):
    """Angle (degrees) for a held item of `length` from (x, y), turned toward the
    horizontal until its tip stays `margin` px above the floor line."""
    for _ in range(40):
        tip_y = y + math.sin(math.radians(angle)) * length
        if tip_y <= SOLE - margin:
            return angle
        angle += -5 if math.cos(math.radians(angle)) >= 0 else 5
    return angle


# --- shared motion tables ---------------------------------------------------------

# Run cycle, 8 frames: (front foot, back foot) as (dx, lift); one foot always on the floor.
RUN_FEET = [
    ((4, 0), (-4, 1)), ((2, 0), (-2, 3)), ((0, 0), (1, 4)), ((-2, 0), (3, 2)),
    ((-4, 1), (4, 0)), ((-2, 3), (2, 0)), ((1, 4), (0, 0)), ((3, 2), (-2, 0)),
]
RUN_BOB = [0, 1, 0, -1, 0, 1, 0, -1]


def run_pose(i, **extra):
    """Frame i of the shared run cycle; the arms swing against the legs."""
    (fdx, fl), (bdx, bl) = RUN_FEET[i]
    swing = -fdx
    base = dict(bob=RUN_BOB[i], lean=1, feet=((bdx, bl), (fdx, fl)),
                hands=((-2 - swing // 2, 6), (2 + swing // 2, 6)),
                phase=i * math.pi / 4, speed=1.0)
    base.update(extra)
    return pose(**base)
