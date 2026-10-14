extends Sprite2D
## Тайловый пол арены. Размер региона берётся из Balance.ARENA_SIZE.


func _ready() -> void:
	region_rect = Rect2(Vector2.ZERO, Vector2(Balance.ARENA_SIZE, Balance.ARENA_SIZE))
