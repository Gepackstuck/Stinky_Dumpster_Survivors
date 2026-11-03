extends Node
## Кадры кладбища для проверки текста: героя с длинным рывком, досье. tools/_preview/yard_text_*.png. Оконный режим.

func _ready() -> void:
	Profile.sandbox = true
	var yard: Node = load("res://scenes/ui/graveyard.tscn").instantiate()
	add_child(yard)
	await get_tree().create_timer(0.6).timeout
	var k: int = 0
	for hero: StringName in [&"squid", &"hobo", &"slime", &"cat"]:
		yard.call("_select", Balance.CHARACTER_ORDER.find(hero))
		await get_tree().create_timer(0.3).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/yard_text_%d.png" % k))
		k += 1
	yard.set("_dossier", true)
	yard.call("_apply_dossier")
	await get_tree().create_timer(0.2).timeout
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/yard_text_%d.png" % k))
	get_tree().quit()
