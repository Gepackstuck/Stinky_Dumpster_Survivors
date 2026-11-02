class_name HpGraph
extends Control
## График ХП за забег (экран итога): кислотная линия по секундам боя, серые засечки начала волн,
## красный крест там, где сдох. Данные - GameState.hp_history / hp_wave_marks.

const LINE: Color = Color(0.2235, 1.0, 0.0784)
const LOW: Color = Color(1.0, 0.93, 0.0)
const BACK: Color = Color(0.04, 0.02, 0.05, 0.85)
const TICK: Color = Color(0.45, 0.45, 0.5)
const DEATH: Color = Color(1.0, 0.1, 0.2)

var died: bool = false


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), BACK)
	draw_rect(Rect2(Vector2.ZERO, size), Color(0.35, 0.3, 0.4), false, 1.0)
	var data: Array[float] = GameState.hp_history
	if data.size() < 2:
		return
	var n: int = data.size()
	var sx: float = (size.x - 2.0) / float(n - 1)
	for mark: int in GameState.hp_wave_marks:
		var x: float = 1.0 + mark * sx
		draw_line(Vector2(x, 1.0), Vector2(x, size.y - 1.0), TICK, 1.0)
	var pts: PackedVector2Array = PackedVector2Array()
	for i: int in n:
		pts.append(Vector2(1.0 + i * sx, 1.0 + (1.0 - data[i]) * (size.y - 3.0)).round())
	for i: int in n - 1:   # ниже трети - жёлтым: «тут чуть не сдох»
		draw_line(pts[i], pts[i + 1], LOW if data[i + 1] < 0.34 else LINE, 1.0)
	if died:
		var end: Vector2 = pts[n - 1]
		draw_line(end + Vector2(-3, -3), end + Vector2(3, 3), DEATH, 1.0)
		draw_line(end + Vector2(-3, 3), end + Vector2(3, -3), DEATH, 1.0)
