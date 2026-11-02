extends Node
## Все балансные числа игры (источник: GDD.md, CONVENTIONS.md, TASKS.md).
## Autoload: Balance. Числа не хардкодить в сценах — брать отсюда.

# --- Арена (Шаг 1) ---
const ARENA_SIZE: float = 520.0        # квадрат ARENA_SIZE x ARENA_SIZE, старт в центре

# --- Игрок (Шаг 1; в GDD чисел нет — стартовые значения) ---
const PLAYER_MOVE_SPEED: float = 100.0
const PLAYER_MAX_HP: float = 18.0
const PLAYER_HURT_COOLDOWN_SEC: float = 0.7  # неуязвимость после попадания

# --- Спавн врагов (Шаг 1: простой хардкод-спавнер) ---

# --- Автоатака (Шаг 1) ---
const WEAPON_TARGET_RANGE: float = 180.0
const PROJECTILE_SPEED: float = 220.0
const PROJECTILE_LIFETIME_SEC: float = 1.2

# --- Подбор XP и перки (Шаг 2) ---
const PICKUP_RADIUS_BASE: float = 36.0       # радиус притягивания XP
const XP_PICKUP_START_SPEED: float = 60.0
const XP_PICKUP_ACCELERATION: float = 500.0
const XP_COLLECT_DISTANCE: float = 5.0
const XP_DROP_SCATTER: float = 4.0           # разброс места падения XP
const PERK_DOUBLE_SHOT_SPREAD_DEG: float = 10.0

# --- Волны (как в Brotato, см. docs/BROTATO_REFERENCE.md) ---
const WAVE_COUNT: int = 15
const WAVE_DURATION_FIRST_SEC: float = 20.0
const WAVE_DURATION_STEP_SEC: float = 4.0
const WAVE_DURATION_MAX_SEC: float = 70.0
const WAVE_DURATION_FINAL_SEC: float = 120.0      # последняя волна (боссы)
const WAVE_ENEMIES_BASE: int = 18   # врагов за 1-ю волну (баланс по Brotato: старт спокойный)
const WAVE_ENEMIES_PER_WAVE: int = 12   # + столько за каждую следующую (к 15-й волне ~136)
const MAX_ALIVE_ENEMIES: int = 160                    # потолок врагов на карте — как в Brotato
const WAVE_MIN_GROUPS: int = 3                       # минимум групп за волну
const WAVE_GROUP_SIZE_BASE: int = 3               # размер группы = BASE + (волна-1)/STEP (±1, +1)
const WAVE_GROUP_SIZE_WAVES_PER_STEP: int = 3
const WAVE_MAX_GAP_SEC: float = 4.0               # максимум секунд между группами врагов (минимум групп = длительность / это)
const WAVE_FIRST_GROUP_SEC: float = 0.5
const WAVE_SPAWN_END_FRACTION: float = 0.85       # последняя группа не позже 85% времени волны
const CAMP_WAIT_SEC: float = 2.5                  # стоишь дольше — начинается облава
const CAMP_RAID_PERIOD_SEC: float = 1.4          # как часто облава подкидывает группу рядом с тобой
const CAMP_RAID_DISTANCE: float = 95.0
const SPAWN_MARKER_SEC: float = 1.0               # красный крест за секунду до появления
const SPAWN_MIN_DISTANCE_FROM_PLAYER: float = 75.0
const SPAWN_ARENA_MARGIN: float = 40.0
const SPAWN_GROUP_SPREAD: float = 28.0
const SPECIAL_WAVE_WINDOWS: Array = [[7, 8], [10, 11], [13, 14]]  # в каждом окне — элита или орда (последнее всегда элита)
const ELITE_CHANCE: float = 1.0
const HORDE_GROUP_MULT: float = 2.0
const ELITE_REWARD_XP_DROPS: int = 6                 # за убийство элиты: куча говна + бесплатный предмет
const ELITE_REWARD_XP_VALUE: int = 14
const ELITE_SPAWN_SEC: float = 2.0
const FINAL_BOSS_SPAWN_SEC: float = 1.5
const WAVE_END_BONUS_XP_BASE: int = 6          # «копание в помойке» в конце волны (аналог Harvesting в Brotato)
const WAVE_END_BONUS_XP_PER_WAVE: int = 2
const WAVE_END_COLLECT_SEC: float = 1.5           # время на авто-сбор материалов после волны
const ENEMY_HP_MULT: float = 0.8                  # общий множитель HP врагов (под Brotato: враги умирают за 1-2 удара)
# Поздние волны растут быстрее (как в Brotato: к 10-й волне экран уже забит, к 15-й это настоящая орда).
const WAVE_LATE_START: int = 7
const WAVE_ENEMIES_LATE: float = 4.0        # + это * (волна - LATE_START)^2 врагов за волну
const WAVE_HP_QUAD: float = 0.5           # + это * (волна-1)^2 к множителю HP
const WAVE_DAMAGE_QUAD: float = 0.06       # + это * (волна-1)^2 к множителю урона
const BOSS_HP_MULT: float = 1.0                   # боссы последней волны крепче обычного роста
const ELITE_HP_MULT: float = 2.0
const WAVE_HP_GROWTH: float = 0.6   # рост HP врагов за волну
const PLAYER_MAX_HIT_FRACTION: float = 0.34   # один удар не снимает больше трети максимума HP (нет ваншотов)
const WAVE_DAMAGE_GROWTH: float = 0.35   # рост урона врагов за волну
const WAVE_SPEED_GROWTH: float = 0.05        # +3% скорости за волну
const WAVE_SPEED_MAX_MULT: float = 1.6
const GROUND_BODY_LAYER: int = 2                 # тела наземных врагов толкаются друг с другом и со стеной
const GROUND_BODY_MASK: int = 34
const FLYER_BODY_LAYER: int = 64                 # летающие: свой слой, сталкиваются только со стеной (бит 6)
const FLYER_BODY_MASK: int = 32
const ENEMY_DAMAGE_MULT: float = 1.0   # общий множитель урона врагов по игроку
const WAVE_ENEMY_UNLOCK: Dictionary = {     # с какой волны тип может выпасть (15 волн)
	&"squid_gopnik": 1, &"chaser": 3, &"microbe": 3, &"charger": 3, &"npc_bot": 3, &"spitter": 3,
	&"looter": 4, &"cockroach": 4, &"bruiser": 5, &"wifi_ghost": 6,
	&"healer": 5, &"glutton": 6, &"egg": 8, &"mamka": 9,
}
const WAVE_ENEMY_WEIGHTS: Dictionary = {    # вес в взвешенном рандоме
	&"squid_gopnik": 10, &"chaser": 8, &"microbe": 5, &"charger": 7, &"npc_bot": 4, &"spitter": 12,
	&"looter": 1, &"cockroach": 4, &"bruiser": 4, &"wifi_ghost": 3,
	&"healer": 3, &"glutton": 3, &"egg": 2, &"mamka": 2,
}
const FINAL_BOSS_POOL: Array[StringName] = [&"boss_zakhar", &"boss_minion"]  # боссы 20-й волны: один или оба
const ELITE_ID: StringName = &"boss_mega_hamster"                           # элита на волнах 11–12, 14–15, 17–18
const BOSS_NAMES: Dictionary = {
	&"boss_mega_hamster": "МЕГА-ХОМЯК",
	&"boss_zakhar": "ЗАХАР ИЗ МОРКОВСКА",
	&"boss_minion": "МИНЬОН-ПСИХ",
}

# --- Боссы: Захар из Морковска ---
const ZAKHAR_ATTACK_INTERVAL_SEC: float = 2.2   # пауза между атаками (в ярости ×0.65 — на <50% HP)
const ZAKHAR_CARROT_DAMAGE: float = 8.0
const ZAKHAR_CARROT_SPEED: float = 140.0
const ZAKHAR_CARROT_FAN_DEG: float = 18.0       # в ярости — веер из трёх
# --- Уровни опасности (как в Brotato): открываются победой на предыдущем. Множители к врагам, шанс модификаторов,
# both_bosses - в финале всегда оба босса, early_elite - элита ещё и на этой волне.
const DANGER_LEVELS: Array = [
	{"name": "ПОМОЙКА", "hp": 1.0, "dmg": 1.0, "speed": 1.0, "mod_add": 0.0, "both_bosses": false, "early_elite": 0,
			"text": "ДЛЯ НОВИЧКОВ И ЛОХОВ. ТО ЕСТЬ ДЛЯ ТЕБЯ"},
	{"name": "ВОНЮЧКА", "hp": 1.12, "dmg": 1.12, "speed": 1.0, "mod_add": 0.05, "both_bosses": false, "early_elite": 0,
			"text": "ВРАГИ ЗЛЕЕ НА 12%. ПАХНЕТ ХУЖЕ"},
	{"name": "ГНИЛЬ", "hp": 1.25, "dmg": 1.25, "speed": 1.04, "mod_add": 0.1, "both_bosses": false, "early_elite": 0,
			"text": "+25% ВРАГАМ, МОДИФИКАТОРЫ ЧАЩЕ"},
	{"name": "ТРУПНЯК", "hp": 1.4, "dmg": 1.4, "speed": 1.07, "mod_add": 0.15, "both_bosses": true, "early_elite": 0,
			"text": "+40% ВРАГАМ. В ФИНАЛЕ ОБА БОССА. ВСЕГДА"},
	{"name": "АД КАНАЛИЗАЦИИ", "hp": 1.6, "dmg": 1.6, "speed": 1.1, "mod_add": 0.2, "both_bosses": true, "early_elite": 5,
			"text": "+60% ВРАГАМ, ЭЛИТА УЖЕ НА 5-Й ВОЛНЕ"},
	{"name": "ДНО ДНА", "hp": 1.85, "dmg": 1.85, "speed": 1.14, "mod_add": 0.3, "both_bosses": true, "early_elite": 5,
			"text": "НИЖЕ ПАДАТЬ НЕКУДА. НО ТЫ ПОПРОБУЙ"},
]

