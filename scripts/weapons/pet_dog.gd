extends Node2D
## Пёс с помойки: носится рядом с игроком, кидается на врагов и кусает сильнее и чаще, чем крыса.

const TEX: GDScript = preload("res://scripts/systems/tex.gd")
const BANTER: GDScript = preload("res://scripts/weapons/pet_banter.gd")
const LINES: Array[String] = ["ГАВ!", "ВУФ!", "РРРР...", "ХРУМ", "КУСЬ!"]

var player: Node2D = null
var _sprite: Sprite2D = null
var _bite_left: float = 0.0
var _anim: float = 0.0
var _home: Vector2 = Vector2.ZERO
var _talk_left: float = 5.0


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = TEX.load_tex("res://assets/sprites/pet_dog.png")
	_sprite.hframes = 6
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	_home = Vector2.from_angle(randf() * TAU) * Balance.PET_LEASH_DIST


func _physics_process(delta: float) -> void:
	if not is_instance_valid(player) or not GameState.run_active:
		return
	_anim += delta
	_talk_left -= delta
	if _talk_left <= 0.0:
		_talk_left = BANTER.next_delay()
		BANTER.say(self, LINES, Color(1.0, 0.7, 0.3))
	var moving: bool = false
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
		moving = true
	_sprite.frame = int(_anim * 11.0) % 4 if moving else 4 + int(_anim * 3.0) % 2
	_sprite.scale = Vector2(1.0 + 0.12 * maxf(_bite_left / Balance.DOG_BITE_SEC, 0.0), 1.0 - 0.1 * maxf(_bite_left / Balance.DOG_BITE_SEC, 0.0))


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
