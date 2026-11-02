class_name WeaponBase
extends Node2D
## Автоатака: стреляет по ближайшему врагу в радиусе. Числа — из Balance.WEAPONS.
## Шаг 1: единственное оружие — заглушка на статах `lighter`.

const TEX: GDScript = preload("res://scripts/systems/tex.gd")
const PROJECTILE_SCENE: PackedScene = preload("res://scenes/weapons/projectile.tscn")
const MUZZLE_DIST: float = 6.0                # кончик оружия от его центра
const RETARGET_INTERVAL_SEC: float = 0.1  # как часто искать цель, пока врагов в радиусе нет

signal fired(direction: Vector2)  # выстрел: для показа оружия в руках

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
var _pellets: int = 1
var _spread_deg: float = 0.0
var _jitter_deg: float = 0.0
var _proj_speed: float = 0.0
var _proj_life: float = 0.0
var _pierce: int = 0
var _texture: Texture2D = preload("res://assets/sprites/projectile.png")


var tier: int = 1  # тир I-IV, ставится до add_child


func _ready() -> void:
	var stats: Dictionary = Balance.WEAPONS[weapon_id]
	_damage = stats["damage"] * Balance.WEAPON_TIER_DAMAGE[tier - 1]
	_cooldown_sec = stats["cooldown"] * Balance.WEAPON_TIER_COOLDOWN[tier - 1]
	_ricochets = WeaponLibrary.stat(weapon_id, tier, "ricochets", 0)
	_ricochet_range = WeaponLibrary.stat(weapon_id, tier, "ricochet_range", 0.0)
	_burn_dps = stats.get("burn_dps", 0.0) * Balance.WEAPON_TIER_DAMAGE[tier - 1]
	_burn_sec = WeaponLibrary.stat(weapon_id, tier, "burn_duration", 0.0)
	_slow_factor = stats.get("slow_factor", 1.0)
	_slow_sec = WeaponLibrary.stat(weapon_id, tier, "slow_duration", 0.0)
	_pellets = WeaponLibrary.stat(weapon_id, tier, "pellets", 1)
	_spread_deg = stats.get("spread_deg", 0.0)
	_jitter_deg = stats.get("jitter_deg", 0.0)
	_proj_speed = stats.get("proj_speed", Balance.PROJECTILE_SPEED)
	_proj_life = WeaponLibrary.stat(weapon_id, tier, "proj_life", Balance.PROJECTILE_LIFETIME_SEC)
	_pierce = WeaponLibrary.stat(weapon_id, tier, "pierce", 0)
	if stats.has("projectile"):
		_texture = TEX.load_tex(stats["projectile"])
	var reach: float = stats.get("range", Balance.WEAPON_TARGET_RANGE)
	_range_sq = reach * reach
	EventBus.player_died.connect(_on_player_died)


const CLAIM_FRAMES: int = 21   # ~0.35 с игрового времени (кадры физики, а не реальные часы: бот гоняет игру на ускорении)
static var _claims: Dictionary = {}


## 0 - только что выстрелил, 1 - готово (для полоски в HUD).
func cooldown_ratio() -> float:
	var full: float = GameState.cooldown_for(_cooldown_sec)
	return 1.0 - clampf(_cooldown_left / maxf(full, 0.001), 0.0, 1.0)


func _physics_process(delta: float) -> void:
	_cooldown_left -= delta
	if _cooldown_left > 0.0:
		return
	var target: Node2D = _find_nearest_enemy()
	if target == null:
		_cooldown_left = RETARGET_INTERVAL_SEC
		return
	_claims[target.get_instance_id()] = Engine.get_physics_frames() + CLAIM_FRAMES
	_fire(target)
	var fire_dir: Vector2 = global_position.direction_to(target.global_position)
	HitFx.muzzle(get_tree(), _muzzle(target), fire_dir, Color(1.0, 0.5, 0.05) if _burn_dps > 0.0 else Color(1.0, 0.92, 0.25))
	fired.emit(global_position.direction_to(target.global_position))
	_cooldown_left = GameState.cooldown_for(_cooldown_sec)


