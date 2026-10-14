class_name Spawner
extends Node
## Спавнит врагов по командам WaveManager: группами, с красным крестом за секунду до появления.
## Враги живут на всей арене (не с краёв экрана) — как в Brotato.

const ENEMY_SCENE: PackedScene = preload("res://scenes/enemies/enemy_base.tscn")

@export var player: Node2D
@export var enemies_root: Node

var _arena_max: Vector2 = Vector2.ZERO
var _markers: Array[SpawnMarker] = []


func _ready() -> void:
	_arena_max = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)


## Группа из count врагов одного типа в случайной точке арены.
func spawn_group(enemy_id: StringName, count: int, hp_mult: float) -> void:
	var room: int = Balance.MAX_ALIVE_ENEMIES - get_tree().get_nodes_in_group(&"enemies").size() - _markers.size()
	count = mini(count, room)
	if count <= 0:
		return
	var center: Vector2 = _random_arena_point()
	for i: int in count:
		var offset: Vector2 = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)) * Balance.SPAWN_GROUP_SPREAD
		_add_marker((center + offset).clamp(Vector2.ZERO, _arena_max), enemy_id, hp_mult)


## Одиночный спавн (элита/босс) в случайной точке.
func spawn_single(enemy_id: StringName, hp_mult: float) -> void:
	_add_marker(_random_arena_point(), enemy_id, hp_mult)


## Конец волны: убрать всех врагов (без дропа и убийств) и отменить ещё не появившихся.
func clear_all() -> void:
	for marker: SpawnMarker in _markers:
		if is_instance_valid(marker):
			marker.queue_free()
	_markers.clear()
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null:
			enemy.vanish()


func _add_marker(at: Vector2, enemy_id: StringName, hp_mult: float) -> void:
	var marker: SpawnMarker = SpawnMarker.new()
	marker.enemy_id = enemy_id
	marker.hp_mult = hp_mult
	marker.position = at
	marker.expired.connect(_on_marker_expired)
	_markers.append(marker)
	enemies_root.get_parent().add_child(marker)


func _on_marker_expired(marker: SpawnMarker) -> void:
	_markers.erase(marker)
	var enemy: EnemyBase = PoolManager.acquire(ENEMY_SCENE) as EnemyBase
	enemies_root.add_child(enemy)
	enemy.setup(player, marker.position, marker.enemy_id, marker.hp_mult)


func _random_arena_point() -> Vector2:
	var margin: float = Balance.SPAWN_ARENA_MARGIN
	var point: Vector2 = Vector2.ZERO
	for attempt: int in 20:
		point = Vector2(randf_range(margin, _arena_max.x - margin), randf_range(margin, _arena_max.y - margin))
		if not is_instance_valid(player) or point.distance_to(player.global_position) >= Balance.SPAWN_MIN_DISTANCE_FROM_PLAYER:
			return point
	return point
