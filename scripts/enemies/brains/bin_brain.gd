extends BossBrain
## Мусорный бак (нейтрал, как «дерево» в Brotato): стоит, не кусается. Разбей — получишь XP, иногда объедки (+ХП).


func on_death() -> void:
	EventBus.bin_destroyed.emit(boss.global_position)
	if randf() < Balance.BIN_HEAL_CHANCE and is_instance_valid(target) and target.has_method(&"heal"):
		target.call(&"heal", Balance.BIN_HEAL_HP)
		HitFx.popup(boss.get_tree(), boss.global_position + Vector2(0.0, -12.0), "+%d ХП: ПОЖРАЛ ОБЪЕДКИ" % int(Balance.BIN_HEAL_HP), Color(0.2235, 1.0, 0.0784), 14.0, 1.0)
