class_name BuddyDog
extends Node2D
## Н16: пёс-спутник. Бегает за героем, кусает врагов (сильнее с уровнем), приносит кости (свою еду - Profile.bones).
## Носит шмотку из гардероба, над головой - кличка. stray = true: подобран в этом забеге (ещё без клички).

const TEX: GDScript = preload("res://scripts/systems/tex.gd")
const BANTER: GDScript = preload("res://scripts/weapons/pet_banter.gd")
const LINES: Array[String] = ["ГАВ!", "ВУФ!", "РРРР...", "ХРУМ", "КУСЬ!", "АУФ"]

var player: Node2D = null
var stray: bool = false
var _sprite: Sprite2D = null
var _wear: Sprite2D = null
var _bite_left: float = 0.0
var _bone_left: float = 0.0
var _anim: float = 0.0
var _home: Vector2 = Vector2(-18.0, 10.0)
var _talk_left: float = 6.0


func _ready() -> void:
	z_index = 2
	_sprite = Sprite2D.new()
	_sprite.texture = TEX.load_tex("res://assets/sprites/buddy_dog.png")
	_sprite.hframes = 6
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	if Profile.dog_wear != "" and not stray:
		_wear = Sprite2D.new()
		_wear.texture = TEX.load_tex("res://assets/sprites/buddy_wear_%s.png" % Profile.dog_wear)
		_wear.hframes = 6
		_wear.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		add_child(_wear)
	var tag: Label = Label.new()
	tag.text = Profile.dog_name if (Profile.dog_name != "" and not stray) else "?"
	tag.position = Vector2(-30.0, -22.0)
	tag.size = Vector2(60.0, 9.0)
	tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	tag.add_theme_color_override(&"font_color", Color(1.0, 0.75, 0.35))
	tag.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	tag.modulate.a = 0.8
	add_child(tag)
	_bone_left = _bone_sec()


func _level() -> int:
	return 1 if stray else Profile.dog_level


func _bone_sec() -> float:
	return Balance.DOG_BONE_SEC * maxf(1.0 - 0.05 * (_level() - 1), 0.5)


func _physics_process(delta: float) -> void:
	if not is_instance_valid(player) or not GameState.run_active:
		return
	_anim += delta
	_talk_left -= delta
	if _talk_left <= 0.0:
		_talk_left = BANTER.next_delay()
		BANTER.say(self, LINES, Color(1.0, 0.7, 0.3))
	if GameState.wave_time_left > 0.0:
		_bone_left -= delta
		if _bone_left <= 0.0:   # притащил кость - себе на прокорм
			_bone_left = _bone_sec()
			Profile.bones += 1
			HitFx.chatter(get_tree(), global_position + Vector2(0.0, -14.0), tr("+1 КОСТЬ"), Color(0.95, 0.92, 0.8), 12.0, 0.9)
	var lvl: int = _level()
	_bite_left -= delta
	var target: EnemyBase = _find_target()
	var goal: Vector2 = player.global_position + _home
	if target != null:
		goal = target.global_position
		if global_position.distance_squared_to(goal) <= 144.0 and _bite_left <= 0.0:
			_bite_left = Balance.DOG_BITE_SEC
			target.hit_by_weapon(Balance.DOG_DAMAGE * GameState.damage_mult * (1.0 + Balance.DOG_LEVEL_DAMAGE * (lvl - 1)), (goal - global_position).normalized() * 90.0, &"pets")
			HitFx.burst(get_tree(), goal, Color(1.0, 0.0, 0.2), 4, 40.0, 2.0, 0.25, true)
	var step: Vector2 = goal - global_position
	var moving: bool = false
	if step.length_squared() > 4.0:
		global_position += step.normalized() * minf(Balance.DOG_SPEED * (1.0 + Balance.DOG_LEVEL_SPEED * (lvl - 1)) * delta, step.length())
		_sprite.flip_h = step.x < 0.0
		moving = true
	_sprite.frame = int(_anim * 11.0) % 4 if moving else 4 + int(_anim * 3.0) % 2
	if _wear != null:
		_wear.frame = _sprite.frame
		_wear.flip_h = _sprite.flip_h


func _find_target() -> EnemyBase:
	var best: EnemyBase = null
	var best_sq: float = Balance.DOG_AGGRO_RANGE * Balance.DOG_AGGRO_RANGE
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy == null or not enemy.is_alive():
			continue
		var dist_sq: float = player.global_position.distance_squared_to(enemy.global_position)
		if dist_sq < best_sq:
			best_sq = dist_sq
			best = enemy
	return best
