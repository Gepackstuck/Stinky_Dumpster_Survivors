class_name Telegraph
extends Node2D
## Предупреждение об атаке врага (как зоны в Brotato, но злее): зона видна сразу полупрозрачной,
## полосатая заливка наползает от центра и доходит до края ровно в момент удара. На конце - череп.
## Формы: линия (рывок, бросок), круг (удар по площади, облако), конус (веер снарядов).

const STRIPE: Texture2D = preload("res://assets/sprites/tele_stripe.png")
const SKULL: Texture2D = preload("res://assets/sprites/tele_skull.png")
const EDGE: Color = Color(1.0, 0.0, 0.2)
const GHOST_ALPHA: float = 0.45
const FILL_ALPHA: float = 0.85

enum Shape { LINE, CIRCLE, CONE }

var _shape: Shape = Shape.LINE
var _dir: Vector2 = Vector2.RIGHT
var _length: float = 40.0
var _width: float = 6.0          # линия: полуширина; конус: полуугол (рад)
var _total: float = 0.5
var _left: float = 0.5
var _follow: Node2D = null


static func line(tree: SceneTree, from: Vector2, dir: Vector2, length: float, half_width: float, sec: float, follow: Node2D = null) -> Telegraph:
	return _spawn(tree, Shape.LINE, from, dir, length, half_width, sec, follow)


static func circle(tree: SceneTree, center: Vector2, radius: float, sec: float, follow: Node2D = null) -> Telegraph:
	return _spawn(tree, Shape.CIRCLE, center, Vector2.RIGHT, radius, 0.0, sec, follow)


static func cone(tree: SceneTree, from: Vector2, dir: Vector2, half_angle_deg: float, length: float, sec: float, follow: Node2D = null) -> Telegraph:
	return _spawn(tree, Shape.CONE, from, dir, length, deg_to_rad(half_angle_deg), sec, follow)


static func _spawn(tree: SceneTree, shape: Shape, at: Vector2, dir: Vector2, length: float, width: float, sec: float, follow: Node2D) -> Telegraph:
	var t: Telegraph = Telegraph.new()
	t._shape = shape
	t._dir = dir.normalized() if dir != Vector2.ZERO else Vector2.RIGHT
	t._length = length
	t._width = width
	t._total = maxf(sec, 0.05)
	t._left = t._total
	t._follow = follow
	t.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	t.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var ground: Node = tree.current_scene.get_node_or_null(^"Ground")   # ребёнок пола: над полом, под телами и пикапами
	(ground if ground != null else tree.current_scene).add_child(t)
	t.global_position = at
	return t


## Точка внутри зоны удара? (для ботов: обходят телеграфы)
func contains(point: Vector2) -> bool:
	var off: Vector2 = point - global_position
	match _shape:
		Shape.LINE:
			var along: float = off.dot(_dir)
			return along >= 0.0 and along <= _length and absf(off.dot(_dir.orthogonal())) <= _width
		Shape.CIRCLE:
			return off.length() <= _length
		_:
			return off.length() <= _length and absf(_dir.angle_to(off)) <= _width


func _process(delta: float) -> void:
	_left -= delta
	if _follow != null:
		if is_instance_valid(_follow):
			global_position = _follow.global_position
		else:
			queue_free()
			return
	if _left <= -0.08:
		queue_free()
		return
	queue_redraw()


func _draw() -> void:
	var t: float = clampf(1.0 - _left / _total, 0.0, 1.0)
	var blink: bool = _left <= 0.0
	var ghost: PackedVector2Array = _points(1.0)
	_fill(ghost, Color(1, 1, 1, GHOST_ALPHA))
	_fill(_points(t), Color(1, 1, 1, 1.0 if blink else FILL_ALPHA))
	var closed: PackedVector2Array = ghost.duplicate()
	closed.append(ghost[0])
	draw_polyline(closed, Color(0.04, 0.04, 0.04, 0.9), 2.0)   # чёрная подложка: контур читается на любом полу
	draw_polyline(closed, Color.WHITE if blink else EDGE, 1.0)
	var tip: Vector2 = Vector2.ZERO if _shape == Shape.CIRCLE else _dir * _length
	draw_texture(SKULL, (tip - SKULL.get_size() * 0.5).round(), Color(1, 1, 1, 0.5 + 0.5 * t))


## Контур формы при заполнении t (0..1).
func _points(t: float) -> PackedVector2Array:
	var pts: PackedVector2Array = PackedVector2Array()
	match _shape:
		Shape.LINE:
			var side: Vector2 = _dir.orthogonal() * _width
			var end: Vector2 = _dir * maxf(_length * t, 1.0)
			pts = PackedVector2Array([side, end + side, end - side, -side])
		Shape.CIRCLE:
			var r: float = maxf(_length * t, 1.0)
			for i: int in 20:
				pts.append(Vector2.from_angle(TAU * i / 20.0) * r)
		Shape.CONE:
			var r2: float = maxf(_length * t, 1.0)
			pts.append(Vector2.ZERO)
			for i: int in 9:
				pts.append(_dir.rotated(lerpf(-_width, _width, i / 8.0)) * r2)
	return pts


func _fill(pts: PackedVector2Array, color: Color) -> void:
	if pts.size() < 3:
		return
	var uvs: PackedVector2Array = PackedVector2Array()
	for p: Vector2 in pts:
		uvs.append((p + global_position) / 8.0)   # тайл привязан к миру: полосы не «едут» за врагом
	draw_colored_polygon(pts, color, uvs, STRIPE)
