class_name WeaponBook
extends Control
## Книга оружия на кладбище: всё оружие игры, закрытое тёмное с условием открытия и прогрессом.

const COLUMNS: int = 6
const CELL_W: float = 76.0
const CELL_H_MAX: float = 70.0
const TOP: float = 24.0
const BOTTOM: float = 246.0   # ниже - подсказка «назад»
const YELLOW: Color = Color(0.968627, 1.0, 0.0)
const GREEN: Color = Color(0.2235, 1.0, 0.0784)
const GREY: Color = Color(0.55, 0.55, 0.6)
const RED: Color = Color(1.0, 0.1, 0.2)


var _cell_h: float = CELL_H_MAX


## Книга-коллекция: вкладки (Q/E, LB/RB). 0 - оружие, дальше сетки значков с курсором (стрелки).
const TABS: Array[String] = ["ОРУЖИЕ", "ХЛАМ", "ЗЛОВОННОЕ", "КОМБО", "МОДИФИКАТОРЫ"]
const GRID_COLS: int = 12
const GRID_STEP: float = 36.0
const CURSOR: Texture2D = preload("res://assets/ui/book_cursor.png")

var _tab: int = 0
var _page: Control = null
var _grid_ids: Array[StringName] = []
var _cursor: int = 0
var _cursor_rect: TextureRect = null
var _info: Label = null
var _info_sub: Label = null


func _ready() -> void:
	size = Vector2(480.0, 270.0)
	mouse_filter = Control.MOUSE_FILTER_STOP
	z_index = 100
	var back: ColorRect = ColorRect.new()
	back.color = Color(0.03, 0.02, 0.04, 1.0)
	back.size = Vector2(480.0, 270.0)
	add_child(back)
	_show_tab(0)


func _input(event: InputEvent) -> void:
	var step: int = 0
	if event is InputEventKey and event.pressed and not event.echo:
		if (event as InputEventKey).physical_keycode == KEY_Q:
			step = -1
		elif (event as InputEventKey).physical_keycode == KEY_E:
			step = 1
	elif event is InputEventJoypadButton and event.pressed:
		if (event as InputEventJoypadButton).button_index == JOY_BUTTON_LEFT_SHOULDER:
			step = -1
		elif (event as InputEventJoypadButton).button_index == JOY_BUTTON_RIGHT_SHOULDER:
			step = 1
	if step != 0:
		get_viewport().set_input_as_handled()
		_show_tab(posmod(_tab + step, TABS.size()))
		return
	if _tab == 0 or _grid_ids.is_empty():
		return
	var move: int = 0
	if event.is_action_pressed(&"ui_left") or event.is_action_pressed(&"move_left"):
		move = -1
	elif event.is_action_pressed(&"ui_right") or event.is_action_pressed(&"move_right"):
		move = 1
	elif event.is_action_pressed(&"ui_up") or event.is_action_pressed(&"move_up"):
		move = -GRID_COLS
	elif event.is_action_pressed(&"ui_down") or event.is_action_pressed(&"move_down"):
		move = GRID_COLS
	if move != 0:
		get_viewport().set_input_as_handled()
		_cursor = clampi(_cursor + move, 0, _grid_ids.size() - 1)
		_update_cursor()


func _show_tab(tab: int) -> void:
	_tab = tab
	if _page != null:
		_page.queue_free()
	_page = Control.new()
	_page.size = size
	_page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_page)
	var tab_w: float = 480.0 / TABS.size()
	for i: int in TABS.size():   # текущая вкладка - жёлтая, остальные серые
		_text(tr(TABS[i]), Vector2(i * tab_w, 4.0), tab_w, YELLOW if i == _tab else GREY, HORIZONTAL_ALIGNMENT_CENTER)
	_text(InputMode.hint(tr("Q / E - ВКЛАДКИ   СТРЕЛКИ - ЛИСТАТЬ   TAB / ESC - НАЗАД"), tr("LB / RB - ВКЛАДКИ   B - НАЗАД")), Vector2(0.0, 255.0), 480.0, GREY, HORIZONTAL_ALIGNMENT_CENTER)
	if _tab == 0:
		_weapons_page()
	else:
		_grid_page()


