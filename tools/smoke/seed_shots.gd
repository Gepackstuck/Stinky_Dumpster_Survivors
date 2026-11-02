extends Node
## Кадры меню с кнопкой «Шизосид» и окна ввода. tools/_preview/seed_*.png

func _ready() -> void:
	Profile.sandbox = true
	_run.call_deferred()


func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/seed_%s.png" % n))


func _run() -> void:
	var menu: Node = load("res://scenes/ui/main_menu.tscn").instantiate()
	get_tree().root.add_child(menu)
	await get_tree().create_timer(0.5).timeout
	await _shot("1_menu")
	menu.call("_open_modes")
	await get_tree().create_timer(0.2).timeout
	await _shot("3_modes")
	menu.call("_close_modes")
	menu.call("_open_seed")
	await get_tree().create_timer(0.2).timeout
	(menu.get("_seed_panel").get("_edit") as LineEdit).text = "ВАСЯ"
	await _shot("2_panel")
	get_tree().quit()
