extends BossBrain
## Н24 Тёща (финал): орёт словами - буквы летят строкой, слово читается («ЛЕНТЯЙ», «НЕУДАЧНИК»);
## рывок со скалкой по прямой; пилёж - кольцо букв вокруг себя. В ярости орёт тремя словами веером.

const ENRAGE_HP_FRACTION: float = 0.5
const ROW_WALK: int = 0
const ROW_SHOUT: int = 1
const ROW_CHARGE: int = 2
const ROW_NAG: int = 3
const ROW_ENRAGE: int = 4
const WORDS: Array[String] = ["ЛЕНТЯЙ", "НЕУДАЧНИК", "ЛОХ", "БЕЗДАРЬ", "ПОЗОР", "ТУНЕЯДЕЦ"]
const LETTER_STEP: float = 13.0

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
	_cooldown = Balance.MIL_ATTACK_INTERVAL_SEC * (0.65 if _enraged() else 1.0)
	var tree: SceneTree = boss.get_tree()
	var aim: Vector2 = direction_to_target()
	var roll: float = randf()
	if roll < 0.45:
		var count: int = 3 if _enraged() else 1
		for k: int in count:
			Telegraph.line(tree, boss.global_position, aim.rotated(deg_to_rad((k - (count - 1) * 0.5) * 22.0)), Balance.TELEGRAPH_SHOT_LENGTH, 22.0, Balance.MIL_CAST_SEC, boss)
		start_cast(ROW_SHOUT, Balance.MIL_CAST_SEC, func() -> void:
			for k: int in count:
				_word(WORDS[randi() % WORDS.size()], aim.rotated(deg_to_rad((k - (count - 1) * 0.5) * 22.0)))
			EventBus.shake_requested.emit(2.0))
	elif roll < 0.75:
		Telegraph.line(tree, boss.global_position, aim, Balance.MIL_CHARGE_SPEED * Balance.MIL_CHARGE_SEC, 20.0, Balance.MIL_CAST_SEC, boss)
		start_cast(ROW_CHARGE, Balance.MIL_CAST_SEC, func() -> void:
			boss.forced_velocity = aim * Balance.MIL_CHARGE_SPEED
			boss.forced_sec = Balance.MIL_CHARGE_SEC, true, Balance.MIL_CHARGE_SEC)
	else:
		Telegraph.circle(tree, boss.global_position, 40.0, Balance.MIL_CAST_SEC)
		start_cast(ROW_NAG, Balance.MIL_CAST_SEC, _nag)


## Слово строкой: буквы стоят рядом слева направо и летят вместе - читается на лету.
func _word(word: String, dir: Vector2) -> void:
	var across: Vector2 = Vector2.RIGHT if absf(dir.x) < 0.7 else Vector2.DOWN   # строка поперёк полёта
	var start: Vector2 = boss.global_position - across * (word.length() - 1) * LETTER_STEP * 0.5 + dir * 16.0
	for i: int in word.length():
		_letter(word[i], start + across * i * LETTER_STEP, dir, Balance.MIL_WORD_SPEED)


## Пилёж: кольцо букв «ПОЗОРПОЗОР...» разлетается во все стороны.
func _nag() -> void:
	var text: String = "ПОЗОРПОЗОРПОЗОР" if not _enraged() else "ПОЗОРПОЗОРПОЗОРПОЗОР"
	for i: int in text.length():
		var dir: Vector2 = Vector2.from_angle(TAU * float(i) / text.length())
		_letter(text[i], boss.global_position + dir * 20.0, dir, Balance.MIL_RING_SPEED)


func _letter(ch: String, from: Vector2, dir: Vector2, speed: float) -> void:
	var tex: Texture2D = load("res://assets/sprites/proj_letter_%d.png" % ch.unicode_at(0)) as Texture2D
	var shot: EnemyProjectile = PoolManager.acquire(PROJECTILE_SCENE) as EnemyProjectile
	boss.get_tree().current_scene.add_child(shot)
	shot.source_id = boss.enemy_id
	shot.launch(from, dir, Balance.MIL_LETTER_DAMAGE * WaveRules.damage_mult(GameState.wave), speed, Balance.PROJECTILE_BOSS_LIFETIME_SEC, tex, 0.0, null)
