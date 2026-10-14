class_name HitFx
extends RefCounted
## Статичные помощники для эффектов попаданий: брызги пикселей и всплывающий текст.
## Всё создаётся в текущей сцене и само удаляется.

const FONT_THEME: Theme = preload("res://assets/ui/theme.tres")


## Взрыв квадратных пикселей из точки. colors — случайный выбор на каждую частицу пачкой.
static func burst(tree: SceneTree, at: Vector2, color: Color, count: int, speed: float, size: float = 2.0, lifetime: float = 0.35, upward: bool = false) -> void:
	var particles: CPUParticles2D = CPUParticles2D.new()
	particles.emitting = false
	particles.one_shot = true
	particles.explosiveness = 1.0
	particles.amount = count
	particles.lifetime = lifetime
	particles.direction = Vector2.UP if upward else Vector2.ZERO
	particles.spread = 60.0 if upward else 180.0
	particles.gravity = Vector2(0.0, -20.0) if upward else Vector2.ZERO
	particles.initial_velocity_min = speed * 0.4
	particles.initial_velocity_max = speed
	particles.damping_min = speed * 1.5
	particles.damping_max = speed * 2.5
	particles.scale_amount_min = size
	particles.scale_amount_max = size * 1.5
	particles.color = color
	particles.z_index = 20
	particles.global_position = at
	tree.current_scene.add_child(particles)
	particles.finished.connect(particles.queue_free)
	particles.emitting = true


## Всплывающая надпись: поднимается и тает.
static func popup(tree: SceneTree, at: Vector2, text: String, color: Color, rise: float = 14.0, duration: float = 0.55) -> void:
	var label: Label = Label.new()
	label.theme = FONT_THEME
	label.text = text
	label.add_theme_color_override(&"font_color", color)
	label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	label.z_index = 30
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tree.current_scene.add_child(label)
	label.reset_size()
	label.global_position = (at - label.size * 0.5).round()
	var tween: Tween = label.create_tween()
	tween.set_parallel(true)
	tween.tween_property(label, "global_position:y", label.global_position.y - rise, duration)
	tween.tween_property(label, "modulate:a", 0.0, duration).set_delay(duration * 0.4)
	tween.chain().tween_callback(label.queue_free)
