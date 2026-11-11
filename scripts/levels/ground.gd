extends Sprite2D
## Пол арены: тайловая земля + случайно рассыпанные декали (лужи, кишки, говно, кости, глаза).
## Декали новые в каждом забеге; приглушены, чтобы не мешать читать врагов.

const DECALS: Texture2D = preload("res://assets/sprites/ground_decals.png")
const DECALS_PATH: String = "res://assets/sprites/ground_decals.png"
const TILE_PATH: String = "res://assets/sprites/ground_tile.png"
const CELL: float = 24.0
const DECAL_ALPHA: float = 0.4   # спокойный пол: враги и пикапы читаются (как в Brotato)
const DECAL_TINT: Color = Color(0.92, 0.72, 0.78)  # приглушает зелёное: декали не должны путаться с опытом


func _ready() -> void:
	var arena: float = Balance.ARENA_SIZE
	region_rect = Rect2(Vector2.ZERO, Vector2(arena, arena))
	var hd: Dictionary = ArtStyle.info(TILE_PATH)
	if not hd.is_empty():   # детальный стиль: своя плитка грязи, пиксельные декали не кладём
		var k: float = ArtStyle.apply(self, TILE_PATH)
		scale = Vector2.ONE * k
		region_rect = Rect2(Vector2.ZERO, Vector2(arena, arena) / k)
	EventBus.bin_destroyed.connect(_on_bin_destroyed)
	EventBus.wave_started.connect(func(_w: int) -> void: _apply_season())
	EventBus.wave_ended.connect(func(_w: int) -> void: _apply_season.call_deferred())
	if not hd.is_empty():
		_scatter_hd_decals(arena)
		return
	var kinds: int = int(DECALS.get_width() / CELL)
	var count: int = int(arena * arena / Balance.GROUND_DECAL_AREA_PX2)
	for i: int in count:
		var decal: Sprite2D = Sprite2D.new()
		decal.texture = DECALS
		decal.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		decal.centered = true
		decal.region_enabled = true
		decal.region_rect = Rect2(Vector2(randi_range(0, kinds - 1) * CELL, 0.0), Vector2(CELL, CELL))
		decal.flip_h = randf() < 0.5
		decal.flip_v = randf() < 0.5
		decal.rotation = (PI * 0.5) * randi_range(0, 3)
		decal.modulate = Color(DECAL_TINT, DECAL_ALPHA)
		decal.position = Vector2(randf_range(0.0, arena), randf_range(0.0, arena)).round()
		add_child(decal)


## Пол красится погодой волны (лето - выжженный, зима - синюшный); плавно, за секунду.
func _apply_season() -> void:
	var tint: Color = Balance.SEASONS.get(GameState.season, {}).get("tint", Color.WHITE)
	create_tween().tween_property(self, ^"modulate", tint, 1.0)


## На месте разбитого бака остаётся случайный мусор (декаль пола) — до конца забега, ярче обычных.
func _on_bin_destroyed(at: Vector2) -> void:
	if ArtStyle.has_hd(TILE_PATH):
		return
	var kinds: int = int(DECALS.get_width() / CELL)
	var decal: Sprite2D = Sprite2D.new()
	decal.texture = DECALS
	decal.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	decal.region_enabled = true
	decal.region_rect = Rect2(Vector2(randi_range(0, kinds - 1) * CELL, 0.0), Vector2(CELL, CELL))
	decal.flip_h = randf() < 0.5
	decal.rotation = (PI * 0.5) * randi_range(0, 3)
	decal.modulate = Color(DECAL_TINT, 0.9)
	decal.position = to_local(at).round()
	add_child(decal)


## Детальный стиль: лужи крови и кучи потрохов по арене, новые в каждом забеге; тёмные, чтобы не спорить с врагами.
func _scatter_hd_decals(arena: float) -> void:
	var d: Dictionary = ArtStyle.info(DECALS_PATH)
	if d.is_empty():
		return
	for i: int in int(arena * arena / Balance.HD_DECAL_AREA_PX2):
		var decal: Sprite2D = Sprite2D.new()
		add_child(decal)
		var k: float = ArtStyle.apply(decal, DECALS_PATH)
		decal.frame = randi() % decal.hframes
		decal.rotation = randf() * TAU
		decal.flip_h = randf() < 0.5
		decal.modulate.a = Balance.HD_DECAL_ALPHA
		decal.global_scale = Vector2.ONE * k * randf_range(0.7, 1.2)
		decal.global_position = global_position + Vector2(randf_range(0.0, arena), randf_range(0.0, arena))
