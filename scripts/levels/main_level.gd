extends ColorRect
## Корень уровня. Сбрасывает состояние забега, задаёт размер арены, ставит игрока в центр.

@onready var _player: Node2D = $Player


func _enter_tree() -> void:
	# До _ready() детей: игрок и HUD сразу видят свежее состояние (и сброшенные перки).
	GameState.reset_run()


func _ready() -> void:
	size = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)
	_player.position = size / 2.0
	add_child(CompanionManager.new())
	if not GameState.weapons.is_empty():
		# у персонажа своё стартовое оружие: выдаём его и запускаем 1-ю волну без выбора
		EventBus.weapons_changed.emit()
		EventBus.perk_chosen.emit(StringName("w_" + String(GameState.weapons[0]["id"])))


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"toggle_fullscreen"):
		var is_full: bool = DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if is_full else DisplayServer.WINDOW_MODE_FULLSCREEN)
