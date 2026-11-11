class_name XpPickup
extends Area2D
## Пиксель XP (слизь). Лежит, пока магнит игрока не позовёт; потом летит к игроку и подбирается.
## Создаётся через PoolManager; после add_child() нужно вызвать setup().

const TEX_PATH: String = "res://assets/sprites/xp_pixel.png"

var _value: int = 0
var _target: Node2D = null
var _speed: float = 0.0
var _phase: float = 0.0
var _k: float = 1.0   # масштаб текселя (детальный стиль)
@onready var _sprite: Sprite2D = $Sprite2D


func _ready() -> void:
	add_to_group(&"pickups")
	_phase = randf() * TAU
	set_physics_process(false)
	if ArtStyle.has_hd(TEX_PATH):   # детальный стиль: светящийся сгусток, виден и во тьме
		_k = ArtStyle.apply(_sprite, TEX_PATH)
		_sprite.scale = Vector2.ONE * _k
		var glow: CanvasItemMaterial = CanvasItemMaterial.new()
		glow.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
		_sprite.material = glow
		get_node(^"FrameAnimator").set_process(false)


## Кристалл покачивается и «поворачивается» (сужается по ширине), дёргано, шагами по 1 px.
func _process(_delta: float) -> void:
	var t: float = Time.get_ticks_msec() * 0.001 * 4.0 + _phase
	_sprite.position.y = roundf(sin(t) * 1.5)
	_sprite.scale.x = snappedf(0.65 + 0.35 * absf(cos(t * 0.8)), 0.1) * _k


func setup(at: Vector2, value: int) -> void:
	global_position = at
	_value = value
	_target = null
	_speed = 0.0
	set_physics_process(false)


func amount() -> int:
	return _value


## Начать лететь к цели (вызывает магнит игрока).
func attract(target: Node2D) -> void:
	if _target != null:
		return
	_target = target
	_speed = Balance.XP_PICKUP_START_SPEED
	set_physics_process(true)


func _physics_process(delta: float) -> void:
	if not is_instance_valid(_target):
		_target = null
		set_physics_process(false)
		return
	_speed += Balance.XP_PICKUP_ACCELERATION * delta
	var to_target: Vector2 = _target.global_position - global_position
	var distance: float = to_target.length()
	if distance <= Balance.XP_COLLECT_DISTANCE:
		_collect()
		return
	global_position += to_target / distance * minf(_speed * delta, distance)


func _collect() -> void:
	_target = null
	set_physics_process(false)
	EventBus.xp_collected.emit(_value)
	PoolManager.release(self)
