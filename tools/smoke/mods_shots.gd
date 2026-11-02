extends Node
## Модификаторы волн по очереди: включаем каждый на 5 с, снимаем кадры tools/_preview/mod_<id>.png (в окне),
## без окна - только проверка на ошибки. В конце MODS DONE.

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.0).timeout
	get_tree().paused = false
	var hurtbox: HurtboxComponent = get_tree().get_first_node_in_group(&"player").get_node(^"Hurtbox")
	var only: String = OS.get_environment("MOD_ONLY")
	for mod: StringName in Balance.WAVE_MODS:
		if only != "" and String(mod) != only:
			continue
		GameState.wave_mod = mod
		GameState.wave_time_left = 60.0
		EventBus.wave_started.emit(GameState.wave)
		var shot_taken: bool = false
		for i: int in 50:
			hurtbox.grant_invulnerability(1.0)
			GameState.wave_time_left = 60.0
			await get_tree().create_timer(0.1).timeout
			if not shot_taken and DisplayServer.get_name() != "headless" and level.find_children("*", "Node2D", true, false).any(func(n: Node) -> bool: return n is GarbageTruck):
				shot_taken = true
				await RenderingServer.frame_post_draw
				get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/mod_%s_live.png" % mod))
		if DisplayServer.get_name() != "headless":
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/mod_%s.png" % mod))
		print("MOD ", mod, " ok")
	GameState.wave_mod = &""
	print("MODS DONE")
	get_tree().quit()
