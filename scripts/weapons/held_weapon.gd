class_name HeldWeapon
extends Node2D
## Оружие в руках героя, как в Brotato: маленький спрайт стоит на кольце вокруг тела (у каждого слота свое место),
## разворачивается на ближайшего врага (8 направлений) и показывает атаку: ствол отдаёт назад, швабра машет,
## носок раздувается. Верхние оружия рисуются за телом, нижние перед ним, чтобы не закрывать героя.
## Висит ребёнком узла оружия (там же сигнал `fired`).

const RING_X: float = 17.0
const RING_Y: float = 12.0
const FIRST_ANGLE: float = 0.5      # первое оружие у правой руки, остальные по кругу
const TRACK_SEC: float = 0.12       # как часто искать цель для поворота
const KICK_DECAY: float = 5.0
const RECOIL_PX: float = 3.0
const SWING_RAD: float = 1.3
const SNAP_RAD: float = PI / 4.0    # поворот шагом 45 градусов (дёрганый пиксель-арт)

var slot_index: int = 0
var slot_count: int = 1

var _sprite: Sprite2D
var _weapon_id: StringName = &""
var _home: Vector2 = Vector2.ZERO
var _aim: Vector2 = Vector2.RIGHT
var _kick: float = 0.0
var _track_left: float = 0.0
var _range_sq: float = 0.0


func _ready() -> void:
	_weapon_id = get_parent().weapon_id
	_range_sq = Balance.WEAPON_TARGET_RANGE * Balance.WEAPON_TARGET_RANGE
	var angle: float = FIRST_ANGLE + TAU * float(slot_index) / float(maxi(slot_count, 1))
	_home = Vector2(cos(angle) * RING_X, sin(angle) * RING_Y)
	_aim = _home.normalized()
	_sprite = Sprite2D.new()
	_sprite.texture = _load_texture("res://assets/sprites/held_%s.png" % _weapon_id)
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var back_layer: Node = get_parent().get_parent().get_node_or_null("HeldBack")
	if back_layer != null and _home.y < -1.0:
		back_layer.add_child(_sprite)   # верхние оружия за телом
		tree_exiting.connect(_sprite.queue_free)
	else:
		add_child(_sprite)
	if get_parent().has_signal(&"fired"):
		get_parent().connect(&"fired", _on_fired)
	_place()


func _on_fired(direction: Vector2) -> void:
	if direction != Vector2.ZERO:
		_aim = direction
	_kick = 1.0


func _process(delta: float) -> void:
	_kick = maxf(_kick - delta * KICK_DECAY, 0.0)
	_track_left -= delta
	if _track_left <= 0.0:
		_track_left = TRACK_SEC
		_track_target()
	_place()


## Смотрим на ближайшего врага в радиусе атаки (без врагов остаёмся как были).
func _track_target() -> void:
	var best_sq: float = _range_sq
	var found: Vector2 = Vector2.ZERO
	var origin: Vector2 = get_parent().global_position
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		if enemy == null:
			continue
		var d: float = origin.distance_squared_to(enemy.global_position)
		if d < best_sq:
			best_sq = d
			found = enemy.global_position - origin
	if found != Vector2.ZERO:
		_aim = found.normalized()


func _place() -> void:
	var angle: float = snappedf(_aim.angle(), SNAP_RAD)
	var offset: Vector2 = Vector2.ZERO
	_sprite.scale = Vector2.ONE
	_sprite.rotation = angle
	_sprite.flip_v = absf(angle) > PI * 0.5 + 0.01    # чтобы смотря влево, не быть вверх ногами
	match _weapon_id:
		&"mop", &"frying_pan", &"rolling_pin":
			var side: float = -1.0 if _sprite.flip_v else 1.0
			_sprite.rotation = angle + side * (-0.5 + SWING_RAD * sin(_kick * PI))   # взмах
			offset = _aim * 3.0 * _kick
		&"sock", &"rotten_cheese":
			_sprite.scale = Vector2.ONE * (1.0 + 0.4 * _kick)                          # раздувается при вони
			offset = Vector2(roundf(sin(_kick * 40.0)), 0.0)
		_:
			offset = -_aim * RECOIL_PX * _kick                                          # отдача
	var base: Vector2 = Vector2(roundf(_home.x), roundf(_home.y))
	var shifted: Vector2 = base + offset
	_sprite.position = Vector2(roundf(shifted.x), roundf(shifted.y))


## Обычная загрузка; если редактор ещё не импортировал новый PNG - читаем файл напрямую (удобно для тестов).
static func _load_texture(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	var image: Image = Image.load_from_file(ProjectSettings.globalize_path(path))
	return ImageTexture.create_from_image(image) if image != null else null
