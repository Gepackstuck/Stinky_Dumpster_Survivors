class_name EnemyNames
extends RefCounted
## Названия врагов для экрана смерти (и будущего бестиария).

const _TITLES: Dictionary[StringName, String] = {
	&"squid_gopnik": "КАЛЬМАР-ГОПНИК",
	&"microbe": "МИКРОБ",
	&"npc_bot": "НПС-БОТ",
	&"cockroach": "ТАРАКАН",
	&"wifi_ghost": "ВАЙФАЙ-ПРИЗРАК",
	&"chaser": "НАВОЗНАЯ МУХА",
	&"charger": "ТЕЛЕЖКА-УБИЙЦА",
	&"spitter": "ПЛЕВАКА",
	&"bruiser": "ГРУЗЧИК-БУГАЙ",
	&"looter": "КРЫСА-ВОРЮГА",
	&"healer": "ЛЕКАРЬ-ПОДЛИЗА",
	&"egg": "ЯЙЦО-ЛИЧИНКА",
	&"mamka": "МАМКА",
	&"glutton": "ЖРУН",
	&"wire": "КОЛЮЧАЯ ПРОВОЛОКА",
}


static func title(enemy_id: StringName) -> String:
	if Balance.BOSS_NAMES.has(enemy_id):
		return Balance.BOSS_NAMES[enemy_id]
	return _TITLES.get(enemy_id, "ХЗ КТО, НО ЖЁСТКО")
