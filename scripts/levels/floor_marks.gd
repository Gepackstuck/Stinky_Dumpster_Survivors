extends Node2D
## Редкие коричневые точки на полу, чтобы было видно, что игрок движется.
## Рисуется один раз (CanvasItem кэширует _draw).

const SPACING: float = 32.0
const DOT_SIZE: Vector2 = Vector2(2.0, 2.0)
const DOT_COLOR: Color = Color8(0x6B, 0x3E, 0x1F)


func _draw() -> void:
	var steps: int = int(Balance.ARENA_SIZE / SPACING)
	for ix: int in range(steps + 1):
		for iy: int in range(steps + 1):
			draw_rect(Rect2(Vector2(ix, iy) * SPACING, DOT_SIZE), DOT_COLOR)
