"""Pillow helpers for agent-authored pixel art in game-studio.

Only Pillow is required. Colors are "#rgb", "#rrggbb", "#rrggbbaa" or
(r, g, b, a) tuples. Coordinates are integer pixels; (0, 0) is top-left.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

TRANSPARENT = (0, 0, 0, 0)


def color(value):
    if isinstance(value, tuple):
        return value if len(value) == 4 else (*value, 255)
    s = value.lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) == 6:
        s += "ff"
    if len(s) != 8:
        raise ValueError(f"bad color: {value!r}")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4, 6))


class Canvas:
    def __init__(self, width, height, fill=TRANSPARENT):
        self.img = Image.new("RGBA", (width, height), color(fill) if fill else TRANSPARENT)

    @property
    def width(self):
        return self.img.width

    @property
    def height(self):
        return self.img.height

    def copy(self):
        c = Canvas(self.width, self.height)
        c.img = self.img.copy()
        return c

    def pixel(self, x, y, value):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.img.putpixel((int(x), int(y)), color(value))
        return self

    def get(self, x, y):
        return self.img.getpixel((int(x), int(y)))

    def rect(self, x0, y0, x1, y1, value, fill=True):
        draw = ImageDraw.Draw(self.img)
        box = (int(x0), int(y0), int(x1), int(y1))
        draw.rectangle(box, outline=color(value), fill=color(value) if fill else None)
        return self

    def ellipse(self, x0, y0, x1, y1, value, fill=True):
        draw = ImageDraw.Draw(self.img)
        box = (int(x0), int(y0), int(x1), int(y1))
        draw.ellipse(box, outline=color(value), fill=color(value) if fill else None)
        return self

    def line(self, x0, y0, x1, y1, value, width=1):
        draw = ImageDraw.Draw(self.img)
        draw.line((int(x0), int(y0), int(x1), int(y1)), fill=color(value), width=int(width))
        return self

    def polygon(self, points, value, fill=True):
        draw = ImageDraw.Draw(self.img)
        pts = [(int(x), int(y)) for x, y in points]
        draw.polygon(pts, outline=color(value), fill=color(value) if fill else None)
        return self

    def paste(self, other, x=0, y=0):
        self.img.alpha_composite(other.img if isinstance(other, Canvas) else other, (int(x), int(y)))
        return self

    def flip_h(self):
        return _wrap(self.img.transpose(Image.Transpose.FLIP_LEFT_RIGHT))

    def flip_v(self):
        return _wrap(self.img.transpose(Image.Transpose.FLIP_TOP_BOTTOM))

    def outline(self, value):
        """Draw a 1px border just outside the opaque silhouette."""
        alpha = self.img.getchannel("A")
        grown = alpha.filter(ImageFilter.MaxFilter(3))
        border = Image.new("RGBA", self.img.size, color(value))
        border.putalpha(grown)
        out = Image.new("RGBA", self.img.size, TRANSPARENT)
        out.alpha_composite(border)
        out.alpha_composite(self.img)
        self.img = out
        return self

    def scale(self, factor):
        if factor == 1:
            return self.copy()
        return _wrap(self.img.resize(
            (self.width * factor, self.height * factor), Image.Resampling.NEAREST))

    def save(self, path, scale=1):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.scale(scale).img.save(path)
        return path

    def palette(self):
        seen = []
        for px in self.img.getdata():
            if px[3] and px not in seen:
                seen.append(px)
        return seen


def _wrap(img):
    c = Canvas(img.width, img.height)
    c.img = img
    return c


def from_rows(rows, palette, scale=1):
    """Build a canvas from ASCII rows. '.' or ' ' is transparent.

    from_rows(["..##..", ".####."], {"#": "#ffcc00"})
    """
    if not rows:
        raise ValueError("rows is empty")
    width = max(len(r) for r in rows)
    c = Canvas(width * scale, len(rows) * scale)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in (".", " "):
                continue
            if ch not in palette:
                raise KeyError(f"row {y}: no color for {ch!r} in palette")
            c.rect(x * scale, y * scale, x * scale + scale - 1, y * scale + scale - 1,
                   palette[ch], fill=True)
    return c


def strip(frames, padding=0, fill=TRANSPARENT):
    """Lay frames out horizontally into one sheet."""
    if not frames:
        raise ValueError("no frames")
    w, h = frames[0].width, frames[0].height
    for f in frames:
        if (f.width, f.height) != (w, h):
            raise ValueError("all frames must have the same size")
    sheet = Canvas(len(frames) * w + (len(frames) - 1) * padding, h, fill)
    for i, f in enumerate(frames):
        sheet.paste(f, i * (w + padding), 0)
    return sheet


def grid(frames, columns, padding=0, fill=TRANSPARENT):
    if not frames:
        raise ValueError("no frames")
    w, h = frames[0].width, frames[0].height
    rows = (len(frames) + columns - 1) // columns
    sheet = Canvas(columns * w + (columns - 1) * padding,
                   rows * h + (rows - 1) * padding, fill)
    for i, f in enumerate(frames):
        sheet.paste(f, (i % columns) * (w + padding), (i // columns) * (h + padding))
    return sheet


def preview(frames, path, scale=6, bg="#2b2b33", grid_lines=True):
    """Big nearest-neighbor preview on a flat background, for the agent to read."""
    if isinstance(frames, Canvas):
        frames = [frames]
    sheet = strip(frames)
    big = sheet.scale(scale)
    canvas = Image.new("RGBA", big.img.size, color(bg))
    canvas.alpha_composite(big.img)
    if grid_lines and scale >= 4:
        draw = ImageDraw.Draw(canvas)
        line_color = (*color("#000000")[:3], 60)
        for x in range(0, canvas.width, scale):
            draw.line((x, 0, x, canvas.height), fill=line_color)
        for y in range(0, canvas.height, scale):
            draw.line((0, y, canvas.width, y), fill=line_color)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)
    return path


def gif(frames, path, fps=8, scale=1):
    if not frames:
        raise ValueError("no frames")
    imgs = []
    for f in frames:
        im = f.scale(scale).img.convert("RGBA")
        base = Image.new("RGBA", im.size, (0, 0, 0, 0))
        base.alpha_composite(im)
        imgs.append(base.convert("P", palette=Image.Palette.ADAPTIVE, colors=255))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    imgs[0].save(path, save_all=True, append_images=imgs[1:],
                 duration=int(1000 / fps), loop=0, disposal=2)
    return path


# --- sprite metadata: frames, fps, anchor -------------------------------------
# The game places a sprite by its ANCHOR (a point in source pixels), never by
# the canvas centre: art is rarely centred on its canvas (lesson 2026-11-16,
# LESSONS.md). Every sprite ships <name>.json next to <name>_strip.png.

def content_bbox(frames):
    """Union of the opaque area of every frame: (x0, y0, x1, y1), x1/y1 exclusive."""
    boxes = [f.img.getchannel("A").getbbox() for f in frames]
    boxes = [b for b in boxes if b]
    if not boxes:
        raise ValueError("every frame is empty")
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def content_centre(frames):
    """Centre of the content over all frames, in source pixels."""
    x0, y0, x1, y1 = content_bbox(frames)
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def write_meta(path, frames, fps, anchor=None, loop=True):
    """Write <name>.json beside the strip: what the game needs to draw it.

    anchor: (x, y) in source pixels that lands on the object's position, e.g.
    the body centre, the feet, the head of a raindrop. None = content centre
    (right only for art that is symmetric around its middle).
    """
    import json

    w, h = frames[0].width, frames[0].height
    ax, ay = anchor if anchor is not None else content_centre(frames)
    meta = {
        "frames": len(frames),
        "frame_size": [w, h],
        "fps": fps,
        "loop": loop,
        "anchor": [ax, ay],
        "anchor_source": "explicit" if anchor is not None else "content_centre",
    }
    check_meta(meta)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return Path(path)


def write_anim_meta(path, animations, anchor=None, ground=False):
    """Write <name>.json for one strip holding several named animations.

    ground=True: a character standing on the floor; its anchor y is the floor
    line, and every frame of every animation not marked {"airborne": True} must
    touch it (lowest opaque pixel row == anchor y - 1). `check_ground` and
    `gamekit art run` enforce it (lesson 2026-11-16: feet floated 8 px / sank 2 px).

    animations: list of {"name", "frames", "fps", "loop"} in strip order. The
    frames of each animation are laid out left to right, one animation after the
    previous one. The game plays `animations[i]` from its `start` for `frames`
    frames, so the frame counts stay in this file and are never typed by hand.
    """
    import json

    flat = []
    entries = []
    for anim in animations:
        frames = anim.get("frames") or []
        if not frames:
            raise ValueError(f"animation {anim.get('name')!r} has no frames")
        size = (frames[0].width, frames[0].height)
        if any((f.width, f.height) != size for f in frames):
            raise ValueError(f"animation {anim.get('name')!r} mixes frame sizes")
        entries.append({
            "name": str(anim.get("name", f"anim{len(entries)}")),
            "start": len(flat),
            "frames": len(frames),
            "fps": float(anim.get("fps", 8)),
            "loop": bool(anim.get("loop", True)),
        })
        if anim.get("durations_ms") is not None:
            durations = anim["durations_ms"]
            if len(durations) != len(frames) or any(float(value) <= 0 for value in durations):
                raise ValueError(f"animation {anim.get('name')!r} has invalid durations_ms")
            entries[-1]["durations_ms"] = [float(value) for value in durations]
        if anim.get("airborne"):
            entries[-1]["airborne"] = True
        if anim.get("hitbox"):
            # measured from the pixels of this animation's active frames, so the
            # hit area always matches the art (lesson 2026-11-16)
            entries[-1]["hitbox"] = fit_hitbox(frames, anim["hitbox"])
        flat.extend(frames)
    if not flat:
        raise ValueError("no animations")

    w, h = flat[0].width, flat[0].height
    ax, ay = anchor if anchor is not None else content_centre(flat)
    meta = {
        "frames": len(flat),
        "frame_size": [w, h],
        "fps": entries[0]["fps"],
        "loop": entries[0]["loop"],
        "anchor": [ax, ay],
        "anchor_source": "explicit" if anchor is not None else "content_centre",
        "animations": entries,
    }
    if ground:
        meta["ground"] = True
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    check_meta(meta)
    if ground:
        sheet = strip(flat).img
        problems = check_ground(meta, sheet)
        if problems:
            raise ValueError("; ".join(problems))
    problems = check_hitbox(meta, strip(flat).img)
    if problems:
        raise ValueError("; ".join(problems))
    Path(path).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return Path(path)


def check_meta(meta, strip_size=None):
    """Raise ValueError when metadata cannot be drawn correctly."""
    problems = []
    w, h = meta.get("frame_size", [0, 0])
    n = meta.get("frames", 0)
    ax, ay = meta.get("anchor", [-1, -1])
    if n < 1:
        problems.append("frames must be >= 1")
    if not (0 <= ax <= w and 0 <= ay <= h):
        problems.append(f"anchor ({ax}, {ay}) is outside the {w}x{h} frame")
    if (ax * 2) % 1 or (ay * 2) % 1:
        problems.append("anchor must be on a whole or half pixel (x.0 or x.5)")
    if meta.get("fps", 0) <= 0:
        problems.append("fps must be > 0")
    animations = meta.get("animations")
    if animations is not None:
        problems.extend(_check_animations(animations, n))
    if strip_size and tuple(strip_size) != (w * n, h):
        problems.append(f"strip is {strip_size[0]}x{strip_size[1]}, meta says {n} x {w}x{h}")
    if problems:
        raise ValueError("; ".join(problems))
    return meta


def check_ground(meta, strip_img):
    """Problems where a grounded sprite's frames do not touch the floor line.

    Only for metadata with "ground": true. The floor is the anchor's y: the
    lowest opaque row of each frame must be exactly anchor_y - 1, except in
    animations marked "airborne" (jumps, knock-backs)."""
    if not meta.get("ground"):
        return []
    w, h = meta["frame_size"]
    floor = int(round(meta["anchor"][1]))
    problems = []
    for anim in meta.get("animations") or [{"name": "default", "start": 0, "frames": meta["frames"]}]:
        if anim.get("airborne"):
            continue
        bad = []
        for i in range(anim["frames"]):
            idx = anim["start"] + i
            bb = strip_img.crop((idx * w, 0, (idx + 1) * w, h)).getchannel("A").getbbox()
            bottom = bb[3] if bb else None
            if bottom != floor:
                bad.append(f"{i}:{'empty' if bottom is None else bottom - floor:+}" if bottom else f"{i}:empty")
        if bad:
            problems.append(f"{anim['name']}: frames off the floor (frame:rows, + = sinks, - = floats) "
                            + ", ".join(bad))
    return problems


HITBOX_ALPHA = 96  # pixels fainter than this (glow, haze) never count as the hit area
HITBOX_SHAPES = ("arc", "circle")


def _hit_pixels(frames, centre, alpha_min=HITBOX_ALPHA):
    """(distance, angle_deg) of every solid pixel centre, relative to `centre`."""
    import math

    cx, cy = centre
    out = []
    for f in frames:
        img = f.img if hasattr(f, "img") else f
        a = img.getchannel("A")
        w, h = img.size
        px = a.load()
        for y in range(h):
            for x in range(w):
                if px[x, y] >= alpha_min:
                    dx, dy = x + 0.5 - cx, y + 0.5 - cy
                    out.append((math.hypot(dx, dy), math.degrees(math.atan2(dy, dx))))
    return out


def _angle_diff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def fit_hitbox(frames, spec):
    """Measure an effect's hit area from its pixels.

    spec: {"shape": "arc"|"circle", "center": [x, y], "active": [first, last],
           "dir_deg": d (arc only; 0 = right, 90 = down)}
    `center` is the pivot in source pixels (the hand for a sword swipe, the
    middle of a spin). Only frames first..last (the frames that deal damage)
    and pixels with alpha >= HITBOX_ALPHA are measured. Returns the spec plus
    "radius" (outer), "inner" and, for arcs, "half_angle_deg", all from pixels,
    so nobody types hit numbers by hand."""
    import math

    shape = spec.get("shape")
    if shape not in HITBOX_SHAPES:
        raise ValueError(f"hitbox shape must be one of {HITBOX_SHAPES}, got {shape!r}")
    first, last = spec.get("active", [0, len(frames) - 1])
    pts = _hit_pixels(frames[first:last + 1], spec["center"])
    if not pts:
        raise ValueError("hitbox: the active frames have no solid pixels")
    box = {"shape": shape, "center": [float(v) for v in spec["center"]], "active": [int(first), int(last)],
           "radius": float(math.ceil(max(d for d, _ in pts))),
           "inner": float(math.floor(min(d for d, _ in pts)))}
    if shape == "arc":
        direction = float(spec.get("dir_deg", 0.0))
        box["dir_deg"] = direction
        box["half_angle_deg"] = float(math.ceil(max(abs(_angle_diff(a, direction)) for _, a in pts)))
    return box


def check_hitbox(meta, strip_img):
    """Problems where an animation's "hitbox" does not match its pixels.

    The hitbox must be what fit_hitbox measures from the active frames (within
    1 px / 3 degrees): a hand-typed or stale hitbox is refused."""
    problems = []
    w, h = meta["frame_size"]
    for anim in meta.get("animations") or []:
        box = anim.get("hitbox")
        if not box:
            continue
        name = anim["name"]
        cx, cy = box.get("center", [-1, -1])
        if not (0 <= cx <= w and 0 <= cy <= h):
            problems.append(f"{name}: hitbox center ({cx}, {cy}) outside the {w}x{h} frame")
            continue
        first, last = box.get("active", [-1, -1])
        if not (0 <= first <= last < anim["frames"]):
            problems.append(f"{name}: hitbox active {box.get('active')} outside 0..{anim['frames'] - 1}")
            continue
        frames = [strip_img.crop(((anim["start"] + i) * w, 0, (anim["start"] + i + 1) * w, h))
                  for i in range(anim["frames"])]
        try:
            fit = fit_hitbox(frames, box)
        except ValueError as e:
            problems.append(f"{name}: {e}")
            continue
        for key, tol in (("radius", 1.0), ("inner", 1.0), ("half_angle_deg", 3.0)):
            if key in fit and abs(float(box.get(key, -999)) - fit[key]) > tol:
                problems.append(f"{name}: hitbox {key} is {box.get(key)}, pixels say {fit[key]} "
                                "(regenerate: pass the hitbox spec to write_anim_meta / export)")
    return problems


def _check_animations(animations, total_frames):
    """Problems with the `animations` list of a sheet metadata (empty = fine)."""
    problems = []
    if not isinstance(animations, list) or not animations:
        return ["animations must be a non-empty list"]
    names = set()
    expected = 0
    for i, anim in enumerate(animations):
        if not isinstance(anim, dict):
            problems.append(f"animation {i} is not an object")
            continue
        name = anim.get("name")
        count = anim.get("frames", 0)
        start = anim.get("start", -1)
        if not isinstance(name, str) or not name:
            problems.append(f"animation {i} has no name")
        elif name in names:
            problems.append(f"animation name {name!r} repeats")
        else:
            names.add(name)
        if not isinstance(count, int) or count < 1:
            problems.append(f"animation {name!r} needs frames >= 1")
            continue
        if start != expected:
            problems.append(f"animation {name!r} starts at {start}, expected {expected} "
                            "(animations must be contiguous from 0)")
        expected += count
        if anim.get("fps", 0) <= 0:
            problems.append(f"animation {name!r} needs fps > 0")
        if "durations_ms" in anim:
            durations = anim["durations_ms"]
            if not isinstance(durations, list) or len(durations) != count:
                problems.append(f"animation {name!r} durations_ms must have one value per frame")
            elif any(not isinstance(value, (int, float)) or value <= 0 for value in durations):
                problems.append(f"animation {name!r} durations_ms values must be positive numbers")
    if expected > total_frames:
        problems.append(f"animations use {expected} frames, sheet has {total_frames}")
    return problems


LIBRESPRITE = os.environ.get("LIBRESPRITE", "libresprite")


def _run(args):
    result = subprocess.run([LIBRESPRITE, "--batch", *map(str, args)],
                            capture_output=True, text=True)
    output = (result.stdout + result.stderr).strip()
    if "Error:" in output:
        raise RuntimeError(f"libresprite failed:\n{output}")
    return output


def to_ase(png, ase):
    """PNG -> .ase for human editing in LibreSprite."""
    Path(ase).parent.mkdir(parents=True, exist_ok=True)
    _run([png, "--save-as", ase])
    if not Path(ase).exists():
        raise RuntimeError(f"libresprite did not write {ase}")
    return Path(ase)


def from_ase(ase, png):
    Path(png).parent.mkdir(parents=True, exist_ok=True)
    _run([ase, "--save-as", png])
    if not Path(png).exists():
        raise RuntimeError(f"libresprite did not write {png}")
    return Path(png)


def sheet_from_ase(ase, png, data=None, sheet_type="horizontal"):
    """Export frames/layers of an .ase to a sheet (+ optional JSON)."""
    args = [ase, "--sheet", png, "--sheet-type", sheet_type]
    if data:
        args += ["--data", data, "--format", "json-array"]
    _run(args)
    if not Path(png).exists():
        raise RuntimeError(f"libresprite did not write {png}")
    return Path(png)


if __name__ == "__main__":
    # Self-check: tiny sprite, outline, sheet, preview, GIF, ASE roundtrip.
    import tempfile

    rows = [
        "....##....",
        "..######..",
        ".########.",
        "..######..",
        "....##....",
    ]
    base = from_rows(rows, {"#": "#ffd34d"})
    frames = []
    for i in range(4):
        c = base.copy().outline("#7a4a00")
        c.pixel(3 + i, 2, "#ffffff")
        frames.append(c)
    # TemporaryDirectory removes everything on exit, also when an assert fails
    # (machine rule: never leave temp output behind).
    with tempfile.TemporaryDirectory(prefix="spritekit-") as tmp:
        d = Path(tmp)
        strip(frames).save(d / "strip.png")
        preview(frames, d / "preview.png", scale=6)
        gif(frames, d / "anim.gif", fps=8, scale=4)
        to_ase(d / "strip.png", d / "strip.ase")
        from_ase(d / "strip.ase", d / "back.png")
        assert Image.open(d / "back.png").size == Image.open(d / "strip.png").size
        assert len(base.palette()) == 1
        # metadata: content-centre default, explicit anchor, and a bad anchor refused
        m = write_meta(d / "m.json", frames, fps=8)
        assert m.exists()
        assert content_centre(frames) == (5.0, 2.5), content_centre(frames)
        write_meta(d / "m2.json", frames, fps=8, anchor=(5.0, 4.5))
        try:
            write_meta(d / "bad.json", frames, fps=8, anchor=(40, 2))
            raise AssertionError("anchor outside the frame was accepted")
        except ValueError:
            pass
        # multi-animation sheet: contiguous starts, per-animation fps/loop, bad input refused
        anims = [
            {"name": "idle", "frames": frames[:2], "fps": 6, "loop": True},
            {"name": "hit", "frames": frames[2:], "fps": 10, "loop": False},
        ]
        m3 = write_anim_meta(d / "m3.json", anims, anchor=(5.0, 4.5))
        import json
        meta3 = json.loads(m3.read_text())
        assert [a["start"] for a in meta3["animations"]] == [0, 2], meta3
        assert meta3["frames"] == 4
        assert meta3["animations"][1]["loop"] is False
        try:
            write_anim_meta(d / "bad2.json", [{"name": "a", "frames": [], "fps": 6}])
            raise AssertionError("animation without frames was accepted")
        except ValueError:
            pass
    print("ok (temp files removed)")
