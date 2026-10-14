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
var _ricochets: int = 0
var _ricochet_range: float = 0.0
var _burn_dps: float = 0.0
var _burn_sec: float = 0.0
var _slow_factor: float = 1.0
var _slow_sec: float = 0.0
var _texture: Texture2D = preload("res://assets/sprites/projectile.png")


var tier: int = 1  # тир I-IV, ставится до add_child


func _ready() -> void:
	var stats: Dictionary = Balance.WEAPONS[weapon_id]
	_damage = stats["damage"] * Balance.WEAPON_TIER_DAMAGE[tier - 1]
	_cooldown_sec = stats["cooldown"] * Balance.WEAPON_TIER_COOLDOWN[tier - 1]
	_ricochets = stats.get("ricochets", 0)
	_ricochet_range = stats.get("ricochet_range", 0.0)
	_burn_dps = stats.get("burn_dps", 0.0) * Balance.WEAPON_TIER_DAMAGE[tier - 1]
	_burn_sec = stats.get("burn_duration", 0.0)
	_slow_factor = stats.get("slow_factor", 1.0)
	_slow_sec = stats.get("slow_duration", 0.0)
	if stats.has("projectile"):
		_texture = load(stats["projectile"]) as Texture2D
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
	_cooldown_left = GameState.cooldown_for(_cooldown_sec)


## Ближайшая цель: враги в приоритете, бак считается «в 1.5 раза дальше» — но если он заметно ближе, бьём по нему.
func _find_nearest_enemy() -> Node2D:
	var nearest: Node2D = null
	var best_sq: float = _range_sq
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		var dist_sq: float = global_position.distance_squared_to(enemy.global_position)
		if dist_sq < best_sq:
			best_sq = dist_sq
			nearest = enemy
	for node: Node in get_tree().get_nodes_in_group(&"neutrals"):
		var bin: Node2D = node as Node2D
		var dist_sq: float = global_position.distance_squared_to(bin.global_position) * 2.25
		if dist_sq < best_sq:
			best_sq = dist_sq
			nearest = bin
	return nearest


func _fire(target: Node2D) -> void:
	var base_direction: Vector2 = global_position.direction_to(target.global_position)
	var count: int = 1 + GameState.extra_projectiles
	var damage: float = GameState.roll_damage(_damage)
	var spread: float = deg_to_rad(Balance.PERK_DOUBLE_SHOT_SPREAD_DEG)
	var root: Node = get_tree().current_scene
	for i: int in count:
		var angle: float = (i - (count - 1) * 0.5) * spread
		var projectile: Projectile = PoolManager.acquire(PROJECTILE_SCENE) as Projectile
		root.add_child(projectile)
		projectile.launch(global_position, base_direction.rotated(angle), damage, Balance.PROJECTILE_SPEED, Balance.PROJECTILE_LIFETIME_SEC)
		projectile.ricochets = _ricochets
		projectile.ricochet_range = _ricochet_range
		projectile.burn_dps = _burn_dps * GameState.damage_mult
		projectile.burn_sec = _burn_sec
		projectile.slow_factor = _slow_factor
		projectile.slow_sec = _slow_sec
		projectile.set_texture(_texture)


func _on_player_died() -> void:
	set_physics_process(false)
