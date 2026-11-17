class_name SpriteHitbox
extends RefCounted
## The hit area of an effect animation, placed in the world the same way the
## sprite is drawn (anchor on a point, uniform scale, optional mirror), so what
## the player sees is exactly what hits.
##
## The numbers come from the animation's "hitbox" in <name>.json, which
## spritekit.fit_hitbox measures from the pixels of the frames that deal damage
## ("active") and `gamekit art run` re-checks. Never type hit radii by hand
## (lesson 2026-11-16: a hand-tuned radius did not match the drawn sweep).
##
## Shapes: "circle" (ring between inner and radius), "arc" (that ring, cut
## to dir_deg ± half_angle_deg), and "rect" (axis-aligned box, half_w x half_h).
##
## Example:
##   var hb := SpriteHitbox.of(slash, "slash_right", shoulder, 2.0)
##   if hb and hb.contains(enemy_center, enemy_radius): ...
##   hb.draw(self, Color.YELLOW)   # debug overlay
##   var hurt := SpriteHitbox.body(slime, pos, 2.0)   # body circle for contact

var shape := "circle"
var center := Vector2.ZERO      # world
var radius := 0.0               # world (circle/arc)
var inner := 0.0                # world (circle/arc)
var half_w := 0.0               # world (rect)
var half_h := 0.0               # world (rect)
var dir := Vector2.RIGHT
var half_angle := PI            # radians
var active_from := 0.0          # seconds into the animation
var active_to := 0.0
var loop_len := 0.0             # > 0: the animation loops; is_active wraps t into one loop


## The hitbox of [param anim] drawn with its anchor on [param point] at
## [param scale] (mirrored when [param flip_h]); null when it has none.
static func of(sheet: SpriteSheet, anim: String, point: Vector2, scale: float, flip_h := false) -> SpriteHitbox:
	if sheet == null:
		return null
	var a := sheet.animation(anim)
	var box: Variant = a.get("hitbox")
	if not box is Dictionary:
		return null
	var hb := SpriteHitbox.new()
	hb.shape = String(box.get("shape", "circle"))
	var c: Array = box.get("center", [sheet.anchor.x, sheet.anchor.y])
	var local := Vector2(float(c[0]), float(c[1])) - sheet.anchor
	var deg := float(box.get("dir_deg", 0.0))
	if flip_h:
		local.x = -local.x
		deg = 180.0 - deg
	hb.center = point + local * scale
	if hb.shape == "rect":
		hb.half_w = float(box.get("half_w", 0.0)) * scale
		hb.half_h = float(box.get("half_h", 0.0)) * scale
	else:
		hb.radius = float(box.get("radius", 0.0)) * scale
		hb.inner = float(box.get("inner", 0.0)) * scale
		hb.dir = Vector2.from_angle(deg_to_rad(deg))
		hb.half_angle = deg_to_rad(float(box.get("half_angle_deg", 180.0))) if hb.shape == "arc" else PI
	var span: Array = box.get("active", [0, int(a.get("frames", 1)) - 1])
	hb.active_from = frame_time(a, int(span[0]))
	hb.active_to = frame_time(a, int(span[1]) + 1)
	if bool(a.get("loop", false)):
		hb.loop_len = frame_time(a, int(a.get("frames", 1)))
	return hb


## The sprite's body circle (its json "body", measured from pixels by
## spritekit.fit_body) placed like the drawn sprite; null when it has none.
## Use it for contact and for being hit instead of a hand-typed radius.
static func body(sheet: SpriteSheet, point: Vector2, scale: float, flip_h := false) -> SpriteHitbox:
	if sheet == null or not sheet.meta.get("body") is Dictionary:
		return null
	var b: Dictionary = sheet.meta["body"]
	var c: Array = b.get("center", [sheet.anchor.x, sheet.anchor.y])
	var local := Vector2(float(c[0]), float(c[1])) - sheet.anchor
	if flip_h:
		local.x = -local.x
	var hb := SpriteHitbox.new()
	hb.shape = "circle"
	hb.center = point + local * scale
	hb.radius = float(b.get("radius", 0.0)) * scale
	hb.active_to = INF
	return hb


## Seconds from the start of animation [param a] to the start of its frame [param i].
static func frame_time(a: Dictionary, i: int) -> float:
	var durations: Variant = a.get("durations_ms", [])
	var n := int(a.get("frames", 1))
	if durations is Array and durations.size() == n:
		var ms := 0.0
		for k in mini(i, n):
			ms += float(durations[k])
		return ms / 1000.0
	return float(mini(i, n)) / maxf(0.001, float(a.get("fps", 8)))


## True while the animation is on a frame that deals damage. A looping animation
## (a flying wave or bullet that lives longer than one loop) is active on its
## active frames in every loop, not only the first.
func is_active(t: float) -> bool:
	if loop_len > 0.0:
		t = fposmod(t, loop_len)
	return t >= active_from and t < active_to


## True when a circle at [param p] of radius [param extra] overlaps the area.
func contains(p: Vector2, extra := 0.0) -> bool:
	if shape == "rect":
		var d := p - center
		return absf(d.x) <= half_w + extra and absf(d.y) <= half_h + extra
	var d := p - center
	var dist := d.length()
	if dist > radius + extra or dist < inner - extra:
		return false
	if shape != "arc" or dist <= extra:
		return true
	var slack := asin(clampf(extra / dist, 0.0, 1.0))
	return absf(d.angle_to(dir)) <= half_angle + slack


## Outline for debug overlays and the sprite lab.
func draw(canvas: CanvasItem, color: Color, width := 1.0) -> void:
	if shape == "rect":
		canvas.draw_rect(Rect2(center - Vector2(half_w, half_h), Vector2(half_w * 2.0, half_h * 2.0)), color, false, width)
	elif shape == "arc":
		var a0 := dir.angle() - half_angle
		var a1 := dir.angle() + half_angle
		canvas.draw_arc(center, radius, a0, a1, 24, color, width)
		canvas.draw_arc(center, maxf(inner, 0.5), a0, a1, 24, color, width)
		for a: float in [a0, a1]:
			var u := Vector2.from_angle(a)
			canvas.draw_line(center + u * inner, center + u * radius, color, width)
	else:
		canvas.draw_arc(center, radius, 0.0, TAU, 48, color, width)
		if inner > 0.5:
			canvas.draw_arc(center, inner, 0.0, TAU, 32, color, width)
