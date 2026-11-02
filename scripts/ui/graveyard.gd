class_name Graveyard
extends Control
## Кладбище: экран выбора персонажа. Закрытый герой - закопанная могила с именем на плите,
## открытый сидит в раскопанной яме. A/D или мышь - выбор, пробел/клик - на помойку.

const UI_BUTTONS: GDScript = preload("res://scripts/ui/ui_buttons.gd")
const BOOK: GDScript = preload("res://scripts/ui/weapon_book.gd")
const MENU_SCENE: String = "res://scenes/ui/main_menu.tscn"
const GAME_SCENE: String = "res://scenes/levels/main.tscn"
const SCREEN: Vector2 = Vector2(480.0, 270.0)
const GRID_TOP: float = 18.0   # сетка могил как в Brotato: все перед глазами
const GRID_MAX_W: float = 450.0
const GRID_MAX_H: float = 134.0
const GRAVE_W: float = 48.0
const GRAVE_H: float = 56.0
const ARROW_H: float = 16.0   # место под подпись и стрелку между рядами
const GRAVE_OPEN: Texture2D = preload("res://assets/ui/grave_open.png")
const ARROW: Texture2D = preload("res://assets/ui/select_arrow.png")
const GATE_POS: Vector2 = Vector2(240.0, 252.0)   # ворота на арену: внизу по центру (арена под кладбищем в бесконечной петле)
var _gate_tex: Texture2D = CharacterLibrary.load_texture("res://assets/sprites/gate.png")
const WALK_SPEED: float = 110.0   # пикселей в секунду по дорожке между могилами
const AISLE: float = 30.0   # проход по центру сетки: по нему герой идёт к воротам и обратно
const GROUND: Texture2D = preload("res://assets/sprites/ground_tile.png")
const GRAVE_CLOSED: Texture2D = preload("res://assets/ui/grave_closed.png")
const PLAYER_TEX: Texture2D = preload("res://assets/sprites/player.png")
const YELLOW: Color = Color(0.968627, 1.0, 0.0)
const PINK: Color = Color(1.0, 0.0627451, 0.941176)
const GREEN: Color = Color(0.2235, 1.0, 0.0784)
const RED: Color = Color(1.0, 0.1, 0.2)
const WHITE: Color = Color(1.0, 1.0, 1.0)
const GREY: Color = Color(0.55, 0.55, 0.6)

## ТОЛЬКО ДЛЯ ТЕСТА (tools/smoke/graves_test): добить список героев повторами до этого числа. В игре всегда 0.
static var test_fill: int = 0
var _ids: Array[StringName] = []
var _graves: Array[Control] = []
var _sitters: Array[Node2D] = []
var _selected: int = 0
var _fresh: Array[StringName] = []
var _time: float = 0.0
var _scale: float = 1.0
var _picker: Control = null          # выбор уровня опасности (после выбора героя, если открыт хоть один)
var _pick_danger: int = 0
var _pick_skulls: Array[TextureRect] = []
var _pick_title: Label = null
var _pick_text: Label = null
var _leaves: Array[TextureRect] = []
var _captions: Array[Label] = []
var _cols: int = 8
var _arrow: TextureRect
var _preview: Sprite2D
var _title: Label
var _tagline: Label
var _dash_label: Label   # рывок героя
var _plus: Label
var _minus: Label
var _weapon: Label
var _status: Label
var _hint: Label
var _leaving: bool = false
var _book: Control = null
var _walker: Node2D = null
var _dossier: bool = false
var _lore: Label = null
var _walk_time: float = 0.0
var _path: PackedVector2Array = PackedVector2Array()
var _path_len: float = 0.0
var _info_nodes: Array[CanvasItem] = []
var _arriving: bool = false
var _speech: Label = null
var _speech_left: float = 0.0


