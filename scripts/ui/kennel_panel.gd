class_name KennelPanel
extends Control
## Н16: будка пса на кладбище. Пёс крупно в своей шмотке, кличка, уровень, кости.
## Кнопки: ПОКОРМИТЬ (кости), ШМОТКА < >, В ЗАБЕГ ДА/НЕТ, НАЗАД. Если пёс без клички - сначала ввод клички.

signal closed

const UI_BUTTONS: GDScript = preload("res://scripts/ui/ui_buttons.gd")
const TEX: GDScript = preload("res://scripts/systems/tex.gd")

var _dog: Sprite2D
var _wear: Sprite2D
var _info: Label
var _buttons: Array[Button] = []
var _name_edit: LineEdit = null
var _anim: float = 0.0


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	z_index = 120
	var back: Panel = Panel.new()
	var box: StyleBoxFlat = StyleBoxFlat.new()
	box.bg_color = Color(0.06, 0.04, 0.03, 0.98)
	box.border_color = Color(1.0, 0.75, 0.35)
	box.set_border_width_all(2)
	back.add_theme_stylebox_override(&"panel", box)
	back.position = Vector2(70.0, 30.0)
	back.size = Vector2(340.0, 210.0)
	add_child(back)
	var kennel: TextureRect = TextureRect.new()
	kennel.texture = TEX.load_tex("res://assets/ui/kennel.png")
	kennel.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	kennel.position = Vector2(84.0, 70.0)
	kennel.scale = Vector2(2.0, 2.0)
	add_child(kennel)
	_dog = Sprite2D.new()
	_dog.texture = TEX.load_tex("res://assets/sprites/buddy_dog.png")
	_dog.hframes = 6
	_dog.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_dog.scale = Vector2(3.0, 3.0)
	_dog.position = Vector2(230.0, 150.0)
	add_child(_dog)
	_wear = Sprite2D.new()
	_wear.hframes = 6
	_wear.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_wear.scale = _dog.scale
	_wear.position = _dog.position
	add_child(_wear)
	_info = _label("", Vector2(80.0, 38.0), 320.0, Color(1.0, 0.75, 0.35))
	if Profile.dog_pending_name or Profile.dog_name == "":
		_ask_name()
	else:
		_build_buttons()
	_refresh()


func _ask_name() -> void:
	_label(tr("ТЫ ПОДОБРАЛ ПСА. КАК НАЗОВЁШЬ?"), Vector2(80.0, 54.0), 320.0, Color.WHITE)
	_name_edit = LineEdit.new()
	_name_edit.position = Vector2(262.0, 80.0)
	_name_edit.size = Vector2(110.0, 18.0)
	_name_edit.max_length = 12
	_name_edit.alignment = HORIZONTAL_ALIGNMENT_CENTER
	_name_edit.text = Balance.DOG_NAMES[randi() % Balance.DOG_NAMES.size()]
	_name_edit.text_submitted.connect(func(_t: String) -> void: _save_name())
	add_child(_name_edit)
	var rnd: Button = _button(tr("СЛУЧАЙНАЯ"), Vector2(262.0, 104.0))
	rnd.pressed.connect(func() -> void: _name_edit.text = Balance.DOG_NAMES[randi() % Balance.DOG_NAMES.size()])
	var ok: Button = _button(tr("ГОТОВО"), Vector2(262.0, 128.0))
	ok.pressed.connect(_save_name)
	_name_edit.grab_focus()


func _save_name() -> void:
	var name: String = _name_edit.text.strip_edges().to_upper()
	Profile.dog_name = name if name != "" else Balance.DOG_NAMES[0]
	Profile.dog_pending_name = false
	Profile.save()
	closed.emit()


func _build_buttons() -> void:
	var feed: Button = _button("", Vector2(262.0, 60.0))
	feed.pressed.connect(func() -> void:
		if Profile.feed_dog():
			HitFx.burst(get_tree(), _dog.global_position, Color(0.95, 0.92, 0.8), 12, 60.0, 2.0, 0.5, true)
		_refresh())
	var wear: Button = _button("", Vector2(262.0, 84.0))
	wear.pressed.connect(func() -> void:
		var options: Array = [""] + Profile.dog_wardrobe
		Profile.dog_wear = options[(options.find(Profile.dog_wear) + 1) % options.size()]
		Profile.save()
		_refresh())
	var take: Button = _button("", Vector2(262.0, 108.0))
	take.pressed.connect(func() -> void:
		Profile.dog_enabled = not Profile.dog_enabled
		Profile.save()
		_refresh())
	var back: Button = _button(tr("НАЗАД"), Vector2(262.0, 132.0))
	back.pressed.connect(func() -> void: closed.emit())
	UI_BUTTONS.add_focus_arrows(_buttons)
	_buttons[0].grab_focus()


func _refresh() -> void:
	var cost: int = Profile.dog_feed_cost()
	_info.text = tr("%s   УР. %d/%d   КОСТИ: %d") % [Profile.dog_name if Profile.dog_name != "" else "?", Profile.dog_level, Balance.DOG_MAX_LEVEL, Profile.bones]
	_wear.visible = Profile.dog_wear != ""
	if _wear.visible:
		_wear.texture = TEX.load_tex("res://assets/sprites/buddy_wear_%s.png" % Profile.dog_wear)
	if _buttons.size() >= 3 and _name_edit == null:
		_buttons[0].text = tr("ПОКОРМИТЬ: %d КОСТЕЙ") % cost if cost > 0 else tr("СЫТ, УР. МАКС")
		_buttons[0].disabled = cost == 0 or Profile.bones < cost
		_buttons[1].text = tr("ШМОТКА: %s") % (tr(Balance.DOG_WEAR_NAMES[Profile.dog_wear]) if Profile.dog_wear != "" else tr("ГОЛЫЙ")) if not Profile.dog_wardrobe.is_empty() else tr("ШМОТОК НЕТ (ДАЮТ ЗА ПОБЕДЫ)")
		_buttons[2].text = tr("В ЗАБЕГ: ДА") if Profile.dog_enabled else tr("В ЗАБЕГ: НЕТ")


func _process(delta: float) -> void:
	_anim += delta
	_dog.frame = 4 + int(_anim * 2.0) % 2
	_wear.frame = _dog.frame


func _input(event: InputEvent) -> void:
	if _name_edit != null:
		return   # пока вводят кличку - клавиши для поля
	if event.is_action_pressed(&"menu_back") or event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		closed.emit()
		return
	var step: int = 0
	if event.is_action_pressed(&"move_up") or event.is_action_pressed(&"ui_up"):
		step = -1
	elif event.is_action_pressed(&"move_down") or event.is_action_pressed(&"ui_down"):
		step = 1
	if step != 0:
		get_viewport().set_input_as_handled()
		var at: int = 0
		for i: int in _buttons.size():
			if _buttons[i].has_focus():
				at = i
		_buttons[posmod(at + step, _buttons.size())].grab_focus()


func _button(text: String, pos: Vector2) -> Button:
	var b: Button = Button.new()
	b.text = text
	b.position = pos
	b.size = Vector2(140.0, 20.0)
	UI_BUTTONS.skin(b, _buttons.size() + 1)
	add_child(b)
	_buttons.append(b)
	return b


func _label(text: String, pos: Vector2, width: float, color: Color) -> Label:
	var l: Label = Label.new()
	l.text = text
	l.position = pos
	l.size = Vector2(width, 10.0)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	l.add_theme_color_override(&"font_color", color)
	l.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
