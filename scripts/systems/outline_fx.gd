class_name OutlineFx
extends RefCounted
## Цветная обводка по тиру, как в Brotato: оружие и шмотки на герое светятся цветом уровня.
## Тир I - без обводки, II - синяя, III - фиолетовая, IV - красная.

const TIER_COLORS: Array[Color] = [Color(0, 0, 0, 0), Color(0.25, 0.6, 1.0), Color(0.78, 0.3, 1.0), Color(1.0, 0.2, 0.2)]

static var _cache: Dictionary = {}


## Копия текстуры с отступом в 1 px и обводкой цветом тира. Тир I - исходная текстура.
static func outlined(texture: Texture2D, tier: int) -> Texture2D:
	if texture == null or tier <= 1:
		return texture
	var key: String = "%d_%d" % [texture.get_instance_id(), tier]
	if _cache.has(key):
		return _cache[key]
	var src: Image = texture.get_image()
	if src == null:
		return texture
	src.convert(Image.FORMAT_RGBA8)
	var w: int = src.get_width()
	var h: int = src.get_height()
	var base: Image = Image.create(w + 2, h + 2, false, Image.FORMAT_RGBA8)
	base.blit_rect(src, Rect2i(0, 0, w, h), Vector2i(1, 1))
	var out: Image = base.duplicate()
	var color: Color = TIER_COLORS[clampi(tier - 1, 0, TIER_COLORS.size() - 1)]
	for y: int in h + 2:
		for x: int in w + 2:
			if base.get_pixel(x, y).a > 0.0:
				continue
			for d: Vector2i in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
				var nx: int = x + d.x
				var ny: int = y + d.y
				if nx >= 0 and ny >= 0 and nx < w + 2 and ny < h + 2 and base.get_pixel(nx, ny).a > 0.0:
					out.set_pixel(x, y, color)
					break
	var result: ImageTexture = ImageTexture.create_from_image(out)
	_cache[key] = result
	return result

