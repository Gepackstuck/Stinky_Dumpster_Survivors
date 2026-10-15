class_name CompanionManager
extends Node
## Питомцы и структуры из предметов: появляются в начале волны рядом с игроком, исчезают в конце (как в Brotato).

const GROUP: StringName = &"companions"
const PET_DOG: GDScript = preload("res://scripts/weapons/pet_dog.gd")
const PET_PIGEON: GDScript = preload("res://scripts/weapons/pet_pigeon.gd")
const MINE: GDScript = preload("res://scripts/weapons/mine_structure.gd")
const LAMP: GDScript = preload("res://scripts/weapons/lamp_structure.gd")
const MORTAR: GDScript = preload("res://scripts/weapons/mortar_structure.gd")


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
		turret.global_position = _spaced(_spawn_point.bind(player.global_position))
	for i: int in GameState.pet_count:
		var rat: PetRat = PetRat.new()
		rat.player = player
		rat.add_to_group(GROUP)
		root.add_child(rat)
		rat.global_position = _spaced(_spawn_point.bind(player.global_position))


	for kind: StringName in [&"drunk", &"granny"]:
		var count: int = GameState.ghost_drunk_count if kind == &"drunk" else GameState.ghost_granny_count
		for i: int in count:
			var ghost: PetGhost = PetGhost.new()
			ghost.kind = kind
			ghost.player = player
			ghost.add_to_group(GROUP)
			root.add_child(ghost)
			ghost.global_position = _spaced(_spawn_point.bind(player.global_position))

	for i: int in int(GameState.comp_counts.get(&"dogs", 0)):
		var dog: Node2D = PET_DOG.new()
		dog.set(&"player", player)
		dog.add_to_group(GROUP)
		root.add_child(dog)
		dog.global_position = _spaced(_spawn_point.bind(player.global_position))
	for i: int in int(GameState.comp_counts.get(&"pigeons", 0)):
		var pigeon: Node2D = PET_PIGEON.new()
		pigeon.set(&"player", player)
		pigeon.add_to_group(GROUP)
		root.add_child(pigeon)
		pigeon.global_position = _spaced(_spawn_point.bind(player.global_position))
	for i: int in int(GameState.comp_counts.get(&"mines", 0)):
		var mine: Node2D = MINE.new()
		mine.add_to_group(GROUP)
		root.add_child(mine)
		mine.global_position = _spaced(_scatter_point.bind(player.global_position))
	for i: int in int(GameState.comp_counts.get(&"lamps", 0)):
		var lamp: Node2D = LAMP.new()
		lamp.add_to_group(GROUP)
		root.add_child(lamp)
		lamp.global_position = _spaced(_near_point.bind(player.global_position))
	for i: int in int(GameState.comp_counts.get(&"mortars", 0)):
		var mortar: Node2D = MORTAR.new()
		mortar.add_to_group(GROUP)
		root.add_child(mortar)
		mortar.global_position = _spaced(_spawn_point.bind(player.global_position))
	_assign_slots()


func _spawn_point(center: Vector2) -> Vector2:
	var offset: Vector2 = Vector2.from_angle(randf() * TAU) * randf_range(Balance.STRUCTURE_SPAWN_MIN_DIST, Balance.STRUCTURE_SPAWN_MAX_DIST)
	return (center + offset).clamp(Vector2(8.0, 8.0), Vector2(Balance.ARENA_SIZE - 8.0, Balance.ARENA_SIZE - 8.0))


## Мины разбрасываются шире: чтобы враги на них налетали.
func _scatter_point(center: Vector2) -> Vector2:
	var offset: Vector2 = Vector2.from_angle(randf() * TAU) * randf_range(Balance.MINE_SPAWN_MIN_DIST, Balance.MINE_SPAWN_MAX_DIST)
	return (center + offset).clamp(Vector2(8.0, 8.0), Vector2(Balance.ARENA_SIZE - 8.0, Balance.ARENA_SIZE - 8.0))


## Лампа стоит почти вплотную к игроку: вонь должна накрывать и его самого, и тех, кто до него добрался.
func _near_point(center: Vector2) -> Vector2:
	var offset: Vector2 = Vector2.from_angle(randf() * TAU) * randf_range(14.0, 34.0)
	return (center + offset).clamp(Vector2(8.0, 8.0), Vector2(Balance.ARENA_SIZE - 8.0, Balance.ARENA_SIZE - 8.0))


## Точка не ближе 18 пикселей к уже стоящим питомцам и постройкам — чтобы каждого было видно.
func _spaced(maker: Callable) -> Vector2:
	var best: Vector2 = maker.call()
	var best_gap: float = -1.0
	for attempt: int in 14:
		var candidate: Vector2 = maker.call()
		var gap: float = 1000.0
		for node: Node in get_tree().get_nodes_in_group(GROUP):
			if node is Node2D and not node.is_queued_for_deletion():
				gap = minf(gap, (node as Node2D).global_position.distance_to(candidate))
		if gap > best_gap:
			best_gap = gap
			best = candidate
		if gap >= 18.0:
			break
	return best


## Ходячие спутники делят кольцо вокруг игрока поровну: у каждого своё место, никто не стоит друг на друге.
func _assign_slots() -> void:
	var followers: Array[Node2D] = []
	for node: Node in get_tree().get_nodes_in_group(GROUP):
		if node is Node2D and "_home" in node:
			followers.append(node as Node2D)
	var count: int = followers.size()
	for i: int in count:
		var ring: float = Balance.PET_LEASH_DIST * (1.0 + 0.55 * float(i % 2))
		followers[i].set(&"_home", Vector2.from_angle(TAU * float(i) / float(maxi(count, 1))) * ring)
	var pigeons: Array[Node] = get_tree().get_nodes_in_group(GROUP).filter(func(n: Node) -> bool: return "_orbit" in n)
	for i: int in pigeons.size():
		pigeons[i].set(&"_orbit", TAU * float(i) / float(pigeons.size()))
