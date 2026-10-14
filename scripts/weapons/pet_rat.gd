class_name PetRat
extends Node2D
## Крыса-приятель: бродит рядом с игроком, бросается на ближайшего врага в зоне и кусает.

const TEXTURE: Texture2D = preload("res://assets/sprites/pet_rat.png")

var player: Node2D = null
var _sprite: Sprite2D = null
var _bite_left: float = 0.0
var _anim: float = 0.0
var _home: Vector2 = Vector2.ZERO


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = TEXTURE
	_sprite.hframes = 2
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	_home = Vector2.from_angle(randf() * TAU) * Balance.PET_LEASH_DIST


func _physics_process(delta: float) -> void:
	if not is_instance_valid(player) or not GameState.run_active:
		return
	_anim += delta
	_sprite.frame = int(_anim * 8.0) % 2
	_bite_left -= delta
	var target: EnemyBase = _find_target()
	var goal: Vector2 = player.global_position + _home
	if target != null:
		goal = target.global_position
		if global_position.distance_squared_to(goal) <= 100.0 and _bite_left <= 0.0:
			_bite_left = Balance.PET_BITE_SEC
			target.hit_by_weapon(Balance.PET_DAMAGE * GameState.damage_mult, (goal - global_position).normalized() * 60.0)
	var step: Vector2 = goal - global_position
	if step.length_squared() > 4.0:
		global_position += step.normalized() * minf(Balance.PET_SPEED * delta, step.length())
		_sprite.flip_h = step.x < 0.0


func _find_target() -> EnemyBase:
	var best: EnemyBase = null
	var best_sq: float = Balance.PET_AGGRO_RANGE * Balance.PET_AGGRO_RANGE
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy == null:
			continue
		var dist_sq: float = player.global_position.distance_squared_to(enemy.global_position)
		if dist_sq < best_sq:
			best_sq = dist_sq
			best = enemy
	return best
