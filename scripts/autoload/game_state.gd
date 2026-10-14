extends Node
## Текущее состояние забега. Autoload: GameState.
## TODO(MP1): подключить сигналы EventBus и обновлять поля.

var hp: float = 0.0
var max_hp: float = 0.0
var xp: int = 0
var level: int = 1
var coins: int = 0
var kills: int = 0
var wave: int = 0
var time: float = 0.0
var run_active: bool = false


## Сбросить состояние перед новым забегом.
func reset_run() -> void:
	# TODO(MP1): взять стартовые значения из Balance, эмитить EventBus.run_started.
	pass
