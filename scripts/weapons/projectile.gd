class_name Projectile
extends Area2D
## Снаряд игрока. Летит по прямой, бьёт первого врага и возвращается в пул.
## Создаётся через PoolManager; после add_child() нужно вызвать launch().

var _direction: Vector2 = Vector2.ZERO
var _speed: float = 0.0
var _damage: float = 0.0
var _life_left: float = 0.0
var _active: bool = false


func _ready() -> void:
	area_entered.connect(_on_area_entered)


func launch(from: Vector2, direction: Vector2, damage: float, speed: float, lifetime_sec: float) -> void:
	global_position = from
	_direction = direction
	_damage = damage
	_speed = speed
	_life_left = lifetime_sec
	_active = true


func _physics_process(delta: float) -> void:
	if not _active:
		return
	global_position += _direction * _speed * delta
	_life_left -= delta
	if _life_left <= 0.0:
		_deactivate()


func _on_area_entered(area: Area2D) -> void:
	if not _active:
		return
	if area is HurtboxComponent:
		(area as HurtboxComponent).receive_hit(_damage)
		_deactivate()


func _deactivate() -> void:
	_active = false
	PoolManager.release(self)
