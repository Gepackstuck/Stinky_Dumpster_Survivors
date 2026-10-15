extends Node
## ТЕСТ: бестиарий с частью убитых врагов. Кадры: tools/_preview/bestiary_*.png (счётчики профиля восстанавливаются).


func _shot(label: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/bestiary_%s.png" % label))


func _ready() -> void:
	var saved: Dictionary = Profile.enemy_kills.duplicate()
	for id: StringName in [&"squid_gopnik", &"chaser", &"spitter", &"charger", &"boss_zakhar", &"trash_bin", &"cockroach"]:
		Profile.enemy_kills[id] = 37
	var book: Control = load("res://scripts/ui/bestiary.gd").new()
	add_child(book)
	await get_tree().create_timer(0.5).timeout
	_shot("a")
	book.call("_select", 7)
	await get_tree().create_timer(0.3).timeout
	_shot("b")
	book.call("_select", 17)
	await get_tree().create_timer(0.3).timeout
	_shot("c")
	book.call("_select", 3)
	await get_tree().create_timer(0.3).timeout
	_shot("d")
	Profile.enemy_kills = saved
	get_tree().quit()
