class_name PilePointer
extends Sprite2D
## Стрелка-вонь на кучу-лотерею, когда её не видно на экране (как стрелка на врагов, но вонючая и волнистая).

const SHEET: Texture2D = preload("res://assets/ui/pile_pointer.png")
const SCREEN: Vector2 = Vector2(480.0, 270.0)
const EDGE_INSET: float = 26.0

var _t: float = 0.0


func _ready() -> void:
	texture = SHEET
	hframes = 4
	hide()


func _process(delta: float) -> void:
	var pile: Node2D = get_tree().get_first_node_in_group(&"mod_pile") as Node2D
	if pile == null or get_tree().paused:
		hide()
		return
	var at: Vector2 = get_viewport().get_canvas_transform() * pile.global_position
	if Rect2(Vector2.ZERO, SCREEN).has_point(at):
		hide()
		return
	show()
	var center: Vector2 = SCREEN * 0.5
	var dir: Vector2 = (at - center).normalized()
	var half: Vector2 = SCREEN * 0.5 - Vector2(EDGE_INSET, EDGE_INSET)
	var k: float = minf(half.x / maxf(absf(dir.x), 0.001), half.y / maxf(absf(dir.y), 0.001))
	position = center + dir * k
	rotation = dir.angle()
	_t += delta
	frame = int(_t * 8.0) % 4
	scale = Vector2.ONE * (1.6 + 0.2 * sin(_t * 7.0))
