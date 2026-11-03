class_name ScratchPanel
extends Control
## Н12: лотерейные билеты стираются по-настоящему. Перед Ларьком - крупный билет «ГОВНОЛОТО», серебряный слой
## стирается зигзагом, под ним - что выпало (пусто, говно, предмет, джекпот). Билеты по очереди; ПРОБЕЛ - быстрее.
## Итоги уже начислены в GameState.scratch_tickets(); здесь только показ (GameState.last_tickets).

signal done

const TICKET: Texture2D = preload("res://assets/ui/ticket_big.png")
const FOIL: Texture2D = preload("res://assets/ui/ticket_foil.png")
const SCALE: float = 2.0
const TICKET_POS: Vector2 = Vector2(110.0, 52.0)
const FOIL_OFFSET: Vector2 = Vector2(19.0, 23.0)   # окно приза на листе билета
const SCRATCH_SEC: float = 1.1
const SHOW_SEC: float = 1.0
const BRUSH: int = 6                                # радиус «монетки» в пикселях слоя
const PASSES: int = 4                               # проходов зигзага по слою

var _tickets: Array[Dictionary] = []
var _index: int = 0
var _t: float = 0.0
var _show_left: float = 0.0
var _scratching: bool = false
var _foil_img: Image
var _foil_tex: ImageTexture
var _foil: TextureRect
var _icon: TextureRect
var _prize: Label
var _counter: Label
var _sound_left: float = 0.0
var _fast: bool = false


func setup(tickets: Array[Dictionary]) -> void:
	_tickets = tickets.duplicate()
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var dim: TextureRect = TextureRect.new()   # затемнение: тот же билет, растянутый и почти чёрный
	dim.texture = TICKET
	dim.modulate = Color(0.0, 0.0, 0.0, 0.75)
	dim.stretch_mode = TextureRect.STRETCH_SCALE
	dim.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	var ticket: TextureRect = TextureRect.new()
	ticket.texture = TICKET
	ticket.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	ticket.position = TICKET_POS
	ticket.scale = Vector2.ONE * SCALE
	add_child(ticket)
	var head: Label = _label("ГОВНОЛОТО", TICKET_POS + Vector2(8.0, 14.0), TICKET.get_width() * SCALE - 16.0, Color(1.0, 0.95, 0.2))
	head.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	head.add_theme_color_override(&"font_shadow_color", Color(0.3, 0.0, 0.0))
	var win: Vector2 = TICKET_POS + FOIL_OFFSET * SCALE
	var win_size: Vector2 = Vector2(FOIL.get_width(), FOIL.get_height()) * SCALE
	_icon = TextureRect.new()
	_icon.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_icon.position = win + Vector2(10.0, (win_size.y - 32.0) * 0.5)
	add_child(_icon)
	_prize = _label("", win + Vector2(46.0, 0.0), win_size.x - 52.0, Color.WHITE)
	_prize.size.y = win_size.y
	_prize.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_prize.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_foil = TextureRect.new()
	_foil.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_foil.position = win
	_foil.scale = Vector2.ONE * SCALE
	add_child(_foil)
	_counter = _label("", Vector2(0.0, TICKET_POS.y + TICKET.get_height() * SCALE + 10.0), 480.0, Color(0.968627, 1.0, 0.0))
	_counter.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	var hint: Label = _label(InputMode.hint("ПРОБЕЛ - БЫСТРЕЕ", "A - БЫСТРЕЕ"), Vector2(0.0, 250.0), 480.0, Color(0.6, 0.6, 0.65))
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_start_ticket()


func _label(text: String, pos: Vector2, width: float, color: Color) -> Label:
	var l: Label = Label.new()
	l.text = text
	l.position = pos
	l.size = Vector2(width, 10.0)
	l.add_theme_color_override(&"font_color", color)
	l.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(l)
	return l


