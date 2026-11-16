class_name SpriteAnchor
extends RefCounted
## Where to draw one frame of a pixel-art strip so that its anchor pixel lands
## on a world point, including when the frame is mirrored.
##
## The anchor is in source pixels from the frame's top-left, e.g. (7.5, 8.5) is
## the middle of the pixel block whose corners are (7, 8) and (8, 9).
## Mirroring uses a negative width; Godot then draws the same area flipped, so a
## source x shows at x' = width - x and the anchor must be mirrored too.
##
## Shared by every game and the sprite lab (addons/gamekit/sprites). Lesson
## 2026-11-16: never centre a sprite on its canvas; never re-derive a flipped rect.
##
## Example:
##   var r := SpriteAnchor.dest_rect(pos, Vector2(16, 16), Vector2(7.5, 8.5), 3.0, true)
##   draw_texture_rect_region(tex, r, src_rect)


## Destination rect for draw_texture_rect_region. [param frame_size] and
## [param anchor] are in source pixels; [param scale] is the display scale.
static func dest_rect(point: Vector2, frame_size: Vector2, anchor: Vector2,
		scale: float, flip_h: bool) -> Rect2:
	var a := Vector2(frame_size.x - anchor.x, anchor.y) if flip_h else anchor
	var rect := Rect2(point - a * scale, frame_size * scale)
	if flip_h:
		rect.size.x = -rect.size.x
	return rect


## Screen position where source pixel [param src] ends up inside [param rect]
## (handles a mirrored rect). Used by tests and debug overlays.
static func screen_of(rect: Rect2, frame_size: Vector2, src: Vector2) -> Vector2:
	var scale := absf(rect.size.y) / frame_size.y
	var x := src.x if rect.size.x >= 0.0 else frame_size.x - src.x
	return rect.position + Vector2(x, src.y) * scale
