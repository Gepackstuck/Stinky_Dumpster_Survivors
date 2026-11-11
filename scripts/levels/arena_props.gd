class_name ArenaProps
extends Node2D
## Новая рисовка: арена - это место, а не пустое поле. Декорации (баки, контейнеры, остовы машин, покрышки, заборы, обломки стен, надгробья)
## по периметру плотнее, внутри редко; всё сортируется по высоте экрана вместе с существами (вид 3/4), у каждого - тень.
## Источники света (фонарь, бочка с огнём) - тёплые пятна на земле, мерцают. Без коллизий: ходить можно, но тут не очень красиво.
## Файлы: assets/hd/props/<имя>.png, описание - assets/hd/props.json. Числа - Balance.HD_PROPS_*.

const META: String = "res://assets/hd/props.json"
const DIR: String = "res://assets/hd/props/"

var _lights: Array[PointLight2D] = []
var _t: float = 0.0
var _flick: Array[float] = []
var _bases: Array[float] = []


func _ready() -> void:
	y_sort_enabled = true
	if not FileAccess.file_exists(META):
		return
	var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(META))
	var names: Array = meta.keys()
	if names.is_empty():
		return
	var arena: float = Balance.ARENA_SIZE
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.seed = hash(GameState.seed_word) if GameState.seed_word != "" else randi()
	var solid: Array = names.filter(func(n: String) -> bool: return not meta[n].has("light"))
	var lamps: Array = names.filter(func(n: String) -> bool: return meta[n].has("light"))
	var placed: Array[Vector2] = []
	for i: int in Balance.HD_PROPS_EDGE:
		var side: int = i % 4
		var along: float = rng.randf_range(20.0, arena - 20.0)
		var inset: float = rng.randf_range(4.0, Balance.HD_PROPS_EDGE_DEPTH)
		var p: Vector2 = [Vector2(along, inset), Vector2(along, arena - inset), Vector2(inset, along), Vector2(arena - inset, along)][side]
		_place(meta, solid[rng.randi() % solid.size()], p, placed, rng)
	for i: int in Balance.HD_PROPS_INNER:
		var p2: Vector2 = Vector2(rng.randf_range(60.0, arena - 60.0), rng.randf_range(60.0, arena - 60.0))
		if p2.distance_to(Vector2(arena, arena) * 0.5) < Balance.HD_PROPS_CLEAR_RADIUS:
			continue
		_place(meta, solid[rng.randi() % solid.size()], p2, placed, rng)
	if not lamps.is_empty():
		for i: int in Balance.HD_PROPS_LIGHTS:
			var p3: Vector2 = Vector2(rng.randf_range(50.0, arena - 50.0), rng.randf_range(50.0, arena - 50.0))
			if p3.distance_to(Vector2(arena, arena) * 0.5) < 50.0:
				continue
			_place(meta, lamps[rng.randi() % lamps.size()], p3, placed, rng)


func _place(meta: Dictionary, name: String, at: Vector2, placed: Array[Vector2], rng: RandomNumberGenerator) -> void:
	for q: Vector2 in placed:
		if q.distance_to(at) < Balance.HD_PROPS_MIN_GAP:
			return
	placed.append(at)
	var info: Dictionary = meta[name]
	var node: Node2D = Node2D.new()
	node.position = at
	var sp: Sprite2D = Sprite2D.new()
	sp.texture = load(DIR + name + ".png") as Texture2D
	sp.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	sp.scale = Vector2.ONE * 0.5
	sp.centered = true
	sp.offset = Vector2(0.0, -float(info["h"]) * 0.5)    # подошва на точке узла: сортировка по низу
	sp.flip_h = rng.randf() < 0.5
	node.add_child(sp)
	ArtStyle.shadow(node, float(info["world_w"]) * 0.9, 0.0)
	if info.has("light"):
		var l: Dictionary = info["light"]
		var light: PointLight2D = PointLight2D.new()
		light.texture = HdAtmosphere.light_texture()
		var c: Array = l["color"]
		light.color = Color(c[0], c[1], c[2])
		light.energy = float(l["energy"])
		light.texture_scale = float(l["radius"]) * 2.0 / 256.0
		light.position = Vector2(0.0, -float(info["h"]) * 0.35)
		node.add_child(light)
		_lights.append(light)
		_flick.append(rng.randf() * TAU)
		_bases.append(float(l["energy"]))
	add_child(node)


func _process(delta: float) -> void:
	_t += delta
	for i: int in _lights.size():
		var f: float = 1.0 + 0.12 * sin(_t * 9.0 + _flick[i]) + 0.08 * sin(_t * 23.0 + _flick[i] * 2.0)   # огонь живой, лампа с перебоями
		_lights[i].energy = _bases[i] * f
