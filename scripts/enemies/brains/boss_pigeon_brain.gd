extends BossBrain
## Голубиный папа (финал): пикирует по прямой (длинная дорожка), бомбит полосу помётом через героя (ряд кругов),
## веер перьев (конус). В ярости чаще и перьев больше.

const FEATHER: Texture2D = preload("res://assets/sprites/proj_milk.png")
const PUDDLE: PackedScene = preload("res://scenes/hazards/poop_puddle.tscn")
const ENRAGE_HP_FRACTION: float = 0.5
const ENRAGE_COOLDOWN_MULT: float = 0.65
const ROW_WALK: int = 0
const ROW_DIVE: int = 1
const ROW_BOMB: int = 2
const ROW_FEATHERS: int = 3
const ROW_ENRAGE: int = 4

var _cooldown: float = 2.0


func _enraged() -> bool:
	return boss.health_fraction() < ENRAGE_HP_FRACTION


func idle_row() -> int:
	return ROW_ENRAGE if _enraged() else ROW_WALK


func physics_tick(delta: float) -> void:
	if tick_cast(delta):
		return
	boss.speed_mult = 1.0
	_cooldown -= delta
	if _cooldown > 0.0:
		return
	_cooldown = Balance.PIGEON_PAPA_ATTACK_INTERVAL_SEC * (ENRAGE_COOLDOWN_MULT if _enraged() else 1.0)
	var roll: float = randf()
	var tree: SceneTree = boss.get_tree()
	var aim: Vector2 = direction_to_target()
	if roll < 0.35:
		Telegraph.line(tree, boss.global_position, aim, Balance.PIGEON_PAPA_DIVE_SPEED * Balance.PIGEON_PAPA_DIVE_SEC, 18.0, Balance.PIGEON_PAPA_CAST_SEC, boss)
		start_cast(ROW_DIVE, Balance.PIGEON_PAPA_CAST_SEC, func() -> void:
			boss.forced_velocity = aim * Balance.PIGEON_PAPA_DIVE_SPEED
			boss.forced_sec = Balance.PIGEON_PAPA_DIVE_SEC, true, Balance.PIGEON_PAPA_DIVE_SEC)
	elif roll < 0.7:
		var through: Vector2 = target.global_position
		var side: Vector2 = aim.orthogonal()
		var spots: Array[Vector2] = []
		for k: int in Balance.PIGEON_PAPA_BOMBS:
			spots.append(through + side * (k - (Balance.PIGEON_PAPA_BOMBS - 1) * 0.5) * 26.0)
		for s: Vector2 in spots:
			Telegraph.circle(tree, s, 13.0, Balance.PIGEON_PAPA_CAST_SEC + 0.4)
		start_cast(ROW_BOMB, Balance.PIGEON_PAPA_CAST_SEC + 0.4, _bomb.bind(spots))
	else:
		var count: int = Balance.PIGEON_PAPA_FEATHERS + (4 if _enraged() else 0)
		Telegraph.cone(tree, boss.global_position, aim, 34.0, Balance.TELEGRAPH_SHOT_LENGTH, Balance.PIGEON_PAPA_CAST_SEC, boss)
		start_cast(ROW_FEATHERS, Balance.PIGEON_PAPA_CAST_SEC, func() -> void:
			for i: int in count:
				var deg: float = (i - (count - 1) * 0.5) * (60.0 / float(count - 1))
				shoot(FEATHER, aim.rotated(deg_to_rad(deg)), Balance.PIGEON_PAPA_FEATHER_DAMAGE, Balance.PIGEON_PAPA_FEATHER_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, 0.0))


func _bomb(spots: Array[Vector2]) -> void:
	for s: Vector2 in spots:
		if target.global_position.distance_to(s) <= 13.0:
			var hb: HurtboxComponent = target.get_node_or_null(^"Hurtbox") as HurtboxComponent
			if hb != null and hb.receive_hit(Balance.PIGEON_PAPA_BOMB_DAMAGE * WaveRules.damage_mult(GameState.wave)):
				GameState.last_damage_source = boss.enemy_id
		var puddle: TimedHazard = PUDDLE.instantiate() as TimedHazard
		boss.get_tree().current_scene.add_child(puddle)
		puddle.source_id = boss.enemy_id
		puddle.setup(s, 12.0, Balance.DEATH_PUDDLE_DAMAGE * WaveRules.hazard_mult(GameState.wave), 3.0)
		puddle.get_node(^"Sprite2D").self_modulate = Color(0.95, 0.95, 0.9)
