class_name DeathScreen
extends CanvasLayer
## Экран смерти: случайная фраза, статистика, кнопка «Ещё раз».

const BORDER_DECOR: Texture2D = preload("res://assets/sprites/arena_border.png")
const GROUND_DECALS: Texture2D = preload("res://assets/sprites/ground_decals.png")
const PANELS: Texture2D = preload("res://assets/ui/death_panels.png")
const PANEL_SIZE: Vector2 = Vector2(360.0, 160.0)
const PANEL_VARIANTS: int = 4
const DECOR_SIZE: Vector2 = Vector2(48.0, 32.0)
const DECOR_COUNT: int = 16
const DECAL_COUNT: int = 40
const DECAL_CELL: float = 24.0
const SCREEN: Vector2 = Vector2(480.0, 270.0)
const PANEL_RECT: Rect2 = Rect2(60.0, 55.0, 360.0, 160.0)

@onready var _decor: Node2D = $Root/Decor
@onready var _panel: TextureRect = $Root/Panel
@onready var _root: Control = $Root
@onready var _title: Label = $Root/Title
@onready var _stats: Label = $Root/Stats
@onready var _retry: Button = $Root/RetryButton


func _ready() -> void:
	_root.hide()
	_retry.pressed.connect(_on_retry)
	EventBus.player_died.connect(_on_player_died)
	EventBus.run_won.connect(_on_run_won)


func _unhandled_input(event: InputEvent) -> void:
	if _root.visible and event.is_action_pressed(&"ui_accept"):
		get_viewport().set_input_as_handled()
		_on_retry()


func _on_player_died() -> void:
	_show_result(FlavorText.random_death())


func _on_run_won() -> void:
	_show_result(FlavorText.random_win())


func _show_result(title: String) -> void:
	_title.text = title
	_stats.text = "УБИТО: %d     УРОВЕНЬ: %d" % [GameState.kills, GameState.level]
	_scatter_decor()
	_root.show()
	_retry.grab_focus()
	get_tree().paused = true


func _on_retry() -> void:
	get_tree().paused = false
	get_tree().reload_current_scene()


## Каждая смерть — новый фон: случайная рамка и случайные декорации с границы арены, кроме зоны панели.
func _scatter_decor() -> void:
	for child: Node in _decor.get_children():
		child.queue_free()
	var panel: AtlasTexture = AtlasTexture.new()
	panel.atlas = PANELS
	panel.region = Rect2(Vector2(randi_range(0, PANEL_VARIANTS - 1) * PANEL_SIZE.x, 0.0), PANEL_SIZE)
	_panel.texture = panel
	var decal_kinds: int = int(GROUND_DECALS.get_width() / DECAL_CELL)
	for i: int in DECAL_COUNT:
		var decal_pos: Vector2 = _random_point_outside_panel()
		_add_sprite(GROUND_DECALS, Rect2(Vector2(randi_range(0, decal_kinds - 1) * DECAL_CELL, 0.0), Vector2(DECAL_CELL, DECAL_CELL)), decal_pos, 1.0)
	var kinds: int = int(BORDER_DECOR.get_width() / DECOR_SIZE.x)
	for i: int in DECOR_COUNT:
		var pos: Vector2 = _random_point_outside_panel()
		_add_sprite(BORDER_DECOR, Rect2(Vector2(randi_range(0, kinds - 1) * DECOR_SIZE.x, 0.0), DECOR_SIZE), pos, 2.0)


func _random_point_outside_panel() -> Vector2:
	for attempt: int in 20:
		var point: Vector2 = Vector2(randf_range(0.0, SCREEN.x), randf_range(0.0, SCREEN.y))
		if not PANEL_RECT.grow(8.0).has_point(point):
			return point.round()
	return Vector2(24.0, 24.0)


func _add_sprite(texture: Texture2D, region: Rect2, pos: Vector2, scale_factor: float) -> void:
	var sprite: Sprite2D = Sprite2D.new()
	sprite.texture = texture
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.region_enabled = true
	sprite.region_rect = region
	sprite.flip_h = randf() < 0.5
	sprite.scale = Vector2.ONE * scale_factor  # целый масштаб — пиксели остаются квадратными
	sprite.position = pos
	_decor.add_child(sprite)
