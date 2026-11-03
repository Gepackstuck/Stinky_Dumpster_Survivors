class_name BottleGrenades
extends Node2D
## Н7: бутылки-гранаты на поле. Наступил на ходу - пнул по ходу движения: катится, бахает об врага
## или в конце пути - урон по площади всем врагам. Стоял рядом при взрыве - автогол (бьёт и тебя).

const BOTTLE: Texture2D = preload("res://assets/sprites/bottle_grenade.png")

var _lying: Array[Sprite2D] = []
var _flying: Array[Dictionary] = []   # {sprite, dir, left}
var _spawn_left: float = 4.0
var _anim: float = 0.0


func _ready() -> void:
	EventBus.wave_ended.connect(func(_w: int) -> void: _clear())


func _physics_process(delta: float) -> void:
	var player: Node2D = get_tree().get_first_node_in_group(&"player") as Node2D
	if player == null or not GameState.run_active or GameState.wave_time_left <= 0.0:
		return
	_anim += delta
	_spawn_left -= delta
	if _spawn_left <= 0.0:
		_spawn_left = Balance.BOTTLE_EVERY_SEC
		if GameState.wave >= Balance.BOTTLE_FROM_WAVE and _lying.size() < Balance.BOTTLE_MAX:
			_spawn(player)
	for b: Sprite2D in _lying:
		b.frame = int(_anim * 6.0) % 2
	_try_kick(player)
	for f: Dictionary in _flying.duplicate():
		_fly(f, delta)


func _spawn(player: Node2D) -> void:
	var b: Sprite2D = Sprite2D.new()
	b.texture = BOTTLE
	b.hframes = 2
	b.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var p: Vector2 = player.global_position + Vector2.from_angle(randf() * TAU) * randf_range(50.0, 150.0)
	b.global_position = p.clamp(Vector2(20, 20), Vector2(Balance.ARENA_SIZE - 20.0, Balance.ARENA_SIZE - 20.0)).round()
	b.rotation = randf() * TAU
	b.z_index = -1   # лежит на полу - под врагами и героем
	add_child(b)
	_lying.append(b)


func _try_kick(player: Node2D) -> void:
	var vel: Vector2 = player.get(&"velocity") if player.get(&"velocity") != null else Vector2.ZERO
	if vel.length() < 10.0:
		return   # стоя не пнёшь - только на ходу
	for b: Sprite2D in _lying.duplicate():
		if b.global_position.distance_to(player.global_position) <= Balance.BOTTLE_KICK_RADIUS:
			_lying.erase(b)
			b.z_index = 0   # пнутая летит поверх пола
			_flying.append({"sprite": b, "dir": vel.normalized(), "left": Balance.BOTTLE_FLY_SEC})
			HitFx.popup(get_tree(), b.global_position + Vector2(0.0, -10.0), tr("ПНУЛ!"), Color(0.97, 1.0, 0.0), 10.0, 0.5)
			AudioManager.play_sfx(&"swing")
			Profile.stat_add(&"bottle_kicks", 1)
			if Profile.stat(&"bottle_kicks") >= 100:
				Achievements.unlock(&"bottle_kicks_100")


func _fly(f: Dictionary, delta: float) -> void:
	var b: Sprite2D = f["sprite"]
	b.global_position += f["dir"] * Balance.BOTTLE_KICK_SPEED * delta
	b.rotation += delta * 18.0
	f["left"] -= delta
	var hit: bool = f["left"] <= 0.0
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null and enemy.is_alive() and enemy.global_position.distance_to(b.global_position) < 10.0:
			hit = true
			break
	if hit:
		_flying.erase(f)
		_explode(b.global_position)
		b.queue_free()


func _explode(at: Vector2) -> void:
	var tree: SceneTree = get_tree()
	HitFx.burst(tree, at, Color(1.0, 0.55, 0.1), 22, 90.0, 3.0, 0.5)
	HitFx.burst(tree, at, Color(0.3, 0.8, 0.3), 10, 60.0, 2.0, 0.4)   # осколки зелёного стекла
	AudioManager.play_sfx(&"explosion")
	EventBus.shake_requested.emit(3.0)
	var damage: float = Balance.BOTTLE_DAMAGE * (1.0 + Balance.BOTTLE_DAMAGE_PER_WAVE * GameState.wave)
	for node: Node in tree.get_nodes_in_group(&"enemies"):
		var enemy: EnemyBase = node as EnemyBase
		if enemy != null and enemy.is_alive() and enemy.global_position.distance_to(at) <= Balance.BOTTLE_RADIUS:
			enemy.hit_by_weapon(damage, at.direction_to(enemy.global_position) * 160.0, &"bottle")
	var player: Node2D = tree.get_first_node_in_group(&"player") as Node2D
	if player != null and player.global_position.distance_to(at) <= Balance.BOTTLE_SELF_RADIUS:
		var hurtbox: HurtboxComponent = player.get_node_or_null(^"Hurtbox") as HurtboxComponent
		if hurtbox != null and hurtbox.receive_hit(Balance.BOTTLE_SELF_DAMAGE):
			GameState.last_damage_source = &"bottle"
			HitFx.popup(tree, player.global_position + Vector2(0.0, -24.0), tr("АВТОГОЛ!"), Color(1.0, 0.2, 0.2), 14.0, 1.0)
			Achievements.unlock(&"bottle_own_goal")


func _clear() -> void:
	for b: Sprite2D in _lying:
		b.queue_free()
	for f: Dictionary in _flying:
		(f["sprite"] as Sprite2D).queue_free()
	_lying.clear()
	_flying.clear()
	_spawn_left = 4.0
