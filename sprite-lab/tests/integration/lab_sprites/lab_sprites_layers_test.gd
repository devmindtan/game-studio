extends RefCounted
## Integration: every layered sprite in the lab composes (layers + outline in
## Godot) to exactly its <name>_strip.png, so equipment swaps line up in games.

const SPRITES := "res://sprites"

var failures: Array[String] = []


func _check(cond: bool, msg: String) -> void:
	if not cond:
		failures.append(msg)


func test_layered_sprites_compose_to_their_strip() -> void:
	var found := 0
	for n in DirAccess.get_directories_at(SPRITES):
		var sheet := SpriteSheet.load_dir(SPRITES.path_join(n), n)
		if sheet == null or sheet.layer_names().is_empty():
			continue
		found += 1
		var want := sheet.texture.get_image()
		want.convert(Image.FORMAT_RGBA8)
		sheet.compose_layers()
		var got := sheet.texture.get_image()
		var diff := _first_visible_diff(got, want)
		_check(diff == "", "%s: composed layers differ from %s_strip.png %s" % [n, n, diff])
	_check(found > 0, "no layered sprite found (swordsman should be)")


## "" when both images look the same: equal alpha everywhere and equal colour
## where visible (Godot's import may change the colour of invisible pixels).
func _first_visible_diff(a: Image, b: Image) -> String:
	if a.get_size() != b.get_size():
		return "size %s vs %s" % [a.get_size(), b.get_size()]
	var da := a.get_data()
	var db := b.get_data()
	for i in range(0, da.size(), 4):
		if da[i + 3] != db[i + 3] or (da[i + 3] > 0 and (da[i] != db[i] or da[i + 1] != db[i + 1] or da[i + 2] != db[i + 2])):
			var px := i / 4
			return "at (%d, %d): %s vs %s" % [px % a.get_width(), px / a.get_width(),
				[da[i], da[i + 1], da[i + 2], da[i + 3]], [db[i], db[i + 1], db[i + 2], db[i + 3]]]
	return ""


func test_override_hides_a_layer() -> void:
	var sheet := SpriteSheet.load_dir(SPRITES.path_join("swordsman"), "swordsman")
	var before := sheet.texture.get_image()
	sheet.compose_layers({"hair": null})
	var after := sheet.texture.get_image()
	_check(before.get_data() != after.get_data(), "hiding the hair layer must change the picture")
