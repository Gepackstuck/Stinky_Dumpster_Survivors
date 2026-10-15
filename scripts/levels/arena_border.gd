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
const DECOR_FRAMES: int = 4   # кадров анимации у каждой декорации (лист: вид × кадр)
const DECOR_STEP_SEC: float = 0.3
# Темы сторон: сверху кладбище+свалка, слева/справа случайно дорога (с машинами) или дома, снизу болото.
enum Zone { GRAVEYARD, ROAD, HOUSES, SWAMP }
const GROUND_INDEX: Dictionary = {Zone.GRAVEYARD: 2, Zone.ROAD: 1, Zone.HOUSES: 3, Zone.SWAMP: 4}
const CAR_SIZE: Vector2 = Vector2(56.0, 26.0)
const GROUND_PATH: String = "res://assets/sprites/border_ground.png"
const HOUSE_COUNT: int = 5
const SWAMP_COUNT: int = 5

var GROUND_SHEET: Texture2D
var TOMBS_TEX: Texture2D
var DUMPS_TEX: Texture2D
var CARS_TEX: Texture2D
var HOUSE_TEXS: Array[Texture2D] = []
var SWAMP_TEXS: Array[Texture2D] = []
const CAR_FRAME_SEC: float = 0.12
const CAR_MIN_PAUSE_SEC: float = 7.0
const CAR_MAX_PAUSE_SEC: float = 20.0
const CAR_KINDS: int = 6
# Ячейки листа проволоки: 0..5 — статичные виды; 6-7 ток (2 кадра); 8-9 огонь (2 кадра).
const STATIC_WIRE_KINDS: int = 6
const ELECTRIC_CELL: int = 6
const FIRE_CELL: int = 8

var _rng: RandomNumberGenerator = RandomNumberGenerator.new()
var _wire_cell: int = 0  # один вид проволоки на весь забег
var _animated: Array[Dictionary] = []
var _anim_time: float = 0.0
var _anim_step: int = 0
var _decor_anim: Array[Dictionary] = []
var _bag: Array[int] = []        # «мешок» видов декора: пока не вытащены все, повторов нет
var _last_kind: int = -1
var _bags: Dictionary = {}
var _themes: Array[int] = []   # тема по сторонам: 0 верх, 1 низ, 2 лево, 3 право
var _cars: Array[Dictionary] = []
var _road_sides: Array[Node2D] = []
var _road_len: Dictionary = {}
var _car_pause: float = 6.0
var _car_time: float = 0.0
var _ground_textures: Dictionary = {}
var _decor_time: float = 0.0


func _load_textures() -> void:
	GROUND_SHEET = CharacterLibrary.load_texture(GROUND_PATH)
	TOMBS_TEX = CharacterLibrary.load_texture("res://assets/sprites/border_tombs.png")
	DUMPS_TEX = CharacterLibrary.load_texture("res://assets/sprites/border_dumps.png")
	CARS_TEX = CharacterLibrary.load_texture("res://assets/sprites/border_cars.png")
	for k: int in HOUSE_COUNT:
		HOUSE_TEXS.append(CharacterLibrary.load_texture("res://assets/sprites/border_house_%d.png" % k))
	for k: int in SWAMP_COUNT:
		SWAMP_TEXS.append(CharacterLibrary.load_texture("res://assets/sprites/border_swamp_%d.png" % k))


func _ready() -> void:
	_load_textures()
	_rng.randomize()
	_wire_cell = _random_wire_cell()
	var arena: float = Balance.ARENA_SIZE
	var thickness: float = Balance.ARENA_BORDER_THICKNESS
	var road_left: bool = _rng.randf() < 0.5
	_themes.assign([Zone.GRAVEYARD, Zone.SWAMP, Zone.ROAD if road_left else Zone.HOUSES, Zone.HOUSES if road_left else Zone.ROAD])
	_add_backdrop(arena, thickness)
	# Контейнер стороны: локальный +x идёт вдоль стороны, локальный -y — наружу от арены.
	# Верх и низ - ровно по длине арены; левая и правая стороны тянутся через углы (дорога идёт от края до края).
	_build_side(Vector2.ZERO, 0.0, 0.0, arena, _themes[0])
	_build_side(Vector2(arena, arena), PI, 0.0, arena, _themes[1])
	_build_side(Vector2(0.0, arena), -PI * 0.5, -thickness, arena + thickness, _themes[2])
	_build_side(Vector2(arena, 0.0), PI * 0.5, -thickness, arena + thickness, _themes[3])
	_add_colliders(arena, thickness)


