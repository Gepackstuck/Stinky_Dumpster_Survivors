class_name UltimateComponent
extends Node
## Ульта героя (Balance.HERO_ULT): копится от убийств, Q / геймпад Y. Виды: nuke (бах вокруг), freeze (все замирают),
## barrage (кольцо снарядов), heal (полхп + неуязвимость), rage (скорость атаки x2). Шлёт EventBus.ult_state для HUD.

const PROJECTILE_SCENE: PackedScene = preload("res://scenes/weapons/projectile.tscn")

@export var body: CharacterBody2D
@export var hurtbox: HurtboxComponent

var _charge: float = 0.0
var _name: String = ""
var _kind: StringName = &"nuke"
var _rage_left: float = 0.0
var _sent: float = -1.0


func _ready() -> void:
	var data: Array = Balance.HERO_ULT.get(GameState.character, ["БАХ", &"nuke"])
	_name = data[0]
	_kind = data[1]
	EventBus.enemy_died.connect(func(id: StringName, _at: Vector2) -> void:
		if not Balance.ENEMIES.get(id, {}).get("neutral", false):
			_charge = minf(_charge + 1.0 / Balance.ULT_KILLS, 1.0))


func ready_to_fire() -> bool:
	return _charge >= 1.0


func _physics_process(delta: float) -> void:
	if _rage_left > 0.0:
		_rage_left -= delta
		if _rage_left <= 0.0:
			GameState.temp_attack_bonus = maxf(GameState.temp_attack_bonus - Balance.ULT_RAGE_BONUS, 0.0)
	if snappedf(_charge, 0.02) != _sent:
		_sent = snappedf(_charge, 0.02)
		EventBus.ult_state.emit(_charge)
	if Input.is_action_just_pressed(&"ult") and ready_to_fire() and not get_tree().paused:
		fire()


func fire() -> void:
	_charge = 0.0
	var at: Vector2 = body.global_position
	var power: float = 1.0 + 0.3 * GameState.wave
	match _kind:
		&"nuke":
			for e: EnemyBase in _enemies_within(at, Balance.ULT_NUKE_RADIUS):
				e.hit_by_weapon(GameState.roll_damage(Balance.ULT_NUKE_DAMAGE * power), at.direction_to(e.global_position) * 320.0, &"ult")
			HitFx.explosion(get_tree(), at, Balance.ULT_NUKE_RADIUS, Color(0.6, 1.0, 0.2))
			EventBus.shake_requested.emit(6.0)
			AudioManager.play_sfx(&"explosion", 0.0)
		&"freeze":
			for e: EnemyBase in _enemies_within(at, 260.0):
				e.slow(0.03, Balance.ULT_FREEZE_SEC)
				e.flash(Color(0.4, 0.7, 1.0))
			HitFx.burst(get_tree(), at, Color(0.4, 0.7, 1.0), 30, 200.0, 3.0, 0.8, true)
		&"barrage":
			for i: int in Balance.ULT_BARRAGE_COUNT:
				var p: Projectile = PoolManager.acquire(PROJECTILE_SCENE) as Projectile
				get_tree().current_scene.add_child(p)
				p.launch(at, Vector2.RIGHT.rotated(TAU * i / Balance.ULT_BARRAGE_COUNT), GameState.roll_damage(Balance.ULT_BARRAGE_DAMAGE * power), 240.0, 1.2)
				p.source_weapon = &"ult"
				p.pierce = 2
		&"heal":
			if body.has_method(&"heal"):
				body.call(&"heal", GameState.max_hp * Balance.ULT_HEAL_FRACTION)
			hurtbox.grant_invulnerability(1.5)
			HitFx.burst(get_tree(), at, Color(0.22, 1.0, 0.08), 26, 120.0, 3.0, 0.8, true)
		&"rage":
			GameState.temp_attack_bonus += Balance.ULT_RAGE_BONUS
			_rage_left = Balance.ULT_RAGE_SEC
			HitFx.burst(get_tree(), at, Color(1.0, 0.2, 0.2), 26, 120.0, 3.0, 0.8, true)
	HitFx.popup(get_tree(), at + Vector2(0.0, -22.0), _name + "!", Color(0.97, 1.0, 0.0), 24.0, 1.4, true)
	EventBus.ult_used.emit(_kind)


func _enemies_within(at: Vector2, r: float) -> Array[EnemyBase]:
	var out: Array[EnemyBase] = []
	for node: Node in get_tree().get_nodes_in_group(&"enemies"):
		var e: EnemyBase = node as EnemyBase
		if e != null and e.is_alive() and e.global_position.distance_to(at) <= r:
			out.append(e)
	return out
