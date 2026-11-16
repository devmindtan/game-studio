#!/usr/bin/env python3
"""Bridge Pixelbolt pose exports into Sprite Lab's fixed-frame strip format."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


def scaffold(name: str, template: str, examples: Path, out_dir: Path) -> None:
    source = examples / f"{template}.poses.json"
    if not source.is_file():
        raise SystemExit(f"Pixelbolt pose template not found: {source}")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{name}.poses.json"
    if target.exists():
        raise SystemExit(f"pose source already exists: {target}")
    data = json.loads(source.read_text(encoding="utf-8"))
    data["name"] = name
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (out_dir / "PIXELBOLT-SOURCE.txt").write_text(
        "Starter pose source copied and renamed from Pixelbolt 0.17.0 "
        f"examples/{template}.poses.json.\n"
        "Copyright (c) 2026 PixelForge contributors; MIT License.\n"
        "Full license text: tools/gamekit/PIXELBOLT-LICENSE.txt.\n",
        encoding="utf-8",
    )
    print(target)


def _frame_image(sheet: Image.Image, item: dict) -> tuple[Image.Image, tuple[int, int]]:
    rect = item["frame"]
    if item.get("rotated"):
        raise ValueError("rotated atlas frames are not supported by Sprite Lab")
    crop = sheet.crop((rect["x"], rect["y"], rect["x"] + rect["w"], rect["y"] + rect["h"]))
    source_size = item.get("sourceSize", {"w": rect["w"], "h": rect["h"]})
    source_w, source_h = int(source_size["w"]), int(source_size["h"])
    source_rect = item.get("spriteSourceSize", {"x": 0, "y": 0, "w": rect["w"], "h": rect["h"]})
    full = Image.new("RGBA", (source_w, source_h), (0, 0, 0, 0))
    full.alpha_composite(crop, (int(source_rect["x"]), int(source_rect["y"])))
    pivot = item.get("anchorPx")
    if not isinstance(pivot, dict):
        anchor = item.get("anchor", item.get("pivot"))
        if not isinstance(anchor, dict):
            raise ValueError("every atlas frame must include anchorPx or anchor")
        pivot = {"x": float(anchor["x"]) * source_w, "y": float(anchor["y"]) * source_h}
    px, py = float(pivot["x"]), float(pivot["y"])
    if px % 0.5 or py % 0.5:
        raise ValueError(f"anchor must land on a whole or half pixel, got ({px}, {py})")
    return full, (round(px * 2), round(py * 2))


def import_atlas(name: str, atlas_path: Path, sheet_path: Path, out_dir: Path) -> None:
    from spritekit import Canvas, preview, strip, write_anim_meta

    atlas = json.loads(atlas_path.read_text(encoding="utf-8"))
    image = Image.open(sheet_path).convert("RGBA")
    source_frames = atlas.get("frames", {})
    animation_map = atlas.get("animations", {})
    if not source_frames or not animation_map:
        raise ValueError("Pixelbolt atlas must contain frames and named animations")

    cache: dict[str, tuple[Image.Image, tuple[int, int], int]] = {}
    all_pivots: list[tuple[int, int]] = []
    for animation in animation_map.values():
        for frame_name in animation["frames"]:
            if frame_name in cache:
                continue
            if frame_name not in source_frames:
                raise ValueError(f"atlas animation references missing frame {frame_name!r}")
            item = source_frames[frame_name]
            frame, pivot = _frame_image(image, item)
            duration = int(item.get("duration", 0))
            if duration <= 0:
                raise ValueError(f"frame {frame_name!r} needs a positive duration")
            cache[frame_name] = (frame, pivot, duration)
            all_pivots.append(pivot)

    sizes = {frame.size for frame, _, _ in cache.values()}
    if len(sizes) != 1:
        raise ValueError(f"atlas frames have inconsistent source sizes: {sorted(sizes)}")
    source_w, source_h = next(iter(sizes))
    target_x = max(pivot[0] for pivot in all_pivots)
    target_y = max(pivot[1] for pivot in all_pivots)
    if any((target_x - px) % 2 or (target_y - py) % 2 for px, py in all_pivots):
        raise ValueError("frame anchors differ by a half pixel; pixel frames can only be shifted by whole pixels")
    offsets = {key: ((target_x - pivot[0]) // 2, (target_y - pivot[1]) // 2)
               for key, (_, pivot, _) in cache.items()}
    frame_w = source_w + max(dx for dx, _ in offsets.values())
    frame_h = source_h + max(dy for _, dy in offsets.values())
    pivot = (target_x, target_y)

    out_dir.mkdir(parents=True, exist_ok=True)
    animations = []
    flat = []
    for anim_name, animation in animation_map.items():
        frames = []
        durations = []
        for frame_name in animation["frames"]:
            src, _, duration = cache[frame_name]
            dx, dy = offsets[frame_name]
            canvas = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
            canvas.alpha_composite(src, (dx, dy))
            frames.append(Canvas(frame_w, frame_h))
            frames[-1].img = canvas
            durations.append(duration)
        total_ms = sum(durations)
        fps = len(frames) * 1000.0 / total_ms
        animations.append({
            "name": anim_name,
            "frames": frames,
            "fps": fps,
            "loop": bool(animation.get("loop", True)),
            "durations_ms": durations,
        })
        flat.extend(frames)
        gifs = [frame.scale(4).img.convert("P", palette=Image.Palette.ADAPTIVE, colors=255) for frame in frames]
        gif_options = {"save_all": True, "append_images": gifs[1:], "duration": durations,
                       "disposal": 2, "optimize": False}
        if animation.get("loop", True):
            gif_options["loop"] = 0
        gifs[0].save(out_dir / f"{anim_name}.gif", **gif_options)

    strip(flat).save(out_dir / f"{name}_strip.png")
    flat[0].save(out_dir / f"{name}.png")
    cols = max(len(anim["frames"]) for anim in animations)
    contact = Canvas(cols * frame_w, len(animations) * frame_h)
    row = 0
    for anim in animations:
        contact.paste(strip(anim["frames"]), 0, row * frame_h)
        row += 1
    preview([contact], out_dir / "preview.png", scale=max(2, 256 // max(frame_w, frame_h)))
    write_anim_meta(out_dir / f"{name}.json", animations, anchor=(target_x / 2, target_y / 2))
    print(f"Imported {len(flat)} frames in {len(animations)} animations; anchor {target_x / 2},{target_y / 2}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    make = sub.add_parser("scaffold")
    make.add_argument("--name", required=True)
    make.add_argument("--template", required=True)
    make.add_argument("--examples", type=Path, required=True)
    make.add_argument("--out-dir", type=Path, required=True)
    convert = sub.add_parser("import")
    convert.add_argument("--name", required=True)
    convert.add_argument("--atlas", type=Path, required=True)
    convert.add_argument("--sheet", type=Path, required=True)
    convert.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "scaffold":
        scaffold(args.name, args.template, args.examples, args.out_dir)
        return
    workspace = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(workspace / "tools/gamekit/pipeline"))
    import_atlas(args.name, args.atlas, args.sheet, args.out_dir)


if __name__ == "__main__":
    main()
