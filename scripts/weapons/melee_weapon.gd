class_name MeleeWeapon
extends Node2D
## Швабра: взмах дугой в сторону ближайшего врага, бьёт всех в секторе и отбрасывает.

@export var weapon_id: StringName = &"mop"

var _damage: float = 0.0
var _cooldown_sec: float = 1.0
var _cooldown_left: float = 0.0
var _knockback: float = 0.0
var _reach: float = 50.0
var _half_arc: float = 1.2
var _swing: float = -1.0
var _swing_dir: float = 0.0


func _ready() -> void:
	var stats: Dictionary = Balance.WEAPONS[weapon_id]
	_damage = stats["damage"]
	_cooldown_sec = stats["cooldown"]
	_knockback = stats["knockback"]
	_reach = stats["reach"]
	_half_arc = deg_to_rad(stats["arc_deg"]) * 0.5
	EventBus.player_died.connect(set_physics_process.bind(false))


func _physics_process(delta: float) -> void:
	if _swing >= 0.0:
		_swing += delta * 6.0
		if _swing > 1.0:
			_swing = -1.0
		queue_redraw()
	_cooldown_left -= delta
	if _cooldown_left > 0.0:
		return
	var target: Node2D = null
	var best_sq: float = _reach * _reach * 2.25  # замахиваемся, если враг в 1.5 длины
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		var d: float = global_position.distance_squared_to(enemy.global_position)
		if enemy != null and d < best_sq:
			best_sq = d
			target = enemy
	if target == null:
		return
	_cooldown_left = _cooldown_sec
	_swing_dir = global_position.direction_to(target.global_position).angle()
	_swing = 0.0
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy == null:
			continue
		var to: Vector2 = enemy.global_position - global_position
		if to.length() <= _reach and absf(angle_difference(_swing_dir, to.angle())) <= _half_arc:
			enemy.hit_by_weapon(_damage * GameState.projectile_damage_mult, to.normalized() * _knockback)


func _draw() -> void:
	if _swing < 0.0:
		return
	var a: float = 1.0 - _swing
	var start: float = _swing_dir - _half_arc
	var sweep: float = _half_arc * 2.0 * minf(_swing * 2.0, 1.0)
	draw_arc(Vector2.ZERO, _reach, start, start + sweep, 16, Color(0.9686, 1.0, 0.0, a), 3.0)
	draw_arc(Vector2.ZERO, _reach - 4.0, start, start + sweep, 16, Color(1.0, 0.0627, 0.9412, a), 2.0)