# --- Модификаторы волн (сюрприз в начале обычной волны) ---
const WAVE_MOD_FROM: int = 3                 # не раньше этой волны
const WAVE_MOD_CHANCE: float = 0.45          # шанс на обычную волну (элита/орда/боссы - без модификаторов)
# Модификаторы: title/line - объявление; fx - эффекты (множители к врагам/игроку, спавнеры, фильтры экрана, эффекты при смерти).
# Ключи fx: enemy_speed, enemy_hp, enemy_damage, enemy_size, enemy_count, coin, player_speed, player_damage, attack_speed,
#   pickup, time_scale, spawn_near (множитель мин. дистанции спавна), spread (разброс выстрелов, град),
#   spawner (acid|truck|lightning|slippers|pigeons|crates|roaches|smoke), overlay (darkness|disco|sewer|hangover),
#   on_death (puddle|explode|revive|jackpot), ice, wind, bounce.
const WAVE_MOD_DATA: Dictionary = {
	&"acid_rain": {"title": "КИСЛОТНЫЙ ДОЖДЬ", "line": "С НЕБА ЛЬЁТ КИСЛОТА. СМОТРИ ПОД НОГИ, ЛОХ", "fx": {"spawner": &"acid"}},
	&"darkness": {"title": "ОТРУБИЛИ СВЕТ", "line": "СВЕТ ОТРУБИЛИ ЗА НЕУПЛАТУ. ТВОЮ", "fx": {"overlay": &"darkness"}},
	&"garbage_truck": {"title": "МУСОРОВОЗ", "line": "МУСОРОВОЗ НЕ ТОРМОЗИТ. ТЫ ТОЖЕ МУСОР", "fx": {"spawner": &"truck"}},
	&"ice": {"title": "ЖИРНЫЙ ПОЛ", "line": "КТО-ТО РАЗЛИЛ ЖИР. СКОЛЬЗИ, ПОКА ЖИВ", "fx": {"ice": true}},
	&"payday": {"title": "ДЕНЬ ЗАРПЛАТЫ", "line": "ГОВНА ВДВОЕ БОЛЬШЕ. ВРАГИ ТОЖЕ ЗЛЕЕ", "fx": {"coin": 2.0, "enemy_speed": 1.25}},
	&"pigeon_raid": {"title": "ГОЛУБИНЫЙ НАЛЁТ", "line": "ГОЛУБИ ПРИЛЕТЕЛИ ОТОМСТИТЬ ЗА СЕМЕЧКИ", "fx": {"spawner": &"pigeons"}},
	&"sewer_flood": {"title": "ПРОРВАЛО КАНАЛИЗАЦИЮ", "line": "ПО КОЛЕНО В ЖИЖЕ. ВСЕ. И ТЫ ТОЖЕ", "fx": {"overlay": &"sewer", "player_speed": 0.8, "enemy_speed": 0.8}},
	&"wind": {"title": "ВЕТЕР С ПОМОЙКИ", "line": "СДУВАЕТ, КАК ПАКЕТ. ТЫ И ЕСТЬ ПАКЕТ", "fx": {"wind": true}},
	&"hangover": {"title": "ПОХМЕЛЬЕ", "line": "ДВОИТСЯ В ГЛАЗАХ. ЗАТО ЗЛОЙ КАК СОБАКА", "fx": {"overlay": &"hangover", "player_damage": 1.25}},
	&"giants": {"title": "ГИГАНТИЗМ", "line": "ВРАГИ ОТЪЕЛИСЬ НА ПОМОЙКЕ. ТЫ НЕТ", "fx": {"enemy_size": 1.5, "enemy_hp": 1.6, "enemy_speed": 0.8, "coin": 1.4}},
	&"dwarfs": {"title": "КАРЛИКИ", "line": "МЕЛКИЕ, БЫСТРЫЕ И ИХ ДОФИГА", "fx": {"enemy_size": 0.6, "enemy_hp": 0.55, "enemy_speed": 1.35, "enemy_count": 1.5}},
	&"poop_death": {"title": "ОБОСРАННЫЕ ВРАГИ", "line": "ДОХНУТ И ГАДЯТ НАПОСЛЕДОК", "fx": {"on_death": &"puddle"}},
	&"disco": {"title": "ДИСКОТЕКА 90-Х", "line": "ВСЕ ТАНЦУЮТ. ТЫ ТОЖЕ, ИНАЧЕ СДОХНЕШЬ", "fx": {"overlay": &"disco", "bounce": true, "attack_speed": 1.25}},
	&"airdrop": {"title": "ГУМАНИТАРКА", "line": "С НЕБА ПАДАЮТ ЯЩИКИ. ИНОГДА НА ГОЛОВУ", "fx": {"spawner": &"crates"}},
	&"slipper_storm": {"title": "ТАПКОПАД", "line": "МАМКИ ВСЕГО РАЙОНА КИДАЮТ ТАПКИ", "fx": {"spawner": &"slippers"}},
	&"magnet": {"title": "МАГНИТНАЯ БУРЯ", "line": "ГОВНО САМО ЛЕТИТ К ТЕБЕ. РОДСТВЕННОЕ", "fx": {"pickup": 4.0, "enemy_speed": 1.1}},
	&"explosive": {"title": "ВЗРЫВООПАСНО", "line": "ВРАГИ НАЖРАЛИСЬ ГОРОХА. ДЕРЖИСЬ ПОДАЛЬШЕ", "fx": {"on_death": &"explode"}},
	&"zombies": {"title": "ЗОМБИ-ВЫХОДНОЙ", "line": "ДОХЛЫЕ ВСТАЮТ. ОНИ ТОЖЕ НЕ ХОТЯТ НА РАБОТУ", "fx": {"on_death": &"revive"}},
	&"smoke_break": {"title": "ПЕРЕКУР", "line": "ВСЯ ПОМОЙКА ВЫШЛА ПОКУРИТЬ", "fx": {"spawner": &"smoke"}},
	&"slowmo": {"title": "ЗАМЕДЛЕННАЯ СЪЁМКА", "line": "КАК В КИНО. ТОЛЬКО ТЫ НЕ ГЕРОЙ", "fx": {"time_scale": 0.75}},
	&"fast_forward": {"title": "ПЕРЕМОТКА", "line": "КТО-ТО НАЖАЛ x1.3. ГОВНА ТОЖЕ БОЛЬШЕ", "fx": {"time_scale": 1.3, "coin": 1.3}},
	&"manholes": {"title": "ОТКРЫТЫЕ ЛЮКИ", "line": "ЛЕЗУТ ИЗ КАНАЛИЗАЦИИ ПРЯМО ПОД НОГАМИ", "fx": {"spawn_near": 0.5}},
	&"lottery": {"title": "ЛОТЕРЕЯ", "line": "У КОГО-ТО ИЗ НИХ В КАРМАНЕ ДЖЕКПОТ", "fx": {"on_death": &"jackpot"}},
	&"thunder": {"title": "ГРОЗА НАД СВАЛКОЙ", "line": "МОЛНИЯ БЬЁТ В САМОЕ ВЫСОКОЕ. ПРИГНИСЬ", "fx": {"spawner": &"lightning"}},
	&"crooked": {"title": "КРИВЫЕ РУКИ", "line": "МАЖЕШЬ, НО ЕСЛИ ПОПАЛ - БОЛЬНО", "fx": {"spread": 18.0, "player_damage": 1.35}},
	&"roach_exodus": {"title": "ТАРАКАНИЙ ИСХОД", "line": "ТАРАКАНЫ ПЕРЕЕЗЖАЮТ. ЧЕРЕЗ ТЕБЯ", "fx": {"spawner": &"roaches", "coin": 1.3}},
	&"few_fat": {"title": "МАЛО, НО ЖИРНО", "line": "ИХ МЕНЬШЕ. ЗАТО КАЖДЫЙ - ШКАФ", "fx": {"enemy_count": 0.5, "enemy_hp": 2.2, "enemy_size": 1.25, "coin": 1.4}},
}
const WAVE_MODS: Array = [&"acid_rain", &"darkness", &"garbage_truck", &"ice", &"payday", &"pigeon_raid", &"sewer_flood", &"wind",
		&"hangover", &"giants", &"dwarfs", &"poop_death", &"disco", &"airdrop", &"slipper_storm", &"magnet", &"explosive",
		&"zombies", &"smoke_break", &"slowmo", &"fast_forward", &"manholes", &"lottery", &"thunder", &"crooked", &"roach_exodus", &"few_fat"]
