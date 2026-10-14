class_name SlipperWeapon
extends WeaponBase
## Тапок: раз в пару секунд кидает тапок по дуге в ближайшего; при падении бьёт всех в радиусе.


func _fire(target: Node2D) -> void:
	var shot: ThrownSlipper = ThrownSlipper.new()
	get_tree().current_scene.add_child(shot)
	shot.launch(global_position, target.global_position, GameState.roll_damage(_damage),
			Balance.WEAPONS[weapon_id]["aoe_radius"], Balance.WEAPONS[weapon_id]["flight_sec"])
