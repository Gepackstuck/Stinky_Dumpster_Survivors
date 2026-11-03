extends Node
## Н18: новые герои в бою. Кот: 9 жизней, удар любой силы - минус одна. HEROES18 OK / FAIL, кадры tools/_preview/heroes18_*.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
var _fails: int = 0


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	for hero: StringName in [&"cat", &"gopnik_jock"]:
		GameState.character = hero
		var level: Node = MAIN.instantiate()
		get_tree().root.add_child(level)
		get_tree().current_scene = level
		await get_tree().create_timer(3.4).timeout
		get_tree().paused = false
		var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
		GameState.add_item(ItemLibrary.SHOES)
		if hero == &"cat":
			var hb: HurtboxComponent = player.get_node(^"Hurtbox") as HurtboxComponent
			var hp0: float = GameState.hp
			GameState.dodge_percent = 0.0   # у кота 4% уворота - «МИМО» ломал проверку случайно
			GameState.block_charges = 0
			GameState.repel_percent = 0.0
			for k: int in 3:
				hb.cancel_invulnerability()
				hb.receive_hit(50.0)
				await get_tree().process_frame
			if not is_equal_approx(GameState.hp, hp0 - 3.0) or not is_equal_approx(GameState.max_hp if GameState.max_hp > 0 else 9.0, GameState.max_hp):
				print("HEROES18 FAIL: кот hp ", hp0, " -> ", GameState.hp)
				_fails += 1
			if hp0 != 9.0:
				print("HEROES18 FAIL: у кота не 9 жизней: ", hp0)
				_fails += 1
		await get_tree().create_timer(2.0).timeout
		if DisplayServer.get_name() != "headless":
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/heroes18_%s.png" % hero))
		level.queue_free()
		await get_tree().process_frame
	print("HEROES18 OK" if _fails == 0 else "HEROES18 FAIL %d" % _fails)
	get_tree().quit()