const LIGHTNING_INTERVAL_SEC: float = 0.9
const LIGHTNING_WARN_SEC: float = 0.8
const LIGHTNING_RADIUS: float = 14.0
const LIGHTNING_DAMAGE: float = 5.0          # × сила волны^0.7; врагам - втрое больше
const SLIPPER_INTERVAL_SEC: float = 0.8
const SLIPPER_SPEED: float = 150.0
const SLIPPER_DAMAGE: float = 2.0
const PIGEON_RAID_INTERVAL_SEC: float = 5.0
const PIGEON_RAID_SPEED: float = 150.0
const PIGEON_RAID_DROP_EVERY_PX: float = 40.0
const CRATE_INTERVAL_SEC: float = 3.0
const CRATE_WARN_SEC: float = 1.2
const CRATE_DAMAGE: float = 4.0
const CRATE_XP_DROPS: int = 6
const ROACH_INTERVAL_SEC: float = 4.0
const ROACH_GROUP: int = 10
const SMOKE_INTERVAL_SEC: float = 2.0
const SMOKE_RADIUS: float = 34.0
const SMOKE_SEC: float = 7.0
const WIND_FORCE: float = 45.0              # px/с снос героя
const WIND_CHANGE_SEC: float = 5.0
const EXPLODE_ON_DEATH_RADIUS: float = 30.0
const EXPLODE_ON_DEATH_DAMAGE: float = 3.0  # по герою, × сила волны^0.7; врагам - 20
const REVIVE_CHANCE: float = 0.35
const JACKPOT_CHANCE: float = 0.03
const JACKPOT_DROPS: int = 12
const DEATH_PUDDLE_CHANCE: float = 0.45
const DEATH_PUDDLE_DAMAGE: float = 1.5      # × сила волны^0.7
const ACID_DROP_INTERVAL_SEC: float = 1.0
const ACID_DROP_WARN_SEC: float = 1.0
const ACID_DROP_RADIUS: float = 16.0
const ACID_DROP_NEAR_PLAYER: float = 0.55      # доля капель рядом с игроком (в радиусе 90)
const ACID_PUDDLE_DAMAGE: float = 2.0          # × сила волны^0.7
const ACID_PUDDLE_SEC: float = 3.5
const DARKNESS_RADIUS: float = 70.0            # px вокруг героя видно
const TRUCK_INTERVAL_SEC: float = 6.5
const TRUCK_WARN_SEC: float = 1.3
const TRUCK_SPEED: float = 380.0
const TRUCK_HALF_WIDTH: float = 24.0
const TRUCK_DAMAGE: float = 6.0                # × сила волны^0.7
const ICE_ACCEL: float = 3.0                   # чем меньше, тем дольше разгон и торможение

# --- Награда за скилл: чистая волна и серия без урона ---
const CLEAN_WAVE_BONUS_BASE: int = 6          # говна за волну без единого попадания
const CLEAN_WAVE_BONUS_PER_WAVE: int = 3      # + за номер волны
const NOHIT_STREAK_TIERS: Array = [[10.0, 0.10], [20.0, 0.25], [40.0, 0.50], [60.0, 0.80]]   # [сек без урона, + доля говна с дропа]

# --- Рывок (у всех героев, у каждого свой): dist - px, sec - длительность, cd - перезарядка, charges - зарядов,
# fx - фишка: knock (отпихнуть вокруг в конце), sweep (урон по пути), slow (тормозит врагов у старта), trail (тормозит по пути),
# blink (телепорт), drunk (кривой, но дольше неуязвим), heal (+ХП), fly (неуязвим весь полёт и чуть дольше).
const DASH_BASE: Dictionary = {"dist": 70.0, "sec": 0.16, "cd": 1.5, "charges": 1, "iframe_extra": 0.08, "fx": &""}
const DASH_FX_RADIUS: float = 40.0
const DASH_FX_SLOW: float = 0.4          # множитель скорости врага
const DASH_FX_SLOW_SEC: float = 2.0
const DASH_FX_KNOCK: float = 300.0
const DASH_FX_DAMAGE: float = 12.0       # урон рывка по пути (растёт с уроном героя)
const DASH_FX_HEAL: float = 1.0
const DASH_DRUNK_DEG: float = 30.0
const DASH_BLOCK_PAD: float = 5.0        # рывок упирается во врага, если тот ближе (его радиус + это) прямо по курсу
const DASH_BLOCK_DOT: float = 0.45       # «по курсу»: косинус угла между рывком и направлением на врага
const HERO_DASH: Dictionary = {
	&"hobo": {"name": "ПЕРЕКАТ ПО ЛУЖЕ", "dist": 55.0, "cd": 2.0, "fx": &"slow"},
	&"squid": {"name": "ЧЕРНИЛЬНЫЙ ПСИХ", "dist": 75.0, "cd": 1.4, "fx": &"slow"},
	&"clerk": {"name": "НА ПЛАНЁРКУ", "dist": 62.0, "cd": 2.2, "charges": 2},
	&"janitor": {"name": "РАЗМАХ МЕТЛОЙ", "dist": 50.0, "cd": 2.0, "fx": &"sweep"},
	&"uncle_vitya": {"name": "ПЬЯНЫЙ КУВЫРОК", "dist": 62.0, "cd": 1.8, "fx": &"drunk"},
	&"blogger": {"name": "ДЛЯ КОНТЕНТА", "dist": 80.0, "cd": 1.3},
	&"granny": {"name": "КЛЮКОЙ ПО ХРЕБТУ", "dist": 40.0, "cd": 2.4, "fx": &"knock"},
	&"courier": {"name": "ОПАЗДЫВАЮ", "dist": 92.0, "cd": 1.1},
	&"pigeon": {"name": "ВСПОРХ", "dist": 95.0, "sec": 0.3, "cd": 2.0, "fx": &"fly"},
	&"punk": {"name": "ШМЫГ", "dist": 52.0, "cd": 0.9, "charges": 2},
	&"shawarma": {"name": "ЖИРНЫЙ СКОЛЬЗ", "dist": 60.0, "cd": 1.7, "fx": &"trail"},
	&"guard": {"name": "ТАРАН", "dist": 50.0, "cd": 2.0, "fx": &"sweep"},
	&"student": {"name": "ПРОГУЛ", "dist": 82.0, "cd": 1.2},
	&"plumber": {"name": "ПО ТРУБАМ", "dist": 75.0, "cd": 2.2, "fx": &"blink"},
	&"dacha": {"name": "ГРЯДКА ЛЕЧИТ", "dist": 45.0, "cd": 2.2, "fx": &"heal"},
	&"skater": {"name": "ОЛЛИ", "dist": 100.0, "sec": 0.2, "cd": 1.6, "charges": 2},
	&"slime": {"name": "ПОЛЗОК", "dist": 60.0, "cd": 1.5, "fx": &"trail"},
}

# --- Телеграфы атак (замах виден заранее: зона + наползающая заливка) ---
const CHARGER_WINDUP_SEC: float = 0.6       # тележка стоит и показывает путь рывка
const CHARGER_DASH_SEC: float = 0.55
const CHARGER_DASH_SPEED: float = 260.0
const SPITTER_WINDUP_SEC: float = 0.4       # плевун надувается и показывает линию плевка
const SPITTER_AIM_LENGTH: float = 60.0
const HAMSTER_SLAM_TELE_RADIUS: float = 60.0
const MINION_WHIRL_TELE_RADIUS: float = 60.0
const TELEGRAPH_SHOT_LENGTH: float = 110.0  # длина линии/конуса для бросков боссов
const ZAKHAR_FART_RADIUS: float = 26.0
const ZAKHAR_FART_DAMAGE: float = 4.0           # за каждый удар (с кулдауном неуязвимости игрока)
const ZAKHAR_FART_LIFETIME_SEC: float = 3.5
const ZAKHAR_KICK_RANGE: float = 70.0
const ZAKHAR_KICK_WINDUP_SEC: float = 0.5       # замах = цикл анимации — мигает жёлтым
const ZAKHAR_CAST_SEC: float = 0.5              # замах броска/пука (цикл анимации)
const ZAKHAR_KICK_SPEED: float = 280.0
const ZAKHAR_KICK_DURATION_SEC: float = 0.25

# --- Боссы: Миньон-псих ---
const MINION_WRENCH_INTERVAL_SEC: float = 1.8
const MINION_WRENCH_DAMAGE: float = 7.0
const MINION_WRENCH_SPEED: float = 150.0
const MINION_WRENCH_FAN_DEG: float = 14.0
const MINION_WRENCH_SPIN: float = 14.0          # рад/с
const MINION_POOP_INTERVAL_SEC: float = 3.2
const MINION_POOP_SPEED: float = 110.0
const MINION_PUDDLE_RADIUS: float = 22.0
const MINION_PUDDLE_DAMAGE: float = 4.0
const MINION_PUDDLE_LIFETIME_SEC: float = 4.0
const MINION_STRAFE_SPEED: float = 45.0         # «психованные» дёрганья в стороны
const MINION_CAST_SEC: float = 0.5               # замах броска (цикл анимации)
const MINION_WHIRL_INTERVAL_SEC: float = 6.0     # вихрь булавой (только в ярости <50% HP)
const MINION_WHIRL_WRENCHES: int = 8
const MINION_ENRAGE_MULT: float = 0.7            # в ярости кулдауны ×0.7
const PROJECTILE_BOSS_LIFETIME_SEC: float = 3.0

