class_name PetGhost
extends Node2D
## Призрак-питомец. drunk - дух друга-алкаша: шатается возле игрока и швыряет бутылки во врагов.
## granny - дух бабки-повитухи: раз в пару секунд либо (30%) лечит игрока, либо кидает тапок во врага.

const PROJECTILE_SCENE: PackedScene = preload("res://scenes/weapons/projectile.tscn")
const BOTTLE: Texture2D = preload("res://assets/sprites/proj_bottle.png")
const SLIPPER: Texture2D = preload("res://assets/sprites/proj_slipper_flat.png")

const BANTER: GDScript = preload("res://scripts/weapons/pet_banter.gd")
const DRUNK_LINES: Array[String] = ["ИК!", "ЗА ЗДОРОВЬЕ!", "Я В ПОРЯДКЕ", "БУЛЬК"]
const GRANNY_LINES: Array[String] = ["ВНУЧЕК...", "ПОКУШАЙ", "ШЬЮ-ШЬЮ", "ДЕРЖИСЬ, ГОВНОЕД"]
var _talk_left: float = 5.0
var kind: StringName = &"drunk"
var player: Node2D = null
var _sprite: Sprite2D = null
var _act_left: float = 0.0
var _anim: float = 0.0
var _home: Vector2 = Vector2.ZERO


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = load("res://assets/sprites/pet_ghost_%s.png" % kind) as Texture2D
	_sprite.hframes = 4
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_sprite.modulate = Color(1.0, 1.0, 1.0, Balance.GHOST_ALPHA)
	add_child(_sprite)
	_home = Vector2.from_angle(randf() * TAU) * Balance.PET_LEASH_DIST
	_act_left = randf_range(0.3, 1.0)


func _physics_process(delta: float) -> void:
	if not is_instance_valid(player) or not GameState.run_active:
		return
	_anim += delta
	_sprite.frame = int(_anim * 5.0) % 4
	_talk_left -= delta
	if _talk_left <= 0.0:
		_talk_left = BANTER.next_delay()
		BANTER.say(self, DRUNK_LINES if kind == &"drunk" else GRANNY_LINES, Color(0.6, 1.0, 1.0) if kind == &"drunk" else Color(1.0, 0.5, 0.95))
	_sprite.position.y = sin(_anim * 3.0) * 2.0   # парит
	_follow(delta)
	_act_left -= delta
	if _act_left <= 0.0:
		_act_left = Balance.GHOST_DRUNK_THROW_SEC if kind == &"drunk" else Balance.GHOST_GRANNY_ACT_SEC
		_act()


func _follow(delta: float) -> void:
	# духи кружатся вокруг игрока: у каждого своё место на кольце, кольцо медленно вращается
	var spin: float = _anim * (0.9 if kind == &"granny" else -0.7)
	var goal: Vector2 = player.global_position + _home.rotated(spin)
	if kind == &"drunk":
		goal += Vector2.from_angle(_anim * 4.0) * Balance.GHOST_DRUNK_WOBBLE * 0.08   # пошатывает
	var step: Vector2 = goal - global_position
	global_position = global_position.lerp(goal, 1.0 - exp(-5.0 * delta))
	if absf(step.x) > 0.5:
		_sprite.flip_h = step.x < 0.0


func _act() -> void:
	if kind == &"granny" and randf() < Balance.GHOST_GRANNY_HEAL_CHANCE:
		if player.has_method(&"heal"):
			player.call(&"heal", Balance.GHOST_GRANNY_HEAL)
			HitFx.popup(get_tree(), player.global_position + Vector2(0.0, -16.0), "+%d ХП: БАБКА ШЕПЧЕТ" % roundi(Balance.GHOST_GRANNY_HEAL), Color(1.0, 0.0627, 0.94), 12.0, 0.9)
		return
	var target: Node2D = _nearest_enemy()
	if target == null:
		return
	var damage: float = Balance.GHOST_DRUNK_DAMAGE if kind == &"drunk" else Balance.GHOST_GRANNY_SLIPPER_DAMAGE
	var projectile: Projectile = PoolManager.acquire(PROJECTILE_SCENE) as Projectile
	get_tree().current_scene.add_child(projectile)
	projectile.launch(global_position, global_position.direction_to(target.global_position), damage * GameState.damage_mult, Balance.GHOST_THROW_SPEED, 1.4)
	projectile.ricochets = 0
	projectile.burn_sec = 0.0
	projectile.slow_sec = 0.0
	projectile.set_texture(BOTTLE if kind == &"drunk" else SLIPPER)
	if kind == &"drunk":
		HitFx.popup(get_tree(), global_position + Vector2(0.0, -14.0), "ИК!", Color(0.968627, 1.0, 0.0), 12.0, 0.5)


func _nearest_enemy() -> Node2D:
	var best: Node2D = null
	var best_sq: float = Balance.GHOST_THROW_RANGE * Balance.GHOST_THROW_RANGE
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		if enemy == null:
			continue
		var dist_sq: float = global_position.distance_squared_to(enemy.global_position)
		if dist_sq < best_sq:
			best_sq = dist_sq
			best = enemy
	return best
