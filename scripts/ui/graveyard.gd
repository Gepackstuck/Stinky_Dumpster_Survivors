class_name Graveyard
extends Control
## Кладбище: экран выбора персонажа. Закрытый герой - закопанная могила с именем на плите,
## открытый сидит в раскопанной яме. A/D или мышь - выбор, пробел/клик - на помойку.

const BOOK: GDScript = preload("res://scripts/ui/weapon_book.gd")
const MENU_SCENE: String = "res://scenes/ui/main_menu.tscn"
const GAME_SCENE: String = "res://scenes/levels/main.tscn"
const SCREEN: Vector2 = Vector2(480.0, 270.0)
const WALK_SEC: float = 0.8   # герой вылезает из ямы и идёт вниз к арене
const GRAVE_TOP: float = 34.0
const GATE_POS: Vector2 = Vector2(240.0, 252.0)   # ворота на арену: внизу по центру (арена под кладбищем в бесконечной петле)
var _gate_tex: Texture2D = CharacterLibrary.load_texture("res://assets/sprites/gate.png")
const ARRIVE_SEC: float = 1.0
const GRAVE_STEP: float = 72.0
const GRAVE_W: float = 48.0
const GROUND: Texture2D = preload("res://assets/sprites/ground_tile.png")
const GRAVE_CLOSED: Texture2D = preload("res://assets/ui/grave_closed.png")
const GRAVE_OPEN: Texture2D = preload("res://assets/ui/grave_open.png")
const PLAYER_TEX: Texture2D = preload("res://assets/sprites/player.png")
const ARROW: Texture2D = preload("res://assets/ui/select_arrow.png")
const YELLOW: Color = Color(0.968627, 1.0, 0.0)
const PINK: Color = Color(1.0, 0.0627451, 0.941176)
const GREEN: Color = Color(0.2235, 1.0, 0.0784)
const RED: Color = Color(1.0, 0.1, 0.2)
const WHITE: Color = Color(1.0, 1.0, 1.0)
const GREY: Color = Color(0.55, 0.55, 0.6)

var _ids: Array[StringName] = []
var _graves: Array[Control] = []
var _sitters: Array[Node2D] = []
var _selected: int = 0
var _fresh: Array[StringName] = []
var _time: float = 0.0
var _arrow: TextureRect
var _title: Label
var _tagline: Label
var _plus: Label
var _minus: Label
var _weapon: Label
var _status: Label
var _hint: Label
var _leaving: bool = false
var _book: Control = null
var _walker: Node2D = null
var _walk_time: float = 0.0
var _walk_from: Vector2 = Vector2.ZERO
var _arriving: bool = false
var _speech: Label = null
var _speech_left: float = 0.0


func _ready() -> void:
	_ids = CharacterLibrary.ids().duplicate()
	_fresh = Profile.fresh_unlocks()
	_selected = maxi(_ids.find(Profile.selected), 0)
	if not Profile.is_unlocked(_ids[_selected]):
		_selected = 0
	_build_background()
	_build_header()
	for i: int in _ids.size():
		_build_grave(i)
	_build_panel()
	_arrow = TextureRect.new()
	_arrow.texture = ARROW
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
	_walk_from = Vector2(240.0, -24.0)   # приходит сверху экрана
	_say("ОХ БЛЯТЬ")
	_walk_time = 0.0
	_arrow.hide()


func _build_menu_button() -> void:
	var menu: Button = Button.new()
	menu.text = "МЕНЮ (ESC)"
	menu.position = Vector2(6.0, 4.0)
	menu.size = Vector2(80.0, 16.0)
	menu.focus_mode = Control.FOCUS_NONE
	menu.pressed.connect(_to_menu)
	add_child(menu)
	var book: Button = Button.new()
	book.text = "ОРУЖИЕ (TAB)"
	book.position = Vector2(SCREEN.x - 86.0, 4.0)
	book.size = Vector2(80.0, 16.0)
	book.focus_mode = Control.FOCUS_NONE
	book.pressed.connect(_toggle_book)
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
	var label: Label = _label(text, Vector2(0.0, 0.0), 80.0, YELLOW, HORIZONTAL_ALIGNMENT_CENTER)
	label.z_index = 30
	_speech = label
	_speech_left = 1.4


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
	var gate: TextureRect = TextureRect.new()
	gate.texture = _gate_tex
	gate.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	gate.position = GATE_POS - _gate_tex.get_size() * 0.5
	gate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(gate)


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


