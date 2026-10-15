extends Node2D
## Голубь-бомбардир: кружит над игроком и роняет помёт на ближайшего врага (удар по площади).

const TEX: GDScript = preload("res://scripts/systems/tex.gd")
const THROWN: GDScript = preload("res://scripts/weapons/thrown_slipper.gd")

var player: Node2D = null
var _sprite: Sprite2D = null
var _bomb_left: float = 0.0
var _anim: float = 0.0
var _orbit: float = 0.0


func _ready() -> void:
	_sprite = Sprite2D.new()
	_sprite.texture = TEX.load_tex("res://assets/sprites/pet_pigeon.png")
	_sprite.hframes = 2
	_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_sprite)
	_orbit = randf() * TAU
	_bomb_left = randf_range(0.5, 1.5)


func _physics_process(delta: float) -> void:
	if not is_instance_valid(player) or not GameState.run_active:
		return
	_anim += delta
	_orbit += delta * 1.3
	_sprite.frame = int(_anim * 8.0) % 2
	_sprite.position.y = -14.0 + sin(_anim * 5.0) * 2.0
	var goal: Vector2 = player.global_position + Vector2.from_angle(_orbit) * Balance.PIGEON_ORBIT_DIST
	var step: Vector2 = goal - global_position
	if step.length_squared() > 1.0:
		global_position += step.normalized() * minf(Balance.PIGEON_SPEED * delta, step.length())
		_sprite.flip_h = step.x < 0.0
	_bomb_left -= delta
	if _bomb_left <= 0.0:
		var target: Node2D = _nearest_enemy()
		if target != null:
			_bomb_left = Balance.PIGEON_BOMB_SEC
			_drop(target)
		else:
			_bomb_left = 0.2


func _drop(target: Node2D) -> void:
	var bomb: Node2D = THROWN.new()
	bomb.set(&"texture", TEX.load_tex("res://assets/sprites/proj_poop.png"))
	get_tree().current_scene.add_child(bomb)
	var aim: Vector2 = target.global_position
	var body: CharacterBody2D = target as CharacterBody2D
	if body != null:
		aim += body.velocity * 0.45
	bomb.call(&"launch", global_position + Vector2(0.0, -10.0), aim, Balance.PIGEON_BOMB_DAMAGE * GameState.damage_mult, Balance.PIGEON_BOMB_RADIUS, 0.45)


func _nearest_enemy() -> Node2D:
	var best: Node2D = null
	var best_sq: float = Balance.PIGEON_RANGE * Balance.PIGEON_RANGE
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		if enemy == null:
			continue
		var dist_sq: float = player.global_position.distance_squared_to(enemy.global_position)
		if dist_sq < best_sq:
			best_sq = dist_sq
			best = enemy
	return best
