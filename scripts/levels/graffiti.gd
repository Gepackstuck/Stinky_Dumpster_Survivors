class_name Graffiti
extends Node2D
## Н30: одно граффити на арене - там, где герой сдох в прошлый раз: «ТУТ СДОХ ДЯДЯ ВИТЯ. ВОЛНА 7».
## Бледное, на полу под всеми: память, а не помеха. Данные - последняя запись Profile.graffiti.

const SPLAT: Texture2D = preload("res://assets/sprites/graffiti_splat.png")
const COLORS: Array[Color] = [Color(1.0, 0.06, 0.94), Color(0.22, 1.0, 0.08), Color(0.97, 1.0, 0.0), Color(0.0, 0.94, 1.0), Color(1.0, 0.4, 0.1)]


func _ready() -> void:
	z_index = -1   # на асфальте, под врагами и пикапами
	if Profile.graffiti.is_empty():
		return
	var e: Dictionary = Profile.graffiti.back()
	var a: float = Balance.ARENA_SIZE
	var at: Vector2 = Vector2(float(e.get("x", a * 0.5)), float(e.get("y", a * 0.5)))
	at = at.clamp(Vector2(10.0, 10.0), Vector2(a - 150.0, a - 20.0))   # надпись целиком на арене
	var color: Color = COLORS[int(e.get("wave", 1)) % COLORS.size()]
	modulate.a = Balance.GRAFFITI_ALPHA
	EventBus.wave_started.connect(func(w: int) -> void:   # память о прошлой смерти - только на 1-й волне, потом не мешает бою
		if w > 1 and is_inside_tree():
			create_tween().tween_property(self, "modulate:a", 0.0, 1.0))
	var splat: Sprite2D = Sprite2D.new()
	splat.texture = SPLAT
	splat.hframes = 3
	splat.frame = int(e.get("wave", 1)) % 3
	splat.centered = false
	splat.position = (at + Vector2(-6.0, -1.0)).round()
	splat.scale = Vector2(2.0, 1.0)
	splat.modulate = color.darkened(0.45)
	add_child(splat)
	var label: Label = Label.new()
	var hero: String = CharacterLibrary.short_title(StringName(e.get("hero", "hobo")))
	label.text = tr("ТУТ СДОХ %s. ВОЛНА %d") % [hero, int(e.get("wave", 1))]
	label.position = (at + Vector2(0.0, -1.0)).round()
	label.add_theme_color_override(&"font_color", color)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)