func _build_grave(i: int) -> void:
	var id: StringName = _ids[i]
	var unlocked: bool = Profile.is_unlocked(id)
	var x: float = (SCREEN.x - GRAVE_STEP * _ids.size()) * 0.5 + GRAVE_STEP * (i + 0.5) - GRAVE_W * 0.5
	var root: Control = Control.new()
	root.position = Vector2(x, GRAVE_TOP)
	root.size = Vector2(GRAVE_W, 70.0)
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
	root.add_child(sitter)
	if unlocked:
		var body: Sprite2D = Sprite2D.new()
		body.texture = CharacterLibrary.sprite_sheet(id) if CharacterLibrary.sprite_sheet(id) != null else PLAYER_TEX
		body.hframes = 4
		body.vframes = 3
		body.frame = 8
		body.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		sitter.add_child(body)
		var hat: Sprite2D = Sprite2D.new()
		hat.texture = CharacterLibrary.hat_icon(id)
		hat.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		hat.scale = Vector2.ONE * 0.5
		hat.position = Vector2(0.0, -10.0)
		sitter.add_child(hat)
	_sitters.append(sitter)
	var caption: Label = Label.new()
	caption.text = CharacterLibrary.short_title(id)
	caption.position = Vector2(-12.0, 58.0)
	caption.size = Vector2(GRAVE_W + 24.0, 10.0)
	caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	caption.mouse_filter = Control.MOUSE_FILTER_IGNORE
	caption.add_theme_color_override(&"font_color", WHITE if unlocked else GREY)
	caption.add_theme_color_override(&"font_shadow_color", Color(0.0, 0.0, 0.0))
	caption.add_theme_constant_override(&"shadow_offset_x", 1)
	caption.add_theme_constant_override(&"shadow_offset_y", 1)
	root.add_child(caption)
	if id in _fresh:
		var tag: Label = Label.new()
		tag.text = "НОВЕНЬКИЙ!"
		tag.position = Vector2(-12.0, -8.0)
		tag.size = Vector2(GRAVE_W + 24.0, 10.0)
		tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		tag.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tag.add_theme_color_override(&"font_color", GREEN)
		tag.add_theme_color_override(&"font_shadow_color", Color(0.0, 0.0, 0.0))
		root.add_child(tag)
	var click: Button = Button.new()
	click.flat = true
	click.focus_mode = Control.FOCUS_NONE
	click.position = Vector2(-10.0, 0.0)
	click.size = Vector2(GRAVE_W + 20.0, 70.0)
	click.pressed.connect(_on_grave_pressed.bind(i))
	click.mouse_entered.connect(_select.bind(i))
	root.add_child(click)


func _build_panel() -> void:
	var panel: Panel = Panel.new()
	panel.position = Vector2(24.0, 122.0)
	panel.size = Vector2(432.0, 112.0)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var style: StyleBoxFlat = StyleBoxFlat.new()
	style.bg_color = Color(0.02, 0.02, 0.03)
	style.border_color = GREEN
	style.set_border_width_all(2)
	panel.add_theme_stylebox_override(&"panel", style)
	add_child(panel)
	_title = _label("", Vector2(36.0, 130.0), 408.0, YELLOW)
	_title.add_theme_color_override(&"font_shadow_color", PINK)
	_tagline = _label("", Vector2(36.0, 144.0), 408.0, WHITE)
	_plus = _label("", Vector2(36.0, 168.0), 200.0, GREEN)
	_minus = _label("", Vector2(244.0, 168.0), 200.0, RED)
	_weapon = _label("", Vector2(36.0, 206.0), 408.0, YELLOW)
	_status = _label("", Vector2(36.0, 218.0), 408.0, GREEN)
	_hint = _label("A/D - ВЫБОР  ПРОБЕЛ - НА ПОМОЙКУ\nESC - МЕНЮ  TAB - ОРУЖИЕ", Vector2(8.0, 240.0), 200.0, GREY)


