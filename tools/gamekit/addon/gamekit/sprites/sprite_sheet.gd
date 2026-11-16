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