func _ready() -> void:
	_ids = CharacterLibrary.ids().duplicate()
	var base_count: int = _ids.size()
	while _ids.size() < test_fill:
		_ids.append(_ids[_ids.size() % base_count])
	_fresh = Profile.fresh_unlocks()
	_selected = maxi(_ids.find(Profile.selected), 0)
	if not Profile.is_unlocked(_ids[_selected]):
		_selected = 0
	_build_background()
	_build_header()
	_layout_grid()
	for i: int in _ids.size():
		_build_grave(i)
	_build_panel()
	_arrow = TextureRect.new()
	_arrow.texture = ARROW
	_arrow.flip_v = true
	_arrow.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_arrow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_arrow)
	_build_menu_button()
	_refresh()
	Profile.announce(_fresh)
	if SceneFlow.from_arena and Profile.is_unlocked(_ids[_selected]):
		SceneFlow.from_arena = false
		_start_arrival.call_deferred()


## Герой вернулся с арены: выходит из ворот и идёт к своей яме.
func _start_arrival() -> void:
	_leaving = true
	_arriving = true
	_walker = _sitters[_selected]
	var rest: Vector2 = _rest_pos(_selected)
	var lane: float = _graves[_selected].position.y - ARROW_H * 0.5   # дорожка над рядом могилы
	_begin_path(PackedVector2Array([Vector2(GATE_POS.x, -24.0), Vector2(GATE_POS.x, lane), Vector2(rest.x, lane), rest]))
	_say("ОХ, ЧЁРТ")
	_arrow.hide()
	_set_info(false)


## Где сидит герой в своей могиле (экранные координаты).
func _rest_pos(i: int) -> Vector2:
	return _graves[i].position + Vector2(GRAVE_W * 0.5, 30.0) * _scale


func _begin_path(points: PackedVector2Array) -> void:
	_path = points
	_path_len = 0.0
	for k: int in range(1, points.size()):
		_path_len += points[k - 1].distance_to(points[k])
	_walk_time = 0.0


## Точка и направление на пройденном расстоянии вдоль маршрута.
func _path_at(dist: float) -> Array:
	var left: float = dist
	for k: int in range(1, _path.size()):
		var seg: float = _path[k - 1].distance_to(_path[k])
		if left <= seg or k == _path.size() - 1:
			var t: float = clampf(left / maxf(seg, 0.001), 0.0, 1.0)
			return [_path[k - 1].lerp(_path[k], t), (_path[k] - _path[k - 1]).normalized()]
		left -= seg
	return [_path[_path.size() - 1], Vector2.DOWN]


func _set_info(shown: bool) -> void:
	for node: CanvasItem in _info_nodes:
		node.visible = shown
	_apply_dossier(shown)


## Досье: вместо цифр показываем, как персонаж выглядит (лор).
func _apply_dossier(shown: bool = true) -> void:
	if _lore == null:
		return
	_lore.visible = shown and _dossier
	_lore.text = CharacterLibrary.lore(_ids[_selected])
	if shown:
		for node: Label in [_tagline, _plus, _minus, _weapon]:
			node.visible = not _dossier


func _build_menu_button() -> void:
	var menu: Button = Button.new()
	menu.text = "МЕНЮ (ESC)"
	menu.position = Vector2(6.0, 4.0)
	menu.size = Vector2(80.0, 16.0)
	menu.focus_mode = Control.FOCUS_NONE
	menu.pressed.connect(_to_menu)
	UI_BUTTONS.skin(menu, 3)
	add_child(menu)
	var book: Button = Button.new()
	book.text = "ОРУЖИЕ (TAB)"
	book.position = Vector2(SCREEN.x - 86.0, 4.0)
	book.size = Vector2(80.0, 16.0)
	book.focus_mode = Control.FOCUS_NONE
	book.pressed.connect(_toggle_book)
	UI_BUTTONS.skin(book, 5)
	add_child(book)


func _toggle_book() -> void:
	if _book != null:
		_book.queue_free()
		_book = null
		return
	_book = BOOK.new()
	add_child(_book)


func _to_menu() -> void:
	if not _leaving:
		_leaving = true
		SceneFlow.go(MENU_SCENE, Vector2.UP)


## Реплика героя над головой (исчезает сама).
func _say(text: String) -> void:
	if _speech != null:
		_speech.queue_free()
	var label: Label = _label(text, _rest_pos(_selected) + Vector2(-50.0, -34.0), 100.0, YELLOW, HORIZONTAL_ALIGNMENT_CENTER)
	label.z_index = 30
	_speech = label
	_speech_left = 1.4


