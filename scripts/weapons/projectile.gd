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
var source_weapon: StringName = &""   # оружие-источник (статистика урона)
var pierce: int = 0   # сколько врагов пробивает насквозь
var trail_kind: StringName = &"tracer"   # tracer — светящийся росчерк, flame — огненный шлейф
var trail_color: Color = Color(1.0, 0.92, 0.25)
var _age: float = 0.0


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
	_age = 0.0
	trail_kind = &"tracer"
	trail_color = Color(1.0, 0.92, 0.25)
	queue_redraw()


func _physics_process(delta: float) -> void:
	if not _active:
		return
	global_position += _direction * _speed * delta
	_age += delta
	_life_left -= delta
	queue_redraw()
	if _life_left <= 0.0:
		_deactivate()


func _on_area_entered(area: Area2D) -> void:
	if not _active:
		return
	if area is HurtboxComponent:
		if area.get_parent() == _ignore:
			return
		GameState.hit_source = source_weapon
		(area as HurtboxComponent).receive_hit(_damage)
		var victim: Node = area.get_parent()
		if burn_sec > 0.0 and victim.has_method(&"ignite"):
			victim.call(&"ignite", burn_dps, burn_sec)
		if slow_sec > 0.0 and victim.has_method(&"slow"):
			victim.call(&"slow", slow_factor, slow_sec)
		HitFx.sparks(get_tree(), global_position, Color(1.0, 0.5, 0.05) if burn_sec > 0.0 else Color(1.0, 0.92, 0.3))
		if pierce > 0:
			pierce -= 1
			return
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


## Трассер: светящийся росчерк с чёрной обводкой за снарядом (или огненный шлейф у зажигалок и горелок) — видно, куда и чем стреляют.
func _draw() -> void:
	if not _active or _direction == Vector2.ZERO:
		return
	var back: Vector2 = -_direction
	if trail_kind == &"flame":
		for i: int in 7:
			var t: float = float(i) / 6.0
			var wob: Vector2 = _direction.orthogonal() * sin(_age * 40.0 + float(i) * 1.7) * (1.0 + t * 2.5)
			var pos: Vector2 = back * (1.0 + t * 7.0) + wob * 0.5
			var radius: float = 1.3 + t * 1.2
			draw_circle(pos, radius + 0.8, Color(0.1, 0.0, 0.0, 0.7 - t * 0.5))   # тёмный ореол, чтобы пламя не терялось на коричневом
		for i: int in 7:
			var t2: float = float(i) / 6.0
			var wob2: Vector2 = _direction.orthogonal() * sin(_age * 40.0 + float(i) * 1.7) * (1.0 + t2 * 2.5)
			var pos2: Vector2 = back * (1.0 + t2 * 7.0) + wob2 * 0.5
			var col: Color = Color(1.0, 0.97, 0.4).lerp(Color(1.0, 0.2, 0.0), t2)
			col.a = 1.0 - t2 * 0.45
			draw_circle(pos2, 1.3 + t2 * 1.2, col)
		draw_circle(Vector2.ZERO, 1.6, Color(1.0, 1.0, 0.85, 1.0))
	else:
		# маленький росчерк, как в Brotato (было 12-28 px толщиной 6 - «жёлтые брёвна» закрывали врагов)
		var length: float = clampf(_speed * 0.03, 4.0, 9.0)
		var tail: Vector2 = back * length
		draw_line(tail, _direction * 1.5, Color(0.05, 0.0, 0.05, 0.7), 3.0)
		draw_line(tail * 0.8, _direction, trail_color, 2.0)
		draw_line(tail * 0.3, _direction * 1.5, Color(1.0, 1.0, 1.0, 1.0), 1.0)
