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
    print("ok (temp files removed)")
