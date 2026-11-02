extends Node
## Кадры книги-коллекции: каждая вкладка, часть открыта. tools/_preview/book_*.png

func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	var k: int = 0
	for id: StringName in Balance.ITEMS:   # открыта примерно половина
		k += 1
		if k % 2 == 0:
			Profile.stat_add(StringName("found_" + String(id)), 1)
	Profile.mods_seen.assign(Balance.WAVE_MODS.slice(0, 6))
	var yard: Node = load("res://scenes/ui/graveyard.tscn").instantiate()
	get_tree().root.add_child(yard)
	await get_tree().create_timer(0.6).timeout
	yard.call("_toggle_book")
	var book: Node = yard.get("_book")
	for tab: int in 5:
		book.call("_show_tab", tab)
		book.set("_cursor", 3)
		if tab > 0:
			book.call("_update_cursor")
		await get_tree().create_timer(0.1).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/book_%d.png" % tab))
	print("BOOK SHOTS DONE")
	get_tree().quit()
