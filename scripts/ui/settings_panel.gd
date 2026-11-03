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
	title.text = tr("SET_TITLE")
	title.position = Vector2(110.0, 58.0)
	title.size = Vector2(260.0, 12.0)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_color_override(&"font_color", YELLOW)
	add_child(title)
	for i: int in 8:
		var b: Button = Button.new()
		b.position = Vector2(140.0, 72.0 + i * 17.0)
		b.size = Vector2(200.0, 16.0)
		UI_BUTTONS.skin(b, i)
		b.pressed.connect(_on_press.bind(i))
		add_child(b)
		_rows.append(b)
	UI_BUTTONS.add_focus_arrows(_rows)
	var hint: Label = Label.new()
	hint.text = InputMode.hint(tr("SET_HINT"), "СТРЕЛКИ - СТРОКА/МЕНЯТЬ   B - НАЗАД")
	hint.position = Vector2(110.0, 209.0)
	hint.size = Vector2(260.0, 10.0)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	hint.add_theme_color_override(&"font_color", Color(0.55, 0.55, 0.6))
	add_child(hint)
	_refresh()
	_rows[0].grab_focus()


func _refresh() -> void:
	_rows[0].text = "%s:  -  %d%%  +" % [tr("SET_SFX"), roundi(Settings.sfx_volume * 100.0)]
	_rows[1].text = "%s:  -  %d%%  +" % [tr("SET_MUSIC"), roundi(Settings.music_volume * 100.0)]
	_rows[2].text = "%s: %s" % [tr("SET_FULLSCREEN"), tr("SET_YES") if Settings.fullscreen else tr("SET_NO")]
	_rows[3].text = "%s: %s" % [tr("SET_SHAKE"), tr("SET_YES") if Settings.screen_shake else tr("SET_NO")]
	_rows[4].text = "%s: %s" % [tr("SET_LANGUAGE"), Settings.language.to_upper()]
	_rows[5].text = "%s: %s" % [tr("SET_VICTORY"), tr("SET_YES") if Settings.victory_cutscene else tr("SET_NO")]
	_rows[6].text = "%s: %s" % [tr("SET_DMG_NUMBERS"), tr(["SET_NO", "SET_CRITS", "SET_ALL"][Settings.damage_numbers])]
	_rows[7].text = tr("SET_BACK")


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
		4:
			var at: int = Settings.LANGUAGES.find(Settings.language)
			Settings.language = Settings.LANGUAGES[posmod(at + (dir if dir != 0 else 1), Settings.LANGUAGES.size())]
		5:
			Settings.victory_cutscene = not Settings.victory_cutscene
		6:
			Settings.damage_numbers = posmod(Settings.damage_numbers + (dir if dir != 0 else 1), 3)
	Settings.save()
	_refresh()


func _on_press(row: int) -> void:
	if row == 7:
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
	elif (event.is_action_pressed(&"move_left") or event.is_action_pressed(&"ui_left")) and row < 7:
		get_viewport().set_input_as_handled()
		_change(row, -1)
	elif (event.is_action_pressed(&"move_right") or event.is_action_pressed(&"ui_right")) and row < 7:
		get_viewport().set_input_as_handled()
		_change(row, 1)
