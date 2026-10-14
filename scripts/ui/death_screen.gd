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

const KILLER_POS: Vector2 = Vector2(170.0, 150.0)
const KILLER_MAX_SIZE: float = 30.0
const KILLER_FRAME_SEC: float = 0.25
const WIRE_TEXTURE: Texture2D = preload("res://assets/sprites/arena_wire.png")

var _killer_sprite: Sprite2D = null
var _killer_label: Label = null
var _killer_id: StringName = &""
var _killer_time: float = 0.0


func _ready() -> void:
	_root.hide()
	_retry.pressed.connect(_on_retry)
	_build_killer()
	EventBus.player_died.connect(_on_player_died)
	EventBus.run_won.connect(_on_run_won)


func _build_killer() -> void:
	_killer_sprite = Sprite2D.new()
	_killer_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_killer_sprite.position = KILLER_POS
	_killer_sprite.hide()
	_root.add_child(_killer_sprite)
	_killer_label = Label.new()
	_killer_label.position = Vector2(KILLER_POS.x + 28.0, KILLER_POS.y - 10.0)
	_killer_label.size = Vector2(260.0, 20.0)
	_killer_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_killer_label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	_killer_label.hide()
	_root.add_child(_killer_label)


## Иконка и имя убийцы: спрайт крутит свои 2 кадра, цвет имени зависит от серьёзности (босс - пульсирует).
func _show_killer(enemy_id: StringName) -> void:
	_killer_id = enemy_id
	_killer_time = 0.0
	_killer_sprite.show()
	_killer_label.show()
	_killer_label.text = "УБИЛ ТЕБЯ:\n%s" % EnemyNames.title(enemy_id)
	_killer_label.add_theme_color_override(&"font_color", EnemyNames.color(enemy_id))
	if enemy_id == &"wire":
		var cell: AtlasTexture = AtlasTexture.new()
		cell.atlas = WIRE_TEXTURE
		cell.region = Rect2(Vector2(5.0 * 48.0, 0.0), Vector2(48.0, 16.0))
		_killer_sprite.texture = cell
		_killer_sprite.hframes = 1
	else:
		_killer_sprite.texture = load("res://assets/sprites/enemy_%s.png" % enemy_id) as Texture2D
		_killer_sprite.hframes = 2
		_killer_sprite.frame = 0
	var size: Vector2 = _killer_sprite.texture.get_size() / Vector2(float(_killer_sprite.hframes), 1.0)
	var k: float = minf(2.0, KILLER_MAX_SIZE / maxf(size.x, size.y))
	_killer_sprite.scale = Vector2.ONE * (floorf(k) if k >= 1.0 else k)


func _process(delta: float) -> void:
	if not _root.visible or _killer_id == &"" or not _killer_sprite.visible:
		return
	_killer_time += delta
	if _killer_sprite.hframes > 1:
		_killer_sprite.frame = int(_killer_time / KILLER_FRAME_SEC) % _killer_sprite.hframes
	if EnemyNames.threat(_killer_id) >= 3:
		_killer_label.modulate.a = 0.65 + 0.35 * sin(_killer_time * 6.0)   # боссов имя мигает
	else:
		_killer_label.modulate.a = 1.0


func _unhandled_input(event: InputEvent) -> void:
	if _root.visible and event.is_action_pressed(&"ui_accept"):
		get_viewport().set_input_as_handled()
		_on_retry()


func _on_player_died() -> void:
	_show_result(FlavorText.random_death(), true)


func _on_run_won() -> void:
	_show_result(FlavorText.random_win())


func _show_result(title: String, died: bool = false) -> void:
	_title.text = title
	_stats.text = "УБИТО: %d     УРОВЕНЬ: %d     ВОЛНА: %d" % [GameState.kills, GameState.level, GameState.wave]
	_killer_id = &""
	_killer_sprite.hide()
	_killer_label.hide()
	if died and GameState.last_damage_source != &"":
		_show_killer(GameState.last_damage_source)
	_scatter_decor()
	_root.show()
	_retry.grab_focus()
	get_tree().paused = true


func _on_retry() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file("res://scenes/ui/graveyard.tscn")


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
