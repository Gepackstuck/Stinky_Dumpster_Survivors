extends BossBrain
## Гопник с крышкой: держит крышку от бака к игроку, но поворачивается медленно.
## Удар спереди проходит на SHIELD_BLOCK, сбоку и со спины - полностью.

const LID: Texture2D = preload("res://assets/sprites/fx_shield_lid.png")

var _facing: Vector2 = Vector2.RIGHT
var _lid: Sprite2D = null
var _ding_left: float = 0.0


func setup(owner_enemy: EnemyBase, player: Node2D) -> void:
	super.setup(owner_enemy, player)
	_facing = Vector2.ZERO   # позиция врага ставится после setup - направление возьмём при первом тике
	if _lid == null:
		_lid = Sprite2D.new()
		_lid.texture = LID
		_lid.z_index = 1
		boss.add_child(_lid)
	_lid.visible = false


func _ensure_facing() -> void:
	if _facing == Vector2.ZERO:
		_facing = direction_to_target()
		_lid.visible = true


func physics_tick(delta: float) -> void:
	_ensure_facing()
	_ding_left -= delta
	var want: float = _facing.angle_to(direction_to_target())
	var step: float = deg_to_rad(Balance.SHIELD_TURN_DEG) * delta
	_facing = _facing.rotated(clampf(want, -step, step))
	_place_lid()


func _place_lid() -> void:
	_lid.position = _facing * 9.0 + Vector2(0.0, 2.0)
	_lid.rotation = _facing.angle()


func filter_damage(damage: float) -> float:
	_ensure_facing()
	var to_player: Vector2 = direction_to_target()
	if absf(rad_to_deg(_facing.angle_to(to_player))) > Balance.SHIELD_ARC_DEG:
		return damage
	var tree: SceneTree = boss.get_tree()
	HitFx.sparks(tree, boss.global_position + _facing * 10.0, Color(0.85, 0.85, 0.9))
	if _ding_left <= 0.0:
		_ding_left = 0.6
		HitFx.popup(tree, boss.global_position + Vector2(0.0, -14.0), TranslationServer.translate("ДЗЫНЬ"), Color(0.75, 0.75, 0.8))
	return damage * Balance.SHIELD_BLOCK


func on_death() -> void:
	if _lid != null:
		_lid.visible = false


func _exit_tree() -> void:
	if is_instance_valid(_lid):
		_lid.queue_free()