# --- Отдача от попаданий ---
const ENEMY_KNOCKBACK_SPEED: float = 120.0   # импульс, который враг получает от попадания
const KNOCKBACK_DECAY: float = 600.0         # px/с² — как быстро гаснет отдача
const PLAYER_HIT_SHAKE: float = 4.0          # px — тряска камеры при уроне по игроку
const SHAKE_DECAY: float = 28.0              # px/с — затухание тряски

# --- Арена и камера ---
const ARENA_BORDER_THICKNESS: float = 64.0  # проволока (16) + зона редких декораций (48) за краем арены
const BORDER_DECOR_CHANCE: float = 0.5   # шанс декорации на каждые 48 px границы
const WIRE_SHOCK_DAMAGE: float = 5.0     # удар током/огнём от проволоки
const ENEMY_PLAYER_MIN_DISTANCE: float = 10.0  # ближе враг не подходит — игрок его расталкивает
const GROUND_DECAL_AREA_PX2: float = 9000.0  # одна декаль пола на столько px² арены
const CAMERA_ZOOM: float = 1.0  # только целое: дробный зум рвёт пиксели (виден шум); «дальше» = больше viewport

# --- Предметы (рюкзак Ларька): плюсы/минусы к статам + особые эффекты ---
# «Обосранные портки Supreme»: шанс, что враг в контакте шарахается от вони и не подходит.
const ITEM_STINKY_PANTS_REPEL_CHANCE: float = 15.0
const SHOP_COMPANION_WEIGHT: int = 4               # питомцы и структуры выпадают в 4 раза чаще обычных предметов
const SHOP_ITEM_CHANCE: float = 0.4                 # шанс, что слот витрины — предмет
const ITEM_REPEL_MAX_PERCENT: float = 35.0
const ITEM_REPEL_RADIUS: float = 46.0               # враги в этом радиусе отлетают от вони
const ITEM_REPEL_PUSH: float = 320.0
const ITEM_THORNS_RADIUS: float = 34.0
const ITEM_EXPLODE_RADIUS: float = 44.0
const ITEM_EXPLODE_DAMAGE: float = 22.0             # * множитель урона
const ITEM_LIFESTEAL_HP: float = 1.0
const ITEM_BURN_DPS: float = 5.0                    # зажигалка: урон в секунду от поджога
const ITEM_BURN_SEC: float = 3.0
const ITEM_BASH_PUSH: float = 360.0                 # лом: сила отбрасывания
const ITEM_STILL_REGEN_SEC: float = 2.0             # бинт: раз в столько секунд на месте лечит
const ITEM_DRUNK_SEC: float = 5.0                   # палёнка: длительность пьянки
const ITEM_DRUNK_ATTACK_BONUS: float = 0.3          # +30% скорости атаки во время пьянки
const ITEM_COMBO_SEC: float = 3.0                   # батарейка: серия живёт столько секунд после убийства
const ITEM_COMBO_MAX_STACKS: int = 6
const ITEM_SLOW_RADIUS: float = 40.0                # доска: враги рядом с бегущим замедляются
const ITEM_SLOW_TICK_SEC: float = 0.25
const ITEM_SLOW_SEC: float = 1.0
const ITEM_STILL_WAIT_SEC: float = 0.4              # сколько надо постоять, чтобы бинт заработал
# tier: 1-4 (цвет рамки), price: цена в говне до роста по волнам, limit: макс. штук (0 — без лимита),
# mods: статы (как у карточек уровня; можно с минусом), fx: coin_bonus/repel/thorns/explode/lifesteal/discount (на штуку)
# --- Комбо предметов: два предмета у героя сливаются в третий при покупке (скрытые, открываются в профиле).
const ITEM_COMBOS: Dictionary = {
	&"combo_smoke": [&"cigarette", &"lighter"],
	&"combo_rotten_lunch": [&"sandwich", &"old_milk"],
	&"combo_stink_set": [&"holey_sock", &"stinky_pants"],
	&"combo_double_head": [&"helmet", &"pot"],
	&"combo_golden_poop": [&"gold_tooth", &"poop_wallet"],
	&"combo_russian_winter": [&"vodka", &"ushanka"],
	&"combo_dacha_defense": [&"bucket_turret", &"bottle_mine"],
	&"combo_friendship": [&"dead_rat", &"stray_dog"],
}
const CURSED_FROM_WAVE: int = 4
const CURSED_SHOP_CHANCE: float = 0.12       # шанс, что товар-предмет в Ларьке - проклятый
const CURSED_HP_DRAIN_SEC: float = 8.0       # портсигар: -1 ХП раз в столько секунд боя

