class_name NotesPanel
extends Control
## Н17: три записки от бомжей на мятых листках: задание, прогресс, награда костями. Esc/N - закрыть.

signal closed

const TEX: GDScript = preload("res://scripts/systems/tex.gd")


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	z_index = 120
	Quests.ensure()
	var back: Panel = Panel.new()
	var box: StyleBoxFlat = StyleBoxFlat.new()
	box.bg_color = Color(0.05, 0.04, 0.03, 0.97)
	box.border_color = Color(0.9, 0.85, 0.7)
	box.set_border_width_all(2)
	back.add_theme_stylebox_override(&"panel", box)
	back.position = Vector2(40.0, 24.0)
	back.size = Vector2(400.0, 222.0)
	add_child(back)
	_label(tr("ЗАПИСКИ ОТ БОМЖЕЙ. ВЫПОЛНИШЬ - ДАДУТ КОСТЕЙ ПСУ"), Vector2(40.0, 30.0), 400.0, Color(0.97, 1.0, 0.0))
	for i: int in Profile.quests.size():
		var q: Dictionary = Profile.quests[i]
		var y: float = 46.0 + i * 62.0
		var note: TextureRect = TextureRect.new()
		note.texture = TEX.load_tex("res://assets/ui/quest_note.png")
		note.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		note.position = Vector2(60.0 + (i % 2) * 8.0, y)
		note.scale = Vector2(3.0, 1.0)   # листок вытянут в ширину, клетка остаётся пиксельной по высоте
		note.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(note)
		_label(Quests.text(q), Vector2(82.0 + (i % 2) * 8.0, y + 10.0), 320.0, Color(0.15, 0.1, 0.1), false)
		var got: int = mini(int(q["got"]), int(q["need"]))
		_label(tr("%d / %d      НАГРАДА: %d КОСТЕЙ") % [got, int(q["need"]), int(q["reward"])], Vector2(82.0 + (i % 2) * 8.0, y + 30.0), 320.0, Color(0.55, 0.2, 0.1), false)
	_label(InputMode.hint(tr("ESC / N - НАЗАД"), tr("B - НАЗАД")), Vector2(40.0, 234.0), 400.0, Color(0.55, 0.55, 0.6))


func _input(event: InputEvent) -> void:
	var key_n: bool = event is InputEventKey and event.pressed and not event.echo and (event as InputEventKey).physical_keycode == KEY_N
	if key_n or event.is_action_pressed(&"menu_back") or event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		closed.emit()


func _label(text: String, pos: Vector2, width: float, color: Color, shadow: bool = true) -> Label:
	var l: Label = Label.new()
	l.text = text
	l.position = pos
	l.size = Vector2(width, 10.0)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER if shadow else HORIZONTAL_ALIGNMENT_LEFT
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	l.add_theme_color_override(&"font_color", color)
	if shadow:
		l.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	else:   # надпись на бумаге: без обводки и тени темы
		l.add_theme_constant_override(&"outline_size", 0)
		l.add_theme_color_override(&"font_shadow_color", Color(0, 0, 0, 0))
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
