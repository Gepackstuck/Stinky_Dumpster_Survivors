class_name HeroShoes
extends Node2D
## Обувь героя = индикатор рывка. У каждого героя своя пара (tools/gen_shoes.py).
## Готовый заряд - ботинок яркий; на перезарядке - серый и наливается цветом снизу вверх;
## зарядился - вспыхивает. Два заряда - по ботинку на заряд, один - оба ботинка вместе.
## При ходьбе ботинки по очереди шагают; жмёшь рывок без сил - краснеют и трясутся.

const CW: int = 8
const CH: int = 6
const STEP_FPS: float = 8.0
const SIDE_GAP: float = 2.0     # в профиль ступни почти друг за другом
const FRONT_GAP: float = 3.5    # анфас/спина - по бокам

var _hero: StringName = &""
var _sheet: Texture2D = null
var _grey: Array[Sprite2D] = []
var _color: Array[Sprite2D] = []
var _part: Array[float] = [1.0, 1.0]
var _step_t: float = 0.0
var _deny_left: float = 0.0
var _sprite: Sprite2D = null
var _animator: Node = null


func _ready() -> void:
	z_index = 1
	_sprite = get_parent().get_node_or_null(^"Sprite2D") as Sprite2D
	_animator = get_parent().get_node_or_null(^"FrameAnimator")
	for i: int in 2:
		var g: Sprite2D = _make()
		g.self_modulate = Color(1.0, 1.0, 1.0, 0.55)   # пустой ботинок - бледный призрак (чёрные туфли тоже видно)
		var c: Sprite2D = _make()
		_grey.append(g)
		_color.append(c)
	set_hero(GameState.character)
	EventBus.dash_state.connect(_on_dash_state)


func set_hero(hero: StringName) -> void:
	_hero = hero
	_sheet = load("res://assets/sprites/shoes_%s.png" % hero) as Texture2D
	visible = _sheet != null
	for s: Sprite2D in _grey + _color:
		s.texture = _sheet


func _make() -> Sprite2D:
	var s: Sprite2D = Sprite2D.new()
	s.centered = false
	s.region_enabled = true
	s.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(s)
	return s


func _on_dash_state(charges: int, max_charges: int, recharge: float) -> void:
	var old: Array[float] = _part.duplicate()
	for i: int in 2:
		var slot: int = i if max_charges > 1 else 0   # один заряд - оба ботинка показывают его
		_part[i] = 1.0 if slot < charges else (recharge if slot == charges else 0.0)
		if old[i] < 1.0 and _part[i] >= 1.0:
			_pop(i)


## Нажал рывок, а сил нет.
func deny() -> void:
	_deny_left = 0.35


func _pop(i: int) -> void:
	var s: Sprite2D = _color[i]
	s.modulate = Color(3.0, 3.0, 3.0)
	s.create_tween().tween_property(s, ^"modulate", Color.WHITE, 0.3)
	HitFx.burst(get_tree(), s.global_position + Vector2(CW * 0.5, CH * 0.5), Color(0.0, 0.94, 1.0), 5, 35.0, 1.0, 0.25)


func _process(delta: float) -> void:
	if _sheet == null or _sprite == null:
		return
	var row: int = int(_animator.get(&"row")) if _animator != null else 0
	var moving: bool = bool(_animator.get(&"active")) if _animator != null else false
	_step_t = _step_t + delta * STEP_FPS if moving else 0.0
	var phase: int = int(_step_t) % 4
	var lift: Array[int] = [0, 0]
	if moving:
		lift = [[2, 1, 0, 0][phase], [0, 0, 2, 1][phase]]
	var side: bool = row == 0
	var toe_left: bool = side and not _sprite.flip_h   # герои нарисованы лицом влево
	var bottom: float = HeroFeet.bottom(_hero, row) + 1.0
	var shake: float = 0.0
	if _deny_left > 0.0:
		_deny_left -= delta
		shake = roundf(sin(_deny_left * 70.0) * 1.5)
	modulate = Color(1.0, 0.3, 0.3) if _deny_left > 0.0 else Color.WHITE
	for i: int in 2:
		var gap: float = SIDE_GAP if side else FRONT_GAP
		var x: float = (-gap if i == 0 else gap)
		var fwd: float = (float(lift[i]) * (-1.0 if toe_left else 1.0)) if side else 0.0
		var top_left: Vector2 = Vector2(x + fwd - CW * 0.5 + shake, bottom - CH - lift[i]).round()
		var cell: int = 0 if side else 1
		_grey[i].region_rect = Rect2((cell + 2) * CW, 0, CW, CH)
		_grey[i].position = top_left
		_grey[i].flip_h = toe_left
		var h: int = roundi(CH * clampf(_part[i], 0.0, 1.0))
		_color[i].visible = h > 0
		_color[i].region_rect = Rect2(cell * CW, CH - h, CW, h)   # заливка снизу вверх
		_color[i].position = top_left + Vector2(0.0, CH - h)
		_color[i].flip_h = toe_left
		# в профиль дальний ботинок - за ближним
		_grey[i].z_index = (0 if (i == 0) != toe_left else 1) if side else 0
		_color[i].z_index = _grey[i].z_index
