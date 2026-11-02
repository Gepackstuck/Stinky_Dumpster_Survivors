extends BossBrain
## Н25 Управляющая компания (финал): будка-окошко на курьих ножках. Сама почти не дерётся:
## штампует квитанции-мины вокруг героя (круги-телеграфы, потом бах), вызывает аварийку (гопники),
## швыряет счета за отопление веером. Иногда «ОБЕД»: шторка закрыта - урон не проходит.

const BILL: Texture2D = preload("res://assets/sprites/proj_bill.png")
const ENRAGE_HP_FRACTION: float = 0.5
const ROW_WALK: int = 0
const ROW_STAMP: int = 1
const ROW_PHONE: int = 2
const ROW_BILLS: int = 3
const ROW_LUNCH: int = 4

var _cooldown: float = 2.0
var _lunch_left: float = 0.0
var _next_lunch: float = 8.0


func _enraged() -> bool:
	return boss.health_fraction() < ENRAGE_HP_FRACTION


func idle_row() -> int:
	return ROW_LUNCH if _lunch_left > 0.0 else ROW_WALK


func filter_damage(damage: float) -> float:
	if _lunch_left <= 0.0:
		return damage
	HitFx.sparks(boss.get_tree(), boss.global_position, Color(0.8, 0.8, 0.85))
	return 0.0   # ОБЕД: окошко закрыто


func physics_tick(delta: float) -> void:
	if _lunch_left > 0.0:
		_lunch_left -= delta
		boss.speed_mult = 0.0
		if _lunch_left <= 0.0:
			boss.set_anim_row(ROW_WALK)
		return
	if tick_cast(delta):
		return
	boss.speed_mult = 1.0
	_next_lunch -= delta
	if _next_lunch <= 0.0:
		_next_lunch = Balance.UK_LUNCH_EVERY_SEC
		_lunch_left = Balance.UK_LUNCH_SEC
		boss.set_anim_row(ROW_LUNCH)
		HitFx.popup(boss.get_tree(), boss.global_position + Vector2(0.0, -46.0), TranslationServer.translate("ОБЕД! ПРИХОДИТЕ ЗАВТРА"), Color(1.0, 1.0, 1.0), 16.0, 1.5, true)
		return
	_cooldown -= delta
	if _cooldown > 0.0:
		return
	_cooldown = Balance.UK_ATTACK_INTERVAL_SEC * (0.65 if _enraged() else 1.0)
	var tree: SceneTree = boss.get_tree()
	var roll: float = randf()
	if roll < 0.45:
		var spots: Array[Vector2] = []
		var n: int = Balance.UK_MINES + (2 if _enraged() else 0)
		for k: int in n:
			spots.append(target.global_position + Vector2.from_angle(TAU * k / n + randf() * 0.5) * randf_range(10.0, 46.0))
		for s: Vector2 in spots:
			Telegraph.circle(tree, s, Balance.UK_MINE_RADIUS, Balance.UK_MINE_DELAY)
		start_cast(ROW_STAMP, 0.4, func() -> void:
			HitFx.popup(tree, boss.global_position + Vector2(0.0, -46.0), TranslationServer.translate("ОПЛАТИТЕ КВИТАНЦИЮ!"), Color(1.0, 0.2, 0.2), 14.0, 1.0)
			tree.create_timer(Balance.UK_MINE_DELAY - 0.4, false).timeout.connect(_explode.bind(spots)))
	elif roll < 0.7:
		start_cast(ROW_PHONE, 0.8, func() -> void:
			HitFx.popup(tree, boss.global_position + Vector2(0.0, -46.0), TranslationServer.translate("ВЫЗВАЛА АВАРИЙКУ!"), Color(1.0, 0.6, 0.1), 14.0, 1.0)
			for k: int in Balance.UK_CALL_COUNT:
				EnemyBase.spawn_enemy(boss.get_parent(), target, &"squid_gopnik", boss.global_position + Vector2.from_angle(TAU * k / Balance.UK_CALL_COUNT) * 30.0, WaveRules.hp_mult(GameState.wave)))
	else:
		var aim: Vector2 = direction_to_target()
		var count: int = Balance.UK_BILLS + (4 if _enraged() else 0)
		Telegraph.cone(tree, boss.global_position, aim, 30.0, Balance.TELEGRAPH_SHOT_LENGTH, 0.55, boss)
		start_cast(ROW_BILLS, 0.55, func() -> void:
			for i: int in count:
				var deg: float = (i - (count - 1) * 0.5) * (56.0 / float(count - 1))
				shoot(BILL, aim.rotated(deg_to_rad(deg)), Balance.UK_BILL_DAMAGE * WaveRules.damage_mult(GameState.wave), Balance.UK_BILL_SPEED, Balance.PROJECTILE_BOSS_LIFETIME_SEC, 6.0))


func _explode(spots: Array[Vector2]) -> void:
	if not is_instance_valid(boss) or not boss.is_alive():
		return
	var tree: SceneTree = boss.get_tree()
	for s: Vector2 in spots:
		HitFx.burst(tree, s, Color(0.95, 0.92, 0.8), 10, 50.0, 2.0, 0.4)   # клочья квитанций
		if is_instance_valid(target) and target.global_position.distance_to(s) <= Balance.UK_MINE_RADIUS:
			var hb: HurtboxComponent = target.get_node_or_null(^"Hurtbox") as HurtboxComponent
			if hb != null and hb.receive_hit(Balance.UK_MINE_DAMAGE * WaveRules.damage_mult(GameState.wave)):
				GameState.last_damage_source = boss.enemy_id
	AudioManager.play_sfx(&"explosion")
