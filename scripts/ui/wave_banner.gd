class_name WaveBanner
extends CanvasLayer
## Баннер «ВОЛНА N» / «БОСС!» с жёсткой фразой. Появляется сверху, висит пару секунд и тает.

const FRAMES: Texture2D = preload("res://assets/ui/banners.png")
const BANNER_SIZE: Vector2 = Vector2(320.0, 52.0)
const HOLD_SEC: float = 2.0
const SLIDE_SEC: float = 0.25
const FADE_SEC: float = 0.4
const SHOWN_Y: float = 48.0

@onready var _root: Control = $Root
@onready var _frame: TextureRect = $Root/Frame
@onready var _title: Label = $Root/Title
@onready var _subtitle: Label = $Root/Subtitle

var _tween: Tween = null
var _small_tween: Tween = null
var _preview: TextureRect = null
var _mini: Label = null
var _mini_sub: Label = null


func _ready() -> void:
	_root.modulate.a = 0.0
	_ready_extra()
	EventBus.wave_started.connect(_on_wave_started)
	EventBus.boss_spawned.connect(_on_boss_spawned)
	EventBus.player_died.connect(func() -> void:
		_root.modulate.a = 0.0
		_mini.modulate.a = 0.0
		_mini_sub.modulate.a = 0.0)


func _ready_extra() -> void:
	_preview = TextureRect.new()
	_preview.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	_preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_preview.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_preview.position = Vector2(10.0, 6.0)
	_preview.size = Vector2(40.0, 40.0)
	_preview.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_preview.visible = false
	_root.add_child(_preview)
	_mini = Label.new()
	_mini.theme = preload("res://assets/ui/theme.tres")
	_mini.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	_mini.add_theme_color_override(&"font_outline_color", Color.BLACK)
	_mini.add_theme_constant_override(&"outline_size", 3)
	_mini.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_mini.position = Vector2(0.0, 34.0)
	_mini.size = Vector2(480.0, 12.0)
	_mini.modulate.a = 0.0
	_mini.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_mini)
	_mini_sub = Label.new()
	_mini_sub.theme = _mini.theme
	_mini_sub.add_theme_color_override(&"font_color", Color(0.93, 0.93, 0.93))
	_mini_sub.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	_mini_sub.add_theme_color_override(&"font_outline_color", Color.BLACK)
	_mini_sub.add_theme_constant_override(&"outline_size", 2)
	_mini_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_mini_sub.position = Vector2(0.0, 54.0)
	_mini_sub.size = Vector2(480.0, 10.0)
	_mini_sub.modulate.a = 0.0
	_mini_sub.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_mini_sub)


func _on_wave_started(wave: int) -> void:
	match GameState.wave_kind:
		&"elite":
			_show_small("ВОЛНА %d: ЭЛИТА!" % wave, FlavorText.random_elite(), Color(1, 0.0627451, 0.2, 1))
		&"horde":
			_show_small("ВОЛНА %d: ОРДА!" % wave, FlavorText.random_horde(), Color(1, 0.0627451, 0.2, 1))
		&"boss":
			_show_small("ВОЛНА %d: БОССЫ!" % wave, "", Color(1, 0.0627451, 0.2, 1))
		_ when GameState.wave_mod != &"":
			_show_small("ВОЛНА %d: %s!" % [wave, Balance.WAVE_MOD_DATA[GameState.wave_mod]["title"]], Balance.WAVE_MOD_DATA[GameState.wave_mod]["line"], Color(0.2235, 1.0, 0.0784))
		_:
			if wave == 1:
				_show(0, "ВОЛНА 1", FlavorText.random_intro(), Color(0.968627, 1, 0, 1))
			else:
				_show_small("ВОЛНА %d" % wave, "", Color(0.968627, 1, 0, 1))


## Маленькое объявление без рамки: заголовок и (необязательно) строчка под ним.
func _show_small(title: String, subtitle: String, color: Color) -> void:
	_mini.text = title
	_mini.add_theme_color_override(&"font_color", color)
	_mini_sub.text = subtitle
	if _small_tween != null and _small_tween.is_valid():
		_small_tween.kill()
	_mini.modulate.a = 1.0
	_mini_sub.modulate.a = 1.0 if subtitle != "" else 0.0
	_mini.position.y = 24.0
	_small_tween = create_tween()
	_small_tween.tween_property(_mini, "position:y", 34.0, 0.18)
	_small_tween.tween_interval(1.1)
	_small_tween.set_parallel(true)
	_small_tween.tween_property(_mini, "modulate:a", 0.0, 0.4)
	_small_tween.tween_property(_mini_sub, "modulate:a", 0.0, 0.4)


func _on_boss_spawned(boss_id: StringName) -> void:
	var sheet: Texture2D = load("res://assets/sprites/enemy_%s.png" % boss_id) as Texture2D
	var texture: AtlasTexture = AtlasTexture.new()   # лист из 4 кадров: в баннере только первый
	texture.atlas = sheet
	texture.region = Rect2(0.0, 0.0, sheet.get_width() / 4.0, sheet.get_height() / float(Balance.ENEMIES[boss_id].get("anim_rows", 1)))
	_show(1, Balance.BOSS_NAMES.get(boss_id, "???"), FlavorText.boss_tagline(boss_id), Color(1, 0.0627451, 0.2, 1), texture)


func _show(variant: int, title: String, subtitle: String, color: Color, preview: Texture2D = null) -> void:
	var atlas: AtlasTexture = AtlasTexture.new()
	atlas.atlas = FRAMES
	atlas.region = Rect2(Vector2(variant * BANNER_SIZE.x, 0.0), BANNER_SIZE)
	_frame.texture = atlas
	_title.text = title
	_title.add_theme_color_override(&"font_color", color)
	_title.add_theme_color_override(&"font_outline_color", Color.BLACK)
	_title.add_theme_constant_override(&"outline_size", 2)
	_subtitle.text = subtitle
	_preview.visible = preview != null
	_preview.texture = preview
	if preview != null:
		_title.offset_left = 56.0
		_title.offset_right = 172.0
		_subtitle.offset_left = 56.0
	else:
		_title.offset_left = 10.0
		_title.offset_right = 150.0
		_subtitle.offset_left = 12.0
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_root.modulate.a = 1.0
	_root.position = Vector2(roundf((480.0 - BANNER_SIZE.x) * 0.5), -BANNER_SIZE.y)  # по центру экрана
	var hold: float = HOLD_SEC + (1.2 if preview != null else 0.0)
	_tween = create_tween()
	_tween.tween_property(_root, "position:y", SHOWN_Y, SLIDE_SEC)
	_tween.tween_interval(hold)
	_tween.tween_property(_root, "modulate:a", 0.0, FADE_SEC)
