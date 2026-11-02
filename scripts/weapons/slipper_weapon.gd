class_name SlipperWeapon
extends WeaponBase
## Тапок (и банка с гвоздями, миномёт): раз в пару секунд кидает снаряд по дуге в ближайшего с упреждением;
## при падении бьёт всех в радиусе.


func _fire(target: Node2D) -> void:
	var stats: Dictionary = Balance.WEAPONS[weapon_id]
	var shot: ThrownSlipper = ThrownSlipper.new()
	shot.source = weapon_id
	if stats.has("projectile"):
		shot.texture = TEX.load_tex(stats["projectile"])
	get_tree().current_scene.add_child(shot)
	var aim: Vector2 = target.global_position
	var body: CharacterBody2D = target as CharacterBody2D
	if body != null:
		aim += body.velocity * float(stats["flight_sec"])   # упреждение: враг успеет сдвинуться за время полёта
	shot.launch(_muzzle(target), aim, GameState.roll_damage(_damage), WeaponLibrary.stat(weapon_id, tier, "aoe_radius"), stats["flight_sec"])
