extends BossBrain
## Обжора: гонится за кучками XP на земле, жрёт их и пухнет. Убьёшь — выплюнет всё съеденное (Gobbler в Brotato).

var _eaten: int = 0


func physics_tick(_delta: float) -> void:
	var best: XpPickup = null
	var best_sq: float = Balance.GLUTTON_EAT_RADIUS * Balance.GLUTTON_EAT_RADIUS
	for node: Node in boss.get_tree().get_nodes_in_group(&"pickups"):
		var pickup: XpPickup = node as XpPickup
		if pickup == null:
			continue
		var d_sq: float = boss.global_position.distance_squared_to(pickup.global_position)
		if d_sq < best_sq:
			best_sq = d_sq
			best = pickup
	if best == null:
		return
	if best_sq < 64.0:
		_eaten += best.amount()
		PoolManager.release(best)
		boss.grow(Balance.GLUTTON_GROW_STEP)
		boss.heal_percent(0.1)
		return
	boss.forced_velocity = boss.global_position.direction_to(best.global_position) * Balance.ENEMIES[&"glutton"]["speed"] * 1.4
	boss.forced_sec = 0.1


func on_death() -> void:
	if _eaten > 0:
		EventBus.xp_drop_requested.emit(boss.global_position, _eaten)
		HitFx.popup(boss.get_tree(), boss.global_position + Vector2(0.0, -12.0), "ВЫБЛЕВАЛ %d" % _eaten, Color(0.968627, 1, 0, 1), 12.0, 0.9)
