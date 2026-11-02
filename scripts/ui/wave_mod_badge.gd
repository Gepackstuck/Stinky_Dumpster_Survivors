class_name WaveModBadge
extends HBoxContainer
## Плашка модификатора волны в HUD (под счётчиком волны): значок + название. Пропадает в конце волны.

var _icon: TextureRect
var _label: Label


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	alignment = BoxContainer.ALIGNMENT_CENTER
	add_theme_constant_override(&"separation", 3)
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
	visible = mod != &"" or bet != ""
	_icon.visible = mod != &""
	if mod != &"":
		_icon.texture = load("res://assets/ui/mod_%s_s.png" % mod) as Texture2D
	_label.text = (Balance.WAVE_MOD_DATA[mod]["title"] if mod != &"" else "") + ("   " if mod != &"" and bet != "" else "") + bet


func _bet_text() -> String:
	if GameState.active_bet.is_empty():
		return ""
	match StringName(GameState.active_bet["kind"]):
		&"no_dash": return "ПАРИ: БЕЗ РЫВКОВ"
		&"kills": return "ПАРИ: %d УБИЙСТВ" % int(GameState.active_bet["kills"])
		&"few_hits": return "ПАРИ: <= 3 УДАРОВ"
		_: return "ПАРИ: ПОЛОВИНА ХП"
