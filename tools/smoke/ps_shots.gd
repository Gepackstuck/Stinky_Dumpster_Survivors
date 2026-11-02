extends Node
## Кадр: подсказки Ларька с кнопками PlayStation. tools/_preview/ps_shop.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(0.8).timeout
	InputMode.pad = true
	InputMode.sony = true
	GameState.wave = 3
	EventBus.wave_ended.emit(3)
	await get_tree().create_timer(0.6).timeout
	await RenderingServer.frame_post_draw
	var img: Image = get_viewport().get_texture().get_image()
	img.get_region(Rect2i(0, int(img.get_height() * 0.72), img.get_width(), int(img.get_height() * 0.28))).save_png(ProjectSettings.globalize_path("res://tools/_preview/ps_shop.png"))
	get_tree().quit()
