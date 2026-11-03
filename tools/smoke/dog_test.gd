extends Node
## Н16: бездомный пёс -> подобрал -> на кладбище кличка и будка; пёс в забеге приносит кости.
## DOG OK / FAIL, кадры tools/_preview/dog_*.png

const MAIN: PackedScene = preload("res://scenes/levels/main.tscn")
var _fails: int = 0


func _ready() -> void:
	Profile.sandbox = true
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _check(ok: bool, what: String) -> void:
	if not ok:
		_fails += 1
		print("DOG FAIL: ", what)


func _shot(n: String) -> void:
	if DisplayServer.get_name() == "headless":
		return
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/dog_%s.png" % n))


func _run() -> void:
	Profile.dog_owned = false
	GameState.character = &"janitor"
	var level: Node = MAIN.instantiate()
	get_tree().root.add_child(level)
	get_tree().current_scene = level
	await get_tree().create_timer(3.4).timeout
	get_tree().paused = false
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	(player.get(&"_health") as HealthComponent).setup(99999.0)
	var stray: StrayDog = StrayDog.new()
	level.add_child(stray)
	stray.global_position = player.global_position + Vector2(10.0, 0.0)
	await get_tree().create_timer(1.0).timeout
	await _shot("1_stray")
	await get_tree().create_timer(Balance.STRAY_ADOPT_SEC).timeout
	_check(GameState.dog_found_run, "пёс подобран")
	var dogs: Array = level.find_children("*", "BuddyDog", true, false)
	_check(not dogs.is_empty(), "пёс бегает за героем")
	var bones0: int = Profile.bones
	(dogs.front() as BuddyDog).set(&"_bone_left", 0.05)
	await get_tree().create_timer(0.3).timeout
	_check(Profile.bones > bones0, "пёс принёс кость")
	await _shot("2_follow")
	EventBus.player_died.emit()   # конец забега - пёс становится твоим
	await get_tree().create_timer(0.3).timeout
	_check(Profile.dog_owned and Profile.dog_pending_name, "после забега пёс твой, ждёт кличку")
	level.queue_free()
	get_tree().paused = false
	var yard: Node = load("res://scenes/ui/graveyard.tscn").instantiate()
	get_tree().root.add_child(yard)
	await get_tree().create_timer(0.8).timeout
	await _shot("3_name")
	var kennel: KennelPanel = yard.get("_kennel")
	_check(kennel != null, "кладбище спросило кличку")
	kennel.call("_save_name")
	await get_tree().process_frame
	Profile.bones = 50
	Profile.dog_level = 1   # не зависеть от живого профиля игрока
	Profile.dog_wardrobe = ["cloak", "bow"]
	Profile.dog_wear = "cloak"
	yard.call("_toggle_kennel")
	await get_tree().create_timer(0.4).timeout
	await _shot("4_kennel")
	_check(Profile.feed_dog() and Profile.dog_level == 2, "покормил - уровень вырос")
	print("DOG OK" if _fails == 0 else "DOG FAIL %d" % _fails)
	get_tree().quit()
