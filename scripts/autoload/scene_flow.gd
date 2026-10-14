extends CanvasLayer
## Переходы между экранами без швов: старый кадр «уезжает» с экрана, под ним уже живёт новая сцена.
## Меню -> кладбище -> арена едем вниз (старый кадр уходит вверх); с арены обратно на кладбище - наоборот.
## Арена и кладбище остаются разными сценами, поэтому во время боя под ареной ничего не видно.

const SLIDE_SEC: float = 0.55

var _busy: bool = false
var from_arena: bool = false   # на кладбище пришли через ворота арены: герой входит оттуда


func _ready() -> void:
	layer = 200
	process_mode = Node.PROCESS_MODE_ALWAYS


## Кладбище стоит ПОД ареной. direction: старый кадр уезжает в сторону, противоположную движению камеры:
## на арену (камера вверх) старый кадр уходит ВНИЗ (передать Vector2.UP), с арены на кладбище - вверх (Vector2.DOWN).
## Vector2.ZERO - просто затемнение.
func go(path: String, direction: Vector2 = Vector2.DOWN) -> void:
	if _busy:
		return
	_busy = true
	get_tree().paused = false
	var frame: Image = get_viewport().get_texture().get_image()
	var cover: TextureRect = TextureRect.new()
	cover.texture = ImageTexture.create_from_image(frame)
	cover.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	cover.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	cover.stretch_mode = TextureRect.STRETCH_SCALE
	var size: Vector2 = get_viewport().get_visible_rect().size
	cover.size = size
	cover.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(cover)
	get_tree().change_scene_to_file(path)
	await get_tree().process_frame
	await get_tree().process_frame
	var tween: Tween = create_tween().set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
	if direction == Vector2.ZERO:
		tween.tween_property(cover, "modulate:a", 0.0, SLIDE_SEC)
	else:
		tween.tween_property(cover, "position", -direction * size, SLIDE_SEC)
	await tween.finished
	cover.queue_free()
	_busy = false
