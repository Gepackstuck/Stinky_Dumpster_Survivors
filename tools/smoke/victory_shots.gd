extends Node
## Кадры ролика победы: 1.5 с, 3.5 с, 6 с. tools/_preview/victory_*.png

func _ready() -> void:
	Profile.sandbox = true
	GameState.character = &"granny"
	_run.call_deferred()


func _run() -> void:
	var scene: Node = load("res://scenes/ui/victory.tscn").instantiate()
	get_tree().root.add_child(scene)
	var t: float = 0.0
	for at: float in [1.6, 3.6, 6.0]:
		await get_tree().create_timer(at - t).timeout
		t = at
		if DisplayServer.get_name() != "headless":
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/victory_%d.png" % int(at)))
	print("VICTORY SHOTS DONE")
	get_tree().quit()
