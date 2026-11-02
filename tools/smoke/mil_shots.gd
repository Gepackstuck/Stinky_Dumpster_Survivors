extends Node
## Н24 Тёща: спавн рядом, кадры атак (слова-снаряды). tools/_preview/mil_*.png; печатает ряды и MIL DONE.
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
	await get_tree().create_timer(3.4).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	(player.get(&"_health") as HealthComponent).setup(99999.0)
	var boss: EnemyBase = EnemyBase.spawn_enemy(level, player, &"boss_mother_in_law", player.global_position + Vector2(0.0, -80.0), 1.0)
	var brain: Node = null
	for c: Node in boss.get_children():
		if c is BossBrain:
			brain = c
	var rows: Array[int] = []
	for k: int in 3:   # заставим проорать слово и снять кадр, пока буквы летят
		brain.set(&"_cooldown", 0.0)
		seed(k * 3 + 1)
		await get_tree().create_timer(1.2).timeout
		rows.append(boss.get_node("FrameAnimator").row)
		if DisplayServer.get_name() != "headless":
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/mil_%d.png" % k))
	print("MIL rows ", rows, " letters ", get_tree().get_nodes_in_group(&"enemy_projectiles").size())
	print("MIL DONE")
	get_tree().quit()