func _weapons_page() -> void:
	var ids: Array[StringName] = []
	for perk_id: StringName in PerkLibrary.WEAPON_PERKS:
		ids.append(StringName(String(perk_id).trim_prefix("w_")))
	var rows: int = ceili(float(ids.size()) / float(COLUMNS))
	_cell_h = minf(CELL_H_MAX, (BOTTOM - TOP) / float(maxi(rows, 1)))   # ряды сжимаются, чтобы всё влезло в экран
	for i: int in ids.size():
		_cell(ids[i], Vector2(12.0 + (i % COLUMNS) * CELL_W, TOP + floorf(float(i) / COLUMNS) * _cell_h))


## id для вкладки сетки (хлам / зловонное / комбо / модификаторы).
func _tab_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	if _tab == 4:
		for m: StringName in Balance.WAVE_MODS:
			out.append(m)
		return out
	for id: StringName in Balance.ITEMS:
		if id == ItemLibrary.SHOES:
			continue
		var cursed: bool = ItemLibrary.is_cursed(id)
		var combo: bool = ItemLibrary.is_combo(id)
		if (_tab == 1 and not cursed and not combo) or (_tab == 2 and cursed) or (_tab == 3 and combo):
			out.append(id)
	return out


static func is_found(tab: int, id: StringName) -> bool:
	match tab:
		3:
			return id in Profile.combos_found
		4:
			return id in Profile.mods_seen
	return Profile.stat(StringName("found_" + String(id))) > 0


func _grid_page() -> void:
	_grid_ids = _tab_ids()
	_cursor = clampi(_cursor, 0, maxi(_grid_ids.size() - 1, 0))
	var found: int = 0
	var rows: int = ceili(float(_grid_ids.size()) / float(GRID_COLS))
	var step_y: float = minf(GRID_STEP, 150.0 / float(maxi(rows, 1)))
	for i: int in _grid_ids.size():
		var id: StringName = _grid_ids[i]
		var open: bool = is_found(_tab, id)
		found += 1 if open else 0
		var icon: TextureRect = TextureRect.new()
		icon.texture = TEX_LOAD.load_tex("res://assets/ui/mod_%s_s.png" % id) if _tab == 4 else ItemLibrary.icon_small(id)
		icon.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		icon.position = Vector2(30.0 + (i % GRID_COLS) * GRID_STEP, 34.0 + floorf(float(i) / GRID_COLS) * step_y).round()
		if not open:
			icon.material = _silhouette()   # неоткрытое - серый силуэт формы
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_page.add_child(icon)
	_text(tr("ОТКРЫТО %d / %d") % [found, _grid_ids.size()], Vector2(0.0, 18.0), 480.0, GREEN, HORIZONTAL_ALIGNMENT_CENTER)
	_cursor_rect = TextureRect.new()
	_cursor_rect.texture = CURSOR
	_cursor_rect.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_cursor_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_page.add_child(_cursor_rect)
	_info = _text("", Vector2(20.0, 192.0), 440.0, YELLOW, HORIZONTAL_ALIGNMENT_CENTER)
	_info.size.y = 16.0
	_info_sub = _text("", Vector2(20.0, 210.0), 440.0, Color.WHITE, HORIZONTAL_ALIGNMENT_CENTER)
	_info_sub.size.y = 30.0   # длинное описание в 2-3 строки
	_update_cursor()


