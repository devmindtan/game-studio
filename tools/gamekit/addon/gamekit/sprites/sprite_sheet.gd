class_name SpriteSheet
extends RefCounted
## One pixel-art sprite as written by its gen.py: <name>_strip.png (every frame
## left to right) + <name>.json (frame_size, anchor, and either one animation or
## an "animations" list of {name, start, frames, fps, loop, durations_ms?}).
##
## Plays animations by name and draws them anchored, so every game and the
## sprite lab use the same rules (addons/gamekit/sprites).
##
## Example:
##   var mage := SpriteSheet.load_dir("res://assets/sprites/custom/mage", "mage")
##   # in _draw():
##   mage.draw(self, "run", _time, position, 3.0, facing < 0.0)

## Name used for a sprite whose json has no "animations" list.
const DEFAULT_ANIM := "default"

var name := ""
var dir := ""                  # folder it was loaded from (layers/ lives there)
var texture: Texture2D
var meta: Dictionary = {}
var frame_size := Vector2.ZERO
var anchor := Vector2.ZERO
var _anims: Array[Dictionary] = []


## Loads <dir>/<name>_strip.png and <dir>/<name>.json. Returns null (and logs)
## when either is missing or the json is not an object.
static func load_dir(dir: String, sprite_name: String) -> SpriteSheet:
	var strip_path := dir.path_join(sprite_name + "_strip.png")
	var json_path := dir.path_join(sprite_name + ".json")
	if not ResourceLoader.exists(strip_path) or not FileAccess.file_exists(json_path):
		push_error("SpriteSheet: missing %s or %s" % [strip_path, json_path])
		return null
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(json_path))
	if not parsed is Dictionary:
		push_error("SpriteSheet: %s is not a JSON object" % json_path)
		return null
	var sheet := from_meta(sprite_name, parsed)
	sheet.dir = dir
	sheet.texture = load(strip_path)
	return sheet


## Builds a sheet from metadata only (no texture); used by load_dir and tests.
static func from_meta(sprite_name: String, m: Dictionary) -> SpriteSheet:
	var s := SpriteSheet.new()
	s.name = sprite_name
	s.meta = m
	var fs: Array = m.get("frame_size", [0, 0])
	s.frame_size = Vector2(float(fs[0]), float(fs[1]))
	var a: Variant = m.get("anchor")
	s.anchor = Vector2(float(a[0]), float(a[1])) if a is Array and a.size() == 2 else s.frame_size * 0.5
	var list: Variant = m.get("animations")
	if list is Array and not list.is_empty():
		for entry: Variant in list:
			if entry is Dictionary:
				s._anims.append(entry)
	else:
		s._anims.append({"name": DEFAULT_ANIM, "start": 0, "frames": int(m.get("frames", 1)),
			"fps": float(m.get("fps", 8)), "loop": bool(m.get("loop", true))})
	return s


## Animation names in sheet order.
func animation_names() -> PackedStringArray:
	var out := PackedStringArray()
	for a in _anims:
		out.append(String(a.get("name", "")))
	return out


## True if the sheet has an animation called [param anim_name].
func has_animation(anim_name: String) -> bool:
	return animation_names().has(anim_name)


## First name in [param names] that this sheet has, or "" (e.g. ["run", "walk"]).
func first_of(names: Array) -> String:
	for n: Variant in names:
		if has_animation(String(n)):
			return String(n)
	return ""


## The entry {name, start, frames, fps, loop}; the first animation if unknown.
func animation(anim_name: String) -> Dictionary:
	for a in _anims:
		if String(a.get("name", "")) == anim_name:
			return a
	return _anims[0] if not _anims.is_empty() else {}


## Seconds for one pass of the animation.
func duration(anim_name: String) -> float:
	var a := animation(anim_name)
	var durations: Variant = a.get("durations_ms", [])
	if durations is Array and durations.size() == int(a.get("frames", 1)) and not durations.is_empty():
		var total_ms := 0.0
		for value: Variant in durations:
			total_ms += float(value)
		return total_ms / 1000.0
	return float(a.get("frames", 1)) / maxf(0.001, float(a.get("fps", 8)))


## Index in the whole strip of the frame to show [param t] seconds into the
## animation. Looping animations wrap; others hold their last frame.
func frame_index(anim_name: String, t: float) -> int:
	var a := animation(anim_name)
	var n := maxi(1, int(a.get("frames", 1)))
	var durations: Variant = a.get("durations_ms", [])
	if durations is Array and durations.size() == n and not durations.is_empty():
		var total := 0.0
		for value: Variant in durations:
			total += maxf(0.001, float(value))
		var elapsed := maxf(t, 0.0) * 1000.0
		if bool(a.get("loop", true)):
			elapsed = fposmod(elapsed, total)
		else:
			elapsed = minf(elapsed, total - 0.001)
		for i in range(n):
			elapsed -= maxf(0.001, float(durations[i]))
			if elapsed < 0.0:
				return int(a.get("start", 0)) + i
		return int(a.get("start", 0)) + n - 1
	var i := int(floor(maxf(t, 0.0) * float(a.get("fps", 8))))
	i = posmod(i, n) if bool(a.get("loop", true)) else mini(i, n - 1)
	return int(a.get("start", 0)) + i


