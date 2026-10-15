extends Node2D
## Пёс с помойки: носится рядом с игроком, кидается на врагов и кусает сильнее и чаще, чем крыса.

const TEX: GDScript = preload("res://scripts/systems/tex.gd")

var player: Node2D = null
var _sprite: Sprite2D = null
var _bite_left: float = 0.0
var _anim: float = 0.0
var _home: Vector2 = Vector2.ZERO


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = TEX.load_tex("res://assets/sprites/pet_dog.png")
	_sprite.hframes = 2
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	_home = Vector2.from_angle(randf() * TAU) * Balance.PET_LEASH_DIST


func _physics_process(delta: float) -> void:
	if not is_instance_valid(player) or not GameState.run_active:
		return
	_anim += delta
	_sprite.frame = int(_anim * 9.0) % 2
	_bite_left -= delta
	var target: EnemyBase = _find_target()
	var goal: Vector2 = player.global_position + _home
	if target != null:
		goal = target.global_position
		if global_position.distance_squared_to(goal) <= 144.0 and _bite_left <= 0.0:
			_bite_left = Balance.DOG_BITE_SEC
			target.hit_by_weapon(Balance.DOG_DAMAGE * GameState.damage_mult, (goal - global_position).normalized() * 90.0)
			HitFx.burst(get_tree(), goal, Color(1.0, 0.0, 0.2), 4, 40.0, 2.0, 0.25, true)
	var step: Vector2 = goal - global_position
	if step.length_squared() > 4.0:
		global_position += step.normalized() * minf(Balance.DOG_SPEED * delta, step.length())
		_sprite.flip_h = step.x < 0.0


func _find_target() -> EnemyBase:
	var best: EnemyBase = null
	var best_sq: float = Balance.DOG_AGGRO_RANGE * Balance.DOG_AGGRO_RANGE
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy == null:
			continue
		var dist_sq: float = player.global_position.distance_squared_to(enemy.global_position)
		if dist_sq < best_sq:
			best_sq = dist_sq
			best = enemy
	return best