## Створки ворот: 0 закрыты, 1 распахнуты.
func _set_gate_open(amount: float) -> void:
	for leaf: TextureRect in _leaves:
		leaf.scale.x = lerpf(1.0, 0.18, clampf(amount, 0.0, 1.0))


func _build_background() -> void:
	var back: ColorRect = ColorRect.new()
	back.color = Color(0.05, 0.07, 0.05)
	back.set_anchors_preset(Control.PRESET_FULL_RECT)
	back.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(back)
	var ground: TextureRect = TextureRect.new()
	ground.texture = GROUND
	ground.stretch_mode = TextureRect.STRETCH_TILE
	ground.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	ground.modulate = Color(0.32, 0.4, 0.3)
	ground.position = Vector2.ZERO
	ground.size = SCREEN
	ground.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(ground)
	var half: float = _gate_tex.get_width() * 0.5
	var top_left: Vector2 = GATE_POS - _gate_tex.get_size() * 0.5
	for side: int in 2:
		var leaf: TextureRect = TextureRect.new()
		var atlas: AtlasTexture = AtlasTexture.new()
		atlas.atlas = _gate_tex
		atlas.region = Rect2(Vector2(half * side, 0.0), Vector2(half, _gate_tex.get_height()))
		leaf.texture = atlas
		leaf.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		leaf.position = top_left + Vector2(half * side, 0.0)
		leaf.size = Vector2(half, _gate_tex.get_height())
		leaf.pivot_offset = Vector2(0.0 if side == 0 else half, 0.0)   # створка поворачивается у внешнего края
		leaf.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(leaf)
		_leaves.append(leaf)


func _label(text: String, pos: Vector2, width: float, color: Color, align: HorizontalAlignment = HORIZONTAL_ALIGNMENT_LEFT) -> Label:
	var label: Label = Label.new()
	label.text = text
	label.position = pos
	label.custom_minimum_size = Vector2(width, 0.0)
	label.size = Vector2(width, 10.0)
	label.horizontal_alignment = align
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override(&"font_color", color)
	label.add_theme_color_override(&"font_shadow_color", Color(0.0, 0.0, 0.0))
	label.add_theme_constant_override(&"shadow_offset_x", 1)
	label.add_theme_constant_override(&"shadow_offset_y", 1)
	add_child(label)
	return label


func _build_header() -> void:
	var head: Label = _label("КЛАДБИЩЕ. КОГО ОТКОПАЕМ?", Vector2(0.0, 10.0), SCREEN.x, YELLOW, HORIZONTAL_ALIGNMENT_CENTER)
	head.add_theme_color_override(&"font_shadow_color", PINK)


func _layout_grid() -> void:
	var n: int = _ids.size()
	for candidate: float in [1.0, 0.875, 0.75, 0.6, 0.5, 0.4]:
		_scale = candidate
		var max_cols: int = maxi(int((GRID_MAX_W - AISLE) / (GRAVE_W * _scale + 4.0)), 1)
		var rows: int = ceili(float(n) / float(max_cols))
		_cols = ceili(float(n) / float(rows))
		if rows * _cell_h() <= GRID_MAX_H:
			return


func _cell_h() -> float:
	return GRAVE_H * _scale + ARROW_H


## Могилы рядами, посередине проход шириной AISLE (под воротами).
func _cell_pos(i: int) -> Vector2:
	var row: int = i / _cols
	var col: int = i % _cols
	var in_row: int = mini(_cols, _ids.size() - row * _cols)
	var left_count: int = in_row / 2
	var step: float = GRAVE_W * _scale + 4.0
	var x: float
	if col < left_count:
		x = GATE_POS.x - AISLE * 0.5 - step * (left_count - col)
	else:
		x = GATE_POS.x + AISLE * 0.5 + step * (col - left_count)
	return Vector2(x + 2.0, GRID_TOP + _cell_h() * row + ARROW_H)


