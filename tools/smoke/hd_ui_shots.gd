extends Node
## Новая пиксельная: экраны интерфейса (главное меню, настройки, карточки выбора старта) -> tools/_preview/hd/05_пиксели/ui_*.png. Оконный режим.

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Profile.sandbox = true
	Settings.art_style = "new"
	ArtStyle.apply_ui()
	_run.call_deferred()


func _shot(name: String) -> void:
	await get_tree().create_timer(0.6).timeout
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/hd/05_пиксели/ui_%s.png" % name))


func _run() -> void:
	var menu: Node = (load("res://scenes/ui/main_menu.tscn") as PackedScene).instantiate()
	get_tree().root.add_child(menu)
	await _shot("меню")
	menu.queue_free()
	GameState.character = &"hobo"
	var level: Node = (load("res://scenes/levels/main.tscn") as PackedScene).instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(1.5).timeout
	await _shot("старт_карточки")
	print("UI SHOTS DONE")
	get_tree().quit()
