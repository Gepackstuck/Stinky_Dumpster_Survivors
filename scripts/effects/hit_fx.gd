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


const SHAPE: GDScript = preload("res://scripts/effects/shape_fx.gd")


## Взрыв: кольцо, огненные пиксели, дым.
static func explosion(tree: SceneTree, at: Vector2, radius: float, color: Color = Color(1.0, 0.55, 0.0)) -> void:
	var ring: Node2D = SHAPE.new()
	ring.set(&"mode", &"ring")
	ring.set(&"radius_max", radius)
	ring.set(&"color", color)
	ring.set(&"life", 0.4)
	ring.z_index = 19
	tree.current_scene.add_child(ring)
	ring.global_position = at
	burst(tree, at, Color(1.0, 0.85, 0.2), 10, radius * 2.4, 3.0, 0.45)
	burst(tree, at, Color(1.0, 0.3, 0.0), 12, radius * 1.8, 3.0, 0.55)
	burst(tree, at, Color(0.15, 0.1, 0.1), 6, radius * 1.0, 4.0, 0.7, true)


## Вспышка выстрела на конце ствола.
static func muzzle(tree: SceneTree, at: Vector2, direction: Vector2, color: Color = Color(1.0, 0.9, 0.2), length: float = 11.0) -> void:
	var flash: Node2D = SHAPE.new()
	flash.set(&"mode", &"flash")
	flash.set(&"radius_max", length)
	flash.set(&"color", color)
	flash.set(&"life", 0.09)
	flash.set(&"dir", direction)
	flash.z_index = 21
	tree.current_scene.add_child(flash)
	flash.global_position = at
	if randf() < 0.35:
		burst(tree, at + direction * 4.0, color, 2, 60.0, 2.0, 0.18)


## Искры в точке попадания снаряда.
static func sparks(tree: SceneTree, at: Vector2, color: Color = Color(1.0, 0.9, 0.3)) -> void:
	if randf() < 0.5:
		burst(tree, at, color, 4, 55.0, 2.0, 0.2)


## Всплывающая надпись: поднимается и тает.
static var _popups_alive: int = 0


static func popup(tree: SceneTree, at: Vector2, text: String, color: Color, rise: float = 14.0, duration: float = 0.55, big: bool = false) -> void:
	if _popups_alive >= Balance.POPUP_MAX_ALIVE and not big:
		return   # экран не должен превращаться в кашу из цифр
	_popups_alive += 1
	var label: Label = Label.new()
	label.theme = FONT_THEME
	label.text = text
	label.add_theme_color_override(&"font_color", color)
	label.add_theme_color_override(&"font_shadow_color", Color.BLACK)
	label.z_index = 30
	if big:
		label.add_theme_color_override(&"font_outline_color", Color(0.7, 0.0, 0.0))
		label.add_theme_constant_override(&"outline_size", 3)
		label.scale = Vector2(2.0, 2.0)   # только целый масштаб: x1.5 рвёт пиксельный шрифт
		label.pivot_offset = label.size * 0.5
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tree.current_scene.add_child(label)
	label.reset_size()
	label.global_position = (at - label.size * 0.5).round()
	var tween: Tween = label.create_tween()
	tween.set_parallel(true)
	tween.tween_property(label, "global_position:y", label.global_position.y - rise, duration)
	tween.tween_property(label, "modulate:a", 0.0, duration).set_delay(duration * 0.4)
	tween.chain().tween_callback(label.queue_free)
	label.tree_exited.connect(func() -> void: _popups_alive = maxi(_popups_alive - 1, 0))
