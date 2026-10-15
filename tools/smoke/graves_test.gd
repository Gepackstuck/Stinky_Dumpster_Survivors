extends Node
## ТЕСТ: кладбище, забитое могилами (повторы героев), и проход героя по дорожкам. Кадры: tools/_preview/graves_*.png


func _ready() -> void:
	_start.call_deferred()


func _start() -> void:
	var tree: SceneTree = get_tree()
	tree.root.remove_child(self)
	tree.root.add_child(self)
	tree.current_scene = null
	_run()


func _shot(label: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/graves_%s.png" % label))


func _run() -> void:
	var yard: Node = null
	for count: int in [10, 30, 45]:
		if yard != null:
			yard.queue_free()
		Graveyard.test_fill = count
		yard = load("res://scenes/ui/graveyard.tscn").instantiate()
		get_tree().root.add_child(yard)
		await get_tree().create_timer(1.0).timeout
		_shot("n%d" % count)
		await get_tree().create_timer(0.2).timeout
	yard.set("_selected", 20)
	yard.call("_refresh")
	yard.call("_choose")
	await get_tree().create_timer(0.7).timeout
	_shot("walk_a")
	await get_tree().create_timer(0.8).timeout
	_shot("walk_b")
	Graveyard.test_fill = 0
	get_tree().quit()