## Ближайшая цель: враги в приоритете, бак считается «в 1.5 раза дальше» — но если он заметно ближе, бьём по нему.
func _find_nearest_enemy() -> Node2D:
	var nearest: Node2D = null
	var best_sq: float = _range_sq
	var fallback: Node2D = null
	var fallback_sq: float = _range_sq
	var now: int = Engine.get_physics_frames()
	if _claims.size() > 300:
		_claims.clear()
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: Node2D = node as Node2D
		var dist_sq: float = global_position.distance_squared_to(enemy.global_position)
		if dist_sq < fallback_sq:
			fallback_sq = dist_sq
			fallback = enemy
		# оружия не лупят все по одному врагу: цель, на которую недавно навёлся другой ствол, пропускаем
		if dist_sq < best_sq and _claims.get(enemy.get_instance_id(), 0) <= now:
			best_sq = dist_sq
			nearest = enemy
	if nearest == null:
		nearest = fallback
		best_sq = fallback_sq
	for node: Node in get_tree().get_nodes_in_group(&"neutrals"):
		var bin: Node2D = node as Node2D
		var dist_sq: float = global_position.distance_squared_to(bin.global_position) * 2.25
		if dist_sq < best_sq:
			best_sq = dist_sq
			nearest = bin
	return nearest


## Откуда вылетает снаряд: из кончика оружия в руках героя (а не из центра тела).
func _muzzle(target: Node2D) -> Vector2:
	for child: Node in get_children():
		if child.has_method(&"sprite_global"):
			var hand: Vector2 = child.call(&"sprite_global")
			return hand + hand.direction_to(target.global_position) * MUZZLE_DIST
	return global_position


func _fire(target: Node2D) -> void:
	var origin: Vector2 = _muzzle(target)
	var base_direction: Vector2 = origin.direction_to(target.global_position)
	var count: int = _pellets + GameState.extra_projectiles
	var damage: float = GameState.roll_damage(_damage)
	var spread: float = deg_to_rad(Balance.PERK_DOUBLE_SHOT_SPREAD_DEG)
	var root: Node = get_tree().current_scene
	for i: int in count:
		var angle: float = (i - (count - 1) * 0.5) * (spread if _pellets == 1 else deg_to_rad(_spread_deg))
		var mod_spread: float = WaveRules.mod_f("spread", 0.0)   # модификатор «кривые руки»
		if mod_spread > 0.0:
			angle += deg_to_rad(randf_range(-mod_spread, mod_spread))
		if _jitter_deg > 0.0:
			angle += deg_to_rad(randf_range(-_jitter_deg, _jitter_deg))
		var projectile: Projectile = PoolManager.acquire(PROJECTILE_SCENE) as Projectile
		root.add_child(projectile)
		projectile.launch(origin, base_direction.rotated(angle), damage, _proj_speed, _proj_life)
		projectile.pierce = _pierce
		projectile.ricochets = _ricochets
		projectile.ricochet_range = _ricochet_range
		projectile.burn_dps = _burn_dps * GameState.damage_mult
		projectile.burn_sec = _burn_sec
		projectile.slow_factor = _slow_factor
		projectile.slow_sec = _slow_sec
		projectile.set_texture(_pick_texture())
		projectile.trail_kind = &"flame" if _burn_dps > 0.0 else &"tracer"
		projectile.trail_color = Color(1.0, 0.5, 0.05) if _burn_dps > 0.0 else (Color(0.5, 1.0, 1.0) if _slow_sec > 0.0 else Color(1.0, 0.92, 0.25))


## Рогатка стреляет мелочью: камень или кусок кала (случайно).
func _pick_texture() -> Texture2D:
	if weapon_id == &"slingshot":
		return TEX.load_tex("res://assets/sprites/proj_stone.png" if randf() < 0.5 else "res://assets/sprites/proj_dung.png")
	return _texture


func _on_player_died() -> void:
	set_physics_process(false)
