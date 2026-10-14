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


## Серьёзность врага для цвета имени: 0 обычный, 1 опасный, 2 элита, 3 босс.
const _THREAT: Dictionary[StringName, int] = {
	&"charger": 1, &"bruiser": 1, &"mamka": 1, &"glutton": 1, &"spitter": 1, &"healer": 1,
	&"boss_mega_hamster": 2, &"boss_zakhar": 3, &"boss_minion": 3,
}
const THREAT_COLORS: Array[Color] = [
	Color(0.91, 0.91, 0.91), Color(1.0, 0.6, 0.1), Color(1.0, 0.1, 0.25), Color(1.0, 0.0627, 0.94)]


static func threat(enemy_id: StringName) -> int:
	return _THREAT.get(enemy_id, 0)


static func color(enemy_id: StringName) -> Color:
	return THREAT_COLORS[threat(enemy_id)]


static func title(enemy_id: StringName) -> String:
	if Balance.BOSS_NAMES.has(enemy_id):
		return Balance.BOSS_NAMES[enemy_id]
	return _TITLES.get(enemy_id, "ХЗ КТО, НО ЖЁСТКО")