func _update_cursor() -> void:
	if _grid_ids.is_empty():
		return
	var rows: int = ceili(float(_grid_ids.size()) / float(GRID_COLS))
	var step_y: float = minf(GRID_STEP, 150.0 / float(maxi(rows, 1)))
	_cursor_rect.position = Vector2(30.0 + (_cursor % GRID_COLS) * GRID_STEP - 4.0, 34.0 + floorf(float(_cursor) / GRID_COLS) * step_y - 4.0).round()
	var id: StringName = _grid_ids[_cursor]
	if not is_found(_tab, id):
		_info.text = "???"
		_info_sub.text = tr(["", "КУПИ В ЛАРЬКЕ ИЛИ НАЙДИ В ЗАНАЧКЕ", "БЕРИ ЗЛОВОННОЕ В ЛАРЬКЕ, ЕСЛИ НЕ ТРУС", "СОБЕРИ ДВА ПРЕДМЕТА, КОТОРЫЕ СЛИПНУТСЯ", "НАСТУПИ В СВЕТЯЩУЮСЯ КУЧУ"][_tab])
		return
	if _tab == 4:
		_info.text = tr(Balance.WAVE_MOD_DATA[id]["title"])
		_info_sub.text = tr(Balance.WAVE_MOD_DATA[id]["line"])
	else:
		_info.text = ItemLibrary.title(id)
		_info_sub.text = ItemLibrary.description(id).replace("\n", "   ")


var _sil_mat: ShaderMaterial = null


## Материал-силуэт: форма значка одним серым цветом (видно, что там что-то есть, но не что).
func _silhouette() -> ShaderMaterial:
	if _sil_mat == null:
		var sh: Shader = Shader.new()
		sh.code = "shader_type canvas_item;\nvoid fragment() { vec4 c = texture(TEXTURE, UV); COLOR = vec4(0.28, 0.25, 0.34, c.a); }"
		_sil_mat = ShaderMaterial.new()
		_sil_mat.shader = sh
	return _sil_mat


const TEX_LOAD: GDScript = preload("res://scripts/systems/tex.gd")


func _cell(id: StringName, pos: Vector2) -> void:
	var open: bool = Profile.is_weapon_unlocked(id)
	var icon: TextureRect = TextureRect.new()
	icon.texture = PerkLibrary.icon_small(StringName("w_" + String(id)))
	icon.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	icon.position = pos + Vector2((CELL_W - 16.0) * 0.5 - 4.0, 0.0)
	icon.modulate = Color.WHITE if open else Color(0.15, 0.15, 0.2)
	_page.add_child(icon)
	var title: String = PerkLibrary.title(StringName("w_" + String(id))) if open else "???"
	_text(title, pos + Vector2(0.0, 17.0), CELL_W - 8.0, Color.WHITE if open else GREY, HORIZONTAL_ALIGNMENT_CENTER)
	if not open:   # открытое видно по белому имени - лишняя строка «ОТКРЫТО» только толкалась
		var rule: Dictionary = Balance.WEAPON_UNLOCK[id]
		_text("%s\n%d/%d" % [_rule_text(rule), mini(Profile.counter(rule["kind"]), rule["need"]), rule["need"]], pos + Vector2(0.0, 29.0), CELL_W - 8.0, RED, HORIZONTAL_ALIGNMENT_CENTER)


func _rule_text(rule: Dictionary) -> String:
	match rule["kind"]:
		&"kills":
			return "УБЕЙ ВРАГОВ"
		&"coins":
			return "СОБЕРИ ГОВНА"
		&"deaths":
			return "СДОХНИ"
		&"wins":
			return "ПРОЙДИ ИГРУ"
	return ""


func _text(text: String, pos: Vector2, width: float, color: Color, align: HorizontalAlignment) -> Label:
	var label: Label = Label.new()
	label.autowrap_mode = TextServer.AUTOWRAP_WORD   # слова не рвём посередине
	label.position = pos
	label.size = Vector2(width, 10.0)
	label.horizontal_alignment = align
	label.text = text
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override(&"font_color", color)
	label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	label.add_theme_constant_override(&"shadow_offset_x", 1)
	label.add_theme_constant_override(&"shadow_offset_y", 1)
	(_page if _page != null else self).add_child(label)
	return label
