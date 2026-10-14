extends ColorRect
## Корень уровня. Сбрасывает состояние забега, задаёт размер арены, ставит игрока в центр.

const ENTER_SEC: float = 0.8

@onready var _player: Node2D = $Player


func _enter_tree() -> void:
	# До _ready() детей: игрок и HUD сразу видят свежее состояние (и сброшенные перки).
	GameState.reset_run()


func _ready() -> void:
	size = Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE)
	_enter_from_top()
	add_child(CompanionManager.new())
	EventBus.run_won.connect(_open_gate)
	if not GameState.weapons.is_empty():
		# у персонажа своё стартовое оружие: выдаём его и запускаем 1-ю волну без выбора
		EventBus.weapons_changed.emit()
		EventBus.perk_chosen.emit(StringName("w_" + String(GameState.weapons[0]["id"])))


## Герой приходит сверху арены (с кладбища) и идёт к центру; пока идёт, управление заблокировано.
func _enter_from_top() -> void:
	var center: Vector2 = size / 2.0
	_player.position = Vector2(center.x, 6.0)
	var animator: FrameAnimatorComponent = _player.get_node_or_null("FrameAnimator") as FrameAnimatorComponent
	_player.set_physics_process(false)
	if animator != null:
		animator.row = 2
		animator.active = true
	var tween: Tween = create_tween()
	tween.tween_property(_player, "position", center, ENTER_SEC)
	await tween.finished
	_player.set_physics_process(true)


## Босс убит: внизу арены открываются ворота на кладбище.
func _open_gate() -> void:
	get_tree().paused = false
	var gate: Node2D = Node2D.new()
	gate.set_script(preload("res://scripts/levels/win_gate.gd"))
	gate.position = Vector2(size.x * 0.5, size.y)
	add_child(gate)
	HitFx.popup(get_tree(), _player.global_position + Vector2(0.0, -20.0), FlavorText.random_win(), Color(0.968627, 1.0, 0.0), 18.0, 2.5)
	HitFx.popup(get_tree(), _player.global_position + Vector2(0.0, 8.0), "ВАЛИ В ВОРОТА ВНИЗУ", Color(0.2235, 1.0, 0.0784), 14.0, 3.0)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"toggle_fullscreen"):
		var is_full: bool = DisplayServer.window_get_mode() == DisplayServer.WINDOW_MODE_FULLSCREEN
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED if is_full else DisplayServer.WINDOW_MODE_FULLSCREEN)
