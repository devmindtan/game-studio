class_name LpcCharacter
extends AnimatedSprite2D
## Plays LPC character animations by action and facing.
##
## Expects a SpriteFrames built by addons/gamekit/lpc/build_sprite_frames.gd (gamekit sprites),
## whose animations are named "<action>_<facing>" (walk_down) or "<action>"
## for one-direction animations (hurt, climb).
##
## Example:
##   var hero := LpcCharacter.new()
##   hero.sprite_frames = load("res://assets/sprites/characters/sample_hero/sample_hero_frames.tres")
##   hero.face(velocity)
##   hero.play_action(&"walk")

const FACINGS: Array[StringName] = [&"up", &"left", &"down", &"right"]

## Current facing: one of FACINGS.
@export var facing: StringName = &"down"


func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST  # crisp pixel art


## Facing for a movement vector; [param fallback] when the vector is ~zero.
## Horizontal wins only when it is strictly larger, so diagonals face up/down.
static func facing_from_vector(v: Vector2, fallback: StringName = &"down") -> StringName:
	if v.length_squared() < 0.0001:
		return fallback
	if absf(v.x) > absf(v.y):
		return &"right" if v.x > 0.0 else &"left"
	return &"down" if v.y > 0.0 else &"up"


## Animation name for an action and facing, e.g. ("walk", "left") -> "walk_left".
static func animation_name(action: StringName, p_facing: StringName) -> StringName:
	return StringName("%s_%s" % [action, p_facing])


## Turns to face [param v] (unchanged when v is ~zero).
func face(v: Vector2) -> void:
	facing = facing_from_vector(v, facing)


## Plays [param action] in the current facing, falling back to the
## one-direction animation of that name. Returns false if neither exists.
func play_action(action: StringName) -> bool:
	if sprite_frames == null:
		return false
	var directed := animation_name(action, facing)
	if sprite_frames.has_animation(directed):
		if animation != directed or not is_playing():
			play(directed)
		return true
	if sprite_frames.has_animation(action):
		if animation != action or not is_playing():
			play(action)
		return true
	return false
