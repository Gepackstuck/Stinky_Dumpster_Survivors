extends ColorRect
## Корень уровня. Сбрасывает состояние забега, задаёт размер арены, ставит игрока в центр.

@onready var _player: Node2D = $Player


func _enter_tree() -> void:
	# До _ready() детей: игрок и HUD сразу видят свежее состояние (и сброшенные перки).
	GameState.reset_run()


func _ready() -> void:
	size = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)
	_player.position = size / 2.0