func _process(delta: float) -> void:
	_decor_time += delta
	var decor_tick: int = int(_decor_time / DECOR_STEP_SEC)
	for entry: Dictionary in _decor_anim:
		var frame: int = (decor_tick + int(entry["phase"])) % DECOR_FRAMES
		var cell: Vector2 = entry["cell"]
		(entry["sprite"] as Sprite2D).region_rect = Rect2(Vector2((int(entry["kind"]) * DECOR_FRAMES + frame) * cell.x, 0.0), cell)
	_update_cars(delta)
	_anim_time += delta
	if _anim_time < ANIM_FRAME_SEC:
		return
	_anim_time = fmod(_anim_time, ANIM_FRAME_SEC)
	_anim_step += 1
	for entry: Dictionary in _animated:
		var sprite: Sprite2D = entry["sprite"]
		var cell: int = entry["cell"] + _anim_step % 2
		sprite.region_rect = Rect2(Vector2(cell * WIRE_SIZE.x, 0.0), WIRE_SIZE)


func _build_side(origin: Vector2, angle: float, from_along: float, to_along: float, theme: int) -> void:
	var side: Node2D = Node2D.new()
	side.position = origin
	side.rotation = angle
	add_child(side)
	_add_ground(side, from_along, to_along, theme)
	if theme == Zone.HOUSES:
		_place_big(side, from_along, to_along, HOUSE_TEXS, 2 + _rng.randi_range(0, 1))
	elif theme == Zone.SWAMP:
		_place_big(side, from_along, to_along, SWAMP_TEXS, 2 + _rng.randi_range(0, 1))
	var wire_at: float = 0.0
	while wire_at < Balance.ARENA_SIZE:   # проволока - только вдоль арены, без «хвостов» в углах
		_add_wire(side, wire_at + WIRE_SIZE.x * 0.5, _wire_cell)
		wire_at += WIRE_SIZE.x
	var along: float = from_along
	while along < to_along:
		_fill_cell(side, along + WIRE_SIZE.x * 0.5, theme)
		along += WIRE_SIZE.x
	if theme == Zone.ROAD:
		_road_sides.append(side)
		_road_len[side] = Vector2(from_along, to_along)


## Земля темы: тайл повторяется по зоне за проволокой (в координатах стороны).
func _add_ground(side: Node2D, from_along: float, to_along: float, theme: int) -> void:
	var idx: int = GROUND_INDEX[theme]
	if not _ground_textures.has(idx):
		var img: Image = GROUND_SHEET.get_image()
		_ground_textures[idx] = ImageTexture.create_from_image(img.get_region(Rect2i(idx * 48, 0, 48, 48)))
	var ground: Sprite2D = Sprite2D.new()
	ground.texture = _ground_textures[idx]
	ground.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	ground.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
	ground.centered = false
	ground.region_enabled = true
	ground.region_rect = Rect2(0.0, 0.0, to_along - from_along, 48.0)
	ground.position = Vector2(from_along, -Balance.ARENA_BORDER_THICKNESS)
	side.add_child(ground)


func _fill_cell(side: Node2D, cx: float, theme: int) -> void:
	var r: float = _rng.randf()
	match theme:
		Zone.GRAVEYARD:
			if r < 0.5:
				_add_themed(side, TOMBS_TEX, "tombs", cx + _rng.randf_range(-8.0, 8.0), Vector2(48.0, 32.0), 20.0, 40.0)
			elif r < 0.68:
				_add_themed(side, DUMPS_TEX, "dumps", cx + _rng.randf_range(-6.0, 6.0), Vector2(48.0, 32.0), 20.0, 40.0)
			elif r < 0.92:
				_add_decor(side, cx + _rng.randf_range(-12.0, 12.0))
		Zone.HOUSES:
			if _rng.randf() < 0.6:
				_add_decor(side, cx + _rng.randf_range(-14.0, 14.0), 0.0, 4.0)   # хлам перед домами
		Zone.SWAMP:
			if r < 0.2:
				_add_decor(side, cx + _rng.randf_range(-12.0, 12.0), 0.0, 4.0)
		_:
			pass   # дорога: пусто, ездят машины


