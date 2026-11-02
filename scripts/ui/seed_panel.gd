class_name SeedPanel
extends Control
## «Шизосид» (идея 16): вводишь любое слово - получаешь один и тот же забег (волны, Ларёк, события).
## Можно гоняться с другом на одном сиде. Пустое слово - случайное из списка.

signal closed
signal chosen(word: String)

const UI_BUTTONS: GDScript = preload("res://scripts/ui/ui_buttons.gd")
const RANDOM_WORDS: Array[String] = ["ВАСЯ", "ШАУРМА", "ПОМОЙКА", "КАЛОШИ", "БОМЖ", "ГОЛУБЬ", "ТАПОК", "МОРКОВСК", "СЫРОК", "ДУБАК"]

var _edit: LineEdit = null


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	z_index = 90
	var back: Panel = Panel.new()
	var box: StyleBoxFlat = StyleBoxFlat.new()
	box.bg_color = Color(0.05, 0.03, 0.04, 0.97)
	box.border_color = Color(0.2235, 1.0, 0.0784)
	box.set_border_width_all(2)
	back.add_theme_stylebox_override(&"panel", box)
	back.position = Vector2(100.0, 70.0)
	back.size = Vector2(280.0, 130.0)
	add_child(back)
	_label(tr("ШИЗОСИД"), Vector2(100.0, 78.0), 280.0, Color(0.97, 1.0, 0.0))
	_label(tr("ВВЕДИ ЛЮБОЕ СЛОВО - ПОЛУЧИШЬ ОДИН И ТОТ ЖЕ ЗАБЕГ. ДАЙ СЛОВО ДРУГУ И СРАВНИТЕ, КТО ЛОХ."), Vector2(110.0, 92.0), 260.0, Color(0.9, 0.9, 0.9))
	_edit = LineEdit.new()
	_edit.position = Vector2(140.0, 128.0)
	_edit.size = Vector2(200.0, 18.0)
	_edit.max_length = 16
	_edit.alignment = HORIZONTAL_ALIGNMENT_CENTER
	_edit.placeholder_text = tr("СЛОВО")
	_edit.text_submitted.connect(func(_t: String) -> void: _go())
	add_child(_edit)
	var go: Button = _button(tr("ПОГНАЛИ"), Vector2(112.0, 166.0), 0)
	go.pressed.connect(_go)
	var rnd: Button = _button(tr("СЛУЧАЙНОЕ"), Vector2(244.0, 166.0), 2)
	rnd.pressed.connect(func() -> void: _edit.text = RANDOM_WORDS[randi() % RANDOM_WORDS.size()])
	_edit.grab_focus()


func _go() -> void:
	var word: String = _edit.text.strip_edges().to_upper()
	if word == "":
		word = RANDOM_WORDS[randi() % RANDOM_WORDS.size()]
	chosen.emit(word)


func _input(event: InputEvent) -> void:
	if event.is_action_pressed(&"menu_back") or event.is_action_pressed(&"ui_cancel"):
		get_viewport().set_input_as_handled()
		closed.emit()


func _button(text: String, pos: Vector2, variant: int) -> Button:
	var b: Button = Button.new()
	b.text = text
	b.position = pos
	b.size = Vector2(124.0, 22.0)
	UI_BUTTONS.skin(b, variant)
	add_child(b)
	return b


func _label(text: String, pos: Vector2, width: float, color: Color) -> Label:
	var l: Label = Label.new()
	l.autowrap_mode = TextServer.AUTOWRAP_WORD
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.position = pos
	l.size = Vector2(width, 10.0)
	l.text = text
	l.add_theme_color_override(&"font_color", color)
	l.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
