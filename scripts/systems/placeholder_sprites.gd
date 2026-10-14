class_name PlaceholderSprites
extends RefCounted
## Программно сгенерированные placeholder-спрайты (ART_STYLE.md).
## Внешних ассетов нет: Image.create_empty() + ImageTexture.create_from_image().
## Текстуры кэшируются, повторные вызовы ничего не аллоцируют.

const OUTLINE: Color = Color8(0x0A, 0x0A, 0x0A)
const PLAYER_FILL: Color = Color8(0x39, 0xFF, 0x14)
const ENEMY_FILL: Color = Color8(0xFF, 0x10, 0xF0)
const PROJECTILE_FILL: Color = Color8(0xF7, 0xFF, 0x00)

static var _cache: Dictionary[StringName, Texture2D] = {}


## Игрок 24x24: зелёный квадрат, чёрная обводка, глаза разного размера.
static func player() -> Texture2D:
	if not _cache.has(&"player"):
		_cache[&"player"] = _make_box(24, 24, PLAYER_FILL, [Rect2i(5, 7, 4, 4), Rect2i(15, 8, 2, 2)])
	return _cache[&"player"]


## Обычный враг 16x16: розовый квадрат, чёрная обводка, глаза разного размера.
static func enemy() -> Texture2D:
	if not _cache.has(&"enemy"):
		_cache[&"enemy"] = _make_box(16, 16, ENEMY_FILL, [Rect2i(3, 4, 3, 3), Rect2i(9, 5, 2, 2)])
	return _cache[&"enemy"]


## Снаряд 4x4: жёлтый «круг».
static func projectile() -> Texture2D:
	if not _cache.has(&"projectile"):
		var img: Image = Image.create_empty(4, 4, false, Image.FORMAT_RGBA8)
		for y: int in 4:
			for x: int in 4:
				var is_corner: bool = (x == 0 or x == 3) and (y == 0 or y == 3)
				if not is_corner:
					img.set_pixel(x, y, PROJECTILE_FILL)
		_cache[&"projectile"] = ImageTexture.create_from_image(img)
	return _cache[&"projectile"]


static func _make_box(width: int, height: int, fill: Color, eyes: Array[Rect2i]) -> Texture2D:
	var img: Image = Image.create_empty(width, height, false, Image.FORMAT_RGBA8)
	for y: int in height:
		for x: int in width:
			var is_edge: bool = x == 0 or y == 0 or x == width - 1 or y == height - 1
			var is_corner: bool = (x == 0 or x == width - 1) and (y == 0 or y == height - 1)
			if is_corner:
				continue
			img.set_pixel(x, y, OUTLINE if is_edge else fill)
	for eye: Rect2i in eyes:
		for y: int in range(eye.position.y, eye.end.y):
			for x: int in range(eye.position.x, eye.end.x):
				img.set_pixel(x, y, OUTLINE)
	return ImageTexture.create_from_image(img)