## Source rect of strip frame [param index].
func src_rect(index: int) -> Rect2:
	return Rect2(Vector2(frame_size.x * index, 0.0), frame_size)


## Draws [param anim_name] at time [param t] with its anchor on [param point].
func draw(canvas: CanvasItem, anim_name: String, t: float, point: Vector2, scale: float,
		flip_h := false, tint := Color.WHITE) -> void:
	draw_index(canvas, frame_index(anim_name, t), point, scale, flip_h, tint)


## Draws strip frame [param index] with its anchor on [param point], snapped to
## whole screen pixels so every source pixel keeps the same size.
func draw_index(canvas: CanvasItem, index: int, point: Vector2, scale: float,
		flip_h := false, tint := Color.WHITE) -> void:
	if texture == null:
		return
	var dest := SpriteAnchor.dest_rect(point, frame_size, anchor, scale, flip_h)
	dest.position = dest.position.round()
	canvas.draw_texture_rect_region(texture, dest, src_rect(index), tint)


# --- layers (equipment) -------------------------------------------------------
# A character drawn in layers (sheet.export_layered in the Sprite Lab) has
# "layers" (z order) and "outline" in its json and layers/<layer>_strip.png
# without outline. compose_layers() stacks them, optionally swapping some (an
# armour piece drawn with the same poses), and outlines each frame exactly like
# spritekit (3x3 max of alpha), so the result matches <name>_strip.png when
# nothing is swapped.


## Layer names in z order (empty for a sprite that is not layered).
func layer_names() -> PackedStringArray:
	var out := PackedStringArray()
	for n: Variant in meta.get("layers", []):
		out.append(String(n))
	return out


## Rebuilds [member texture] from the layer strips. [param overrides] maps a
## layer name to a Texture2D strip of the same size (equipment) or to null (hide
## that layer). Example: sheet.compose_layers({"torso": chest_tex, "hair": null})
func compose_layers(overrides := {}) -> void:
	var names := layer_names()
	if names.is_empty():
		push_error("SpriteSheet %s has no layers" % name)
		return
	var stacked: Image = null
	for n in names:
		var tex: Texture2D = null
		if overrides.has(n):
			tex = overrides[n]
		else:
			tex = load(dir.path_join("layers").path_join(n + "_strip.png"))
		if tex == null:
			continue
		var img := tex.get_image()
		img.convert(Image.FORMAT_RGBA8)
		if stacked == null:
			stacked = Image.create_empty(img.get_width(), img.get_height(), false, Image.FORMAT_RGBA8)
		stacked.blend_rect(img, Rect2i(Vector2i.ZERO, img.get_size()), Vector2i.ZERO)
	if stacked == null:
		return
	var outline := Color.html(String(meta.get("outline", "#1b1726")))
	texture = ImageTexture.create_from_image(outline_frames(stacked, int(frame_size.x), int(frame_size.y), outline))


## 1 px outline around the opaque pixels of every [param fw] x [param fh] frame
## of a strip (alpha of the border = max alpha of the 3x3 around it, inside the
## same frame), with the strip drawn on top. Same result as spritekit's
## Canvas.outline per frame.
static func outline_frames(src: Image, fw: int, fh: int, color: Color) -> Image:
	var w := src.get_width()
	var h := src.get_height()
	var data := src.get_data()
	var out := PackedByteArray()
	out.resize(data.size())
	var cr := color.r8
	var cg := color.g8
	var cb := color.b8
	for y in h:
		for x in w:
			var fx0 := (x / fw) * fw
			var i := (y * w + x) * 4
			var sa := data[i + 3]
			var ba := 0
			for dy in range(-1, 2):
				var yy := y + dy
				if yy < 0 or yy >= h:
					continue
				for dx in range(-1, 2):
					var xx := x + dx
					if xx < fx0 or xx >= fx0 + fw or xx >= w:
						continue
					ba = maxi(ba, data[(yy * w + xx) * 4 + 3])
			if sa == 255 or ba == 0:
				out[i] = data[i]
				out[i + 1] = data[i + 1]
				out[i + 2] = data[i + 2]
				out[i + 3] = sa
				continue
			# src over border (PIL alpha_composite)
			var sa_f := sa / 255.0
			var ba_f := ba / 255.0
			var oa := sa_f + ba_f * (1.0 - sa_f)
			out[i] = roundi((data[i] * sa_f + cr * ba_f * (1.0 - sa_f)) / oa)
			out[i + 1] = roundi((data[i + 1] * sa_f + cg * ba_f * (1.0 - sa_f)) / oa)
			out[i + 2] = roundi((data[i + 2] * sa_f + cb * ba_f * (1.0 - sa_f)) / oa)
			out[i + 3] = roundi(oa * 255.0)
	return Image.create_from_data(w, h, false, Image.FORMAT_RGBA8, out)