func _build_grave(i: int) -> void:
	var id: StringName = _ids[i]
	var unlocked: bool = Profile.is_unlocked(id)
	var root: Control = Control.new()
	root.position = _cell_pos(i)
	root.size = Vector2(GRAVE_W, GRAVE_H)
	root.scale = Vector2.ONE * _scale
	add_child(root)
	_graves.append(root)
	var pic: TextureRect = TextureRect.new()
	pic.texture = GRAVE_OPEN if unlocked else GRAVE_CLOSED
	pic.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	pic.position = Vector2(0.0, 52.0 - pic.texture.get_height() + 4.0)
	root.add_child(pic)
	var sitter: Node2D = Node2D.new()
	sitter.position = Vector2(GRAVE_W * 0.5, 30.0)
	sitter.scale = Vector2.ONE * 1.25   # герой крупнее могилы: видно, кого выбираешь
	root.add_child(sitter)
	if unlocked:
		var body: Sprite2D = Sprite2D.new()
		body.texture = CharacterLibrary.sprite_sheet(id) if CharacterLibrary.sprite_sheet(id) != null else PLAYER_TEX
		body.hframes = 4
		body.vframes = 3
		body.frame = 8
		body.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		sitter.add_child(body)
	_sitters.append(sitter)
	if _scale >= 0.75:
		var caption: Label = Label.new()
		caption.text = CharacterLibrary.short_title(id) if unlocked else "???"
		caption.position = (root.position + Vector2(-8.0, GRAVE_H * _scale - 3.0)).round()   # целые пиксели, иначе шрифт ломается
		caption.size = Vector2(roundf(GRAVE_W * _scale + 16.0), 10.0)
		caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		caption.mouse_filter = Control.MOUSE_FILTER_IGNORE
		caption.add_theme_font_size_override(&"font_size", 6)
		caption.add_theme_color_override(&"font_shadow_color", Color(0.0, 0.0, 0.0))
		caption.add_theme_constant_override(&"shadow_offset_x", 1)
		caption.add_theme_constant_override(&"shadow_offset_y", 1)
		add_child(caption)
		_captions.append(caption)
	else:
		_captions.append(null)
	if id in _fresh:
		var tag: Label = Label.new()
		tag.text = "!"
		tag.position = Vector2(GRAVE_W - 8.0, -2.0)
		tag.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tag.add_theme_color_override(&"font_color", GREEN)
		tag.add_theme_color_override(&"font_shadow_color", Color(0.0, 0.0, 0.0))
		tag.add_theme_constant_override(&"shadow_offset_x", 1)
		tag.add_theme_constant_override(&"shadow_offset_y", 1)
		root.add_child(tag)
	if unlocked:   # отметки побед по уровням опасности: 6 медалей в полный размер, несобранные - тёмные силуэты
		var won: Array = Profile.hero_wins.get(id, [])
		var row: Panel = Panel.new()
		var box: StyleBoxFlat = StyleBoxFlat.new()
		box.bg_color = Color(0.04, 0.02, 0.05, 0.8)
		row.add_theme_stylebox_override(&"panel", box)
		row.size = Vector2(44.0, 10.0)
		row.position = (root.position + Vector2(GRAVE_W * _scale * 0.5 - 22.0, GRAVE_H * _scale - 13.0)).round()
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(row)
		for d: int in Balance.DANGER_LEVELS.size():
			var mark: TextureRect = TextureRect.new()
			mark.texture = load("res://assets/ui/mark_%d.png" % d if d in won else "res://assets/ui/mark_empty.png") as Texture2D
			mark.position = Vector2(1.0 + d * 7.0, 1.0)
			mark.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
			mark.mouse_filter = Control.MOUSE_FILTER_IGNORE
			row.add_child(mark)
	var click: Button = Button.new()
	click.flat = true
	click.focus_mode = Control.FOCUS_NONE
	click.size = Vector2(GRAVE_W, GRAVE_H)
	click.pressed.connect(_on_grave_pressed.bind(i))
	click.mouse_entered.connect(_select.bind(i))
	root.add_child(click)


