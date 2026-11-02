extends Node
## Кадры: заначка-контейнер (прогресс и открытие) и комментатор-бомж. tools/_preview/stash_*.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/stash_%s.png" % n))


func _run() -> void:
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.2).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	var stash: StashDumpster = StashDumpster.new()
	level.add_child(stash)
	stash.global_position = player.global_position + Vector2(8.0, 0.0)
	EventBus.boss_spawned.emit(&"boss_rat_queen")
	await get_tree().create_timer(1.0).timeout
	await _shot("1_progress")
	await get_tree().create_timer(1.3).timeout
	await _shot("2_open")
	get_tree().quit()