func _start_ticket() -> void:
	var t: Dictionary = _tickets[_index]
	_counter.text = tr("БИЛЕТ %d ИЗ %d") % [_index + 1, _tickets.size()]
	_foil_img = FOIL.get_image()
	_foil_img.convert(Image.FORMAT_RGBA8)
	_foil_tex = ImageTexture.create_from_image(_foil_img)
	_foil.texture = _foil_tex
	_icon.texture = null
	match t["kind"]:
		&"coins":
			_prize.text = tr("+%d ГОВНА") % int(t["coins"])
			_prize.add_theme_color_override(&"font_color", Color(0.968627, 1.0, 0.0))
			_icon.texture = load("res://assets/ui/item_poop_wallet.png")
		&"item":
			_prize.text = ItemLibrary.title(t["item"])
			_prize.add_theme_color_override(&"font_color", Color(0.2235, 1.0, 0.0784))
			_icon.texture = ItemLibrary.icon(t["item"])
		&"jackpot":
			_prize.text = tr("ДЖЕКПОТ! +%d ГОВНА") % int(t["coins"])
			_prize.add_theme_color_override(&"font_color", Color(1.0, 0.063, 0.94))
			_icon.texture = load("res://assets/ui/item_combo_golden_poop.png")
		_:
			_prize.text = tr("ПУСТО. ЛОХ.")
			_prize.add_theme_color_override(&"font_color", Color(1.0, 0.1, 0.2))
	_t = 0.0
	_scratching = true


func _process(delta: float) -> void:
	var speed: float = 3.0 if _fast or _tickets.size() > 4 else 1.0
	if _scratching:
		var before: float = _t
		_t = minf(_t + delta * speed / SCRATCH_SEC, 1.0)
		_scratch_between(before, _t)
		_sound_left -= delta
		if _sound_left <= 0.0:
			_sound_left = 0.11
			AudioManager.play_sfx(&"scratch", 0.15)
		if _t >= 1.0:
			_scratching = false
			_foil.visible = false
			_show_left = SHOW_SEC / speed
			_reveal_sound()
	else:
		_show_left -= delta
		if _show_left <= 0.0:
			_index += 1
			if _index >= _tickets.size():
				done.emit()
				queue_free()
				return
			_foil.visible = true
			_start_ticket()


## Стереть слой вдоль зигзага от прогресса a до b (монетка ходит туда-сюда сверху вниз).
func _scratch_between(a: float, b: float) -> void:
	var w: int = _foil_img.get_width()
	var h: int = _foil_img.get_height()
	var steps: int = maxi(int((b - a) * 220.0), 1)
	for i: int in steps + 1:
		var p: float = lerpf(a, b, float(i) / steps)
		var lane: float = p * PASSES
		var row: int = mini(int(lane), PASSES - 1)
		var along: float = lane - row
		if row % 2 == 1:
			along = 1.0 - along
		var cx: int = int(along * (w - 1))
		var cy: int = int((row + 0.5) / PASSES * h)
		for dy: int in range(-BRUSH, BRUSH + 1):
			for dx: int in range(-BRUSH, BRUSH + 1):
				if dx * dx + dy * dy <= BRUSH * BRUSH + randi() % 6:
					var x: int = cx + dx
					var y: int = cy + dy
					if x >= 0 and y >= 0 and x < w and y < h:
						_foil_img.set_pixel(x, y, Color(0, 0, 0, 0))
	_foil_tex.update(_foil_img)


func _reveal_sound() -> void:
	match _tickets[_index]["kind"]:
		&"coins": AudioManager.play_sfx(&"buy", 0.0)
		&"item": AudioManager.play_sfx(&"combo", 0.0)
		&"jackpot": AudioManager.play_sfx(&"roulette_win", 0.0)
		_: AudioManager.play_sfx(&"streak_break", 0.0)


func _input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_accept"):
		get_viewport().set_input_as_handled()
		_fast = true
		if not _scratching:
			_show_left = 0.0