func _input(event: InputEvent) -> void:
	if _leaving:
		return
	var key: InputEventKey = event as InputEventKey
	if key != null and key.pressed and not key.echo and key.keycode == KEY_TAB:
		get_viewport().set_input_as_handled()
		_toggle_book()
		return
	if key != null and key.pressed and not key.echo and key.keycode == KEY_ESCAPE:
		get_viewport().set_input_as_handled()
		if _book != null:
			_toggle_book()
		else:
			_to_menu()
		return
	if _book != null:
		return
	if event.is_action_pressed(&"move_left") or event.is_action_pressed(&"ui_left"):
		get_viewport().set_input_as_handled()
		_select(posmod(_selected - 1, _ids.size()))
	elif event.is_action_pressed(&"move_right") or event.is_action_pressed(&"ui_right"):
		get_viewport().set_input_as_handled()
		_select(posmod(_selected + 1, _ids.size()))
	elif event.is_action_pressed(&"ui_accept"):
		get_viewport().set_input_as_handled()
		_choose()


func _on_grave_pressed(i: int) -> void:
	_select(i)
	_choose()


func _select(i: int) -> void:
	_selected = i
	_refresh()


func _choose() -> void:
	var id: StringName = _ids[_selected]
	if not Profile.is_unlocked(id):
		_status.text = "ЗАКОПАН НАГЛУХО. СНАЧАЛА: %s" % CharacterLibrary.unlock_text(id)
		_status.add_theme_color_override(&"font_color", RED)
		return
	Profile.selected = id
	Profile.save()
	GameState.character = id
	_leaving = true
	_walker = _sitters[_selected]
	_walk_from = _walker.global_position
	_walk_time = 0.0
	_arrow.hide()
	await get_tree().create_timer(WALK_SEC).timeout
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
	if unlocked:
		_status.text = "ОТКОПАН. ЖМИ ПРОБЕЛ."
		_status.add_theme_color_override(&"font_color", GREEN)
	else:
		_status.text = "ЗАКОПАН: %s %s" % [CharacterLibrary.unlock_text(id), CharacterLibrary.progress_text(id)]
		_status.add_theme_color_override(&"font_color", RED)
	_place_arrow()


func _place_arrow() -> void:
	var root: Control = _graves[_selected]
	_arrow.position = Vector2(root.position.x + GRAVE_W * 0.5 - ARROW.get_width() * 0.5, root.position.y + 70.0)


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
		var span: float = ARRIVE_SEC if _arriving else WALK_SEC
		var t: float = clampf(_walk_time / span, 0.0, 1.0)
		var rest: Vector2 = _graves[_selected].position + Vector2(GRAVE_W * 0.5, 30.0)
		var gate_point: Vector2 = GATE_POS + Vector2(0.0, 10.0)
		var from: Vector2 = _walk_from
		var to: Vector2 = rest if _arriving else gate_point
		_walker.global_position = (from.lerp(to, t)).round()
		if _speech != null:
			_speech.position = _walker.global_position + Vector2(-40.0, -26.0)
		_walker.scale = Vector2.ONE if _arriving else Vector2.ONE * (1.0 - 0.4 * t)
		var body: Sprite2D = _walker.get_child(0) as Sprite2D
		if body != null:
			body.frame = (8 + int(_walk_time * 10.0) % 4) if t < 1.0 or not _arriving else 8
		if _arriving and t >= 1.0:
			_arriving = false
			_leaving = false
			_walker.scale = Vector2.ONE
			_walker.z_index = 0
			_walker = null
			_arrow.show()
		return
	for i: int in _graves.size():
		var chosen: bool = i == _selected
		var pulse: float = 0.5 + 0.5 * sin(_time * 12.0)
		_graves[i].modulate = Color(1.0, 1.0, 1.0).lerp(Color(1.0, 1.0, 0.45), pulse * 0.5) if chosen else Color(0.55, 0.55, 0.6)
		_sitters[i].position.y = 30.0 + (roundf(sin(_time * 6.0 + float(i))) if chosen else 0.0)
	_arrow.position.y = _graves[_selected].position.y + 70.0 + roundf(2.0 * sin(_time * 10.0))