func _pull(bag_name: String, kinds: int) -> int:
	var bag: Array = _bags.get(bag_name, [])
	if bag.is_empty():
		for k: int in kinds:
			bag.append(k)
		bag.shuffle()
	var kind: int = bag.pop_back()
	_bags[bag_name] = bag
	return kind


func _add_themed(side: Node2D, tex: Texture2D, bag_name: String, x: float, cell: Vector2, depth_min: float, depth_max: float) -> void:
	var kinds: int = int(tex.get_width() / (cell.x * DECOR_FRAMES))
	var kind: int = _pull(bag_name, kinds)
	var sprite: Sprite2D = _make_sprite(tex, kind, 0, cell)
	sprite.flip_h = _rng.randf() < 0.5
	sprite.position = Vector2(x, -(WIRE_SIZE.y + cell.y * 0.5 + _rng.randf_range(0.0, Balance.ARENA_BORDER_THICKNESS - WIRE_SIZE.y - cell.y)))
	sprite.rotation = -side.rotation
	side.add_child(sprite)
	_decor_anim.append({"sprite": sprite, "kind": kind, "phase": _rng.randi_range(0, DECOR_FRAMES - 1), "cell": cell})


## Огромные постройки/болотные объекты: на всю сторону 2–3 штуки, разной формы, стоят вплотную к дальнему краю зоны.
func _place_big(side: Node2D, from_along: float, to_along: float, texs: Array[Texture2D], want: int) -> void:
	var order: Array[int] = []
	for k: int in texs.size():
		order.append(k)
	order.shuffle()
	var length: float = to_along - from_along
	var picked: Array[int] = []
	var total: float = 0.0
	for k: int in order:
		var w: float = texs[k].get_width() / float(DECOR_FRAMES)
		if picked.size() < want and total + w <= length - 16.0:
			picked.append(k)
			total += w
	var gap: float = (length - total) / float(picked.size() + 1)
	var x: float = from_along + gap
	for k: int in picked:
		var tex: Texture2D = texs[k]
		var cell: Vector2 = Vector2(tex.get_width() / float(DECOR_FRAMES), tex.get_height())
		var sprite: Sprite2D = _make_sprite(tex, 0, 0, cell)
		sprite.position = Vector2(x + cell.x * 0.5, -(WIRE_SIZE.y + 6.0) - cell.y * 0.5)
		if absf(absf(side.rotation) - PI * 0.5) > 0.1:   # сверху/снизу большие объекты стоят ровно; по бокам - лёжа вдоль стороны
			sprite.rotation = -side.rotation
		side.add_child(sprite)
		_decor_anim.append({"sprite": sprite, "kind": 0, "phase": _rng.randi_range(0, DECOR_FRAMES - 1), "cell": cell})
		x += cell.x + gap


func _make_sprite(tex: Texture2D, kind: int, frame: int, cell: Vector2) -> Sprite2D:
	var sprite: Sprite2D = Sprite2D.new()
	sprite.texture = tex
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.region_enabled = true
	sprite.region_rect = Rect2(Vector2((kind * DECOR_FRAMES + frame) * cell.x, 0.0), cell)
	return sprite


## Машины: изредка проезжают по дороге (две полосы, встречные).
func _update_cars(delta: float) -> void:
	_car_time += delta
	if not _road_sides.is_empty():
		_car_pause -= delta
		if _car_pause <= 0.0:
			_car_pause = _rng.randf_range(CAR_MIN_PAUSE_SEC, CAR_MAX_PAUSE_SEC)
			_spawn_car()
	var frame: int = int(_car_time / CAR_FRAME_SEC) % 2
	for i: int in range(_cars.size() - 1, -1, -1):
		var car: Dictionary = _cars[i]
		var sprite: Sprite2D = car["sprite"]
		sprite.position.x += float(car["speed"]) * delta
		sprite.region_rect = Rect2(Vector2((int(car["kind"]) * 2 + frame) * CAR_SIZE.x, 0.0), CAR_SIZE)
		var past_end: bool = (float(car["speed"]) > 0.0 and sprite.position.x > float(car["end_x"])) or (float(car["speed"]) < 0.0 and sprite.position.x < float(car["end_x"]))
		if past_end:
			sprite.queue_free()
			_cars.remove_at(i)


