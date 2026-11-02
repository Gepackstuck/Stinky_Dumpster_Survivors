extends BossBrain
## Захар из Морковска: кидает морковку (в ярости веером), пердит ядовитым облаком, пинает рывком.
## Каждая атака — свой ряд листа: замах проигрывается целиком, удар в конце цикла.

const CARROT: Texture2D = preload("res://assets/sprites/proj_carrot.png")
const CLOUD_SCENE: PackedScene = preload("res://scenes/hazards/stink_cloud.tscn")
const ENRAGE_HP_FRACTION: float = 0.5
const ENRAGE_COOLDOWN_MULT: float = 0.65
const FIRST_ATTACK_DELAY_SEC: float = 1.5
# ряды листа enemy_boss_zakhar.png
const ROW_WALK: int = 0
const ROW_THROW: int = 1
const ROW_FART: int = 2
const ROW_KICK: int = 3
const ROW_ENRAGE: int = 4
const ROW_FAN: int = 5

var _cooldown: float = FIRST_ATTACK_DELAY_SEC


func _enraged() -> bool:
	return boss.health_fraction() < ENRAGE_HP_FRACTION


func idle_row() -> int:
	return ROW_ENRAGE if _enraged() else ROW_WALK


func physics_tick(delta: float) -> void:
	if tick_cast(delta):
		return
	boss.speed_mult = 1.0
	_cooldown -= delta
	if _cooldown <= 0.0:
		_choose_attack()


func _choose_attack() -> void:
	var enraged: bool = _enraged()
	_cooldown = Balance.ZAKHAR_ATTACK_INTERVAL_SEC * (ENRAGE_COOLDOWN_MULT if enraged else 1.0)
	if distance_to_target() < Balance.ZAKHAR_KICK_RANGE and randf() < 0.6:
		boss.flash(Color(0.9686, 1.0, 0.0))  # замах: мигает жёлтым
		var kick_aim: Vector2 = direction_to_target()
		Telegraph.line(boss.get_tree(), boss.global_position, kick_aim, Balance.ZAKHAR_KICK_SPEED * Balance.ZAKHAR_KICK_DURATION_SEC + 10.0, float(Balance.ENEMIES[boss.enemy_id]["radius"]) * 0.8, Balance.ZAKHAR_KICK_WINDUP_SEC, boss)
		start_cast(ROW_KICK, Balance.ZAKHAR_KICK_WINDUP_SEC, _kick.bind(kick_aim), true, Balance.ZAKHAR_KICK_DURATION_SEC)
		return
	var aim: Vector2 = direction_to_target()
	if randf() < 0.6:
		if enraged:
			Telegraph.cone(boss.get_tree(), boss.global_position, aim, Balance.ZAKHAR_CARROT_FAN_DEG + 4.0, Balance.TELEGRAPH_SHOT_LENGTH, Balance.ZAKHAR_CAST_SEC, boss)
		else:
			Telegraph.line(boss.get_tree(), boss.global_position, aim, Balance.TELEGRAPH_SHOT_LENGTH, 4.0, Balance.ZAKHAR_CAST_SEC, boss)
		start_cast(ROW_FAN if enraged else ROW_THROW, Balance.ZAKHAR_CAST_SEC, _throw_carrots.bind(enraged, aim))
	else:
		Telegraph.circle(boss.get_tree(), boss.global_position, Balance.ZAKHAR_FART_RADIUS, Balance.ZAKHAR_CAST_SEC, boss)
		start_cast(ROW_FART, Balance.ZAKHAR_CAST_SEC, _fart)


func _throw_carrots(enraged: bool, base: Vector2) -> void:
	var angles: Array[float] = [0.0]
	if enraged:
		angles = [-Balance.ZAKHAR_CARROT_FAN_DEG, 0.0, Balance.ZAKHAR_CARROT_FAN_DEG]
	for deg: float in angles:
		shoot(CARROT, base.rotated(deg_to_rad(deg)), Balance.ZAKHAR_CARROT_DAMAGE,
				Balance.ZAKHAR_CARROT_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, 10.0)


func _fart() -> void:
	HitFx.burst(boss.get_tree(), boss.global_position, Color(0.2235, 1.0, 0.0784), 16, 70.0, 3.0, 0.6)
	var cloud: TimedHazard = CLOUD_SCENE.instantiate() as TimedHazard
	boss.get_tree().current_scene.add_child(cloud)
	cloud.source_id = boss.enemy_id
	cloud.setup(boss.global_position, Balance.ZAKHAR_FART_RADIUS, Balance.ZAKHAR_FART_DAMAGE, Balance.ZAKHAR_FART_LIFETIME_SEC)


func _kick(aim: Vector2) -> void:
	boss.forced_velocity = aim * Balance.ZAKHAR_KICK_SPEED
	boss.forced_sec = Balance.ZAKHAR_KICK_DURATION_SEC
	HitFx.burst(boss.get_tree(), boss.global_position, Color(0.9686, 1.0, 0.0), 8, 80.0)
