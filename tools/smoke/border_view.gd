extends Node2D
## Проверка границы арены: строит её, снимает общий вид (камера отдалена) в tools/_preview/border_view_N.png, N = 0..2 (три раскладки).
const BORDER: GDScript = preload("res://scripts/levels/arena_border.gd")
var _shots: int = 0


func _ready() -> void:
	var cam: Camera2D = Camera2D.new()
	cam.position = Vector2(260.0, 260.0)
	cam.zoom = Vector2.ONE * 0.42
	add_child(cam)
	get_window().size = Vector2i(1280, 960)
	await get_tree().create_timer(0.2).timeout
	_spawn()


func _spawn() -> void:
	for n: Node in get_children():
		if n is Node2D and n.get_script() == BORDER:
			n.queue_free()
	var b: Node2D = BORDER.new()
	add_child(b)
	await get_tree().create_timer(14.0).timeout    # ждём, чтобы проехала машина
	get_viewport().get_texture().get_image().save_png("res://tools/_preview/border_view_%d.png" % _shots)
	_shots += 1
	if _shots >= 2:
		get_tree().quit()
	else:
		_spawn()
