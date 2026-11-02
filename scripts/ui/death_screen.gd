class_name DeathScreen
extends CanvasLayer
## Экран смерти: случайная фраза, статистика, кнопка «Ещё раз».

const HINTS: GDScript = preload("res://scripts/systems/unlock_hints.gd")
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

const KILLER_POS: Vector2 = Vector2(92.0, 126.0)
const SOURCE_ICONS: Dictionary = {&"pets": "item_dead_rat", &"structures": "item_bucket_turret", &"thorns": "item_barbed_wire",
		&"items": "item_diarrhea", &"turret": "item_bucket_turret", &"stink_lamp": "item_stink_lamp", &"cart_mortar": "item_cart_mortar"}
const SOURCE_TITLES: Dictionary = {&"pets": "ПИТОМЦЫ", &"structures": "ПОСТРОЙКИ", &"thorns": "ШИПЫ", &"items": "ПРЕДМЕТЫ", &"dash": "РЫВОК", &"other": "ПРОЧЕЕ"}
const BAR_UNDER: Texture2D = preload("res://assets/ui/hp_bar_under.png")
const BAR_FILL: Texture2D = preload("res://assets/ui/hp_bar_fill.png")
const DASH_ICON: Texture2D = preload("res://assets/ui/hud_dash_full.png")
const KILLER_MAX_SIZE: float = 30.0
const KILLER_FRAME_SEC: float = 0.25
const WIRE_TEXTURE: Texture2D = preload("res://assets/sprites/arena_wire.png")

var _hint_label: Label = null
var _killer_sprite: Sprite2D = null
var _killer_label: Label = null
var _killer_id: StringName = &""
var _killer_time: float = 0.0
var _graph: HpGraph = null
var _graph_label: Label = null
var _damage_box: VBoxContainer = null
var _won: bool = false
var _endless_button: Button = null


func _ready() -> void:
	_root.hide()
	_retry.pressed.connect(_on_retry)
	_build_killer()
	_graph_label = Label.new()
	_graph_label.text = "ТВОИ ХП ЗА ЗАБЕГ:"
	_graph_label.position = Vector2(76.0, 140.0)
	_graph_label.add_theme_color_override(&"font_color", Color(0.7, 0.7, 0.75))
	_root.add_child(_graph_label)
	_graph = HpGraph.new()
	_graph.position = Vector2(76.0, 151.0)
	_graph.size = Vector2(158.0, 28.0)
	_root.add_child(_graph)
	_endless_button = Button.new()
	_endless_button.text = "БЕСКОНЕЧНО"
	_endless_button.position = Vector2(300.0, 184.0)
	_endless_button.size = Vector2(100.0, 22.0)
	preload("res://scripts/ui/ui_buttons.gd").skin(_endless_button, 4)
	_endless_button.visible = false
	_endless_button.pressed.connect(func() -> void:
		_won = false
		_root.hide()
		EventBus.endless_requested.emit())
	_root.add_child(_endless_button)
	_damage_box = VBoxContainer.new()
	_damage_box.position = Vector2(246.0, 110.0)
	_damage_box.add_theme_constant_override(&"separation", 1)
	_root.add_child(_damage_box)
	_hint_label = Label.new()
	_hint_label.position = Vector2(20.0, 220.0)
	_hint_label.size = Vector2(440.0, 40.0)
	_hint_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint_label.add_theme_color_override(&"font_color", Color(0.2235, 1.0, 0.0784))
	_hint_label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	_hint_label.add_theme_constant_override(&"shadow_offset_x", 1)
	_hint_label.add_theme_constant_override(&"shadow_offset_y", 1)
	_hint_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_root.add_child(_hint_label)
	EventBus.player_died.connect(_on_player_died)
	EventBus.run_won.connect(_on_run_won)


func _build_killer() -> void:
	_killer_sprite = Sprite2D.new()
	_killer_sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_killer_sprite.position = KILLER_POS
	_killer_sprite.hide()
	_root.add_child(_killer_sprite)
	_killer_label = Label.new()
	_killer_label.position = Vector2(KILLER_POS.x + 18.0, KILLER_POS.y - 10.0)
	_killer_label.size = Vector2(130.0, 20.0)
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
	if enemy_id == &"garbage_truck" or Balance.WAVE_MOD_DATA.has(enemy_id) or enemy_id in [&"thunder", &"airdrop"]:
		var icon_id: String = {&"thunder": "thunder", &"airdrop": "airdrop"}.get(enemy_id, String(enemy_id))
		_killer_sprite.texture = load("res://assets/sprites/garbage_truck.png" if enemy_id == &"garbage_truck" else "res://assets/ui/mod_%s.png" % icon_id) as Texture2D
		_killer_sprite.hframes = 2 if enemy_id == &"garbage_truck" else 1
		_killer_sprite.vframes = 1
		_killer_sprite.frame = 0
	elif enemy_id == &"wire":
		var cell: AtlasTexture = AtlasTexture.new()
		cell.atlas = WIRE_TEXTURE
		cell.region = Rect2(Vector2(5.0 * 48.0, 0.0), Vector2(48.0, 16.0))
		_killer_sprite.texture = cell
		_killer_sprite.hframes = 1
		_killer_sprite.vframes = 1
	else:
		_killer_sprite.texture = load("res://assets/sprites/enemy_%s.png" % enemy_id) as Texture2D
		_killer_sprite.hframes = 4
		_killer_sprite.vframes = int(Balance.ENEMIES[enemy_id].get("anim_rows", 1))
		_killer_sprite.frame = 0
	var size: Vector2 = _killer_sprite.texture.get_size() / Vector2(float(_killer_sprite.hframes), float(_killer_sprite.vframes))
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
	_won = true
	_show_result(FlavorText.random_win(), false)   # итоги; кнопка ведёт обратно на арену к воротам