const ITEMS: Dictionary = {
	&"cigarette": {"tier": 1, "price": 14, "limit": 0, "mods": {&"speed": 6.0, &"max_hp": -3.0}},
	&"sandwich": {"tier": 1, "price": 15, "limit": 0, "mods": {&"max_hp": 8.0, &"dodge": -3.0}},
	&"holey_sock": {"tier": 1, "price": 13, "limit": 0, "mods": {&"dodge": 6.0, &"armor": -1.0}},
	&"pot": {"tier": 1, "price": 16, "limit": 0, "mods": {&"armor": 2.0, &"speed": -3.0}},
	&"energy_can": {"tier": 1, "price": 16, "limit": 0, "mods": {&"attack_speed": 10.0, &"max_hp": -4.0}},
	&"poop_wallet": {"tier": 1, "price": 18, "limit": 0, "fx": {&"coin_bonus": 10.0}},
	&"old_milk": {"tier": 2, "price": 26, "limit": 0, "mods": {&"regen": 3.0, &"damage": -4.0}},
	&"nail_knuckles": {"tier": 2, "price": 28, "limit": 0, "mods": {&"damage": 10.0, &"dodge": -4.0}},
	&"dirty_glasses": {"tier": 2, "price": 26, "limit": 0, "mods": {&"crit": 6.0, &"armor": -1.0}},
	&"junk_magnet": {"tier": 2, "price": 24, "limit": 0, "mods": {&"pickup": 40.0, &"damage": -3.0}},
	&"stinky_pants": {"tier": 2, "price": 30, "limit": 4, "fx": {&"repel": ITEM_STINKY_PANTS_REPEL_CHANCE}},
	&"foil_hat": {"tier": 3, "price": 40, "limit": 0, "mods": {&"dodge": 10.0, &"attack_speed": -5.0}},
	&"shawarma": {"tier": 3, "price": 42, "limit": 0, "mods": {&"max_hp": 14.0, &"regen": 2.0, &"speed": -6.0}},
	&"coupon": {"tier": 3, "price": 38, "limit": 5, "fx": {&"discount": 8.0}},
	&"barbed_wire": {"tier": 3, "price": 40, "limit": 0, "fx": {&"thorns": 6.0}, "mods": {&"armor": 1.0}},
	&"diarrhea": {"tier": 4, "price": 70, "limit": 3, "fx": {&"explode": 20.0}},
	&"bloody_rag": {"tier": 4, "price": 68, "limit": 4, "fx": {&"lifesteal": 8.0}},
	&"dead_rat": {"tier": 1, "price": 24, "limit": 3, "fx": {&"pets": 1.0}},
	&"bucket_turret": {"tier": 2, "price": 36, "limit": 3, "fx": {&"turrets": 1.0}},
	&"ghost_drunk": {"tier": 2, "price": 34, "limit": 2, "fx": {&"ghost_drunk": 1.0}},
	&"ghost_granny": {"tier": 2, "price": 36, "limit": 2, "fx": {&"ghost_granny": 1.0}},
	&"golden_toilet": {"tier": 4, "price": 90, "limit": 1, "mods": {&"damage": 14.0, &"crit": 8.0, &"armor": 2.0, &"speed": -8.0}},
	&"bottle_cap": {"tier": 1, "price": 12, "limit": 0, "mods": {&"armor": 1.0, &"dodge": -2.0}},
	&"gum": {"tier": 1, "price": 13, "limit": 0, "mods": {&"pickup": 25.0, &"speed": -2.0}},
	&"ushanka": {"tier": 1, "price": 15, "limit": 0, "mods": {&"max_hp": 6.0, &"speed": -3.0}},
	&"lighter": {"tier": 1, "price": 14, "limit": 0, "mods": {&"damage": 6.0, &"max_hp": -3.0}, "fx": {&"burn": 15.0}},
	&"plastic_bag": {"tier": 1, "price": 14, "limit": 0, "mods": {&"pickup": 30.0, &"armor": -1.0}},
	&"rubber_boot": {"tier": 1, "price": 15, "limit": 0, "mods": {&"speed": 5.0, &"dodge": -3.0}},
	&"vodka": {"tier": 2, "price": 26, "limit": 0, "mods": {&"damage": 9.0, &"dodge": -5.0}, "fx": {&"drunk": 6.0}},
	&"hot_dog": {"tier": 2, "price": 25, "limit": 0, "mods": {&"max_hp": 10.0, &"attack_speed": -4.0}},
	&"binoculars": {"tier": 2, "price": 27, "limit": 0, "mods": {&"crit": 7.0, &"speed": -3.0}},
	&"scarf": {"tier": 2, "price": 26, "limit": 0, "mods": {&"armor": 2.0, &"attack_speed": -4.0}},
	&"skateboard": {"tier": 2, "price": 28, "limit": 4, "mods": {&"speed": 10.0, &"armor": -1.0}, "fx": {&"slow_field": 1.0}},
	&"dried_fish": {"tier": 2, "price": 24, "limit": 0, "mods": {&"attack_speed": 8.0, &"dodge": -3.0}},
	&"helmet": {"tier": 3, "price": 40, "limit": 3, "mods": {&"armor": 3.0, &"speed": -5.0}, "fx": {&"block": 1.0}},
	&"bandage": {"tier": 3, "price": 38, "limit": 0, "mods": {&"regen": 4.0, &"damage": -5.0}, "fx": {&"still_regen": 1.0}},
	&"crowbar": {"tier": 3, "price": 42, "limit": 0, "mods": {&"damage": 14.0, &"speed": -6.0}, "fx": {&"bash": 12.0}},
	&"gold_tooth": {"tier": 3, "price": 40, "limit": 0, "mods": {&"crit": 10.0, &"max_hp": -5.0}, "fx": {&"crit_coin": 30.0}},
	&"battery": {"tier": 3, "price": 40, "limit": 0, "mods": {&"attack_speed": 15.0, &"armor": -2.0}, "fx": {&"combo": 4.0}},
	&"crown": {"tier": 4, "price": 75, "limit": 1, "mods": {&"max_hp": 12.0, &"damage": 8.0, &"armor": 1.0, &"dodge": -5.0}, "fx": {&"crown": 15.0}},
	&"junk_backpack": {"tier": 4, "price": 72, "limit": 0, "mods": {&"pickup": 60.0, &"max_hp": 10.0, &"speed": -6.0}, "fx": {&"stash": 30.0}},
	&"bone_club": {"tier": 4, "price": 80, "limit": 0, "mods": {&"damage": 20.0, &"attack_speed": 8.0, &"speed": -10.0}},
	&"stray_dog": {"tier": 2, "price": 34, "limit": 3, "fx": {&"dogs": 1.0}},
	&"bomber_pigeon": {"tier": 2, "price": 36, "limit": 3, "fx": {&"pigeons": 1.0}},
	&"bottle_mine": {"tier": 1, "price": 20, "limit": 4, "fx": {&"mines": 2.0}},
	&"stink_lamp": {"tier": 3, "price": 42, "limit": 2, "fx": {&"lamps": 1.0}},
	&"cart_mortar": {"tier": 3, "price": 46, "limit": 2, "fx": {&"mortars": 1.0}},
	# --- Проклятые: огромный плюс и мерзкий минус. В Ларьке отдельным шансом с CURSED_FROM_WAVE.
	&"cursed_cigcase": {"tier": 3, "price": 40, "limit": 1, "cursed": true, "mods": {&"damage": 40.0}, "fx": {&"hp_drain": 1.0}},
	&"cursed_teeth": {"tier": 3, "price": 40, "limit": 1, "cursed": true, "mods": {&"attack_speed": 35.0}, "fx": {&"enemy_haste": 15.0}},
	&"cursed_chain": {"tier": 2, "price": 30, "limit": 1, "cursed": true, "mods": {&"armor": 8.0, &"speed": -25.0}},
	&"cursed_wallet": {"tier": 2, "price": 26, "limit": 1, "cursed": true, "mods": {&"max_hp": -8.0}, "fx": {&"coin_bonus": 60.0}},
	&"cursed_voodoo": {"tier": 3, "price": 38, "limit": 1, "cursed": true, "fx": {&"thorns": 15.0, &"dash_cost": 1.0}},
	&"cursed_shawarma": {"tier": 2, "price": 30, "limit": 1, "cursed": true, "mods": {&"max_hp": 20.0}, "fx": {&"no_regen": 1.0}},
	&"cursed_mirror": {"tier": 3, "price": 36, "limit": 1, "cursed": true, "mods": {&"crit": 25.0, &"dodge": -15.0}},
	&"cursed_rat_crown": {"tier": 3, "price": 42, "limit": 1, "cursed": true, "mods": {&"damage": -15.0, &"max_hp": -5.0}, "fx": {&"pets": 3.0}},
	# --- Комбо: не продаются, получаются слиянием двух предметов (Balance.ITEM_COMBOS).
	&"combo_smoke": {"tier": 4, "price": 0, "limit": 1, "combo": true, "mods": {&"damage": 15.0, &"speed": 5.0}, "fx": {&"burn": 25.0}},
	&"combo_rotten_lunch": {"tier": 4, "price": 0, "limit": 1, "combo": true, "mods": {&"max_hp": 20.0, &"regen": 3.0}, "fx": {&"explode": 10.0}},
	&"combo_stink_set": {"tier": 4, "price": 0, "limit": 1, "combo": true, "fx": {&"repel": 35.0, &"thorns": 8.0}},
	&"combo_double_head": {"tier": 4, "price": 0, "limit": 1, "combo": true, "mods": {&"armor": 6.0}, "fx": {&"block": 2.0}},
	&"combo_golden_poop": {"tier": 4, "price": 0, "limit": 1, "combo": true, "fx": {&"coin_bonus": 50.0, &"crit_coin": 40.0}},
	&"combo_russian_winter": {"tier": 4, "price": 0, "limit": 1, "combo": true, "mods": {&"max_hp": 10.0, &"dodge": 10.0}, "fx": {&"drunk": 20.0}},
	&"combo_dacha_defense": {"tier": 4, "price": 0, "limit": 1, "combo": true, "fx": {&"turrets": 2.0, &"mines": 2.0}},
	&"combo_friendship": {"tier": 4, "price": 0, "limit": 1, "combo": true, "mods": {&"damage": 5.0}, "fx": {&"pets": 2.0, &"dogs": 1.0}},
}

# --- Забег ---
const MAX_ENEMIES_ON_SCREEN: int = 500  # CONVENTIONS.md

