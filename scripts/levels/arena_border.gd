extends Node2D
## Граница арены: несколько рядов мусорных баков, машин, трупов, заборов и стен + невидимые стены.
## Расстановка случайная и новая в каждом забеге (сцена пересоздаётся при рестарте).

const BORDER_TEXTURE: Texture2D = preload("res://assets/sprites/arena_border.png")
const SEGMENT_SIZE: Vector2 = Vector2(48.0, 32.0)
const SEGMENT_KINDS: int = 9
const WALL_LAYER: int = 32  # слой 6 «wall»
const SKIP_CHANCE: float = 0.12  # иногда оставляем дыру в ряду — выглядит живее


func _ready() -> void:
	var arena: float = Balance.ARENA_SIZE
	var thickness: float = Balance.ARENA_BORDER_THICKNESS
	var rows: int = int(ceilf(thickness / SEGMENT_SIZE.y))
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.randomize()
	for row: int in rows:
		var depth: float = SEGMENT_SIZE.y * (row + 0.5)
		var shift: float = SEGMENT_SIZE.x * 0.5 * (row % 2)  # шахматный сдвиг рядов
		var x: float = -thickness - shift
		while x < arena + thickness:
			var cx: float = x + SEGMENT_SIZE.x * 0.5
			_add_segment(Vector2(cx, -depth), 0.0, rng, row)
			_add_segment(Vector2(cx, arena + depth), PI, rng, row)
			x += SEGMENT_SIZE.x
		var y: float = -shift
		while y < arena:
			var cy: float = y + SEGMENT_SIZE.x * 0.5
			_add_segment(Vector2(-depth, cy), -PI * 0.5, rng, row)
			_add_segment(Vector2(arena + depth, cy), PI * 0.5, rng, row)
			y += SEGMENT_SIZE.x
	_add_colliders(arena, thickness)


func _add_segment(center: Vector2, angle: float, rng: RandomNumberGenerator, row: int) -> void:
	if row > 0 and rng.randf() < SKIP_CHANCE:
		return  # внешний ряд местами с прорехами; первый ряд сплошной
	var sprite: Sprite2D = Sprite2D.new()
	sprite.texture = BORDER_TEXTURE
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.region_enabled = true
	var kind: int = rng.randi_range(0, SEGMENT_KINDS - 1)
	sprite.region_rect = Rect2(Vector2(kind * SEGMENT_SIZE.x, 0.0), SEGMENT_SIZE)
	sprite.flip_h = rng.randf() < 0.5
	sprite.position = center
	sprite.rotation = angle
	add_child(sprite)


func _add_colliders(arena: float, thickness: float) -> void:
	var body: StaticBody2D = StaticBody2D.new()
	body.collision_layer = WALL_LAYER
	body.collision_mask = 0
	add_child(body)
	var span: float = arena + thickness * 2.0
	var rects: Array[Rect2] = [
		Rect2(-thickness, -thickness, span, thickness),
		Rect2(-thickness, arena, span, thickness),
		Rect2(-thickness, 0.0, thickness, arena),
		Rect2(arena, 0.0, thickness, arena),
	]
	for rect: Rect2 in rects:
		var shape: RectangleShape2D = RectangleShape2D.new()
		shape.size = rect.size
		var collision: CollisionShape2D = CollisionShape2D.new()
		collision.shape = shape
		collision.position = rect.position + rect.size * 0.5
		body.add_child(collision)
