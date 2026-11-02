class_name Bestiary
extends Control
## Бестиарий: все враги игры. Убитые показаны с описанием, статами и счётчиком убийств за всё время,
## ненайденные - чёрным силуэтом «???». Листать A/D/W/S или стрелками, ESC / TAB / ПРОБЕЛ - назад.

signal closed

const COLUMNS: int = 6
const CELL: Vector2 = Vector2(46.0, 46.0)
const GRID_POS: Vector2 = Vector2(10.0, 30.0)
const PANEL_POS: Vector2 = Vector2(304.0, 28.0)
const PANEL_W: float = 168.0
const YELLOW: Color = Color(0.968627, 1.0, 0.0)
const GREEN: Color = Color(0.2235, 1.0, 0.0784)
const GREY: Color = Color(0.55, 0.55, 0.6)
const RED: Color = Color(1.0, 0.1, 0.2)
const ARROW: Texture2D = preload("res://assets/ui/select_arrow.png")

var _ids: Array[StringName] = []
var _sprites: Array[Sprite2D] = []
var _selected: int = 0
var _time: float = 0.0
var _arrow: TextureRect = null
var _name: Label = null
var _desc: Label = null
var _stats: Label = null
var _kills: Label = null
var _big: Sprite2D = null
var _counter: Label = null


func _ready() -> void:
	size = Vector2(480.0, 270.0)
	mouse_filter = Control.MOUSE_FILTER_STOP
	z_index = 100
	process_mode = Node.PROCESS_MODE_ALWAYS
	var back: ColorRect = ColorRect.new()
	back.color = Color(0.03, 0.02, 0.04, 1.0)
	back.size = size
	add_child(back)
	_label("БЕСТИАРИЙ. КТО ТЕБЯ ЖРАЛ", Vector2(0.0, 8.0), 480.0, YELLOW, HORIZONTAL_ALIGNMENT_CENTER)
	for id: StringName in Balance.ENEMIES:
		_ids.append(id)
	for i: int in _ids.size():
		_build_cell(i)
	_arrow = TextureRect.new()
	_arrow.texture = ARROW
	_arrow.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_arrow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_arrow.pivot_offset = ARROW.get_size() * 0.5
	_arrow.rotation = PI
	add_child(_arrow)
	_big = Sprite2D.new()
	_big.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_big.position = PANEL_POS + Vector2(PANEL_W * 0.5, 30.0)
	add_child(_big)
	_name = _label("", PANEL_POS + Vector2(0.0, 58.0), PANEL_W, Color.WHITE, HORIZONTAL_ALIGNMENT_CENTER)
	_desc = _label("", PANEL_POS + Vector2(0.0, 72.0), PANEL_W, Color(0.91, 0.91, 0.91), HORIZONTAL_ALIGNMENT_LEFT)
	_desc.size.y = 80.0
	_stats = _label("", PANEL_POS + Vector2(0.0, 168.0), PANEL_W, GREEN, HORIZONTAL_ALIGNMENT_LEFT)
	_kills = _label("", PANEL_POS + Vector2(0.0, 196.0), PANEL_W, YELLOW, HORIZONTAL_ALIGNMENT_LEFT)
	_counter = _label("", Vector2(10.0, 236.0), 280.0, GREY, HORIZONTAL_ALIGNMENT_LEFT)
	_label("A/D/W/S - ЛИСТАТЬ     ESC / ПРОБЕЛ - НАЗАД", Vector2(0.0, 254.0), 480.0, GREY, HORIZONTAL_ALIGNMENT_CENTER)
	_select(0)


func _cell_pos(i: int) -> Vector2:
	return GRID_POS + Vector2((i % COLUMNS) * CELL.x, floorf(float(i) / COLUMNS) * CELL.y)


## Рядов анимации в листе врага (у боссов несколько; в бестиарии играем только ход).
func _rows(id: StringName) -> int:
	return int(Balance.ENEMIES[id].get("anim_rows", 1))


func _build_cell(i: int) -> void:
	var id: StringName = _ids[i]
	var tex: Texture2D = load("res://assets/sprites/enemy_%s.png" % id) as Texture2D
	var sprite: Sprite2D = Sprite2D.new()
	sprite.texture = tex
	sprite.hframes = 4
	sprite.vframes = _rows(id)
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var frame: Vector2 = tex.get_size() / Vector2(4.0, float(_rows(id)))
	var k: float = minf(1.0, 30.0 / maxf(frame.x, frame.y))
	sprite.scale = Vector2.ONE * (1.0 if k >= 1.0 else k)
	if Profile.killed(id) <= 0:
		sprite.modulate = Color(0.0, 0.0, 0.0, 1.0)
	sprite.position = _cell_pos(i) + CELL * 0.5 + Vector2(0.0, 4.0)
	add_child(sprite)
	_sprites.append(sprite)
	if Profile.killed(id) <= 0:
		var mark: Label = _label("?", _cell_pos(i) + Vector2(0.0, 15.0), CELL.x, GREY, HORIZONTAL_ALIGNMENT_CENTER)
		mark.z_index = 2


