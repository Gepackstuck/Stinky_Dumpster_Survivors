class_name HdCorpse
extends Sprite2D
## Детальный стиль: тело убитого врага доигрывает ряд «смерть» и тает. Не сталкивается, ничего не считает.

var _fps: float = 12.0
var _first: int = 0
var _count: int = 1
var _t: float = 0.0


static func spawn(parent: Node, from: Sprite2D, at: Vector2, row: int, count: int, fps: float) -> void:
	var c: HdCorpse = HdCorpse.new()
	c.texture = from.texture
	c.hframes = from.hframes
	c.vframes = from.vframes
	c.texture_filter = from.texture_filter
	c.scale = from.scale
	c.flip_h = from.flip_h
	c.z_index = -1   # под живыми
	c._first = row * from.hframes
	c._count = count
	c._fps = fps
	c.frame = c._first
	parent.add_child(c)
	c.global_position = at


func _process(delta: float) -> void:
	_t += delta
	var i: int = int(_t * _fps)
	if i < _count:
		frame = _first + i
		return
	frame = _first + _count - 1
	var fade: float = (_t - _count / _fps) / Balance.HD_CORPSE_FADE_SEC
	modulate.a = 1.0 - fade
	if fade >= 1.0:
		queue_free()
