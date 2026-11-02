class_name Graffiti
extends Node2D
## Н30: граффити на краю арены - память о прошлых смертях: «ТУТ СДОХ ДЯДЯ ВИТЯ. ВОЛНА 7».
## Берёт последние смерти из Profile.graffiti; мазок баллончиком под надписью, кислотные цвета.

const SPLAT: Texture2D = preload("res://assets/sprites/graffiti_splat.png")
const COLORS: Array[Color] = [Color(1.0, 0.06, 0.94), Color(0.22, 1.0, 0.08), Color(0.97, 1.0, 0.0), Color(0.0, 0.94, 1.0), Color(1.0, 0.4, 0.1)]


func _ready() -> void:
	z_index = 2
	var list: Array = Profile.graffiti.slice(maxi(Profile.graffiti.size() - Balance.GRAFFITI_MAX, 0))
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = list.size() * 7919 + Profile.deaths
	var a: float = Balance.ARENA_SIZE
	for i: int in list.size():
		var e: Dictionary = list[i]
		var top: bool = i % 2 == 0   # сверху и снизу арены, вперемешку
		var x: float = 30.0 + (a - 120.0) * (float(i / 2) + 0.5) / maxf(ceilf(list.size() / 2.0), 1.0) + rng.randf_range(-12.0, 12.0)
		var y: float = 8.0 if top else a - 18.0   # на асфальте у самой колючки: не под HUD и не в декорациях
		var color: Color = COLORS[rng.randi() % COLORS.size()]
		var splat: Sprite2D = Sprite2D.new()
		splat.texture = SPLAT
		splat.hframes = 3
		splat.frame = rng.randi() % 3
		splat.centered = false
		splat.position = Vector2(x - 6.0, y - 1.0).round()
		splat.scale = Vector2(2.0, 1.0)   # мазок шире надписи
		splat.modulate = color.darkened(0.35)
		add_child(splat)
		var label: Label = Label.new()
		var hero: String = CharacterLibrary.short_title(StringName(e.get("hero", "hobo")))
		label.text = tr("ТУТ СДОХ %s. ВОЛНА %d") % [hero, int(e.get("wave", 1))]
		label.position = Vector2(x, y - 1.0).round()
		label.add_theme_color_override(&"font_color", color)
		label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
		label.add_theme_constant_override(&"shadow_offset_x", 1)
		label.add_theme_constant_override(&"shadow_offset_y", 1)
		label.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(label)
