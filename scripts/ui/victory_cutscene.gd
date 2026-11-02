extends Control
## Ролик победы (идея 19): герой выходит из ворот, а за ними - помойка ещё больше (тизер бесконечности).
## ~8 с, любая кнопка - пропустить. Выключается в настройках (Settings.victory_cutscene). Дальше - кладбище.

const GRAVEYARD: String = "res://scenes/ui/graveyard.tscn"
const SKY: Texture2D = preload("res://assets/ui/victory_sky.png")
const FAR: Texture2D = preload("res://assets/ui/victory_far.png")
const NEAR: Texture2D = preload("res://assets/ui/victory_near.png")
const LENGTH_SEC: float = 8.0

var _t: float = 0.0
var _far: TextureRect
var _near: TextureRect
var _hero: Sprite2D
var _lines: Array[Label] = []
var _leaving: bool = false


func _ready() -> void:
	size = Vector2(480.0, 270.0)
	_layer(SKY, Vector2.ZERO)
	_far = _layer(FAR, Vector2(0.0, 120.0))
	_near = _layer(NEAR, Vector2(0.0, 140.0))
	_hero = Sprite2D.new()
	_hero.texture = CharacterLibrary.sprite_sheet(GameState.character)
	_hero.hframes = 4
	_hero.vframes = 3
	_hero.frame = 4   # спиной к камере: уходит вдаль
	_hero.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_hero.position = Vector2(240.0, 290.0)
	_hero.scale = Vector2(3.0, 3.0)
	add_child(_hero)
	var texts: Array[String] = [tr("ТЫ ВЫБРАЛСЯ..."), tr("...НА ПОМОЙКУ ПОБОЛЬШЕ."), tr("ТУТ ДАЖЕ ГОЛУБИ ЗЛЕЕ. УДАЧИ, ЛОХ.")]
	var colors: Array[Color] = [Color(0.97, 1.0, 0.0), Color(1.0, 0.06, 0.94), Color(0.9, 0.9, 0.9)]
	for i: int in texts.size():
		var l: Label = Label.new()
		l.text = texts[i]
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.autowrap_mode = TextServer.AUTOWRAP_WORD
		l.size = Vector2(240.0, 12.0)
		l.scale = Vector2(2.0, 2.0) if i < 2 else Vector2.ONE
		l.position = Vector2(0.0, 30.0 + i * 26.0) if i < 2 else Vector2(120.0, 84.0)
		if i == 2:
			l.size = Vector2(240.0, 12.0)
		l.add_theme_color_override(&"font_color", colors[i])
		l.add_theme_color_override(&"font_shadow_color", Color.BLACK)
		l.add_theme_constant_override(&"shadow_offset_x", 1)
		l.add_theme_constant_override(&"shadow_offset_y", 1)
		l.modulate.a = 0.0
		add_child(l)
		_lines.append(l)
	var skip: Label = Label.new()
	skip.text = InputMode.hint(tr("ЛЮБАЯ КНОПКА - ПРОПУСТИТЬ"), tr("ЛЮБАЯ КНОПКА - ПРОПУСТИТЬ"))
	skip.position = Vector2(0.0, 256.0)
	skip.size = Vector2(472.0, 10.0)
	skip.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	skip.add_theme_color_override(&"font_color", Color(0.75, 0.75, 0.8))
	skip.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	add_child(skip)


func _layer(tex: Texture2D, pos: Vector2) -> TextureRect:
	var r: TextureRect = TextureRect.new()
	r.texture = tex
	r.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	r.position = pos
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(r)
	return r


func _process(delta: float) -> void:
	_t += delta
	var k: float = clampf(_t / LENGTH_SEC, 0.0, 1.0)
	_far.position.x = roundf(-k * 120.0)    # параллакс: дальнее ползёт медленно, ближнее быстрее
	_near.position.x = roundf(-k * 240.0)
	var walk: float = clampf(_t / 5.0, 0.0, 1.0)   # герой уходит по дороге вдаль и уменьшается
	_hero.position = Vector2(240.0, lerpf(290.0, 196.0, walk)).round()
	_hero.scale = Vector2.ONE * (3.0 if walk < 0.4 else (2.0 if walk < 0.8 else 1.0))
	_hero.frame = 4 + (int(_t * 8.0) % 4 if walk < 1.0 else 0)
	var starts: Array[float] = [1.2, 3.0, 4.8]
	for i: int in _lines.size():
		_lines[i].modulate.a = clampf((_t - starts[i]) * 2.0, 0.0, 1.0)
	if _t >= LENGTH_SEC:
		_leave()


func _input(event: InputEvent) -> void:
	if _t < 0.5:
		return
	if (event is InputEventKey or event is InputEventJoypadButton or event is InputEventMouseButton) and event.is_pressed():
		get_viewport().set_input_as_handled()
		_leave()


func _leave() -> void:
	if _leaving:
		return
	_leaving = true
	SceneFlow.from_arena = true
	SceneFlow.go(GRAVEYARD, Vector2.DOWN)
