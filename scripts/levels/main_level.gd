extends ColorRect
## Корень уровня. Задаёт размер арены, ставит игрока в центр и стартует забег.

@onready var _player: Node2D = $Player


func _ready() -> void:
	size = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)
	_player.position = size / 2.0
	GameState.reset_run()
