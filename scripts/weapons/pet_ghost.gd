class_name PetGhost
extends Node2D
## Призрак-питомец. drunk — дух друга-алкаша: шатаясь, летит к врагу и бьёт. granny — дух бабки-повитухи:
## держится возле игрока, раз в несколько секунд лечит его и лупит тапком врагов вплотную.

var kind: StringName = &"drunk"
var player: Node2D = null
var _sprite: Sprite2D = null
var _hit_left: float = 0.0
var _heal_left: float = 0.0
var _anim: float = 0.0
var _home: Vector2 = Vector2.ZERO


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://assets/sprites/pet_ghost_%s.png" % kind) as Texture2D
	_sprite.hframes = 2
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_sprite.modulate = Color(1.0, 1.0, 1.0, 0.82)
	add_child(_sprite)
	_home = Vector2.from_angle(randf() * TAU) * Balance.PET_LEASH_DIST
	_heal_left = Balance.GHOST_GRANNY_HEAL_SEC


func _physics_process(delta: float) -> void:
	if not is_instance_valid(player) or not GameState.run_active:
		return
	_anim += delta
	_sprite.frame = int(_anim * 3.0) % 2
	_sprite.position.y = sin(_anim * 3.0) * 2.0   # парит
	_hit_left -= delta
	if kind == &"drunk":
		_drunk_step(delta)
	else:
		_granny_step(delta)


func _drunk_step(delta: float) -> void:
	var target: EnemyBase = _nearest_enemy(player.global_position, Balance.PET_AGGRO_RANGE)
	var goal: Vector2 = player.global_position + _home
	if target != null:
		goal = target.global_position
		if global_position.distance_squared_to(goal) <= 144.0 and _hit_left <= 0.0:
			_hit_left = Balance.GHOST_DRUNK_HIT_SEC
			target.hit_by_weapon(Balance.GHOST_DRUNK_DAMAGE * GameState.damage_mult, (goal - global_position).normalized() * 160.0)
			HitFx.popup(get_tree(), global_position + Vector2(0.0, -14.0), "ИК!", Color(0.968627, 1.0, 0.0), 12.0, 0.5)
	var step: Vector2 = goal - global_position
	if step.length_squared() > 4.0:
		var dir: Vector2 = step.normalized()
		var wobble: Vector2 = dir.orthogonal() * sin(_anim * 4.0) * Balance.GHOST_DRUNK_WOBBLE   # шатает из стороны в сторону
		global_position += (dir * Balance.GHOST_DRUNK_SPEED + wobble) * delta
		_sprite.flip_h = step.x < 0.0


func _granny_step(delta: float) -> void:
	var goal: Vector2 = player.global_position + _home
	var step: Vector2 = goal - global_position
	if step.length_squared() > 4.0:
		global_position += step.normalized() * minf(Balance.PET_SPEED * 0.7 * delta, step.length())
		_sprite.flip_h = step.x < 0.0
	_heal_left -= delta
	if _heal_left <= 0.0:
		_heal_left = Balance.GHOST_GRANNY_HEAL_SEC
		if player.has_method(&"heal"):
			player.call(&"heal", Balance.GHOST_GRANNY_HEAL)
			HitFx.popup(get_tree(), player.global_position + Vector2(0.0, -16.0), "+%d ХП: БАБКА ШЕПЧЕТ" % roundi(Balance.GHOST_GRANNY_HEAL), Color(1.0, 0.0627, 0.94), 12.0, 0.9)
	var victim: EnemyBase = _nearest_enemy(global_position, Balance.GHOST_GRANNY_SLIPPER_RANGE)
	if victim != null and _hit_left <= 0.0:
		_hit_left = Balance.GHOST_GRANNY_SLIPPER_SEC
		victim.hit_by_weapon(Balance.GHOST_GRANNY_SLIPPER_DAMAGE * GameState.damage_mult, (victim.global_position - global_position).normalized() * 140.0)


func _nearest_enemy(from: Vector2, range_px: float) -> EnemyBase:
	var best: EnemyBase = null
	var best_sq: float = range_px * range_px
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy == null:
			continue
		var dist_sq: float = from.distance_squared_to(enemy.global_position)
		if dist_sq < best_sq:
			best_sq = dist_sq
			best = enemy
	return best
