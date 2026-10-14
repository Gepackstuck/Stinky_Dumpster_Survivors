class_name DeathScreen
extends CanvasLayer
## Экран смерти: случайная фраза, статистика, кнопка «Ещё раз».

@onready var _root: Control = $Root
@onready var _title: Label = $Root/Title
@onready var _stats: Label = $Root/Stats
@onready var _retry: Button = $Root/RetryButton


func _ready() -> void:
	_root.hide()
	_retry.pressed.connect(_on_retry)
	EventBus.player_died.connect(_on_player_died)


func _unhandled_input(event: InputEvent) -> void:
	if _root.visible and event.is_action_pressed(&"ui_accept"):
		get_viewport().set_input_as_handled()
		_on_retry()


func _on_player_died() -> void:
	_title.text = FlavorText.random_death()
	_stats.text = "УБИТО: %d\nУРОВЕНЬ: %d" % [GameState.kills, GameState.level]
	_root.show()
	_retry.grab_focus()
	get_tree().paused = true


func _on_retry() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()
