extends RefCounted
## Unit tests for SpriteSheet frame selection (addons/gamekit/sprites/sprite_sheet.gd).

const SheetScript := preload("res://addons/gamekit/sprites/sprite_sheet.gd")

# Two animations in one strip: idle frames 0-3 (looping), attack frames 4-8 (once).
const MULTI := {
	"frames": 9, "frame_size": [16, 16], "anchor": [8.0, 15.0],
	"animations": [
		{"name": "idle", "start": 0, "frames": 4, "fps": 4.0, "loop": true},
		{"name": "attack", "start": 4, "frames": 5, "fps": 10.0, "loop": false},
	],
}
const SINGLE := {"frames": 3, "frame_size": [8, 8], "fps": 6.0, "loop": true, "anchor": [3.5, 3.5]}

var failures: Array[String] = []


func _check(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)


func test_looping_animation_wraps_within_its_frames() -> void:
	var s: SpriteSheet = SheetScript.from_meta("m", MULTI)
	_check(s.frame_index("idle", 0.0) == 0, "idle t=0")
	_check(s.frame_index("idle", 0.99) == 3, "idle t=0.99 -> 3, got %d" % s.frame_index("idle", 0.99))
	_check(s.frame_index("idle", 1.0) == 0, "idle wraps at 1 s")


func test_one_shot_animation_starts_at_its_offset_and_holds_last_frame() -> void:
	var s: SpriteSheet = SheetScript.from_meta("m", MULTI)
	_check(s.frame_index("attack", 0.0) == 4, "attack starts at strip frame 4")
	_check(s.frame_index("attack", 10.0) == 8, "attack holds frame 8, got %d" % s.frame_index("attack", 10.0))
	_check(is_equal_approx(s.duration("attack"), 0.5), "attack lasts 5 / 10 fps = 0.5 s")


func test_single_strip_sheet_is_one_default_animation() -> void:
	var s: SpriteSheet = SheetScript.from_meta("one", SINGLE)
	_check(s.animation_names() == PackedStringArray([SpriteSheet.DEFAULT_ANIM]), "names %s" % s.animation_names())
	_check(s.frame_index(SpriteSheet.DEFAULT_ANIM, 0.5) == 0 + 3 % 3, "6 fps * 0.5 s = frame 3 -> wraps to 0")
	_check(s.anchor == Vector2(3.5, 3.5) and s.frame_size == Vector2(8, 8), "anchor/frame size from meta")


func test_first_of_picks_the_first_existing_name() -> void:
	var s: SpriteSheet = SheetScript.from_meta("m", MULTI)
	_check(s.first_of(["run", "walk", "attack"]) == "attack", "first_of skips missing names")
	_check(s.first_of(["run"]) == "", "first_of returns empty when none exist")


func test_src_rect_follows_frame_size() -> void:
	var s: SpriteSheet = SheetScript.from_meta("m", MULTI)
	_check(s.src_rect(5) == Rect2(80, 0, 16, 16), "frame 5 at x=80, got %s" % s.src_rect(5))
