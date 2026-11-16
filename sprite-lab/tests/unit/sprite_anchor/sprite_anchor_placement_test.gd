extends RefCounted
## Unit tests for SpriteAnchor (run by addons/gamekit/test/run_tests.gd).

const SpriteAnchorScript := preload("res://addons/gamekit/sprites/sprite_anchor.gd")

const FRAME := Vector2(16, 16)
const ANCHOR := Vector2(7.5, 8.5)  # the firefly's body centre
const POINT := Vector2(100, 200)
const SCALE := 3.0

var failures: Array[String] = []


func _check(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)


func test_anchor_lands_on_point_unflipped() -> void:
	var r := SpriteAnchorScript.dest_rect(POINT, FRAME, ANCHOR, SCALE, false)
	var at := SpriteAnchorScript.screen_of(r, FRAME, ANCHOR)
	_check(at.is_equal_approx(POINT), "unflipped anchor at %s, want %s" % [at, POINT])
	_check(r.size == FRAME * SCALE, "unflipped size %s" % r.size)


func test_anchor_lands_on_point_flipped() -> void:
	var r := SpriteAnchorScript.dest_rect(POINT, FRAME, ANCHOR, SCALE, true)
	var at := SpriteAnchorScript.screen_of(r, FRAME, ANCHOR)
	_check(at.is_equal_approx(POINT), "flipped anchor at %s, want %s" % [at, POINT])
	_check(r.size.x < 0.0, "flipped rect must have a negative width")


func test_flip_does_not_move_an_off_centre_anchor() -> void:
	# The bug this guards: centring on the canvas made an off-centre sprite jump
	# by (2 * offset * scale) px each time it turned around.
	var a := SpriteAnchorScript.screen_of(
		SpriteAnchorScript.dest_rect(POINT, FRAME, ANCHOR, SCALE, false), FRAME, ANCHOR)
	var b := SpriteAnchorScript.screen_of(
		SpriteAnchorScript.dest_rect(POINT, FRAME, ANCHOR, SCALE, true), FRAME, ANCHOR)
	_check(a.is_equal_approx(b), "anchor moved from %s to %s when flipped" % [a, b])


func test_centre_anchor_matches_plain_centring() -> void:
	var r := SpriteAnchorScript.dest_rect(POINT, FRAME, FRAME * 0.5, SCALE, false)
	_check(r.get_center().is_equal_approx(POINT), "centre anchor should centre the rect")
