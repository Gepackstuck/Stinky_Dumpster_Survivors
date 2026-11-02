class_name RouletteScreen
extends CanvasLayer
## Рулетка модификатора (после Ларька, если вступил в кучу): покрышка с 8 сегментами-значками крутится,
## её толкает случайный герой с кладбища, гвоздь сверху показывает выпавшее. Сама доигрывает и отдаёт результат
## (EventBus.roulette_done) - без ввода, чтобы и бот, и игрок не застревали.

const TIRE: Texture2D = preload("res://assets/ui/roulette_tire.png")
const STAND: Texture2D = preload("res://assets/ui/roulette_stand.png")
const NAIL: Texture2D = preload("res://assets/ui/roulette_nail.png")
const CENTER: Vector2 = Vector2(240.0, 128.0)
const R: float = 50.0
const COLORS: Array[Color] = [Color(1.0, 0.0, 0.2), Color(0.97, 1.0, 0.0), Color(0.22, 1.0, 0.08), Color(1.0, 0.06, 0.94),
		Color(0.0, 0.94, 1.0), Color(1.0, 0.5, 0.0), Color(0.6, 0.2, 1.0), Color(0.55, 0.35, 0.15)]

var _root: Control
var _wheel: Node2D
var _tire: Sprite2D
var _spinner: Sprite2D
var _title: Label
var _sub: Label
var _segments: Array[StringName] = []
var _last_tick: int = -1


func _ready() -> void:
	layer = 30
	process_mode = Node.PROCESS_MODE_ALWAYS
	_root = Control.new()
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_root.visible = false
	add_child(_root)
	var solid: Panel = Panel.new()   # плотная подложка: мир под рулеткой не просвечивает
	var box: StyleBoxFlat = StyleBoxFlat.new()
	box.bg_color = Color(0.05, 0.02, 0.05, 0.92)
	solid.add_theme_stylebox_override(&"panel", box)
	solid.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.add_child(solid)
	var dim: TextureRect = TextureRect.new()
	dim.texture = preload("res://assets/ui/dim_checker.png")
	dim.stretch_mode = TextureRect.STRETCH_TILE
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.modulate = Color(0.1, 0.05, 0.1, 0.9)
	_root.add_child(dim)
	var stand: Sprite2D = Sprite2D.new()
	stand.texture = STAND
	stand.position = CENTER + Vector2(0.0, 66.0)
	_root.add_child(stand)
	_wheel = Node2D.new()
	_wheel.position = CENTER
	_wheel.draw.connect(_draw_wheel)
	_root.add_child(_wheel)
	_tire = Sprite2D.new()
	_tire.texture = TIRE
	_wheel.add_child(_tire)
	var nail: Sprite2D = Sprite2D.new()
	nail.texture = NAIL
	nail.position = CENTER + Vector2(0.0, -R - 12.0)
	_root.add_child(nail)
	_spinner = Sprite2D.new()
	_spinner.hframes = 4
	_spinner.vframes = 3
	_spinner.scale = Vector2.ONE * 1.6
	_spinner.position = CENTER + Vector2(78.0, 30.0)
	_spinner.flip_h = false
	_root.add_child(_spinner)
	_title = _label(Vector2(0.0, 14.0), Color(0.97, 1.0, 0.0), 1.5)
	_sub = _label(Vector2(0.0, 232.0), Color.WHITE, 1.0)
	for node: CanvasItem in [_root, _wheel, _tire, stand, nail, _spinner]:
		node.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	EventBus.roulette_requested.connect(_spin)


func _label(pos: Vector2, color: Color, s: float) -> Label:
	var l: Label = Label.new()
	l.position = pos
	l.size = Vector2(480.0 / s, 12.0)
	l.scale = Vector2.ONE * s
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_color_override(&"font_color", color)
	l.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	l.add_theme_constant_override(&"shadow_offset_x", 1)
	l.add_theme_constant_override(&"shadow_offset_y", 1)
	_root.add_child(l)
	return l


func _draw_wheel() -> void:
	var n: int = _segments.size()
	if n == 0:
		return
	for i: int in n:
		var a0: float = TAU * i / n - PI * 0.5 - PI / n
		var pts: PackedVector2Array = PackedVector2Array([Vector2.ZERO])
		for k: int in 9:
			pts.append(Vector2.from_angle(a0 + TAU / n * k / 8.0) * (R - 2.0))
		_wheel.draw_colored_polygon(pts, COLORS[i % COLORS.size()].darkened(0.25))
		_wheel.draw_polyline(PackedVector2Array([Vector2.ZERO, pts[1]]), Color(0.05, 0.05, 0.05), 1.0)



func _spin() -> void:
	var result: StringName = Profile.next_mod()
	var others: Array = Balance.WAVE_MODS.filter(func(m: StringName) -> bool: return m != result)
	others.shuffle()
	_segments.clear()
	var at: int = randi() % Balance.ROULETTE_SEGMENTS
	for i: int in Balance.ROULETTE_SEGMENTS:
		_segments.append(result if i == at else others[i if i < at else i - 1])
	var hero: StringName = Balance.CHARACTER_ORDER[randi() % Balance.CHARACTER_ORDER.size()]
	_spinner.texture = CharacterLibrary.sprite_sheet(hero)
	_title.text = "КРУТИТ %s" % CharacterLibrary.title(hero)
	_sub.text = "НОГА В ГОВНЕ - КРУТИ БАРАБАН"
	_wheel.rotation = 0.0
	for child: Node in _wheel.get_children():
		if child != _tire:
			child.queue_free()
	var n: int = _segments.size()
	for i: int in n:   # значки сегментов - спрайтами, крутятся вместе с колесом
		var mid_angle: float = TAU * i / n - PI * 0.5
		var icon: Sprite2D = Sprite2D.new()
		icon.texture = load("res://assets/ui/mod_%s_s.png" % _segments[i]) as Texture2D
		icon.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		icon.position = Vector2.from_angle(mid_angle) * (R * 0.64)
		icon.rotation = mid_angle + PI * 0.5
		icon.scale = Vector2.ONE * 1.1
		_wheel.add_child(icon)
	_wheel.move_child(_tire, -1)
	_wheel.queue_redraw()
	_root.visible = true
	get_tree().paused = true
	# сегмент i под гвоздём, когда поворот = -TAU*i/n; плюс 5-7 полных оборотов
	var target: float = -TAU * at / Balance.ROULETTE_SEGMENTS - TAU * randi_range(5, 7) + randf_range(-0.25, 0.25) * TAU / Balance.ROULETTE_SEGMENTS
	var tw: Tween = create_tween()
	tw.tween_method(_set_angle, 0.0, target, Balance.ROULETTE_SPIN_SEC).set_trans(Tween.TRANS_QUART).set_ease(Tween.EASE_OUT)
	await tw.finished
	AudioManager.play_sfx(&"roulette_win", 0.0)
	var data: Dictionary = Balance.WAVE_MOD_DATA[result]
	_title.text = "ВЫПАЛО: %s!" % data["title"]
	_sub.text = data["line"]
	await get_tree().create_timer(1.8, true).timeout
	_root.visible = false
	get_tree().paused = false
	EventBus.roulette_done.emit(result)


func _set_angle(a: float) -> void:
	_wheel.rotation = a
	var seg: int = int(floor(-a / (TAU / Balance.ROULETTE_SEGMENTS)))
	if seg != _last_tick:
		_last_tick = seg
		AudioManager.play_sfx(&"roulette_tick", 0.05)
	_spinner.frame = int(absf(a) * 3.0) % 4   # толкает колесо
