class_name ModesPanel
extends Control
## Меню РЕЖИМЫ: Шизосид (Н16), Бесконечная помойка (Н32), Ларёк закрыт (Н33). W/S - выбор, пробел - ОК, Esc - назад.
## chosen(mode) - режим выбран ("seed" - открыть ввод слова, иначе id режима для GameState.mode).

signal closed
signal chosen(mode: StringName)

const UI_BUTTONS: GDScript = preload("res://scripts/ui/ui_buttons.gd")
const MODES: Array[StringName] = [&"seed", &"endless", &"closed", &"duel"]
const TITLES: Dictionary = {&"seed": "ШИЗОСИД", &"endless": "БЕСКОНЕЧНАЯ ПОМОЙКА", &"closed": "ЛАРЁК ЗАКРЫТ", &"duel": "БИТВА ГЕРОЕВ"}
const LINES: Dictionary = {
	&"seed": "ОДНО СЛОВО - ОДИН И ТОТ ЖЕ ЗАБЕГ. ГОНЯЙСЯ С ДРУГОМ.",
	&"endless": "БЕЗ КОНЦА. БОСС КАЖДЫЕ 5 ВОЛН. СКОЛЬКО ПРОТЯНЕШЬ, ЛОХ?",
	&"closed": "ЛАРЬКА НЕТ. ВСЁ ИЗ ЗАНАЧЕК И НАХОДОК ПОСЛЕ ВОЛНЫ.",
	&"duel": "ДВОЕ ПО ОЧЕРЕДИ, ОДИН СИД, 5 ВОЛН. У КОГО БОЛЬШЕ ТРУПОВ - ТОТ НЕ ЛОХ.",
}

var _buttons: Array[Button] = []
var _line: Label = null


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
	back.position = Vector2(100.0, 56.0)
	back.size = Vector2(280.0, 170.0)
	add_child(back)
	_label(tr("РЕЖИМЫ"), Vector2(100.0, 62.0), Color(0.97, 1.0, 0.0))
	for i: int in MODES.size():
		var b: Button = Button.new()
		b.text = tr(TITLES[MODES[i]]) + _best(MODES[i])
		b.position = Vector2(140.0, 76.0 + i * 22.0)
		b.size = Vector2(200.0, 20.0)
		UI_BUTTONS.skin(b, i + 1)
		b.pressed.connect(func() -> void: chosen.emit(MODES[i]))
		b.focus_entered.connect(func() -> void: _line.text = tr(LINES[MODES[i]]))
		add_child(b)
		_buttons.append(b)
	UI_BUTTONS.add_focus_arrows(_buttons)
	_line = _label("", Vector2(110.0, 168.0), Color(0.9, 0.9, 0.9))
	_line.size = Vector2(260.0, 10.0)
	_line.autowrap_mode = TextServer.AUTOWRAP_WORD
	_label(InputMode.hint(tr("W/S - ВЫБОР   ПРОБЕЛ - ОК   ESC - НАЗАД"), tr("СТРЕЛКИ - ВЫБОР   A - ОК   B - НАЗАД")), Vector2(100.0, 210.0), Color(0.55, 0.55, 0.6))
	_buttons[0].grab_focus()


func _best(mode: StringName) -> String:
	if mode == &"endless" and Profile.stat(&"mode_endless_best") > 0:
		return " (%d)" % Profile.stat(&"mode_endless_best")
	return ""


func _input(event: InputEvent) -> void:
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


func _label(text: String, pos: Vector2, color: Color) -> Label:
	var l: Label = Label.new()
	l.text = text
	l.position = pos
	l.size = Vector2(280.0, 10.0)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_color_override(&"font_color", color)
	l.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l
