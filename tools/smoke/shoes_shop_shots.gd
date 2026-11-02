extends Node
## Ларёк с обувью героя и герой до/после покупки. tools/_preview/shoes_shop_*.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/shoes_shop_%s.png" % n))


func _run() -> void:
	GameState.character = &"granny"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.2).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	(player.get(&"_health") as HealthComponent).setup(99999.0)
	Input.action_press(&"dash")
	await get_tree().physics_frame
	Input.action_release(&"dash")
	await get_tree().create_timer(0.2).timeout
	await _shot("1_barefoot")
	var lu: Node = level.get_node(^"LevelUpScreen")
	GameState.coins = 60
	GameState.shop_offers.assign(ShopLibrary.fill_offers([], 2))
	lu.set("_queue", [])
	lu.call("_show_choices")
	await get_tree().create_timer(0.3).timeout
	await _shot("2_shop")
	GameState.add_item(ItemLibrary.SHOES)
	lu.call("_on_next_pressed")
	get_tree().paused = false
	await get_tree().create_timer(0.6).timeout
	await _shot("3_shod")
	get_tree().quit()
