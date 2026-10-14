class_name EnemyPointer
extends Sprite2D
## Указатель на ближайшего врага, когда ни один не виден на экране. Случайный мерзкий вид, мягкое свечение.

const SHEET: Texture2D = preload("res://assets/ui/enemy_pointers.png")
const VARIANTS: int = 7
const FRAME_SIZE: Vector2 = Vector2(32.0, 22.0)
const SCREEN: Vector2 = Vector2(480.0, 270.0)
const EDGE_INSET: float = 22.0

var _was_visible: bool = false
var _t: float = 0.0


func _ready() -> void:
	texture = SHEET
	region_enabled = true
	hide()


func _process(delta: float) -> void:
	var enemies: Node = get_tree().current_scene.get_node_or_null("Enemies")
	if enemies == null or not GameState.run_active or get_tree().paused:
		_set_shown(false)
		return
	var xform: Transform2D = get_viewport().get_canvas_transform()
	var center: Vector2 = SCREEN * 0.5
	var best: float = INF
	var best_pos: Vector2 = Vector2.ZERO
	for child: Node in enemies.get_children():
		var enemy: Node2D = child as Node2D
		if enemy == null:
			continue
		var screen_pos: Vector2 = xform * enemy.global_position
		if Rect2(Vector2.ZERO, SCREEN).has_point(screen_pos):
			_set_shown(false)
			return
		var d: float = screen_pos.distance_squared_to(center)
		if d < best:
			best = d
			best_pos = screen_pos
	if best == INF:
		_set_shown(false)
		return
	_set_shown(true)
	var dir: Vector2 = (best_pos - center).normalized()
	var half: Vector2 = SCREEN * 0.5 - Vector2(EDGE_INSET, EDGE_INSET)
	var k: float = minf(half.x / maxf(absf(dir.x), 0.001), half.y / maxf(absf(dir.y), 0.001))
	position = center + dir * k
	rotation = dir.angle()
	_t += delta
	modulate = Color(1.0, 1.0, 1.0, 0.75 + 0.25 * sin(_t * 6.0))  # лёгкая пульсация = «это интерфейс»


func _set_shown(on: bool) -> void:
	if on and not _was_visible:
		var v: int = randi_range(0, VARIANTS - 1)
		region_rect = Rect2(Vector2(v * FRAME_SIZE.x, 0.0), FRAME_SIZE)
	_was_visible = on
	visible = on
