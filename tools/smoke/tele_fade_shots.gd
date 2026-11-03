extends Node2D
## Кадр: линия (рывок), длинная линия (плевок) и конус маркеров врагов - дальний конец должен таять.
## tools/_preview/tele_fade.png. Оконный режим.

func _ready() -> void:
	var bg: ColorRect = ColorRect.new()
	bg.color = Color(0.36, 0.22, 0.1)
	bg.size = Vector2(480, 270)
	add_child(bg)
	get_tree().current_scene = self
	Telegraph.line(get_tree(), Vector2(40, 60), Vector2.RIGHT, 160.0, 8.0, 3.0)
	Telegraph.line(get_tree(), Vector2(40, 140), Vector2(1, 0.2), 420.0, 3.5, 3.0)
	Telegraph.cone(get_tree(), Vector2(300, 200), Vector2(1, -0.3), 30.0, 170.0, 3.0)
	await get_tree().create_timer(1.6).timeout
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/tele_fade.png"))
	get_tree().quit()
