class_name Spawner
extends Node
## Простой спавнер (Шаг 1): держит Balance.ENEMY_TARGET_COUNT врагов вокруг игрока.
## Погибших пополняет раз в Balance.ENEMY_RESPAWN_INTERVAL_SEC. Волны — Шаг 3.

const ENEMY_SCENE: PackedScene = preload("res://scenes/enemies/enemy_base.tscn")

@export var player: Node2D
@export var enemies_root: Node

@onready var _respawn_timer: Timer = $RespawnTimer

var _alive: int = 0
var _arena_max: Vector2 = Vector2.ZERO


func _ready() -> void:
	_arena_max = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_died.connect(_on_player_died)
	_respawn_timer.wait_time = Balance.ENEMY_RESPAWN_INTERVAL_SEC
	_respawn_timer.timeout.connect(_fill)
	_fill.call_deferred()
	_respawn_timer.start()


func _fill() -> void:
	while _alive < Balance.ENEMY_TARGET_COUNT:
		_spawn_one()


func _spawn_one() -> void:
	var enemy: EnemyBase = PoolManager.acquire(ENEMY_SCENE) as EnemyBase
	enemies_root.add_child(enemy)
	enemy.setup(player, _random_spawn_position())
	_alive += 1


func _random_spawn_position() -> Vector2:
	var angle: float = randf() * TAU
	var distance: float = randf_range(Balance.ENEMY_SPAWN_RADIUS_MIN, Balance.ENEMY_SPAWN_RADIUS_MAX)
	var spawn_position: Vector2 = player.global_position + Vector2.from_angle(angle) * distance
	return spawn_position.clamp(Vector2.ZERO, _arena_max)


func _on_enemy_died(_enemy_id: StringName, _position: Vector2) -> void:
	_alive = maxi(_alive - 1, 0)


func _on_player_died() -> void:
	_respawn_timer.stop()