# --- XP / уровни ---
const XP_LEVEL_FACTOR: float = 1.0      # XP до следующего уровня = FACTOR * (уровень + 3)^2 (как в Brotato, масштаб под наши дропы)
const OUTLINE_ALPHA: float = 0.45                 # прозрачность обводки персонажей (тоньше на вид)
const OUTLINE_LOW_HP_COLOR: Color = Color(1.0, 0.93, 0.0)   # мало ХП — моча
const OUTLINE_FULL_HP_COLOR: Color = Color(1.0, 0.0, 0.2)   # полное ХП — красный
const OUTLINE_HP_CURVE: float = 2.0
const LEVEL_UP_CHOICES: int = 4
# Статы при повышении уровня (Brotato): значения по тирам I-IV.
const STAT_VALUES: Dictionary = {
	&"max_hp": [3.0, 6.0, 9.0, 12.0],
	&"regen": [2.0, 3.0, 4.0, 5.0],
	&"damage": [5.0, 8.0, 12.0, 16.0],
	&"attack_speed": [5.0, 10.0, 15.0, 20.0],
	&"speed": [3.0, 6.0, 9.0, 12.0],
	&"armor": [1.0, 2.0, 3.0, 4.0],
	&"dodge": [3.0, 6.0, 9.0, 12.0],
	&"pickup": [15.0, 30.0, 45.0, 60.0],
	&"crit": [3.0, 5.0, 7.0, 9.0],
}
const STAT_TIER2_CHANCE_PER_LEVEL: float = 0.04    # шанс II-тира на карточку = (ур-1)*это, до 0.5
const STAT_TIER3_CHANCE_PER_LEVEL: float = 0.025   # III-тир = (ур-5)*это, до 0.3
const STAT_TIER4_CHANCE_PER_LEVEL: float = 0.01    # IV-тир = (ур-15)*это, до 0.1
const STAT_GUARANTEED_TIER: Dictionary = {5: 2, 10: 3, 15: 3, 20: 3}  # гарантированный минимум тира по уровню; с 25-го каждый 5-й — IV
# --- Оружие и Ларёк (Brotato) ---
# Открытие оружия (как в Brotato): без записи - доступно сразу. kind - счётчик профиля, need - порог, text - подсказка.
const WEAPON_UNLOCK: Dictionary = {
	&"frying_pan": {"kind": &"deaths", "need": 1},
	&"bottle": {"kind": &"deaths", "need": 2},
	&"rolling_pin": {"kind": &"coins", "need": 300},
	&"pipe_gun": {"kind": &"kills", "need": 400},
	&"spray_can": {"kind": &"kills", "need": 1000},
	&"rotten_cheese": {"kind": &"wins", "need": 1},
	&"crossbow": {"kind": &"coins", "need": 1500},
	&"mosin": {"kind": &"wins", "need": 2},
	&"shiv": {"kind": &"deaths", "need": 4},
	&"shovel": {"kind": &"wins", "need": 3},
	&"blowtorch": {"kind": &"coins", "need": 3000},
	&"syringe": {"kind": &"kills", "need": 2000},
	&"tin_bomb": {"kind": &"coins", "need": 6000},
	&"extension_cord": {"kind": &"kills", "need": 3000},
}
const WEAPON_SLOTS: int = 6
const WEAPON_TIER_DAMAGE: Array[float] = [1.0, 1.5, 2.0, 2.7]      # множитель урона по тирам I-IV
const WEAPON_TIER_COOLDOWN: Array[float] = [1.0, 0.92, 0.85, 0.75]  # множитель паузы между атаками
# Классы оружия (как в Brotato): у оружия 1-2 класса. За 2..6 оружий одного класса в слотах - бонус набора (копии считаются).
const WEAPON_CLASSES: Dictionary = {
	&"lighter": [&"fire"], &"sock": [&"stinky"], &"slingshot": [&"guns"], &"laser_pointer": [&"guns"],
	&"mop": [&"household", &"stinky"], &"slipper": [&"fire"], &"condensed_milk": [&"kitchen"],
	&"pipe_gun": [&"guns"], &"crossbow": [&"guns"], &"frying_pan": [&"kitchen"], &"rolling_pin": [&"kitchen"],
	&"rotten_cheese": [&"stinky", &"kitchen"], &"spray_can": [&"fire", &"stinky"], &"bottle": [&"prison", &"guns"],
	&"mosin": [&"guns"], &"plunger": [&"household", &"stinky"], &"shiv": [&"prison"], &"shovel": [&"household"],
	&"blowtorch": [&"fire", &"household"], &"syringe": [&"prison"], &"tin_bomb": [&"fire", &"household"],
	&"extension_cord": [&"household", &"fire"],
}
# Бонус набора: "mod" - стат (как у предметов) или "fx" - эффект; values - за 2, 3, 4, 5, 6 оружий класса.
const WEAPON_CLASS_BONUS: Dictionary = {
	&"kitchen": {"mod": &"max_hp", "values": [2.0, 4.0, 6.0, 9.0, 12.0]},
	&"household": {"mod": &"armor", "values": [1.0, 2.0, 3.0, 4.0, 5.0]},
	&"guns": {"mod": &"crit", "values": [3.0, 6.0, 9.0, 12.0, 15.0]},
	&"fire": {"fx": &"burn", "values": [5.0, 10.0, 15.0, 20.0, 25.0]},
	&"stinky": {"fx": &"repel", "values": [3.0, 6.0, 9.0, 12.0, 15.0]},
	&"prison": {"fx": &"lifesteal", "values": [3.0, 6.0, 9.0, 12.0, 15.0]},
}
# Тир меняет не только урон и паузу: прибавка к свойству оружия на тирах I-IV (к значению из WEAPONS).
const WEAPON_TIER_PROPS: Dictionary = {
	&"lighter": {"burn_duration": [0.0, 0.5, 1.0, 1.5]},
	&"sock": {"radius": [0.0, 8.0, 16.0, 26.0]},
	&"slingshot": {"ricochets": [0, 1, 1, 2]},
	&"laser_pointer": {"beam_half_width": [0.0, 1.0, 2.0, 3.0]},
	&"mop": {"arc_deg": [0.0, 15.0, 30.0, 45.0], "reach": [0.0, 4.0, 8.0, 12.0]},
	&"slipper": {"aoe_radius": [0.0, 6.0, 12.0, 20.0]},
	&"condensed_milk": {"slow_duration": [0.0, 0.5, 1.0, 1.5], "pierce": [0, 0, 1, 1]},
	&"pipe_gun": {"pellets": [0, 1, 2, 3]},
	&"crossbow": {"pierce": [0, 1, 2, 3]},
	&"frying_pan": {"knockback": [0.0, 60.0, 120.0, 200.0], "arc_deg": [0.0, 10.0, 20.0, 30.0]},
	&"rolling_pin": {"reach": [0.0, 4.0, 8.0, 12.0]},
	&"rotten_cheese": {"radius": [0.0, 8.0, 16.0, 26.0]},
	&"spray_can": {"proj_life": [0.0, 0.04, 0.08, 0.12]},
	&"bottle": {"ricochets": [0, 1, 2, 3]},
	&"mosin": {"pierce": [0, 1, 2, 4]},
	&"plunger": {"knockback": [0.0, 60.0, 120.0, 200.0]},
	&"shiv": {"arc_deg": [0.0, 10.0, 20.0, 30.0]},
	&"shovel": {"arc_deg": [0.0, 15.0, 30.0, 45.0]},
	&"blowtorch": {"pierce": [0, 1, 1, 2]},
	&"syringe": {"burn_duration": [0.0, 1.0, 2.0, 3.0], "pierce": [0, 0, 1, 1]},
	&"tin_bomb": {"aoe_radius": [0.0, 6.0, 12.0, 20.0]},
	&"extension_cord": {"chain_jumps": [0, 1, 2, 3]},
}
const WEAPON_PRICE: Dictionary = {&"lighter": 22, &"sock": 24, &"slingshot": 22, &"mop": 26, &"laser_pointer": 24, &"slipper": 30, &"condensed_milk": 22,
		&"pipe_gun": 26, &"crossbow": 30, &"frying_pan": 24, &"rolling_pin": 20, &"rotten_cheese": 26, &"spray_can": 24, &"bottle": 22, &"mosin": 34,
		&"plunger": 22, &"shiv": 18, &"shovel": 30, &"blowtorch": 28, &"syringe": 24, &"tin_bomb": 30, &"extension_cord": 28}
const PERK_PRICE: Dictionary = {&"speed": 14, &"regen": 16, &"double_shot": 30, &"loot_goblin": 12}
const SHOP_SLOTS: int = 4
const SHOP_PRICE_TIER_MULT: Array[float] = [1.0, 2.0, 3.5, 6.0]
const COIN_PER_XP: float = 1.3   # сколько говна даёт 1 XP
const SHOP_PRICE_WAVE_GROWTH: float = 0.15          # цена *(1 + это * волна)
const SHOP_WEAPON_CHANCE: float = 0.45              # шанс, что слот — оружие (предмет — SHOP_ITEM_CHANCE, иначе перк)
const SHOP_TIER2_PER_WAVE: float = 0.05             # II-тир: (волна-1)*это, до 0.5
const SHOP_TIER3_PER_WAVE: float = 0.03             # III-тир: (волна-3)*это, до 0.35
const SHOP_TIER4_PER_WAVE: float = 0.015            # IV-тир: (волна-7)*это, до 0.2
const RECYCLE_FRACTION: float = 0.5                 # возврат говна за переработку
const REROLL_BASE_COST: int = 3
const REROLL_WAVE_FACTOR: float = 0.7               # + волна * это
const REROLL_STEP_COST: int = 2                     # + за каждый реролл в эту волну
const ARMOR_MIN_FACTOR: float = 0.45                # броня режет урон не больше чем на 55%
const ARMOR_K: float = 15.0                         # урон *= K/(K+броня)
const DODGE_MAX_PERCENT: float = 60.0
const CRIT_DAMAGE_MULT: float = 2.0
const REGEN_HP_PER_POINT: float = 0.6               # хп за интервал на 1 очко регена
const BIN_COUNT_BASE: int = 2                       # мусорных баков на волну
const BIN_COUNT_WAVES_PER_EXTRA: int = 4            # +1 бак за столько волн
const BIN_VARIANTS: int = 4                         # видов бака с разной начинкой
const BIN_HEAL_CHANCE: float = 0.4
const BIN_HEAL_HP: float = 3.0
const HEALER_RADIUS: float = 60.0
const HEALER_INTERVAL_SEC: float = 2.5
const HEALER_FRACTION: float = 0.15
const EGG_HATCH_SEC: float = 5.0
const MAMKA_SPAWN_COUNT: int = 3
const GLUTTON_EAT_RADIUS: float = 140.0
const GLUTTON_GROW_STEP: float = 0.08
const GLUTTON_MAX_SCALE: float = 1.9

# --- Враги: hp, damage, speed, xp, coins (GDD) ---
const ENEMIES: Dictionary = {
	&"squid_gopnik": {"hp": 40.0, "damage": 2.5, "speed": 68.0, "xp": 2, "coins": 1},
	&"microbe": {"hp": 60.0, "damage": 1.5, "speed": 40.0, "xp": 3, "coins": 1},
	&"npc_bot": {"hp": 32.0, "damage": 2.0, "speed": 50.0, "xp": 2, "coins": 1},
	&"cockroach": {"hp": 9.0, "damage": 2.0, "speed": 140.0, "xp": 1, "coins": 2},
	&"wifi_ghost": {"hp": 50.0, "damage": 3.0, "speed": 70.0, "xp": 4, "coins": 2, "flying": true},
	# Враги Шага 4 (поведение как в Brotato): group_mult — множитель размера группы.
	&"chaser": {"hp": 10.0, "damage": 1.0, "speed": 90.0, "xp": 1, "coins": 1, "radius": 5.0, "group_mult": 1.4, "flying": true},
	&"charger": {"hp": 50.0, "damage": 2.5, "speed": 70.0, "xp": 3, "coins": 1, "radius": 8.0, "group_mult": 0.7,
			"brain": "res://scripts/enemies/brains/charger_brain.gd"},
	&"spitter": {"hp": 34.0, "damage": 2.0, "speed": 60.0, "xp": 3, "coins": 1, "radius": 7.0, "group_mult": 1.0,
			"brain": "res://scripts/enemies/brains/spitter_brain.gd"},
	&"bruiser": {"hp": 170.0, "damage": 3.0, "speed": 55.0, "xp": 8, "coins": 3, "radius": 13.0, "group_mult": 0.3},
	&"looter": {"hp": 90.0, "damage": 1.0, "speed": 85.0, "xp": 25, "coins": 10, "radius": 7.0, "group_mult": 0.0,
			"brain": "res://scripts/enemies/brains/looter_brain.gd"},
	# Враги Шага 4б (Brotato: healer, slasher egg, spawner, gobbler, tree).
	&"healer": {"hp": 36.0, "damage": 1.0, "speed": 55.0, "xp": 4, "coins": 1, "radius": 7.0, "group_mult": 0.4,
			"brain": "res://scripts/enemies/brains/healer_brain.gd"},
	&"egg": {"hp": 24.0, "damage": 0.0, "speed": 0.0, "xp": 2, "coins": 0, "radius": 6.0, "group_mult": 0.3, "contact": false,
			"brain": "res://scripts/enemies/brains/egg_brain.gd"},
	&"mamka": {"hp": 140.0, "damage": 2.0, "speed": 45.0, "xp": 6, "coins": 2, "radius": 12.0, "group_mult": 0.25,
			"brain": "res://scripts/enemies/brains/mamka_brain.gd"},
	&"glutton": {"hp": 60.0, "damage": 2.0, "speed": 70.0, "xp": 5, "coins": 2, "radius": 8.0, "group_mult": 0.4,
			"brain": "res://scripts/enemies/brains/glutton_brain.gd"},
	&"trash_bin": {"hp": 40.0, "damage": 0.0, "speed": 0.0, "xp": 6, "coins": 0, "radius": 12.0, "group_mult": 0.0,
			"contact": false, "neutral": true, "brain": "res://scripts/enemies/brains/bin_brain.gd"},
	# Босс-заглушка Шага 3 (особое поведение — позже); radius — размер тела в px.
	&"boss_mega_hamster": {"hp": 600.0, "damage": 5.0, "speed": 35.0, "xp": 30, "coins": 20, "radius": 28.0, "anim_rows": 5,
			"brain": "res://scripts/enemies/brains/boss_hamster_brain.gd"},
	&"boss_zakhar": {"hp": 900.0, "damage": 4.0, "speed": 45.0, "xp": 40, "coins": 25, "radius": 30.0, "anim_rows": 6,
			"brain": "res://scripts/enemies/brains/boss_zakhar_brain.gd"},
	&"boss_minion": {"hp": 700.0, "damage": 3.0, "speed": 70.0, "xp": 40, "coins": 25, "radius": 22.0, "anim_rows": 5,
			"brain": "res://scripts/enemies/brains/boss_minion_brain.gd"},
}

