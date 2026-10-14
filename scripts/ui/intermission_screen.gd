class_name IntermissionScreen
extends CanvasLayer
## Экран между волнами (как магазин в Brotato). Пока магазина нет (Шаг 5) — итог волны,
## превью следующей волны (элита/орда/боссы видны заранее, как в Brotato) и кнопка «Дальше».

const PANELS: Texture2D = preload("res://assets/ui/death_panels.png")
const PANEL_SIZE: Vector2 = Vector2(360.0, 160.0)
const PANEL_VARIANTS: int = 4

@onready var _root: Control = $Root
@onready var _panel: TextureRect = $Root/Panel
@onready var _title: Label = $Root/Title
@onready var _info: Label = $Root/Info
@onready var _next: Label = $Root/Next
@onready var _button: Button = $Root/NextButton


func _ready() -> void:
	_root.hide()
	_button.pressed.connect(_on_next_pressed)
	EventBus.levelups_done.connect(_on_levelups_done)
	EventBus.player_died.connect(func() -> void: _root.hide())
	EventBus.run_won.connect(func() -> void: _root.hide())


func _on_levelups_done() -> void:
	if not GameState.run_active:
		return
	var panel: AtlasTexture = AtlasTexture.new()
	panel.atlas = PANELS
	panel.region = Rect2(Vector2(randi_range(0, PANEL_VARIANTS - 1) * PANEL_SIZE.x, 0.0), PANEL_SIZE)
	_panel.texture = panel
	var next_wave: int = GameState.wave + 1
	_title.text = "ВОЛНА %d ПРОЙДЕНА" % GameState.wave
	_info.text = "Ларёк закрыт — ты ещё не заслужил.\nУБИТО: %d   УРОВЕНЬ: %d" % [GameState.kills, GameState.level]
	var kind: StringName = GameState.special_waves.get(next_wave, &"normal")
	var label: String = {&"elite": " — ЭЛИТА!", &"horde": " — ОРДА!", &"boss": " — БОССЫ!"}.get(kind, "")
	_next.text = "ДАЛЬШЕ: ВОЛНА %d%s" % [next_wave, label]
	_next.add_theme_color_override(&"font_color", Color(1, 0.0627451, 0.2, 1) if kind != &"normal" else Color(0.968627, 1, 0, 1))
	_root.show()
	_button.grab_focus()
	get_tree().paused = true


func _on_next_pressed() -> void:
	_root.hide()
	get_tree().paused = false
	EventBus.next_wave_requested.emit()
