class_name BossBrain
extends Node
## База «мозга» босса: атаки по таймерам. Живёт дочерним узлом врага; тикает из EnemyBase._physics_process.

const PROJECTILE_SCENE: PackedScene = preload("res://scenes/weapons/enemy_projectile.tscn")

var boss: EnemyBase = null
var target: Node2D = null
var _cast_left: float = 0.0
var _cast_action: Callable = Callable()
var _cast_stop: bool = true
var _cast_hold_after: float = 0.0
var _hold_left: float = 0.0


func setup(owner_enemy: EnemyBase, player: Node2D) -> void:
	boss = owner_enemy
	target = player


func physics_tick(_delta: float) -> void:
	pass


## Ряд листа в обычном движении (наследники возвращают ряд ярости и т.п.).
func idle_row() -> int:
	return 0


## Атака с замахом: проигрываем ряд анимации sec секунд (босс стоит, если stop), потом action;
## после удара ряд ещё держится hold_after секунд (рывок, перекат).
func start_cast(row: int, sec: float, action: Callable, stop: bool = true, hold_after: float = 0.0) -> void:
	boss.set_anim_row(row)
	_cast_left = sec
	_cast_action = action
	_cast_stop = stop
	_cast_hold_after = hold_after
	_hold_left = 0.0


func is_casting() -> bool:
	return _cast_left > 0.0 or _hold_left > 0.0


## Тик замаха; true — пока босс занят анимацией атаки. Звать в начале physics_tick.
func tick_cast(delta: float) -> bool:
	if _cast_left > 0.0:
		_cast_left -= delta
		if _cast_stop:
			boss.speed_mult = 0.0
		if _cast_left <= 0.0:
			_cast_action.call()
			_hold_left = _cast_hold_after
			if _hold_left <= 0.0:
				boss.set_anim_row(idle_row())
		return true
	if _hold_left > 0.0:
		_hold_left -= delta
		if _hold_left <= 0.0:
			boss.set_anim_row(idle_row())
		return false
	boss.set_anim_row(idle_row(), false)
	return false


## Вызывается, когда враг убит (не при исчезновении в конце волны).
func on_death() -> void:
	pass


func direction_to_target() -> Vector2:
	return boss.global_position.direction_to(target.global_position)


func distance_to_target() -> float:
	return boss.global_position.distance_to(target.global_position)


func shoot(texture: Texture2D, direction: Vector2, damage: float, speed: float, lifetime_sec: float,
		spin_rad: float = 0.0, landing_hazard: PackedScene = null) -> void:
	var shot: EnemyProjectile = PoolManager.acquire(PROJECTILE_SCENE) as EnemyProjectile
	boss.get_tree().current_scene.add_child(shot)
	shot.source_id = boss.enemy_id
	shot.launch(boss.global_position, direction, damage, speed, lifetime_sec, texture, spin_rad, landing_hazard)
