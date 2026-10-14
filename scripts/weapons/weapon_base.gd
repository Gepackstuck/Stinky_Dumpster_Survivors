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
	var base_direction: Vector2 = global_position.direction_to(target.global_position)
	var count: int = 1 + GameState.extra_projectiles
	var damage: float = _damage * GameState.projectile_damage_mult
	var spread: float = deg_to_rad(Balance.PERK_DOUBLE_SHOT_SPREAD_DEG)
	var root: Node = get_tree().current_scene
	for i: int in count:
		var angle: float = (i - (count - 1) * 0.5) * spread
		var projectile: Projectile = PoolManager.acquire(PROJECTILE_SCENE) as Projectile
		root.add_child(projectile)
		projectile.launch(global_position, base_direction.rotated(angle), damage, Balance.PROJECTILE_SPEED, Balance.PROJECTILE_LIFETIME_SEC)


func _on_player_died() -> void:
	set_physics_process(false)
