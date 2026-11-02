class_name SettingsPanel
extends Control
## Настройки (из главного меню и паузы): ЗВУКИ / МУЗЫКА (громкость шагами), ПОЛНЫЙ ЭКРАН, ТРЯСКА ЭКРАНА, НАЗАД.
## W/S (крестовина) - строка, A/D - менять, пробел/A - переключить, Esc/B - назад. Сохраняет в Settings.

signal closed

const UI_BUTTONS: GDScript = preload("res://scripts/ui/ui_buttons.gd")
const STEP: float = 0.1
const YELLOW: Color = Color(0.968627, 1.0, 0.0)

var _rows: Array[Button] = []


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	process_mode = Node.PROCESS_MODE_ALWAYS
	z_index = 110
	var back: Panel = Panel.new()   # плотная плашка: под ней ничего не просвечивает
	var box: StyleBoxFlat = StyleBoxFlat.new()
	box.bg_color = Color(0.05, 0.02, 0.06, 0.97)
	box.border_color = Color(0.2235, 1.0, 0.0784)
	box.set_border_width_all(2)
	back.add_theme_stylebox_override(&"panel", box)
	back.position = Vector2(110.0, 50.0)
	back.size = Vector2(260.0, 170.0)
	add_child(back)
	var title: Label = Label.new()
	title.text = "НАСТРОЙКИ"
	title.position = Vector2(110.0, 58.0)
	title.size = Vector2(260.0, 12.0)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_color_override(&"font_color", YELLOW)
	add_child(title)
	for i: int in 5:
		var b: Button = Button.new()
		b.position = Vector2(140.0, 80.0 + i * 24.0)
		b.size = Vector2(200.0, 20.0)
		UI_BUTTONS.skin(b, i)
		b.pressed.connect(_on_press.bind(i))
		add_child(b)
		_rows.append(b)
	UI_BUTTONS.add_focus_arrows(_rows)
	var hint: Label = Label.new()
	hint.text = InputMode.hint("W/S - СТРОКА   A/D - МЕНЯТЬ   ESC - НАЗАД", "КРЕСТ - СТРОКА/МЕНЯТЬ   B - НАЗАД")
	hint.position = Vector2(110.0, 204.0)
	hint.size = Vector2(260.0, 10.0)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.add_theme_color_override(&"font_color", Color(0.55, 0.55, 0.6))
	add_child(hint)
	_refresh()
	_rows[0].grab_focus()


func _refresh() -> void:
	_rows[0].text = "ЗВУКИ:  -  %d%%  +" % roundi(Settings.sfx_volume * 100.0)
	_rows[1].text = "МУЗЫКА:  -  %d%%  +" % roundi(Settings.music_volume * 100.0)
	_rows[2].text = "ПОЛНЫЙ ЭКРАН: %s" % ("ДА" if Settings.fullscreen else "НЕТ")
	_rows[3].text = "ТРЯСКА ЭКРАНА: %s" % ("ДА" if Settings.screen_shake else "НЕТ")
	_rows[4].text = "НАЗАД"


func _focused() -> int:
	for i: int in _rows.size():
		if _rows[i].has_focus():
			return i
	return 0


func _change(row: int, dir: int) -> void:
	match row:
		0:
			Settings.sfx_volume = clampf(snappedf(Settings.sfx_volume + STEP * dir, STEP), 0.0, 1.0)
			AudioManager.play_sfx(&"pickup", 0.0)
		1:
			Settings.music_volume = clampf(snappedf(Settings.music_volume + STEP * dir, STEP), 0.0, 1.0)
		2:
			Settings.fullscreen = not Settings.fullscreen
		3:
			Settings.screen_shake = not Settings.screen_shake
	Settings.save()
	_refresh()


func _on_press(row: int) -> void:
	if row == 4:
		closed.emit()
	else:
		_change(row, 1 if row < 2 else 0)


func _input(event: InputEvent) -> void:
	var row: int = _focused()
	if event.is_action_pressed(&"menu_back") or event.is_action_pressed(&"pause"):
		get_viewport().set_input_as_handled()
		closed.emit()
	elif event.is_action_pressed(&"move_up") or event.is_action_pressed(&"ui_up"):
		get_viewport().set_input_as_handled()
		_rows[posmod(row - 1, _rows.size())].grab_focus()
	elif event.is_action_pressed(&"move_down") or event.is_action_pressed(&"ui_down"):
		get_viewport().set_input_as_handled()
		_rows[posmod(row + 1, _rows.size())].grab_focus()
	elif (event.is_action_pressed(&"move_left") or event.is_action_pressed(&"ui_left")) and row < 4:
		get_viewport().set_input_as_handled()
		_change(row, -1)
	elif (event.is_action_pressed(&"move_right") or event.is_action_pressed(&"ui_right")) and row < 4:
		get_viewport().set_input_as_handled()
		_change(row, 1)
