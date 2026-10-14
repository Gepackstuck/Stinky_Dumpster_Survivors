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


func _ready() -> void:
	_root.modulate.a = 0.0
	EventBus.wave_started.connect(_on_wave_started)
	EventBus.boss_spawned.connect(_on_boss_spawned)
	EventBus.player_died.connect(func() -> void: _root.modulate.a = 0.0)


func _on_wave_started(wave: int) -> void:
	match GameState.wave_kind:
		&"elite":
			_show(1, "ВОЛНА %d: ЭЛИТА!" % wave, FlavorText.random_boss(), Color(1, 0.0627451, 0.2, 1))
		&"horde":
			_show(1, "ВОЛНА %d: ОРДА!" % wave, FlavorText.random_boss(), Color(1, 0.0627451, 0.2, 1))
		&"boss":
			_show(1, "ВОЛНА %d: БОССЫ!" % wave, FlavorText.random_boss(), Color(1, 0.0627451, 0.2, 1))
		_:
			_show(0, "ВОЛНА %d" % wave, FlavorText.random_wave(), Color(0.968627, 1, 0, 1))


func _on_boss_spawned(boss_id: StringName) -> void:
	_show(1, "БОСС: %s" % Balance.BOSS_NAMES.get(boss_id, "???"), FlavorText.random_boss(), Color(1, 0.0627451, 0.2, 1))


func _show(variant: int, title: String, subtitle: String, color: Color) -> void:
	var atlas: AtlasTexture = AtlasTexture.new()
	atlas.atlas = FRAMES
	atlas.region = Rect2(Vector2(variant * BANNER_SIZE.x, 0.0), BANNER_SIZE)
	_frame.texture = atlas
	_title.text = title
	_title.add_theme_color_override(&"font_color", color)
	_subtitle.text = subtitle
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_root.modulate.a = 1.0
	_root.position = Vector2(roundf((480.0 - BANNER_SIZE.x) * 0.5), -BANNER_SIZE.y)  # по центру экрана
	_tween = create_tween()
	_tween.tween_property(_root, "position:y", SHOWN_Y, SLIDE_SEC)
	_tween.tween_interval(HOLD_SEC)
	_tween.tween_property(_root, "modulate:a", 0.0, FADE_SEC)
