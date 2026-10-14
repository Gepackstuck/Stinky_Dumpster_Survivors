class_name PauseMenu
extends CanvasLayer
## Простейшее меню паузы по Esc: продолжить / заново / выйти.

const PANELS: Texture2D = preload("res://assets/ui/death_panels.png")
const PANEL_SIZE: Vector2 = Vector2(360.0, 160.0)
const PANEL_VARIANTS: int = 4

@onready var _root: Control = $Root
@onready var _panel: TextureRect = $Root/Panel
@onready var _resume: Button = $Root/Resume
@onready var _restart: Button = $Root/Restart
@onready var _quit: Button = $Root/Quit


func _ready() -> void:
	_root.hide()
	_resume.pressed.connect(_close)
	_restart.pressed.connect(_on_restart)
	_quit.pressed.connect(func() -> void: get_tree().quit())


func _input(event: InputEvent) -> void:
	if not _root.visible:
		return
	var step: int = 0
	if event.is_action_pressed(&"move_up"):
		step = -1
	elif event.is_action_pressed(&"move_down"):
		step = 1
	if step == 0:
		return
	get_viewport().set_input_as_handled()  # W/S и стрелки — между кнопками
	var buttons: Array[Button] = [_resume, _restart, _quit]
	var current: int = 0
	for i: int in buttons.size():
		if buttons[i].has_focus():
			current = i
	buttons[posmod(current + step, buttons.size())].grab_focus()


func _unhandled_input(event: InputEvent) -> void:
	var key: InputEventKey = event as InputEventKey
	if key == null or not key.pressed or key.echo or key.keycode != KEY_ESCAPE:
		return
	get_viewport().set_input_as_handled()
	if _root.visible:
		_close()
	elif not get_tree().paused and GameState.run_active and GameState.wave > 0:
		_open()


func _open() -> void:
	var panel: AtlasTexture = AtlasTexture.new()
	panel.atlas = PANELS
	panel.region = Rect2(Vector2(randi_range(0, PANEL_VARIANTS - 1) * PANEL_SIZE.x, 0.0), PANEL_SIZE)
	_panel.texture = panel
	_root.show()
	get_tree().paused = true
	_resume.grab_focus()


func _close() -> void:
	_root.hide()
	get_tree().paused = false


func _on_restart() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()
