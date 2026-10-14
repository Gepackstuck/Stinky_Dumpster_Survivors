class_name CompanionManager
extends Node
## Питомцы и структуры из предметов: появляются в начале волны рядом с игроком, исчезают в конце (как в Brotato).

const GROUP: StringName = &"companions"


func _ready() -> void:
	EventBus.wave_started.connect(func(_wave: int) -> void: _respawn())
	EventBus.wave_ended.connect(func(_wave: int) -> void: _clear())
	EventBus.player_died.connect(_clear)
	EventBus.run_won.connect(_clear)


func _clear() -> void:
	for node: Node in get_tree().get_nodes_in_group(GROUP):
		node.queue_free()


func _respawn() -> void:
	_clear()
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player == null:
		return
	var root: Node = get_tree().current_scene
	for i: int in GameState.turret_count:
		var turret: TurretStructure = TurretStructure.new()
		turret.weapon_id = &"turret"
		turret.add_to_group(GROUP)
		root.add_child(turret)
		turret.global_position = _spawn_point(player.global_position)
	for i: int in GameState.pet_count:
		var rat: PetRat = PetRat.new()
		rat.player = player
		rat.add_to_group(GROUP)
		root.add_child(rat)
		rat.global_position = _spawn_point(player.global_position)


	for kind: StringName in [&"drunk", &"granny"]:
		var count: int = GameState.ghost_drunk_count if kind == &"drunk" else GameState.ghost_granny_count
		for i: int in count:
			var ghost: PetGhost = PetGhost.new()
			ghost.kind = kind
			ghost.player = player
			ghost.add_to_group(GROUP)
			root.add_child(ghost)
			ghost.global_position = _spawn_point(player.global_position)


func _spawn_point(center: Vector2) -> Vector2:
	var offset: Vector2 = Vector2.from_angle(randf() * TAU) * randf_range(Balance.STRUCTURE_SPAWN_MIN_DIST, Balance.STRUCTURE_SPAWN_MAX_DIST)
	return (center + offset).clamp(Vector2(8.0, 8.0), Vector2(Balance.ARENA_SIZE - 8.0, Balance.ARENA_SIZE - 8.0))
