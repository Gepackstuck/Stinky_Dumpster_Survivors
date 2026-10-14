extends BossBrain
## Захар из Морковска: кидает морковку (в ярости веером), пердит ядовитым облаком, пинает рывком.

const CARROT: Texture2D = preload("res://assets/sprites/proj_carrot.png")
const CLOUD_SCENE: PackedScene = preload("res://scenes/hazards/stink_cloud.tscn")
const ENRAGE_HP_FRACTION: float = 0.5
const ENRAGE_COOLDOWN_MULT: float = 0.65
const FIRST_ATTACK_DELAY_SEC: float = 1.5

enum State { WALK, KICK_WINDUP }

var _state: State = State.WALK
var _cooldown: float = FIRST_ATTACK_DELAY_SEC
var _windup_left: float = 0.0


func physics_tick(delta: float) -> void:
	match _state:
		State.WALK:
			boss.speed_mult = 1.0
			_cooldown -= delta
			if _cooldown <= 0.0:
				_choose_attack()
		State.KICK_WINDUP:
			boss.speed_mult = 0.0
			_windup_left -= delta
			if _windup_left <= 0.0:
				_kick()


func _choose_attack() -> void:
	var enraged: bool = boss.health_fraction() < ENRAGE_HP_FRACTION
	_cooldown = Balance.ZAKHAR_ATTACK_INTERVAL_SEC * (ENRAGE_COOLDOWN_MULT if enraged else 1.0)
	if distance_to_target() < Balance.ZAKHAR_KICK_RANGE and randf() < 0.6:
		_state = State.KICK_WINDUP
		_windup_left = Balance.ZAKHAR_KICK_WINDUP_SEC
		boss.flash(Color(0.9686, 1.0, 0.0))  # замах: мигает жёлтым
		return
	if randf() < 0.6:
		_throw_carrots(enraged)
	else:
		_fart()


func _throw_carrots(enraged: bool) -> void:
	var base: Vector2 = direction_to_target()
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


func _kick() -> void:
	_state = State.WALK
	boss.forced_velocity = direction_to_target() * Balance.ZAKHAR_KICK_SPEED
	boss.forced_sec = Balance.ZAKHAR_KICK_DURATION_SEC
	HitFx.burst(boss.get_tree(), boss.global_position, Color(0.9686, 1.0, 0.0), 8, 80.0)
