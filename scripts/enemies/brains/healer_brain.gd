extends BossBrain
## Знахарка: держится на расстоянии от игрока и лечит раненых врагов рядом (как Healer в Brotato).

var _timer: float = 1.0


func physics_tick(delta: float) -> void:
	var distance: float = distance_to_target()
	if distance > 120.0:
		boss.speed_mult = 1.0
	elif distance < 80.0:
		boss.speed_mult = -0.6
	else:
		boss.speed_mult = 0.0
	_timer -= delta
	if _timer <= 0.0:
		_timer = Balance.HEALER_INTERVAL_SEC
		_heal_allies()


func _heal_allies() -> void:
	var radius_sq: float = Balance.HEALER_RADIUS * Balance.HEALER_RADIUS
	var healed: bool = false
	for node: Node in boss.get_tree().get_nodes_in_group(&"enemies"):
		var ally: EnemyBase = node as EnemyBase
		if ally == null or ally == boss or ally.health_fraction() >= 1.0:
			continue
		if boss.global_position.distance_squared_to(ally.global_position) <= radius_sq:
			ally.heal_percent(Balance.HEALER_FRACTION)
			healed = true
	if healed:
		HitFx.burst(boss.get_tree(), boss.global_position, Color(0.2235, 1.0, 0.0784), 10, Balance.HEALER_RADIUS, 2.0, 0.5, true)
		HitFx.popup(boss.get_tree(), boss.global_position + Vector2(0.0, -10.0), "+ЛЕЧУ, СУКА", Color(0.2235, 1.0, 0.0784), 12.0, 0.8)
