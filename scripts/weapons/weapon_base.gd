class_name WeaponBase
extends Node2D
## Автоатака: стреляет по ближайшему врагу в радиусе. Числа — из Balance.WEAPONS.
## Шаг 1: единственное оружие — заглушка на статах `lighter`.

const PROJECTILE_SCENE: PackedScene = preload("res://scenes/weapons/projectile.tscn")
const RETARGET_INTERVAL_SEC: float = 0.1  # как часто искать цель, пока врагов в радиусе нет

@export var weapon_id: StringName = &"lighter"

var _damage: float = 0.0
var _cooldown_sec: float = 0.0
var _cooldown_left: float = 0.0
var _range_sq: float = 0.0


func _ready() -> void:
	var stats: Dictionary = Balance.WEAPONS[weapon_id]
	_damage = stats["damage"]
	_cooldown_sec = stats["cooldown"]
	_range_sq = Balance.WEAPON_TARGET_RANGE * Balance.WEAPON_TARGET_RANGE
	EventBus.player_died.connect(_on_player_died)


func _physics_process(delta: float) -> void:
	_cooldown_left -= delta
	if _cooldown_left > 0.0:
		return
	var target: Node2D = _find_nearest_enemy()
	if target == null:
		_cooldown_left = RETARGET_INTERVAL_SEC
		return
	_fire(target)
	_cooldown_left = _cooldown_sec


func _find_nearest_enemy() -> Node2D:
	var nearest: Node2D = null
	var best_sq: float = _range_sq
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		var dist_sq: float = global_position.distance_squared_to(enemy.global_position)
		if dist_sq < best_sq:
			best_sq = dist_sq
			nearest = enemy
	return nearest


func _fire(target: Node2D) -> void:
	var direction: Vector2 = global_position.direction_to(target.global_position)
	var projectile: Projectile = PoolManager.acquire(PROJECTILE_SCENE) as Projectile
	get_tree().current_scene.add_child(projectile)
	projectile.launch(global_position, direction, _damage, Balance.PROJECTILE_SPEED, Balance.PROJECTILE_LIFETIME_SEC)


func _on_player_died() -> void:
	set_physics_process(false)
