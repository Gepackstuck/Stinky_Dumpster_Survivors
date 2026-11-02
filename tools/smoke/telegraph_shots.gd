extends Node
## Кадры телеграфов: тележка, плевун и боссы рядом с героем; снимает кадр, когда на экране есть телеграф.
## Кадры: tools/_preview/tele_*.png. Нужен оконный режим (open -g ... --windowed --screen 1).

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
var _shots: int = 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	for set_ids: Array in [[&"boss_rat_queen"], [&"boss_blue_whale"]]:
		GameState.character = &"janitor"
		var level: Node = MAIN.instantiate()
		get_tree().root.add_child(level)
		get_tree().current_scene = level   # как в настоящей игре
		await get_tree().create_timer(3.5).timeout   # баннер волны уходит
		get_tree().paused = false
		var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
		GameState.weapons.clear()
		EventBus.weapons_changed.emit()   # без оружия: враги живут и атакуют
		for k: int in set_ids.size():
			EnemyBase.spawn_enemy(level, player, set_ids[k], player.global_position + Vector2.from_angle(TAU * k / set_ids.size() + 0.4) * (60.0 if set_ids.size() > 1 else 90.0), 1.0)
		var taken: int = 0
		for i: int in 160:
			GameState.hp = GameState.max_hp
			await get_tree().create_timer(0.05).timeout
			var teles: int = 0
			teles = get_tree().current_scene.find_children("*", "Node2D", true, false).filter(func(n: Node) -> bool: return n is Telegraph).size()
			if (teles > 0 or i % 25 == 24) and taken < 4 and i % 3 == 0:
				taken += 1
				_shots += 1
				await RenderingServer.frame_post_draw
				var img: Image = get_viewport().get_texture().get_image()
				var c: Vector2 = img.get_size() * 0.5
				var crop: Image = img.get_region(Rect2i(int(c.x) - 120, int(c.y) - 70, 240, 140))
				crop.resize(480, 280, Image.INTERPOLATE_NEAREST)
				crop.save_png(ProjectSettings.globalize_path("res://tools/_preview/tele_%d.png" % _shots))
		level.queue_free()
		await get_tree().process_frame
	print("TELE DONE ", _shots)
	get_tree().quit()
