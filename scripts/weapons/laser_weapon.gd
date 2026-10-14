class_name LaserWeapon
extends WeaponBase
## Лазерная указка: мгновенный красный луч в сторону ближайшей цели, пробивает всех на линии.

var _beam_dir: Vector2 = Vector2.RIGHT
var _beam_len: float = 0.0
var _beam_t: float = 0.0


func _physics_process(delta: float) -> void:
	super(delta)
	if _beam_t > 0.0:
		_beam_t -= delta * 12.0
		queue_redraw()


func _fire(target: Node2D) -> void:
	var dir: Vector2 = global_position.direction_to(target.global_position)
	var half_width: float = Balance.WEAPONS[weapon_id]["beam_half_width"]
	var length: float = Balance.WEAPON_TARGET_RANGE
	for group: StringName in [&"enemies", &"neutrals"]:
		for node: Node in get_tree().get_nodes_in_group(group):
			var enemy: EnemyBase = node as EnemyBase
			if enemy == null:
				continue
			var to: Vector2 = enemy.global_position - global_position
			var along: float = to.dot(dir)
			if along > 0.0 and along < length and absf(to.cross(dir)) <= half_width + 5.0:
				enemy.hit_by_weapon(GameState.roll_damage(_damage))
	_beam_dir = dir
	_beam_len = minf(global_position.distance_to(target.global_position) + 60.0, length)
	_beam_t = 1.0
	queue_redraw()


func _draw() -> void:
	if _beam_t <= 0.0:
		return
	draw_line(Vector2.ZERO, _beam_dir * _beam_len, Color(1.0, 0.0627, 0.94, _beam_t * 0.35), 4.0)
	draw_line(Vector2.ZERO, _beam_dir * _beam_len, Color(1.0, 0.1, 0.2, _beam_t), 1.0)
	draw_circle(_beam_dir * _beam_len, 2.0, Color(1.0, 1.0, 1.0, _beam_t))
