extends WeaponBase
## Удлинитель: электрическая дуга бьёт ближайшего врага и перескакивает на соседних (урон слабеет с каждым прыжком).

var _arcs: Array[Dictionary] = []   # {pts: PackedVector2Array (локальные), t: 0..1}


func _physics_process(delta: float) -> void:
	super(delta)
	if _arcs.is_empty():
		return
	for arc: Dictionary in _arcs:
		arc["t"] = float(arc["t"]) - delta * 6.0
	_arcs = _arcs.filter(func(arc: Dictionary) -> bool: return float(arc["t"]) > 0.0)
	queue_redraw()


func _fire(target: Node2D) -> void:
	var stats: Dictionary = Balance.WEAPONS[weapon_id]
	var origin: Vector2 = _muzzle(target)
	var damage: float = GameState.roll_damage(_damage)
	var hit: Array[Node2D] = []
	var points: PackedVector2Array = PackedVector2Array([to_local(origin)])
	var current: Node2D = target
	for i: int in int(stats["chain_jumps"]) + 1:
		points.append(to_local(current.global_position))
		var enemy: EnemyBase = current as EnemyBase
		if enemy != null:
			enemy.hit_by_weapon(damage)
		HitFx.burst(get_tree(), current.global_position, Color(0.0, 0.94, 1.0), 4, 50.0, 2.0, 0.25, true)
		hit.append(current)
		damage *= float(stats["chain_falloff"])
		current = _next_link(current, hit, float(stats["chain_range"]))
		if current == null:
			break
	_arcs.append({"pts": points, "t": 1.0})
	queue_redraw()


func _next_link(from: Node2D, hit: Array[Node2D], reach: float) -> Node2D:
	var best: Node2D = null
	var best_sq: float = reach * reach
	for group: StringName in [&"enemies", &"neutrals"]:
		for node: Node in get_tree().get_nodes_in_group(group):
			var enemy: Node2D = node as Node2D
			if enemy == null or enemy in hit:
				continue
			var d: float = from.global_position.distance_squared_to(enemy.global_position)
			if d < best_sq:
				best_sq = d
				best = enemy
	return best


func _draw() -> void:
	for arc: Dictionary in _arcs:
		var pts: PackedVector2Array = arc["pts"]
		var a: float = float(arc["t"])
		var path: PackedVector2Array = PackedVector2Array()
		for i: int in pts.size() - 1:
			var from: Vector2 = pts[i]
			var to: Vector2 = pts[i + 1]
			var steps: int = maxi(int(from.distance_to(to) / 8.0), 1)
			for s: int in steps:
				var point: Vector2 = from.lerp(to, float(s) / float(steps))
				if s > 0:
					point += Vector2(randf_range(-3.0, 3.0), randf_range(-3.0, 3.0))
				path.append(point)
		path.append(pts[pts.size() - 1])
		if path.size() >= 2:
			draw_polyline(path, Color(0.0, 0.94, 1.0, a * 0.5), 4.0)
			draw_polyline(path, Color(1.0, 1.0, 1.0, a), 1.0)
