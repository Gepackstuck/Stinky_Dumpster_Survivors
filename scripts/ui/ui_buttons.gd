extends RefCounted
## Свои рамки кнопок: у каждой кнопки меню свой вариант, а не один размноженный шаблон.

const VARIANTS: int = 6
static var _cache: Dictionary = {}


## Одеть кнопку в рамку варианта `variant` (по кругу) и фирменные цвета текста.
static func skin(button: Button, variant: int) -> void:
	var index: int = posmod(variant, VARIANTS)
	var normal: StyleBoxTexture = StyleBoxTexture.new()
	normal.texture = _tex("button_v%d" % index)
	var hover: StyleBoxTexture = StyleBoxTexture.new()
	hover.texture = _tex("button_v%d_hover" % index)
	button.add_theme_stylebox_override(&"normal", normal)
	button.add_theme_stylebox_override(&"hover", hover)
	button.add_theme_stylebox_override(&"pressed", hover)
	button.add_theme_stylebox_override(&"focus", hover)
	button.add_theme_color_override(&"font_color", Color(0.968627, 1.0, 0.0))
	for key: StringName in [&"font_hover_color", &"font_focus_color", &"font_pressed_color"]:
		button.add_theme_color_override(key, Color.WHITE)
	button.add_theme_color_override(&"font_shadow_color", Color(1.0, 0.0627451, 0.941176))


static func _tex(name: String) -> Texture2D:
	if _cache.has(name):
		return _cache[name]
	var path: String = "res://assets/ui/%s.png" % name
	var texture: Texture2D = null
	if ResourceLoader.exists(path):
		texture = load(path) as Texture2D
	else:
		var image: Image = Image.load_from_file(ProjectSettings.globalize_path(path))
		texture = ImageTexture.create_from_image(image) if image != null else null
	_cache[name] = texture
	return texture
