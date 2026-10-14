extends Node
## Текущее состояние забега. Autoload: GameState.

var hp: float = 0.0
var max_hp: float = 0.0
var xp: int = 0
var level: int = 1
var coins: int = 0
var kills: int = 0
var wave: int = 0
var time: float = 0.0
var run_active: bool = false


func _ready() -> void:
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_died.connect(_on_player_died)


## Сбросить состояние перед новым забегом.
func reset_run() -> void:
	max_hp = Balance.PLAYER_MAX_HP
	hp = max_hp
	xp = 0
	level = 1
	coins = 0
	kills = 0
	wave = 0
	time = 0.0
	run_active = true
	EventBus.run_started.emit()


func _on_enemy_died(_enemy_id: StringName, _position: Vector2) -> void:
	kills += 1


func _on_player_died() -> void:
	run_active = false
	EventBus.run_ended.emit()
