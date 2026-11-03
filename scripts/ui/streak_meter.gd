class_name StreakMeter
extends Label
## Серия без урона в HUD: «БЕЗ ЦАРАПИН +25%». Видна с первой ступени; при сбросе гаснет.

const COLORS: Array[Color] = [Color(0.968627, 1.0, 0.0), Color(0.2235, 1.0, 0.0784), Color(0.0, 0.94, 1.0), Color(1.0, 0.063, 0.94)]


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	add_theme_color_override(&"font_shadow_color", Color.BLACK)
	EventBus.streak_changed.connect(_on_streak)
	EventBus.run_started.connect(func() -> void: visible = false)


func _on_streak(tier: int, bonus: float, _broken: bool) -> void:
	visible = tier > 0
	if tier > 0:
		text = tr("БЕЗ ЦАРАПИН: +%d%% ГОВНА") % roundi(bonus * 100.0)   # под полосками слева - не на таймере волны
		add_theme_color_override(&"font_color", COLORS[mini(tier, COLORS.size()) - 1])
		pivot_offset = Vector2(0.0, size.y * 0.5)
		scale = Vector2.ONE * 1.4
		create_tween().tween_property(self, "scale", Vector2.ONE, 0.25)
