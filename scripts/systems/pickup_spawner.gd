class_name PickupSpawner
extends Node
## Роняет XP-пиксели на месте убитых врагов (слушает EventBus.enemy_died).

const XP_PICKUP_SCENE: PackedScene = preload("res://scenes/pickups/xp_pickup.tscn")

@export var pickups_root: Node


func _ready() -> void:
	EventBus.enemy_died.connect(_on_enemy_died)


func _on_enemy_died(enemy_id: StringName, death_position: Vector2) -> void:
	var stats: Dictionary = Balance.ENEMIES[enemy_id]
	# Отложенно: враг умирает внутри физического колбэка, а добавлять Area2D в дерево тогда нельзя.
	_spawn_xp.call_deferred(death_position, stats["xp"])


func _spawn_xp(at: Vector2, value: int) -> void:
	var pickup: XpPickup = PoolManager.acquire(XP_PICKUP_SCENE) as XpPickup
	pickups_root.add_child(pickup)
	var scatter: Vector2 = Vector2(
		randf_range(-Balance.XP_DROP_SCATTER, Balance.XP_DROP_SCATTER),
		randf_range(-Balance.XP_DROP_SCATTER, Balance.XP_DROP_SCATTER))
	pickup.setup(at + scatter, value)