func _spawn_car() -> void:
	var side: Node2D = _road_sides[_rng.randi_range(0, _road_sides.size() - 1)]
	var span: Vector2 = _road_len[side]
	var dir: float = 1.0 if _rng.randf() < 0.5 else -1.0
	var kind: int = _rng.randi_range(0, CAR_KINDS - 1)
	var sprite: Sprite2D = Sprite2D.new()
	sprite.texture = CARS_TEX
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.region_enabled = true
	sprite.region_rect = Rect2(Vector2(kind * 2 * CAR_SIZE.x, 0.0), CAR_SIZE)
	sprite.flip_h = dir < 0.0
	var lane_y: float = -(WIRE_SIZE.y + (13.0 if dir > 0.0 else 35.0))   # полоса по направлению
	var start_x: float = span.x - CAR_SIZE.x if dir > 0.0 else span.y + CAR_SIZE.x
	sprite.position = Vector2(start_x, lane_y)
	sprite.z_index = 1
	side.add_child(sprite)
	_cars.append({"sprite": sprite, "kind": kind, "speed": dir * _rng.randf_range(70.0, 130.0), "end_x": span.y + CAR_SIZE.x if dir > 0.0 else span.x - CAR_SIZE.x})


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
	hitbox.source_id = &"wire"
	hitbox.collision_layer = 0
	hitbox.collision_mask = 1
	var shape: RectangleShape2D = RectangleShape2D.new()
	shape.size = Vector2(WIRE_SIZE.x, WIRE_SIZE.y + 3.0)
	var collision: CollisionShape2D = CollisionShape2D.new()
	collision.shape = shape
	collision.position = Vector2(center_x, -WIRE_SIZE.y * 0.5 + 1.5)  # торчит на 3 px в арену
	hitbox.add_child(collision)
	side.add_child(hitbox)


func _add_decor(side: Node2D, center_x: float, depth_min: float = 0.0, depth_max: float = -1.0) -> void:
	var kinds: int = int(DECOR_TEXTURE.get_width() / (DECOR_SIZE.x * DECOR_FRAMES))
	var sprite: Sprite2D = Sprite2D.new()
	sprite.texture = DECOR_TEXTURE
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sprite.region_enabled = true
	var kind: int = _next_kind(kinds)
	sprite.region_rect = Rect2(Vector2(kind * DECOR_FRAMES * DECOR_SIZE.x, 0.0), DECOR_SIZE)
	_decor_anim.append({"sprite": sprite, "kind": kind, "phase": _rng.randi_range(0, DECOR_FRAMES - 1), "cell": DECOR_SIZE})
	sprite.flip_h = _rng.randf() < 0.5
	# Зона за проволокой: от WIRE_SIZE.y до толщины границы.
	var far: float = Balance.ARENA_BORDER_THICKNESS - WIRE_SIZE.y - DECOR_SIZE.y
	var depth: float = WIRE_SIZE.y + DECOR_SIZE.y * 0.5 + _rng.randf_range(depth_min, far if depth_max < 0.0 else minf(depth_max, far))
	sprite.position = Vector2(center_x, -depth)
	sprite.rotation = -side.rotation   # предметы стоят ровно, а не лежат на боку
	side.add_child(sprite)


func _next_kind(kinds: int) -> int:
	if _bag.is_empty():
		for k: int in kinds:
			_bag.append(k)
		_bag.shuffle()
		if _bag.size() > 1 and _bag.back() == _last_kind:   # на стыке мешков тоже без подряд-повторов
			_bag.push_front(_bag.pop_back())
	_last_kind = _bag.pop_back()
	return _last_kind


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