func _build_panel() -> void:
	var panel: Panel = Panel.new()
	panel.position = Vector2(24.0, 154.0)
	panel.size = Vector2(432.0, 88.0)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = Color(0.02, 0.02, 0.03)
	style.border_color = GREEN
	style.set_border_width_all(2)
	panel.add_theme_stylebox_override(&"panel", style)
	add_child(panel)
	_info_nodes.append(panel)
	_preview = Sprite2D.new()
	_preview.position = Vector2(58.0, 198.0)
	_preview.scale = Vector2.ONE * 2.6
	_preview.hframes = 4
	_preview.vframes = 3
	_preview.frame = 8
	_preview.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_preview)
	_info_nodes.append(_preview)
	_title = _label("", Vector2(96.0, 158.0), 350.0, YELLOW)
	_title.add_theme_color_override(&"font_shadow_color", PINK)
	_tagline = _label("", Vector2(96.0, 168.0), 350.0, WHITE)
	_plus = _label("", Vector2(96.0, 180.0), 210.0, GREEN)
	_minus = _label("", Vector2(316.0, 180.0), 130.0, RED)
	_weapon = _label("", Vector2(96.0, 213.0), 350.0, YELLOW)
	_dash_label = _label("", Vector2(96.0, 222.0), 350.0, Color(0.0, 0.94, 1.0))
	_status = _label("", Vector2(96.0, 231.0), 350.0, GREEN)
	for node: Label in [_title, _tagline, _plus, _minus, _weapon, _dash_label, _status]:
		_info_nodes.append(node)
	_lore = _label("", Vector2(96.0, 170.0), 346.0, WHITE)
	_lore.visible = false
	_hint = _label("WASD - ВЫБОР   E - ДОСЬЕ\nПРОБЕЛ - ПОГНАЛИ", Vector2(8.0, 243.0), 200.0, GREY)


func _input(event: InputEvent) -> void:
	if _leaving:
		return
	var key: InputEventKey = event as InputEventKey
	if key != null and key.pressed and not key.echo and key.keycode == KEY_TAB:
		get_viewport().set_input_as_handled()
		_toggle_book()
		return
	if key != null and key.pressed and not key.echo and key.keycode == KEY_E and _book == null and _walker == null:
		get_viewport().set_input_as_handled()
		_dossier = not _dossier
		_apply_dossier()
		return
	if key != null and key.pressed and not key.echo and key.keycode == KEY_ESCAPE:
		get_viewport().set_input_as_handled()
		if _book != null:
			_toggle_book()
		elif _picker != null:
			_close_picker()
		else:
			_to_menu()
		return
	if _book != null:
		return
	if _picker != null:
		_picker_input(event)
		return
	if event.is_action_pressed(&"move_left") or event.is_action_pressed(&"ui_left"):
		get_viewport().set_input_as_handled()
		_select(posmod(_selected - 1, _ids.size()))
	elif event.is_action_pressed(&"move_right") or event.is_action_pressed(&"ui_right"):
		get_viewport().set_input_as_handled()
		_select(posmod(_selected + 1, _ids.size()))
	elif event.is_action_pressed(&"move_up") or event.is_action_pressed(&"ui_up"):
		get_viewport().set_input_as_handled()
		_select(posmod(_selected - _cols, _ids.size()))
	elif event.is_action_pressed(&"move_down") or event.is_action_pressed(&"ui_down"):
		get_viewport().set_input_as_handled()
		_select(posmod(_selected + _cols, _ids.size()))
	elif event.is_action_pressed(&"ui_accept"):
		get_viewport().set_input_as_handled()
		_choose()


