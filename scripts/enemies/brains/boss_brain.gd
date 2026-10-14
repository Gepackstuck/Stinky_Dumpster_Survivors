class_name BossBrain
extends Node
## База «мозга» босса: атаки по таймерам. Живёт дочерним узлом врага; тикает из EnemyBase._physics_process.

const PROJECTILE_SCENE: PackedScene = preload("res://scenes/weapons/enemy_projectile.tscn")

var boss: EnemyBase = null
var target: Node2D = null


func setup(owner_enemy: EnemyBase, player: Node2D) -> void:
	boss = owner_enemy
	target = player


func physics_tick(_delta: float) -> void:
	pass


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
