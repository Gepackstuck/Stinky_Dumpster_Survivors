class_name GarbageTruck
extends Node2D
## Мусоровоз (модификатор волны): проносится через арену по прямой, давит героя (урон) и врагов (насмерть).
## Путь заранее показан телеграфом. launch() после add_child().

const SHEET: Texture2D = preload("res://assets/sprites/garbage_truck.png")

var _dir: Vector2 = Vector2.RIGHT
var _end: Vector2 = Vector2.ZERO
var _hit_player: bool = false
var _anim: float = 0.0
@onready var _sprite: Sprite2D = $Sprite2D


func launch(from: Vector2, to: Vector2) -> void:
	global_position = from
	_end = to
	_dir = from.direction_to(to)
	_sprite.rotation = _dir.angle()
	_sprite.flip_v = _dir.x < -0.5   # едет влево - не вверх колёсами
	z_index = 3


func _physics_process(delta: float) -> void:
	global_position += _dir * Balance.TRUCK_SPEED * delta
	_anim += delta
	_sprite.frame = int(_anim * 12.0) % 2
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player != null and not _hit_player and _inside(player.global_position):
		var hurtbox: HurtboxComponent = player.get_node_or_null(^"Hurtbox") as HurtboxComponent
		if hurtbox != null and hurtbox.receive_hit(Balance.TRUCK_DAMAGE * WaveRules.hazard_mult(GameState.wave)):
			GameState.last_damage_source = &"garbage_truck"
			_hit_player = true
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null and enemy.is_alive() and _inside(enemy.global_position):
			enemy.hit_by_weapon(99999.0, _dir.orthogonal() * 200.0)
	if global_position.distance_to(_end) < Balance.TRUCK_SPEED * delta * 1.5 or global_position.dot(_dir) > _end.dot(_dir) + 1.0:
		queue_free()


func _inside(point: Vector2) -> bool:
	var off: Vector2 = point - global_position
	return absf(off.dot(_dir)) < 24.0 and absf(off.dot(_dir.orthogonal())) < Balance.TRUCK_HALF_WIDTH
