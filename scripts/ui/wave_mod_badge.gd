class_name WaveModBadge
extends HBoxContainer
## Плашка модификатора волны в HUD (под счётчиком волны): значок + название. Пропадает в конце волны.

var _icon: TextureRect
var _season: TextureRect
var _label: Label


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	alignment = BoxContainer.ALIGNMENT_CENTER
	add_theme_constant_override(&"separation", 3)
	_season = TextureRect.new()   # погода забега: значок виден всю волну
	_season.custom_minimum_size = Vector2(16.0, 16.0)
	_season.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	add_child(_season)
	_icon = TextureRect.new()
	_icon.custom_minimum_size = Vector2(16.0, 16.0)
	_icon.stretch_mode = TextureRect.STRETCH_KEEP_CENTERED
	add_child(_icon)
	_label = Label.new()
	_label.add_theme_color_override(&"font_color", Color(0.2235, 1.0, 0.0784))
	_label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	add_child(_label)
	visible = false
	EventBus.wave_started.connect(func(_w: int) -> void: _refresh())
	EventBus.wave_ended.connect(func(_w: int) -> void: visible = false)


func _refresh() -> void:
	var mod: StringName = GameState.wave_mod
	var bet: String = _bet_text()
	var weather: StringName = GameState.season
	visible = mod != &"" or bet != "" or weather != &""
	_season.visible = weather != &""
	if weather != &"":
		_season.texture = load("res://assets/ui/hud_season_%s.png" % weather) as Texture2D
	_icon.visible = mod != &""
	if mod != &"":
		_icon.texture = load("res://assets/ui/mod_%s_s.png" % mod) as Texture2D
	var parts: PackedStringArray = []
	if weather != &"":
		parts.append(tr(Balance.SEASONS[weather]["name"]).get_slice(":", 0))
	if mod != &"":
		parts.append(Balance.WAVE_MOD_DATA[mod]["title"])
	if bet != "":
		parts.append(bet)
	_label.text = "   ".join(parts)


func _bet_text() -> String:
	if GameState.active_bet.is_empty():
		return ""
	match StringName(GameState.active_bet["kind"]):
		&"no_dash": return "ПАРИ: БЕЗ РЫВКОВ"
		&"kills": return "ПАРИ: %d УБИЙСТВ" % int(GameState.active_bet["kills"])
		&"few_hits": return "ПАРИ: <= 3 УДАРОВ"
		_: return "ПАРИ: ПОЛОВИНА ХП"
