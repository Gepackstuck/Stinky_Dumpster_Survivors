class_name BuddyKeeper
extends Node
## Н16: выпускает пса на арену в начале забега (если он есть и включён) и иногда сажает бездомного пса в волне.


func _ready() -> void:
	EventBus.wave_started.connect(_on_wave_started)
	_spawn_buddy.call_deferred()


func _spawn_buddy() -> void:
	if not Profile.dog_owned or not Profile.dog_enabled or GameState.mode == &"duel":
		return
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player == null:
		return
	var dog: BuddyDog = BuddyDog.new()
	dog.player = player
	get_parent().add_child(dog)
	dog.global_position = player.global_position + Vector2(-18.0, 10.0)


func _on_wave_started(wave: int) -> void:
	if Profile.dog_owned or GameState.dog_found_run or wave < Balance.STRAY_FROM_WAVE or GameState.wave_kind != &"normal":
		return
	if randf() >= Balance.STRAY_CHANCE:
		return
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player == null:
		return
	var stray: StrayDog = StrayDog.new()
	get_parent().add_child(stray)
	var p: Vector2 = player.global_position + Vector2.from_angle(randf() * TAU) * randf_range(70.0, 140.0)
	stray.global_position = p.clamp(Vector2(30, 30), Vector2(Balance.ARENA_SIZE - 30.0, Balance.ARENA_SIZE - 30.0))
