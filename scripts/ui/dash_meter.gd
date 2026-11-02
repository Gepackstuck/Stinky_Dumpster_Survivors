class_name DashMeter
extends Control
## Шкала рывка в HUD: по кеде на заряд; перезаряжающаяся кеда заполняется снизу вверх. Слушает EventBus.dash_state.

const FULL: Texture2D = preload("res://assets/ui/hud_dash_full.png")
const EMPTY: Texture2D = preload("res://assets/ui/hud_dash_empty.png")
const STEP: float = 15.0

var _icons: Array[TextureProgressBar] = []


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	EventBus.dash_state.connect(_on_dash_state)


func _on_dash_state(charges: int, max_charges: int, recharge: float) -> void:
	while _icons.size() < max_charges:
		var icon: TextureProgressBar = TextureProgressBar.new()
		icon.texture_under = EMPTY
		icon.texture_progress = FULL
		icon.fill_mode = TextureProgressBar.FILL_BOTTOM_TO_TOP
		icon.max_value = 1.0
		icon.step = 0.0
		icon.position = Vector2(_icons.size() * STEP, 0.0)
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(icon)
		_icons.append(icon)
	for i: int in _icons.size():
		var bar: TextureProgressBar = _icons[i]
		bar.visible = i < max_charges
		bar.value = 1.0 if i < charges else (recharge if i == charges else 0.0)
		bar.modulate = Color.WHITE if i < charges else Color(0.8, 0.8, 0.8)
