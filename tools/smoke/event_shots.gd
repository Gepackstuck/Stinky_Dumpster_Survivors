extends Node
## Кадры событий между волнами: меняла и спорщик. tools/_preview/event_*.png

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
	GameState.wave = 5
	GameState.coins = 120
	for kind: StringName in [&"trader", &"bet"]:
		var ev: WaveEvent = WaveEvent.new()
		ev.process_mode = Node.PROCESS_MODE_ALWAYS
		level.get_node(^"LevelUpScreen").add_child(ev)
		ev.setup(kind)
		await get_tree().create_timer(0.3).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/event_%s.png" % kind))
		ev.choose(1)
		await get_tree().process_frame
	get_tree().quit()
