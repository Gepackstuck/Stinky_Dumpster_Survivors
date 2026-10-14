class_name AuraWeapon
extends Node2D
## Вонючий носок: периодическая волна вони вокруг игрока бьёт всех врагов в радиусе.

@export var weapon_id: StringName = &"sock"

var _damage: float = 0.0
var _cooldown_sec: float = 1.0
var _cooldown_left: float = 0.0
var _radius: float = 60.0
var _wave: float = -1.0  # 0..1 — прогресс кольца, -1 — не рисуем


func _ready() -> void:
	var stats: Dictionary = Balance.WEAPONS[weapon_id]
	_damage = stats["damage"]
	_cooldown_sec = stats["cooldown"]
	_radius = stats["radius"]
	EventBus.player_died.connect(set_physics_process.bind(false))


func _physics_process(delta: float) -> void:
	if _wave >= 0.0:
		_wave += delta * 4.0
		if _wave > 1.0:
			_wave = -1.0
		queue_redraw()
	_cooldown_left -= delta
	if _cooldown_left > 0.0:
		return
	_cooldown_left = GameState.cooldown_for(_cooldown_sec)
	var r_sq: float = _radius * _radius
	var hit_any: bool = false
	for node: Node in get_tree().get_nodes_in_group(&"enemies") + get_tree().get_nodes_in_group(&"neutrals"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null and global_position.distance_squared_to(enemy.global_position) <= r_sq:
			enemy.hit_by_weapon(GameState.roll_damage(_damage))
			hit_any = true
	if hit_any:
		_wave = 0.0
		HitFx.burst(get_tree(), global_position, Color(0.2235, 1.0, 0.0784), 10, _radius * 1.2, 3.0, 0.5, true)


func _draw() -> void:
	if _wave < 0.0:
		return
	var r: float = _radius * _wave
	var a: float = 1.0 - _wave
	draw_arc(Vector2.ZERO, r, 0.0, TAU, 28, Color(0.2235, 1.0, 0.0784, a), 2.0)
	draw_arc(Vector2.ZERO, r * 0.8, 0.0, TAU, 24, Color(0.9686, 1.0, 0.0, a * 0.7), 1.0)