func _select(index: int) -> void:
	_selected = posmod(index, _ids.size())
	var id: StringName = _ids[_selected]
	_arrow.position = _cell_pos(_selected) + Vector2((CELL.x - ARROW.get_width()) * 0.5, -6.0)
	var known: bool = Profile.killed(id) > 0
	var tex: Texture2D = load("res://assets/sprites/enemy_%s.png" % id) as Texture2D
	_big.texture = tex
	_big.hframes = 4
	_big.vframes = _rows(id)
	var frame: Vector2 = tex.get_size() / Vector2(4.0, float(_rows(id)))
	_big.scale = Vector2.ONE * maxf(1.0, floorf(46.0 / maxf(frame.x, frame.y)))
	_big.modulate = Color.WHITE if known else Color(0.0, 0.0, 0.0, 1.0)
	if known:
		var data: Dictionary = Balance.ENEMIES[id]
		_name.text = EnemyNames.title(id)
		_name.add_theme_color_override(&"font_color", EnemyNames.color(id))
		_desc.text = EnemyNames.description(id)
		if data.get("neutral", false):
			_stats.text = "ХП: %d     НЕ КУСАЕТСЯ" % roundi(data["hp"])
		else:
			_stats.text = "ХП: %d     УРОН: %s\nСКОРОСТЬ: %d%s" % [roundi(data["hp"]), _num(data["damage"]), roundi(data["speed"]), "     ЛЕТАЕТ" if data.get("flying", false) else ""]
		_kills.text = "УБИТО ЗА ВСЁ ВРЕМЯ: %d" % Profile.killed(id)
	else:
		_name.text = "???"
		_name.add_theme_color_override(&"font_color", GREY)
		_desc.text = "Тебя ещё никто не убил, и ты никого из них тоже. Убей такого, и узнаешь, кто это."
		_stats.text = ""
		_kills.text = ""
	var known_count: int = 0
	for e: StringName in _ids:
		if Profile.killed(e) > 0:
			known_count += 1
	_counter.text = "ОТКРЫТО: %d/%d" % [known_count, _ids.size()]


func _num(value: float) -> String:
	return str(roundi(value)) if is_equal_approx(value, roundf(value)) else "%.1f" % value


func _process(delta: float) -> void:
	_time += delta
	for i: int in _sprites.size():
		_sprites[i].frame = int(_time * (5.0 if i == _selected else 0.0)) % 4
	_arrow.position.y = _cell_pos(_selected).y - 6.0 + roundf(sin(_time * 6.0) * 1.5)
	_big.frame = int(_time * 5.0) % 4


func _input(event: InputEvent) -> void:
	if not visible:
		return
	var step: int = 0
	var key: InputEventKey = event as InputEventKey
	if event.is_action_pressed(&"move_left") or event.is_action_pressed(&"ui_left"):
		step = -1
	elif event.is_action_pressed(&"move_right") or event.is_action_pressed(&"ui_right"):
		step = 1
	elif event.is_action_pressed(&"move_up") or event.is_action_pressed(&"ui_up"):
		step = -COLUMNS
	elif event.is_action_pressed(&"move_down") or event.is_action_pressed(&"ui_down"):
		step = COLUMNS
	if step != 0:
		get_viewport().set_input_as_handled()
		_select(clampi(_selected + step, 0, _ids.size() - 1) if absi(step) == COLUMNS else _selected + step)
		return
	if event.is_action_pressed(&"ui_accept") or event.is_action_pressed(&"ui_cancel") or (key != null and key.pressed and not key.echo and (key.keycode == KEY_ESCAPE or key.keycode == KEY_TAB)):
		get_viewport().set_input_as_handled()
		closed.emit()


func _label(text: String, pos: Vector2, width: float, color: Color, align: HorizontalAlignment) -> Label:
	var label: Label = Label.new()
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.position = pos
	label.size = Vector2(width, 10.0)
	label.horizontal_alignment = align
	label.text = text
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	label.add_theme_color_override(&"font_color", color)
	label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	label.add_theme_constant_override(&"shadow_offset_x", 1)
	label.add_theme_constant_override(&"shadow_offset_y", 1)
	add_child(label)
	return label
