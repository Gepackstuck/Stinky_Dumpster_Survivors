extends Sprite2D
## Пол арены: тайловая земля + случайно рассыпанные декали (лужи, кишки, говно, кости, глаза).
## Декали новые в каждом забеге; приглушены, чтобы не мешать читать врагов.

const DECALS: Texture2D = preload("res://assets/sprites/ground_decals.png")
const CELL: float = 24.0
const DECAL_ALPHA: float = 0.45
const DECAL_TINT: Color = Color(0.85, 0.6, 0.68)  # приглушает зелёное: декали не должны путаться с опытом


func _ready() -> void:
	var arena: float = Balance.ARENA_SIZE
	region_rect = Rect2(Vector2.ZERO, Vector2(arena, arena))
	EventBus.bin_destroyed.connect(_on_bin_destroyed)
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


## На месте разбитого бака остаётся случайный мусор (декаль пола) — до конца забега, ярче обычных.
func _on_bin_destroyed(at: Vector2) -> void:
	var kinds: int = int(DECALS.get_width() / CELL)
	var decal: Sprite2D = Sprite2D.new()
	decal.texture = DECALS
	decal.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	decal.region_enabled = true
	decal.region_rect = Rect2(Vector2(randi_range(0, kinds - 1) * CELL, 0.0), Vector2(CELL, CELL))
	decal.flip_h = randf() < 0.5
	decal.rotation = (PI * 0.5) * randi_range(0, 3)
	decal.modulate = Color(DECAL_TINT, 0.8)
	decal.position = to_local(at).round()
	add_child(decal)
