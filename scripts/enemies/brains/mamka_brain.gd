extends BossBrain
## Мамка: медленная туша. Когда её убивают, из брюха вылезают мухи (Spawner в Brotato).


func on_death() -> void:
	var parent: Node = boss.get_parent()
	for i: int in Balance.MAMKA_SPAWN_COUNT:
		var offset: Vector2 = Vector2.from_angle(TAU * i / Balance.MAMKA_SPAWN_COUNT + randf()) * 12.0
		EnemyBase.spawn_enemy.call_deferred(parent, target, &"chaser", boss.global_position + offset, WaveRules.hp_mult(GameState.wave))
	HitFx.popup(boss.get_tree(), boss.global_position + Vector2(0.0, -12.0), "РОДИЛА, БЛЯДЬ", Color(1.0, 0.0627, 0.9412), 12.0, 0.9)
