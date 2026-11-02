class_name UltMeter
extends TextureProgressBar
## Шкала ульты в HUD: вонючая бомба заполняется снизу вверх, полная - мигает и подсказывает кнопку.

var _label: Label
var _t: float = 0.0


func _ready() -> void:
	texture_under = preload("res://assets/ui/hud_ult_empty.png")
	texture_progress = preload("res://assets/ui/hud_ult_full.png")
	fill_mode = TextureProgressBar.FILL_BOTTOM_TO_TOP
	max_value = 1.0
	step = 0.0
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	_label = Label.new()
	_label.position = Vector2(15.0, 0.0)
	_label.add_theme_color_override(&"font_color", Color(0.97, 1.0, 0.0))
	_label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	add_child(_label)
	EventBus.ult_state.connect(func(c: float) -> void: value = c)


func _process(delta: float) -> void:
	_t += delta
	var full: bool = value >= 1.0
	_label.text = InputMode.hint("Q!", "Y!") if full else ""
	modulate = Color(1, 1, 1, 0.7 + 0.3 * sin(_t * 8.0)) if full else Color.WHITE