# --- Боссы (GDD) ---
const BOSS_MEGA_HAMSTER_SPAWN_SEC: float = 300.0
const BOSS_MEGA_HAMSTER_SPLIT_COUNT: int = 8  # микробов при смерти
const HAMSTER_ATTACK_INTERVAL_SEC: float = 2.6   # пауза между атаками (в ярости ×0.65 — на <50% HP)
const HAMSTER_CAST_SEC: float = 0.5              # замах = один цикл анимации (4 кадра по 8 fps)
const HAMSTER_SEED_DAMAGE: float = 6.0
const HAMSTER_SEED_SPEED: float = 130.0
const HAMSTER_SEED_FAN_DEG: float = 20.0         # веер из пяти семечек
const HAMSTER_SLAM_SEEDS: int = 12               # ударная волна: кольцо семечек
const HAMSTER_SLAM_SPEED: float = 95.0
const HAMSTER_ROLL_SPEED: float = 210.0
const HAMSTER_ROLL_SEC: float = 0.9
const BOSS_UNCLE_VITYA_SPAWN_SEC: float = 600.0
const BOSS_UNCLE_VITYA_AURA_RADIUS: float = 100.0
const BOSS_UNCLE_VITYA_AURA_DPS: float = 2.0
const BOSS_BLUE_WHALE_SPAWN_SEC: float = 900.0
const BOSS_BLUE_WHALE_TEARS_COUNT: int = 5  # веер снарядов

# --- Оружие: damage, cooldown (GDD) ---
const WEAPONS: Dictionary = {
	&"lighter": {"damage": 9.0, "cooldown": 0.35, "burn_dps": 2.0, "burn_duration": 3.0, "tag": "ПОДЖИГАЕТ"},
	&"sock": {"damage": 12.0, "cooldown": 1.0, "radius": 60.0, "tag": "ВОНЬ ВОКРУГ"},
	&"slingshot": {"damage": 8.0, "cooldown": 0.6, "ricochets": 2, "ricochet_range": 110.0, "tag": "ОТСКОКИ"},
	&"laser_pointer": {"damage": 3.0, "cooldown": 0.2, "beam_half_width": 5.0, "tag": "ПРОБИВАЕТ"},
	&"mop": {"damage": 14.0, "cooldown": 0.8, "knockback": 240.0, "reach": 52.0, "arc_deg": 140.0, "tag": "ОТБРОС"},
	&"slipper": {"damage": 25.0, "cooldown": 2.5, "aoe_radius": 40.0, "flight_sec": 0.5, "tag": "ВЗРЫВ"},
	&"condensed_milk": {"damage": 6.0, "cooldown": 0.5, "slow_factor": 0.5, "slow_duration": 2.0,
			"projectile": "res://assets/sprites/proj_milk.png", "tag": "ЗАМЕДЛЯЕТ"},
	&"turret": {"damage": 7.0, "cooldown": 0.9, "tag": "ТУРЕЛЬ", "structure": true},
	&"stink_lamp": {"damage": 4.0, "cooldown": 0.5, "radius": 70.0, "tag": "ЛАМПА", "structure": true},
	&"cart_mortar": {"damage": 24.0, "cooldown": 2.4, "aoe_radius": 42.0, "flight_sec": 0.6, "range": 230.0,
			"projectile": "res://assets/sprites/proj_tin_bomb.png", "tag": "МИНОМЁТ", "structure": true},   # структура: стоит на месте, стреляет сама
	# --- Пачка 2: pellets/spread_deg/jitter_deg/proj_speed/proj_life/pierce - у стрелков; reach/arc_deg/knockback - у ближних; radius - у аур
	&"pipe_gun": {"damage": 4.0, "cooldown": 1.1, "pellets": 5, "spread_deg": 9.0, "proj_life": 0.45, "tag": "ДРОБЬ"},
	&"crossbow": {"damage": 14.0, "cooldown": 1.2, "pierce": 3, "proj_speed": 300.0, "tag": "ПРОБИВАЕТ"},
	&"frying_pan": {"damage": 24.0, "cooldown": 0.95, "knockback": 420.0, "reach": 38.0, "arc_deg": 100.0, "tag": "ОТБРОС"},
	&"rolling_pin": {"damage": 7.0, "cooldown": 0.3, "knockback": 90.0, "reach": 40.0, "arc_deg": 90.0, "tag": "БЫСТРАЯ"},
	&"rotten_cheese": {"damage": 4.0, "cooldown": 0.5, "radius": 85.0, "tag": "ВОНЬ ВОКРУГ"},
	&"spray_can": {"damage": 2.0, "cooldown": 0.1, "jitter_deg": 12.0, "proj_life": 0.32, "burn_dps": 1.5, "burn_duration": 2.0, "tag": "ПОДЖИГАЕТ"},
	&"bottle": {"damage": 10.0, "cooldown": 1.0, "ricochets": 4, "ricochet_range": 140.0, "projectile": "res://assets/sprites/proj_bottle.png", "tag": "ОТСКОКИ"},
	&"mosin": {"damage": 42.0, "cooldown": 2.1, "pierce": 2, "proj_speed": 520.0, "proj_life": 1.2, "tag": "СНАЙПЕР"},
	# --- Пачка 3: range - дальность прицела (меньше общей), chain_* - цепная молния
	&"plunger": {"damage": 21.0, "cooldown": 0.8, "knockback": 340.0, "reach": 44.0, "arc_deg": 90.0, "tag": "ОТБРОС"},
	&"shiv": {"damage": 5.0, "cooldown": 0.2, "knockback": 40.0, "reach": 30.0, "arc_deg": 70.0, "tag": "ОЧЕНЬ БЫСТРАЯ"},
	&"shovel": {"damage": 34.0, "cooldown": 1.35, "knockback": 220.0, "reach": 48.0, "arc_deg": 120.0, "tag": "ТЯЖЁЛАЯ"},
	&"blowtorch": {"damage": 3.0, "cooldown": 0.11, "jitter_deg": 9.0, "proj_speed": 300.0, "proj_life": 0.3, "pierce": 2, "range": 95.0,
			"burn_dps": 3.0, "burn_duration": 2.5, "projectile": "res://assets/sprites/proj_flame.png", "tag": "ПОДЖИГАЕТ"},
	&"syringe": {"damage": 6.0, "cooldown": 0.5, "proj_speed": 380.0, "pierce": 1, "burn_dps": 3.5, "burn_duration": 4.0,
			"projectile": "res://assets/sprites/proj_poison.png", "tag": "ЯД"},
	&"tin_bomb": {"damage": 30.0, "cooldown": 2.3, "aoe_radius": 46.0, "flight_sec": 0.55, "projectile": "res://assets/sprites/proj_tin_bomb.png", "tag": "ВЗРЫВ"},
	&"extension_cord": {"damage": 9.0, "cooldown": 0.8, "chain_jumps": 3, "chain_range": 80.0, "chain_falloff": 0.85, "tag": "ЦЕПНАЯ МОЛНИЯ"},
}

