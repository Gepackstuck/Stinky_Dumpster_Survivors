class_name Projectile
extends Area2D
## Снаряд игрока. Летит по прямой, бьёт первого врага и возвращается в пул.
## Создаётся через PoolManager; после add_child() нужно вызвать launch().

var _direction: Vector2 = Vector2.ZERO
var _speed: float = 0.0
var _damage: float = 0.0
var _life_left: float = 0.0
var _active: bool = false
var ricochets: int = 0
var ricochet_range: float = 0.0
var _ignore: Node = null
var burn_dps: float = 0.0
var burn_sec: float = 0.0
var slow_factor: float = 1.0
var slow_sec: float = 0.0


func _ready() -> void:
	area_entered.connect(_on_area_entered)


func set_texture(texture: Texture2D) -> void:
	$Sprite2D.texture = texture


func launch(from: Vector2, direction: Vector2, damage: float, speed: float, lifetime_sec: float) -> void:
	global_position = from
	_direction = direction
	_damage = damage
	_speed = speed
	_life_left = lifetime_sec
	_ignore = null
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
		if area.get_parent() == _ignore:
			return
		(area as HurtboxComponent).receive_hit(_damage)
		var victim: Node = area.get_parent()
		if burn_sec > 0.0 and victim.has_method(&"ignite"):
			victim.call(&"ignite", burn_dps, burn_sec)
		if slow_sec > 0.0 and victim.has_method(&"slow"):
			victim.call(&"slow", slow_factor, slow_sec)
		if ricochets > 0 and _try_ricochet(area.get_parent()):
			return
		_deactivate()


## Отскок к ближайшему другому врагу в радиусе. false — цели нет, снаряд гаснет.
func _try_ricochet(hit: Node) -> bool:
	var best: Node2D = null
	var best_sq: float = ricochet_range * ricochet_range
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		if enemy == null or enemy == hit:
			continue
		var d: float = global_position.distance_squared_to(enemy.global_position)
		if d < best_sq:
			best_sq = d
			best = enemy
	if best == null:
		return false
	ricochets -= 1
	_ignore = hit
	_direction = global_position.direction_to(best.global_position)
	_life_left = maxf(_life_left, 0.5)
	return true


func _deactivate() -> void:
	_active = false
	PoolManager.release(self)