## Выбор опасности: 6 черепов, A/D - уровень, пробел - в бой, Esc - назад. Закрытые уровни - тёмные.
func _open_picker() -> void:
	_pick_danger = clampi(Profile.last_danger, 0, Profile.danger_unlocked)
	_picker = Control.new()
	_picker.position = Vector2(90.0, 46.0)
	_picker.size = Vector2(300.0, 92.0)
	_picker.z_index = 60
	add_child(_picker)
	var back: Panel = Panel.new()   # плотная плашка с кислотной рамкой: могилы под ней не просвечивают
	var box: StyleBoxFlat = StyleBoxFlat.new()
	box.bg_color = Color(0.06, 0.02, 0.07)
	box.border_color = PINK
	box.set_border_width_all(2)
	back.add_theme_stylebox_override(&"panel", box)
	back.size = _picker.size
	_picker.add_child(back)
	var head: Label = _label("ВЫБЕРИ, НАСКОЛЬКО ГЛУБОКО ПАДАТЬ", Vector2(0.0, 4.0), 300.0, YELLOW, HORIZONTAL_ALIGNMENT_CENTER)
	head.reparent(_picker, false)
	_pick_skulls.clear()
	for d: int in Balance.DANGER_LEVELS.size():
		var skull: TextureRect = TextureRect.new()
		skull.texture = load("res://assets/ui/danger_%d.png" % d) as Texture2D
		skull.position = Vector2(48.0 + d * 36.0, 18.0)
		skull.scale = Vector2.ONE * 2.0
		skull.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		_picker.add_child(skull)
		_pick_skulls.append(skull)
	_pick_title = _label("", Vector2(0.0, 54.0), 300.0, PINK, HORIZONTAL_ALIGNMENT_CENTER)
	_pick_title.reparent(_picker, false)
	_pick_text = _label("", Vector2(0.0, 66.0), 300.0, WHITE, HORIZONTAL_ALIGNMENT_CENTER)
	_pick_text.reparent(_picker, false)
	var hint: Label = _label("A/D - УРОВЕНЬ   ПРОБЕЛ - ПОГНАЛИ   ESC - НАЗАД", Vector2(0.0, 79.0), 300.0, GREY, HORIZONTAL_ALIGNMENT_CENTER)
	hint.reparent(_picker, false)
	_refresh_picker()


func _refresh_picker() -> void:
	for d: int in _pick_skulls.size():
		var open: bool = d <= Profile.danger_unlocked
		_pick_skulls[d].modulate = (Color.WHITE if d == _pick_danger else Color(0.6, 0.6, 0.6)) if open else Color(0.15, 0.15, 0.18)
		_pick_skulls[d].position.y = 14.0 if d == _pick_danger else 18.0
	var data: Dictionary = Balance.DANGER_LEVELS[_pick_danger]
	_pick_title.text = "ОПАСНОСТЬ %d: %s" % [_pick_danger, data["name"]]
	_pick_text.text = data["text"]


func _picker_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"move_left") or event.is_action_pressed(&"ui_left"):
		get_viewport().set_input_as_handled()
		_pick_danger = maxi(_pick_danger - 1, 0)
		_refresh_picker()
	elif event.is_action_pressed(&"move_right") or event.is_action_pressed(&"ui_right"):
		get_viewport().set_input_as_handled()
		_pick_danger = mini(_pick_danger + 1, Profile.danger_unlocked)
		_refresh_picker()
	elif event.is_action_pressed(&"ui_accept"):
		get_viewport().set_input_as_handled()
		_choose()


func _close_picker() -> void:
	if _picker != null:
		_picker.queue_free()
		_picker = null


func _on_grave_pressed(i: int) -> void:
	_select(i)
	_choose()


func _select(i: int) -> void:
	var changed: bool = i != _selected
	_selected = i
	_refresh()
	if changed and not _leaving and Profile.is_unlocked(_ids[i]):
		_say(CharacterLibrary.quip(_ids[i]))


func _choose() -> void:
	var id: StringName = _ids[_selected]
	if not Profile.is_unlocked(id):
		_status.text = "ЗАКОПАН НАГЛУХО. СНАЧАЛА: %s" % CharacterLibrary.unlock_text(id)
		_status.add_theme_color_override(&"font_color", RED)
		return
	if Profile.danger_unlocked > 0 and _picker == null:
		_open_picker()
		return
	Profile.selected = id
	Profile.save()
	GameState.character = id
	GameState.danger = _pick_danger if Profile.danger_unlocked > 0 else 0
	Profile.last_danger = GameState.danger
	_close_picker()
	_leaving = true
	_arrow.hide()
	_set_info(false)
	_walker = _sitters[_selected]
	var rest: Vector2 = _rest_pos(_selected)
	var lane: float = _graves[_selected].position.y + GRAVE_H * _scale + ARROW_H * 0.5   # дорожка под рядом могилы
	_begin_path(PackedVector2Array([rest, Vector2(rest.x, lane), Vector2(GATE_POS.x, lane), GATE_POS + Vector2(0.0, 10.0)]))
	await get_tree().create_timer(_path_len / WALK_SPEED).timeout
	SceneFlow.go(GAME_SCENE, Vector2.DOWN)


