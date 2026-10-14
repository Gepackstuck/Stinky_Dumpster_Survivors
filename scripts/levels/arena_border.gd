extends Node2D
## Граница арены: ряд проволоки (в каждом забеге один случайный вид), за ним редкие декорации.
## Электрическая и горящая проволока бьют игрока. Расстановка новая при каждом старте/рестарте.

const DECOR_TEXTURE: Texture2D = preload("res://assets/sprites/arena_border.png")
const WIRE_TEXTURE: Texture2D = preload("res://assets/sprites/arena_wire.png")
const DECOR_SIZE: Vector2 = Vector2(48.0, 32.0)
const WIRE_SIZE: Vector2 = Vector2(48.0, 16.0)
const BACKDROP_COLOR: Color = Color(0.2353, 0.1333, 0.0627)  # тёмная земля под декорациями
const WALL_LAYER: int = 32  # слой 6 «wall»
const ANIM_FRAME_SEC: float = 0.125
# Ячейки листа проволоки: 0..5 — статичные виды; 6-7 ток (2 кадра); 8-9 огонь (2 кадра).
const STATIC_WIRE_KINDS: int = 6
const ELECTRIC_CELL: int = 6
const FIRE_CELL: int = 8

var _rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _wire_cell: int = 0  # один вид проволоки на весь забег
var _animated: Array[Dictionary] = []
var _anim_time: float = 0.0
var _anim_step: int = 0


func _ready() -> void:
	_rng.randomize()
	_wire_cell = _random_wire_cell()
	var arena: float = Balance.ARENA_SIZE
	var thickness: float = Balance.ARENA_BORDER_THICKNESS
	_add_backdrop(arena, thickness)
	# Контейнер стороны: локальный +x идёт вдоль стороны, локальный -y — наружу от арены.
	_build_side(Vector2.ZERO, 0.0, -thickness, arena + thickness)
	_build_side(Vector2(arena, arena), PI, -thickness, arena + thickness)
	_build_side(Vector2(0.0, arena), -PI * 0.5, 0.0, arena)
	_build_side(Vector2(arena, 0.0), PI * 0.5, 0.0, arena)
	_add_colliders(arena, thickness)


func _process(delta: float) -> void:
	_anim_time += delta
	if _anim_time < ANIM_FRAME_SEC:
		return
	_anim_time = fmod(_anim_time, ANIM_FRAME_SEC)
	_anim_step += 1
	for entry: Dictionary in _animated:
		var sprite: Sprite2D = entry["sprite"]
		var cell: int = entry["cell"] + _anim_step % 2
		sprite.region_rect = Rect2(Vector2(cell * WIRE_SIZE.x, 0.0), WIRE_SIZE)


func _build_side(origin: Vector2, angle: float, from_along: float, to_along: float) -> void:
	var side: Node2D = Node2D.new()
	side.position = origin
	side.rotation = angle
	add_child(side)
	var along: float = from_along
	while along < to_along:
		_add_wire(side, along + WIRE_SIZE.x * 0.5, _wire_cell)
		if _rng.randf() < Balance.BORDER_DECOR_CHANCE:
			_add_decor(side, along + WIRE_SIZE.x * 0.5 + _rng.randf_range(-12.0, 12.0))
		along += WIRE_SIZE.x


func _random_wire_cell() -> int:
	var pick: int = _rng.randi_range(0, STATIC_WIRE_KINDS + 1)
	if pick < STATIC_WIRE_KINDS:
		return pick
	return ELECTRIC_CELL if pick == STATIC_WIRE_KINDS else FIRE_CELL


func _add_wire(side: Node2D, center_x: float, cell: int) -> void:
	var sprite: Sprite2D = Sprite2D.new()
	sprite.texture = WIRE_TEXTURE
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.region_enabled = true
	sprite.region_rect = Rect2(Vector2(cell * WIRE_SIZE.x, 0.0), WIRE_SIZE)
	sprite.position = Vector2(center_x, -WIRE_SIZE.y * 0.5)
	side.add_child(sprite)
	if cell >= ELECTRIC_CELL:
		_animated.append({"sprite": sprite, "cell": cell})
		_add_shock_area(side, center_x)


func _add_shock_area(side: Node2D, center_x: float) -> void:
	var hitbox: HitboxComponent = HitboxComponent.new()
	hitbox.damage = Balance.WIRE_SHOCK_DAMAGE
	hitbox.collision_layer = 0
	hitbox.collision_mask = 1
	var shape: RectangleShape2D = RectangleShape2D.new()
	shape.size = Vector2(WIRE_SIZE.x, WIRE_SIZE.y + 3.0)
	var collision: CollisionShape2D = CollisionShape2D.new()
	collision.shape = shape
	collision.position = Vector2(center_x, -WIRE_SIZE.y * 0.5 + 1.5)  # торчит на 3 px в арену
	hitbox.add_child(collision)
	side.add_child(hitbox)


func _add_decor(side: Node2D, center_x: float) -> void:
	var kinds: int = int(DECOR_TEXTURE.get_width() / DECOR_SIZE.x)
	var sprite: Sprite2D = Sprite2D.new()
	sprite.texture = DECOR_TEXTURE
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.region_enabled = true
	sprite.region_rect = Rect2(Vector2(_rng.randi_range(0, kinds - 1) * DECOR_SIZE.x, 0.0), DECOR_SIZE)
	sprite.flip_h = _rng.randf() < 0.5
	# Зона за проволокой: от WIRE_SIZE.y до толщины границы.
	var depth: float = WIRE_SIZE.y + DECOR_SIZE.y * 0.5 + _rng.randf_range(0.0, Balance.ARENA_BORDER_THICKNESS - WIRE_SIZE.y - DECOR_SIZE.y)
	sprite.position = Vector2(center_x, -depth)
	side.add_child(sprite)


func _add_backdrop(arena: float, thickness: float) -> void:
	for rect: Rect2 in _border_rects(arena, thickness):
		var fill: ColorRect = ColorRect.new()
		fill.color = BACKDROP_COLOR
		fill.position = rect.position
		fill.size = rect.size
		fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(fill)


func _add_colliders(arena: float, thickness: float) -> void:
	var body: StaticBody2D = StaticBody2D.new()
	body.collision_layer = WALL_LAYER
	body.collision_mask = 0
	add_child(body)
	for rect: Rect2 in _border_rects(arena, thickness):
		var shape: RectangleShape2D = RectangleShape2D.new()
		shape.size = rect.size
		var collision: CollisionShape2D = CollisionShape2D.new()
		collision.shape = shape
		collision.position = rect.position + rect.size * 0.5
		body.add_child(collision)


func _border_rects(arena: float, thickness: float) -> Array[Rect2]:
	var span: float = arena + thickness * 2.0
	return [
		Rect2(-thickness, -thickness, span, thickness),
		Rect2(-thickness, arena, span, thickness),
		Rect2(-thickness, 0.0, thickness, arena),
		Rect2(arena, 0.0, thickness, arena),
	]
