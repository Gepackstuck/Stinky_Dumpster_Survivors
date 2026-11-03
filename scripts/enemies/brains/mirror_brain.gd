extends BossBrain
## Трюмо-мутант: то мутное (бей), то блестит - урон не проходит, а в ответ летят осколки.
## Перед блеском мигает голубым, пока блестит - вокруг лучи.

const GLOW: Texture2D = preload("res://assets/sprites/fx_mirror_glow.png")
const SHARD: Texture2D = preload("res://assets/sprites/proj_glass.png")

var _timer: float = 0.0
var _phase: int = 0   # 0 мутное, 1 мигает, 2 блестит
var _glow: Sprite2D = null
var _shard_left: float = 0.0
var _anim_t: float = 0.0


func setup(owner_enemy: EnemyBase, player: Node2D) -> void:
	super.setup(owner_enemy, player)
	_phase = 0
	_timer = randf_range(1.0, Balance.MIRROR_OFF_SEC)
	if _glow == null:
		_glow = Sprite2D.new()
		_glow.texture = GLOW
		_glow.hframes = 4
		boss.add_child(_glow)
	_glow.visible = false


func physics_tick(delta: float) -> void:
	_timer -= delta
	_shard_left -= delta
	match _phase:
		0:
			boss.speed_mult = 1.0
			if _timer <= 0.0:
				_phase = 1
				_timer = Balance.MIRROR_WARN_SEC
		1:
			boss.flash(Color(0.0, 0.94, 1.0))
			if _timer <= 0.0:
				_phase = 2
				_timer = Balance.MIRROR_ON_SEC
				_glow.visible = true
				boss.modulate = Color(1.3, 1.6, 1.8)
		2:
			boss.speed_mult = 0.4
			_anim_t += delta
			_glow.frame = int(_anim_t * 10.0) % 4
			if _timer <= 0.0:
				_phase = 0
				_timer = Balance.MIRROR_OFF_SEC
				_glow.visible = false
				boss.modulate = Color.WHITE


func filter_damage(damage: float) -> float:
	if _phase != 2:
		return damage
	var tree: SceneTree = boss.get_tree()
	HitFx.sparks(tree, boss.global_position, Color(0.7, 0.95, 1.0))
	if _shard_left <= 0.0:
		_shard_left = Balance.MIRROR_SHARD_GAP_SEC
		HitFx.chatter(tree, boss.global_position + Vector2(0.0, -16.0), TranslationServer.translate("ОТРАЖАЮ!"), Color(0.0, 0.94, 1.0))
		# удар пришёл из физического колбэка - снаряд рождаем отложенно, иначе Godot ругается и тормозит
		shoot.call_deferred(SHARD, direction_to_target(), Balance.MIRROR_SHARD_DAMAGE * WaveRules.damage_mult(GameState.wave),
				Balance.MIRROR_SHARD_SPEED, 2.5, 10.0)
	return 0.0


func on_death() -> void:
	boss.modulate = Color.WHITE
	if _glow != null:
		_glow.visible = false


func _exit_tree() -> void:
	if is_instance_valid(_glow):
		_glow.queue_free()
	if is_instance_valid(boss):
		boss.modulate = Color.WHITE
