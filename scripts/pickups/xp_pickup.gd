class_name XpPickup
extends Area2D
## Пиксель XP (слизь). Лежит, пока магнит игрока не позовёт; потом летит к игроку и подбирается.
## Создаётся через PoolManager; после add_child() нужно вызвать setup().

var _value: int = 0
var _target: Node2D = null
var _speed: float = 0.0


func _ready() -> void:
	set_physics_process(false)


func setup(at: Vector2, value: int) -> void:
	global_position = at
	_value = value
	_target = null
	_speed = 0.0
	set_physics_process(false)


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
