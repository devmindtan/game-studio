extends RefCounted
## Unit tests for SpriteSheet.outline_frames (layered characters / equipment).

var failures: Array[String] = []


func _check(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)


func test_outline_surrounds_pixel_inside_its_frame_only() -> void:
	# two 4x4 frames side by side; one opaque pixel on the right edge of frame 0
	var img := Image.create_empty(8, 4, false, Image.FORMAT_RGBA8)
	img.set_pixel(3, 1, Color.WHITE)
	var out := SpriteSheet.outline_frames(img, 4, 4, Color.BLACK)
	_check(out.get_pixel(3, 1) == Color.WHITE, "the pixel itself stays")
	_check(out.get_pixel(2, 1).a > 0.99 and out.get_pixel(2, 1).r < 0.01, "left neighbour becomes outline")
	_check(out.get_pixel(3, 0).a > 0.99 and out.get_pixel(2, 2).a > 0.99, "up and diagonal neighbours outlined")
	_check(out.get_pixel(4, 1).a == 0.0, "outline must not bleed into the next frame")
	_check(out.get_pixel(0, 3).a == 0.0, "far pixels stay empty")
