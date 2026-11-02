class_name Commentator
extends Control
## Комментатор-бомж: редкие злобные реплики внизу экрана в ключевые моменты (не чаще Balance.COMMENT_GAP_SEC).
## Портрет - голова Бомжа Васи, реплики - FlavorText.COMMENTS[повод].

var _icon: Sprite2D
var _label: Label
var _last: float = -100.0
var _was_low: bool = false


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	position = Vector2(4.0, 238.0)
	_icon = Sprite2D.new()
	_icon.texture = CharacterLibrary.sprite_sheet(&"hobo")
	_icon.hframes = 4
	_icon.vframes = 3
	_icon.frame = 8
	_icon.region_enabled = false
	_icon.position = Vector2(12.0, 14.0)
	_icon.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(_icon)
	_label = Label.new()
	_label.position = Vector2(26.0, 6.0)
	_label.size = Vector2(300.0, 20.0)
	_label.add_theme_color_override(&"font_color", Color(0.95, 0.95, 0.85))
	_label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	add_child(_label)
	modulate.a = 0.0
	EventBus.boss_spawned.connect(func(_id: StringName) -> void: _say(&"boss"))
	EventBus.streak_changed.connect(func(t: int, _b: float, broken: bool) -> void: _say(&"streak_break" if broken else (&"streak" if t >= 2 else &"")))
	EventBus.pile_stepped.connect(func() -> void: _say(&"pile", true))
	EventBus.ult_used.connect(func(_k: StringName) -> void: _say(&"ult"))
	EventBus.parried.connect(func(_at: Vector2) -> void: _say(&"parry"))
	EventBus.wave_ended.connect(func(_w: int) -> void:
		if GameState.hp < GameState.max_hp * 0.2:
			_say(&"survived", true))


func _process(_delta: float) -> void:
	var low: bool = GameState.run_active and GameState.hp < GameState.max_hp * 0.25 and GameState.hp > 0.0
	if low and not _was_low:
		_say(&"low_hp")
	_was_low = low


func _say(reason: StringName, force: bool = false) -> void:
	if reason == &"":
		return
	var now: float = Time.get_ticks_msec() / 1000.0
	if not force and now - _last < Balance.COMMENT_GAP_SEC:
		return
	var lines: Array = FlavorText.COMMENTS.get(reason, [])
	if lines.is_empty():
		return
	_last = now
	_label.text = "ВАСЯ: " + String(lines[randi() % lines.size()])
	var tw: Tween = create_tween()
	tw.tween_property(self, "modulate:a", 1.0, 0.15)
	tw.tween_interval(Balance.COMMENT_SHOW_SEC)
	tw.tween_property(self, "modulate:a", 0.0, 0.4)