func _show_result(title: String, died: bool = false) -> void:
	_title.text = title
	var secs: int = GameState.hp_history.size()
	_stats.text = "УБИТО %d   УР. %d   ВОЛНА %d/%d   %d:%02d   %s" % [GameState.kills, GameState.level, GameState.wave, Balance.WAVE_COUNT,
			secs / 60, secs % 60, WaveRules.danger_v("name")]
	_graph.died = died
	_graph.queue_redraw()
	_fill_damage()
	_retry.text = "К ВОРОТАМ" if _won else "ЕЩЁ РАЗ"
	_endless_button.visible = _won and not GameState.endless
	if GameState.daily or GameState.endless:
		var best: int = int(Profile.daily_best.get(str(GameState.daily_seed), 0)) if GameState.daily else Profile.endless_best
		_stats.text += "   ОЧКИ %d (РЕКОРД %d)" % [GameState.run_score(_won), maxi(best, GameState.run_score(_won))] if GameState.daily else "   РЕКОРД ВОЛНЫ %d" % maxi(best, GameState.wave)
	_killer_id = &""
	_killer_sprite.hide()
	_killer_label.hide()
	if died and GameState.last_damage_source != &"":
		_show_killer(GameState.last_damage_source)
	var lines: Array[String] = []
	var why: String = BuildAdvisor.top()
	if died and why != "":
		lines.append("ПОЧЕМУ СДОХ: " + why)
	if died:
		lines.append_array(HINTS.death_lines())
	_hint_label.text = "\n".join(lines.slice(0, 3))
	_scatter_decor()
	_root.show()
	_retry.grab_focus()
	get_tree().paused = true


## Урон по источникам: топ-5 полосками с иконками (кто реально тащил забег).
func _fill_damage() -> void:
	for child: Node in _damage_box.get_children():
		child.queue_free()
	var head: Label = Label.new()
	head.text = "КТО ТАЩИЛ (УРОН):"
	head.add_theme_color_override(&"font_color", Color(0.7, 0.7, 0.75))
	_damage_box.add_child(head)
	var src: Dictionary = GameState.damage_by_source
	var keys: Array = src.keys()
	keys.sort_custom(func(a: StringName, b: StringName) -> bool: return src[a] > src[b])
	var top: float = float(src[keys[0]]) if not keys.is_empty() else 1.0
	for key: StringName in keys.slice(0, 5):
		var row: HBoxContainer = HBoxContainer.new()
		row.add_theme_constant_override(&"separation", 3)
		var icon: TextureRect = TextureRect.new()
		icon.custom_minimum_size = Vector2(12.0, 12.0)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icon.texture = _source_icon(key)
		row.add_child(icon)
		var bar: TextureProgressBar = TextureProgressBar.new()
		bar.texture_under = BAR_UNDER
		bar.texture_progress = BAR_FILL
		bar.texture_progress_offset = Vector2(2, 2)
		bar.max_value = top
		bar.value = float(src[key])
		bar.tint_progress = Color(0.2235, 1.0, 0.0784)
		bar.custom_minimum_size = Vector2(72.0, 10.0)
		row.add_child(bar)
		var num: Label = Label.new()
		num.text = "%d %s" % [roundi(src[key]), _source_title(key)]
		num.add_theme_color_override(&"font_color", Color(0.95, 0.95, 0.95))
		num.add_theme_font_size_override(&"font_size", 6)
		row.add_child(num)
		_damage_box.add_child(row)


func _source_icon(key: StringName) -> Texture2D:
	if key == &"dash":
		return DASH_ICON
	if SOURCE_ICONS.has(key):
		return load("res://assets/ui/%s_s.png" % SOURCE_ICONS[key]) as Texture2D
	if Balance.WEAPONS.has(key):
		return PerkLibrary.icon_small(ShopLibrary.perk_id_of(key))
	return load("res://assets/ui/item_poop_wallet_s.png") as Texture2D


func _source_title(key: StringName) -> String:
	if SOURCE_TITLES.has(key):
		return SOURCE_TITLES[key]
	if Balance.WEAPONS.has(key) and not Balance.WEAPONS[key].get("structure", false):
		return PerkLibrary.title(ShopLibrary.perk_id_of(key))
	return "ПОСТРОЙКИ"


func _on_retry() -> void:
	if _won:   # победа: панель убираем, герой идёт к воротам сам
		_won = false
		_root.hide()
		get_tree().paused = false
		return
	SceneFlow.from_arena = true
	SceneFlow.go("res://scenes/ui/graveyard.tscn", Vector2.DOWN)


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
	var kinds: int = int(BORDER_DECOR.get_width() / (DECOR_SIZE.x * 4.0))
	for i: int in DECOR_COUNT:
		var pos: Vector2 = _random_point_outside_panel()
		_add_sprite(BORDER_DECOR, Rect2(Vector2(randi_range(0, kinds - 1) * DECOR_SIZE.x * 4.0, 0.0), DECOR_SIZE), pos, 2.0)


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
