extends Node2D
## Короткие вспышки: кольцо взрыва и вспышка выстрела. Сами рисуются и удаляются.

var mode: StringName = &"ring"
var radius_max: float = 40.0
var color: Color = Color(1.0, 0.55, 0.0)
var life: float = 0.35
var dir: Vector2 = Vector2.RIGHT
var _t: float = 0.0


func _process(delta: float) -> void:
	_t += delta
	if _t >= life:
		queue_free()
		return
	queue_redraw()


func _draw() -> void:
	var k: float = clampf(_t / life, 0.0, 1.0)
	if mode == &"ring":
		var r: float = radius_max * (1.0 - pow(1.0 - k, 3.0))
		draw_circle(Vector2.ZERO, r * 0.75, Color(1.0, 0.95, 0.4, (1.0 - k) * 0.55))
		draw_circle(Vector2.ZERO, r * 0.45, Color(1.0, 1.0, 1.0, (1.0 - k) * 0.7))
		draw_arc(Vector2.ZERO, r, 0.0, TAU, 32, Color(color.r, color.g, color.b, 1.0 - k), 3.0 * (1.0 - k) + 1.0)
		draw_arc(Vector2.ZERO, r * 0.7, 0.0, TAU, 24, Color(1.0, 0.2, 0.0, (1.0 - k) * 0.8), 2.0)
	else:
		var length: float = radius_max * (1.0 - k * 0.4)
		var side: Vector2 = dir.orthogonal()
		var pts: PackedVector2Array = PackedVector2Array([Vector2.ZERO + side * 2.5, dir * length, Vector2.ZERO - side * 2.5, -dir * 3.0])
		draw_colored_polygon(pts, Color(color.r, color.g, color.b, 1.0 - k))
		var inner: PackedVector2Array = PackedVector2Array([side * 1.2, dir * length * 0.6, -side * 1.2, -dir * 1.5])
		draw_colored_polygon(inner, Color(1.0, 1.0, 1.0, 1.0 - k))