# --- Структуры и питомцы (появляются в начале волны, пропадают в конце) ---
const TURRET_WINDUP_SEC: float = 0.35            # ствол набухает перед выстрелом
const TURRET_MUZZLE_DIST: float = 12.0           # откуда вылетает снаряд (от центра ведра)
const STRUCTURE_SPAWN_MIN_DIST: float = 28.0      # от игрока
const STRUCTURE_SPAWN_MAX_DIST: float = 90.0
const PET_DAMAGE: float = 6.0
const PET_BITE_SEC: float = 0.55
const PET_SPEED: float = 120.0
const PET_AGGRO_RANGE: float = 110.0              # от игрока: дальше крыса не бегает за врагом
const GHOST_ALPHA: float = 0.32                    # призраки почти прозрачные, не отвлекают
const GHOST_THROW_RANGE: float = 150.0
const GHOST_THROW_SPEED: float = 190.0
const GHOST_DRUNK_DAMAGE: float = 14.0           # призрак друга-алкаша швыряет бутылки
const GHOST_DRUNK_THROW_SEC: float = 1.0
const GHOST_DRUNK_SPEED: float = 60.0
const GHOST_DRUNK_WOBBLE: float = 45.0             # px/с боковой «болтанки»
const GHOST_GRANNY_ACT_SEC: float = 1.4            # бабка-повитуха: раз в столько секунд...
const GHOST_GRANNY_HEAL_CHANCE: float = 0.3        # ...с таким шансом лечит, иначе кидает тапок
const GHOST_GRANNY_HEAL: float = 1.0
const GHOST_GRANNY_SLIPPER_DAMAGE: float = 9.0
const DOG_DAMAGE: float = 9.0                     # пёс: кусает сильнее и чаще крысы
const DOG_BITE_SEC: float = 0.45
const DOG_SPEED: float = 155.0
const DOG_AGGRO_RANGE: float = 130.0
const PIGEON_BOMB_SEC: float = 2.2                # голубь-бомбардир
const PIGEON_BOMB_DAMAGE: float = 14.0
const PIGEON_BOMB_RADIUS: float = 34.0
const PIGEON_RANGE: float = 150.0
const PIGEON_SPEED: float = 95.0
const PIGEON_ORBIT_DIST: float = 32.0
const MINE_DAMAGE: float = 32.0                   # мина из крышек
const MINE_RADIUS: float = 44.0
const MINE_TRIGGER_DIST: float = 20.0
const MINE_SPAWN_MIN_DIST: float = 40.0
const MINE_SPAWN_MAX_DIST: float = 130.0
const LAMP_SLOW_FACTOR: float = 0.45              # лампа-вонялка
const PET_LEASH_DIST: float = 38.0                # где ходит рядом с игроком без цели

# --- Перки (GDD) ---
const PERK_CAFFEINE_ATTACK_SPEED_MULT: float = 1.5
const PERK_CAFFEINE_MAX_HP_MULT: float = 0.8
const PERK_TOXIC_POSITIVITY_DAMAGE: float = 10.0
const PERK_TOXIC_POSITIVITY_RADIUS: float = 30.0
const PERK_LOOT_GOBLIN_PICKUP_RADIUS_MULT: float = 2.0
const PERK_LOOT_GOBLIN_MOVE_SPEED_MULT: float = 0.9
const PERK_CRINGE_AURA_SLOW_FACTOR: float = 0.3
const PERK_CRINGE_AURA_RADIUS: float = 80.0
const PERK_SECOND_WIND_CHANCE: float = 0.2
const PERK_SECOND_WIND_DAMAGE: float = 15.0
const PERK_SECOND_WIND_RADIUS: float = 100.0
const PERK_DOUBLE_SHOT_EXTRA_PROJECTILES: int = 1
const PERK_DOUBLE_SHOT_DAMAGE_MULT: float = 0.85
const PERK_SPEED_BONUS: float = 0.1
const PERK_SPEED_MAX_STACKS: int = 5
const PERK_REGEN_HP: float = 1.0
const PERK_REGEN_INTERVAL_SEC: float = 5.0

# --- Мета-прогрессия, цены в ₽ (GDD, пост-MVP) ---
const SHOP_PRICES: Dictionary = {
	&"max_hp_10": 50,
	&"move_speed_5": 40,
	&"start_weapon_level": 100,
	&"unlock_weapon": 150,
	&"reroll": 80,
}


# --- Персонажи кладбища (Шаг 8). mods/fx - как у предметов; weapon - стартовое оружие (пусто - выбор в начале).
# unlock: open | kills | coins | deaths | wins (накопительные счётчики профиля).
const CHARACTER_ORDER: Array[StringName] = [&"hobo", &"squid", &"clerk", &"janitor", &"uncle_vitya", &"blogger", &"granny", &"courier", &"pigeon", &"punk", &"shawarma", &"guard", &"student", &"plumber", &"dacha", &"skater", &"slime"]
const CHARACTERS: Dictionary = {
	&"hobo": {"weapon": &"", "mods": {&"max_hp": 4.0, &"pickup": 15.0}, "unlock": &"open", "need": 0, "tint": Color(1.0, 1.0, 1.0), "hat": &"ushanka"},
	&"squid": {"weapon": &"mop", "mods": {&"damage": 15.0, &"speed": 8.0, &"max_hp": -3.0}, "unlock": &"open", "need": 0, "tint": Color(0.65, 0.85, 1.0), "hat": &"cigarette"},
	&"clerk": {"weapon": &"slingshot", "mods": {&"crit": 12.0, &"attack_speed": 10.0, &"max_hp": -4.0, &"armor": -1.0}, "unlock": &"open", "need": 0, "tint": Color(0.85, 0.85, 1.0), "hat": &"dirty_glasses"},
	&"janitor": {"weapon": &"sock", "mods": {&"armor": 3.0, &"max_hp": 6.0, &"speed": -8.0, &"pickup": 20.0}, "unlock": &"kills", "need": 300, "tint": Color(1.0, 0.85, 0.6), "hat": &"helmet"},
	&"uncle_vitya": {"weapon": &"lighter", "mods": {&"dodge": 12.0, &"damage": -8.0}, "fx": {&"burn": 20.0}, "unlock": &"deaths", "need": 1, "tint": Color(1.0, 0.7, 0.7), "hat": &"vodka"},
	&"blogger": {"weapon": &"laser_pointer", "mods": {&"damage": -12.0, &"crit": 8.0}, "fx": {&"coin_bonus": 40.0}, "unlock": &"coins", "need": 600, "tint": Color(0.8, 1.0, 0.8), "hat": &"gold_tooth"},
	&"granny": {"weapon": &"slipper", "mods": {&"max_hp": 6.0, &"armor": 2.0, &"speed": -10.0}, "fx": {&"thorns": 3.0}, "unlock": &"kills", "need": 600, "tint": Color(1, 1, 1), "hat": &"scarf"},
	&"courier": {"weapon": &"spray_can", "mods": {&"speed": 20.0, &"attack_speed": 8.0, &"max_hp": -4.0}, "fx": {&"coin_bonus": 25.0}, "unlock": &"coins", "need": 1000, "tint": Color(1, 1, 1), "hat": &"bottle_cap"},
	&"pigeon": {"weapon": &"condensed_milk", "mods": {&"dodge": 10.0, &"speed": 10.0, &"max_hp": -5.0}, "fx": {&"lifesteal": 5.0}, "unlock": &"deaths", "need": 5, "tint": Color(1, 1, 1), "hat": &"dried_fish"},
	&"punk": {"weapon": &"frying_pan", "mods": {&"damage": 10.0, &"armor": -1.0, &"speed": 6.0}, "fx": {&"pets": 1.0}, "unlock": &"wins", "need": 1, "tint": Color(1, 1, 1), "hat": &"crowbar"},
	&"shawarma": {"weapon": &"rolling_pin", "mods": {&"max_hp": 8.0, &"damage": -5.0, &"armor": 1.0}, "fx": {&"coin_bonus": 15.0}, "unlock": &"coins", "need": 2500, "tint": Color(1, 1, 1), "hat": &"shawarma"},
	&"guard": {"weapon": &"mosin", "mods": {&"armor": 2.0, &"crit": 10.0, &"speed": -10.0}, "unlock": &"kills", "need": 2000, "tint": Color(1, 1, 1), "hat": &"binoculars"},
	&"student": {"weapon": &"bottle", "mods": {&"attack_speed": 20.0, &"max_hp": -4.0, &"speed": 8.0}, "unlock": &"deaths", "need": 10, "tint": Color(1, 1, 1), "hat": &"energy_can"},
	&"plumber": {"weapon": &"pipe_gun", "mods": {&"damage": 8.0, &"armor": 1.0, &"speed": -5.0}, "unlock": &"kills", "need": 3500, "tint": Color(1, 1, 1), "hat": &"pot"},
	&"dacha": {"weapon": &"rotten_cheese", "mods": {&"max_hp": 10.0, &"speed": -12.0, &"pickup": 30.0}, "unlock": &"coins", "need": 4000, "tint": Color(1, 1, 1), "hat": &"plastic_bag"},
	&"skater": {"weapon": &"crossbow", "mods": {&"speed": 25.0, &"dodge": 10.0, &"max_hp": -5.0}, "unlock": &"deaths", "need": 15, "tint": Color(1, 1, 1), "hat": &"skateboard"},
	&"slime": {"weapon": &"plunger", "mods": {&"max_hp": 6.0, &"damage": 6.0, &"speed": -6.0, &"pickup": 10.0}, "fx": {&"thorns": 2.0}, "unlock": &"kills", "need": 5000, "tint": Color(1, 1, 1), "hat": &"rubber_boot"},
}
