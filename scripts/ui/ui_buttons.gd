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


## Опасная кнопка: красная рамка, красный текст (выход из игры).
static func skin_danger(button: Button) -> void:
	skin(button, 4)
	button.add_theme_color_override(&"font_color", Color(1.0, 0.25, 0.3))
	button.add_theme_color_override(&"font_hover_color", Color(1.0, 0.25, 0.3))
	button.add_theme_color_override(&"font_shadow_color", Color(0.4, 0.0, 0.05))


## Две стрелки по бокам кнопки, на которой фокус (покачиваются). Видно, что выберешь, даже если рамки мало.
static func add_focus_arrows(buttons: Array) -> void:
	if buttons.is_empty():
		return
	var host: Control = buttons[0].get_parent() as Control
	var tex: Texture2D = _tex("select_arrow")
	var arrows: Array[TextureRect] = []
	for turn: float in [PI * 0.5, -PI * 0.5]:
		var arrow: TextureRect = TextureRect.new()
		arrow.texture = tex
		arrow.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		arrow.mouse_filter = Control.MOUSE_FILTER_IGNORE
		arrow.pivot_offset = tex.get_size() * 0.5
		arrow.rotation = turn
		arrow.z_index = 50
		arrow.visible = false
		host.add_child(arrow)
		arrows.append(arrow)
	var state: Dictionary = {"button": null, "bob": 0.0}
	var place: Callable = func() -> void:
		var button: Button = state["button"] as Button
		if button == null:
			return
		var mid: float = button.position.y + button.size.y * 0.5 - tex.get_height() * 0.5
		var bob: float = roundf(state["bob"])
		arrows[0].position = Vector2(button.position.x - 16.0 + bob, mid)
		arrows[1].position = Vector2(button.position.x + button.size.x + 2.0 - bob, mid)
	var tween: Tween = host.create_tween().set_loops().set_pause_mode(Tween.TWEEN_PAUSE_PROCESS)
	tween.tween_method(func(v: float) -> void:
		state["bob"] = v
		place.call(), 0.0, 3.0, 0.35)
	tween.tween_method(func(v: float) -> void:
		state["bob"] = v
		place.call(), 3.0, 0.0, 0.35)
	for button: Button in buttons:
		button.focus_entered.connect(func() -> void:
			state["button"] = button
			place.call()
			for arrow: TextureRect in arrows:
				arrow.visible = true)
		button.focus_exited.connect(func() -> void:
			for arrow: TextureRect in arrows:
				arrow.visible = host.get_viewport().gui_get_focus_owner() in buttons)
		if button.has_focus():
			state["button"] = button
			place.call()
			for arrow: TextureRect in arrows:
				arrow.visible = true


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
