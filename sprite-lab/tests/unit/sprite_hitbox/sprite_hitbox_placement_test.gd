extends RefCounted
## Unit tests for SpriteHitbox: the json hit area lands where the sprite is
## drawn (anchor, scale, mirror) and its active window follows the frame times.

var failures: Array[String] = []


func _check(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)


func _sheet() -> SpriteSheet:
	return SpriteSheet.from_meta("t", {
		"frames": 5, "frame_size": [48, 48], "fps": 16.0, "anchor": [24.0, 24.0],
		"animations": [{"name": "slash", "start": 0, "frames": 5, "fps": 16.0, "loop": false,
			"durations_ms": [50.0, 50.0, 70.0, 70.0, 60.0],
			"hitbox": {"shape": "arc", "center": [28.0, 24.0], "active": [1, 2], "radius": 20.0,
				"inner": 15.0, "dir_deg": 0.0, "half_angle_deg": 68.0}}]})


func test_hitbox_scales_from_anchor() -> void:
	var hb := SpriteHitbox.of(_sheet(), "slash", Vector2(100, 100), 2.0)
	_check(hb.center.is_equal_approx(Vector2(108, 100)), "centre 4px right of anchor x2 -> (108,100), got %s" % hb.center)
	_check(is_equal_approx(hb.radius, 40.0) and is_equal_approx(hb.inner, 30.0), "radii x2")


func test_hitbox_mirrors_with_sprite() -> void:
	var hb := SpriteHitbox.of(_sheet(), "slash", Vector2(100, 100), 2.0, true)
	_check(hb.center.is_equal_approx(Vector2(92, 100)), "mirrored centre (92,100), got %s" % hb.center)
	_check(hb.dir.is_equal_approx(Vector2.LEFT), "mirrored arc points left, got %s" % hb.dir)


func test_arc_contains_front_ring_only() -> void:
	var hb := SpriteHitbox.of(_sheet(), "slash", Vector2.ZERO, 1.0)
	var c := hb.center
	_check(hb.contains(c + Vector2(18, 0)), "on the ring in front: hit")
	_check(not hb.contains(c + Vector2(-18, 0)), "behind: no hit")
	_check(not hb.contains(c + Vector2(25, 0)), "beyond the radius: no hit")
	_check(hb.contains(c + Vector2(25, 0), 6.0), "body radius 6 reaching the ring: hit")
	_check(not hb.contains(c + Vector2(5, 0)), "inside the inner gap: no hit")


func test_active_window_follows_durations() -> void:
	var hb := SpriteHitbox.of(_sheet(), "slash", Vector2.ZERO, 1.0)
	_check(is_equal_approx(hb.active_from, 0.05) and is_equal_approx(hb.active_to, 0.17),
		"active frames 1..2 = 0.05..0.17 s, got %s..%s" % [hb.active_from, hb.active_to])
	_check(not hb.is_active(0.02) and hb.is_active(0.1) and not hb.is_active(0.2), "is_active window")


func test_no_hitbox_returns_null() -> void:
	var s := SpriteSheet.from_meta("n", {"frames": 1, "frame_size": [8, 8], "fps": 8.0})
	_check(SpriteHitbox.of(s, "default", Vector2.ZERO, 1.0) == null, "sprite without hitbox -> null")