func _refresh() -> void:
	var id: StringName = _ids[_selected]
	var unlocked: bool = Profile.is_unlocked(id)
	_title.text = CharacterLibrary.title(id)
	_tagline.text = CharacterLibrary.tagline(id)
	var plus: PackedStringArray = PackedStringArray()
	var minus: PackedStringArray = PackedStringArray()
	for line: String in CharacterLibrary.stat_lines(id):
		if line.begins_with("-"):
			minus.append(line)
		else:
			plus.append(line)
	_plus.text = "\n".join(plus)
	_minus.text = "\n".join(minus)
	_weapon.text = CharacterLibrary.weapon_line(id)
	_dash_label.text = CharacterLibrary.dash_line(id)
	if unlocked:
		_status.text = "ОТКОПАН. ЖМИ ПРОБЕЛ."
		_status.add_theme_color_override(&"font_color", GREEN)
	else:
		_status.text = "ЗАКОПАН: %s %s" % [CharacterLibrary.unlock_text(id), CharacterLibrary.progress_text(id)]
		_status.add_theme_color_override(&"font_color", RED)
	for k: int in _captions.size():
		if _captions[k] != null:
			var open_k: bool = Profile.is_unlocked(_ids[k])
			_captions[k].add_theme_color_override(&"font_color", YELLOW if k == _selected else (WHITE if open_k else GREY))
	var sheet: Texture2D = CharacterLibrary.sprite_sheet(id)
	_preview.texture = (sheet if sheet != null else PLAYER_TEX) if unlocked else null
	_preview.visible = unlocked
	if _lore != null and not _info_nodes.is_empty():
		_apply_dossier((_info_nodes[0] as CanvasItem).visible)


func _process(delta: float) -> void:
	_time += delta
	if _speech != null:
		_speech_left -= delta
		if _speech_left <= 0.0:
			_speech.queue_free()
			_speech = null
	if _walker != null:
		_walk_time += delta
		_walker.z_index = 20
		var dist: float = minf(WALK_SPEED * _walk_time, _path_len)
		var t: float = dist / maxf(_path_len, 0.001)
		var at: Array = _path_at(dist)
		var dir: Vector2 = at[1]
		if not _arriving:
			_set_gate_open(1.0 - (_path_len - dist - 14.0) / 60.0)
		_walker.global_position = (at[0] as Vector2).round()
		if _speech != null:
			_speech.position = _walker.global_position + Vector2(-40.0, -26.0)
		_walker.scale = Vector2.ONE * _scale if _arriving else Vector2.ONE * maxf(_scale, 1.4) * (1.0 - 0.12 * t)
		var body: Sprite2D = _walker.get_child(0) as Sprite2D
		if body != null:
			var step_frame: int = int(_walk_time * 10.0) % 4
			if absf(dir.x) > absf(dir.y):
				body.frame = step_frame
				body.flip_h = dir.x > 0.0
			elif dir.y < 0.0:
				body.frame = 4 + step_frame
			else:
				body.frame = 8 + step_frame
			if _arriving and t >= 1.0:
				body.frame = 8
				body.flip_h = false
		if _arriving and t >= 1.0:
			_arriving = false
			_leaving = false
			_walker.scale = Vector2.ONE
			_walker.z_index = 0
			_walker.position = Vector2(GRAVE_W * 0.5, 30.0)
			_walker = null
			_arrow.show()
			_set_info(true)
		return
	if _preview != null and _preview.visible:
		_preview.frame = 8 + int(_time * 7.0) % 4   # герой в карточке «шагает» на месте
	for i: int in _graves.size():
		var chosen: bool = i == _selected
		var pulse: float = 0.5 + 0.5 * sin(_time * 12.0)
		_graves[i].modulate = Color(1.0, 1.0, 1.0).lerp(Color(1.0, 1.0, 0.6), pulse * 0.3) if chosen else Color(0.55, 0.55, 0.6)
		_sitters[i].position.y = 30.0 + (roundf(sin(_time * 6.0)) if chosen else 0.0)
	_arrow.position = _graves[_selected].position + Vector2(GRAVE_W * 0.5 * _scale - ARROW.get_width() * 0.5, -16.0 + roundf(2.0 * sin(_time * 10.0)))
