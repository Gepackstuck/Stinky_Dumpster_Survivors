extends Node
## Все балансные числа игры (источник: GDD.md, CONVENTIONS.md, TASKS.md).
## Autoload: Balance. Числа не хардкодить в сценах — брать отсюда.

# --- Арена (Шаг 1) ---
const ARENA_SIZE: float = 520.0        # квадрат ARENA_SIZE x ARENA_SIZE, старт в центре

# --- Игрок (Шаг 1; в GDD чисел нет — стартовые значения) ---
const PLAYER_MOVE_SPEED: float = 100.0
const PLAYER_MAX_HP: float = 40.0
const PLAYER_HURT_COOLDOWN_SEC: float = 0.5  # неуязвимость после попадания

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
const WAVE_COUNT: int = 20
const WAVE_DURATION_FIRST_SEC: float = 20.0
const WAVE_DURATION_STEP_SEC: float = 5.0
const WAVE_DURATION_MAX_SEC: float = 60.0
const WAVE_DURATION_FINAL_SEC: float = 90.0       # 20-я волна (боссы)
const WAVE_GROUPS_BASE: int = 9                   # групп врагов за волну = BASE + номер волны
const WAVE_GROUP_SIZE_BASE: int = 5               # размер группы = BASE + волна/4 (±1)
const WAVE_GROUP_SIZE_WAVES_PER_STEP: int = 2
const WAVE_FIRST_GROUP_SEC: float = 0.5
const WAVE_SPAWN_END_FRACTION: float = 0.85       # последняя группа не позже 85% времени волны
const SPAWN_MARKER_SEC: float = 1.0               # красный крест за секунду до появления
const SPAWN_MIN_DISTANCE_FROM_PLAYER: float = 120.0
const SPAWN_ARENA_MARGIN: float = 40.0
const SPAWN_GROUP_SPREAD: float = 28.0
const SPECIAL_WAVE_WINDOWS: Array = [[11, 12], [14, 15], [17, 18]]  # в каждом окне — элита или орда (последнее всегда элита)
const ELITE_CHANCE: float = 0.6
const HORDE_GROUP_MULT: float = 2.0
const ELITE_SPAWN_SEC: float = 2.0
const FINAL_BOSS_SPAWN_SEC: float = 1.5
const WAVE_END_COLLECT_SEC: float = 1.5           # время на авто-сбор материалов после волны
const WAVE_HP_GROWTH: float = 0.18          # +15% HP за каждую волну после первой
const WAVE_DAMAGE_GROWTH: float = 0.10       # +10% урона врагов за волну
const WAVE_SPEED_GROWTH: float = 0.03        # +3% скорости за волну
const WAVE_SPEED_MAX_MULT: float = 1.4
const WAVE_ENEMY_UNLOCK: Dictionary = {     # с какой волны тип может выпасть
	&"squid_gopnik": 1, &"microbe": 2, &"npc_bot": 3, &"cockroach": 4, &"wifi_ghost": 6,
}
const WAVE_ENEMY_WEIGHTS: Dictionary = {    # вес в взвешенном рандоме
	&"squid_gopnik": 10, &"microbe": 6, &"npc_bot": 6, &"cockroach": 4, &"wifi_ghost": 3,
}
const FINAL_BOSS_POOL: Array[StringName] = [&"boss_zakhar", &"boss_minion"]  # боссы 20-й волны: один или оба
const ELITE_ID: StringName = &"boss_mega_hamster"                           # элита на волнах 11–12, 14–15, 17–18
const BOSS_NAMES: Dictionary = {
	&"boss_mega_hamster": "МЕГА-ХОМЯК",
	&"boss_zakhar": "ЗАХАР ИЗ МОРКОВСКА",
	&"boss_minion": "МИНЬОН-ЕБАНАТ",
}

# --- Боссы: Захар из Морковска ---
const ZAKHAR_ATTACK_INTERVAL_SEC: float = 2.2   # пауза между атаками (в ярости ×0.65 — на <50% HP)
const ZAKHAR_CARROT_DAMAGE: float = 8.0
const ZAKHAR_CARROT_SPEED: float = 140.0
const ZAKHAR_CARROT_FAN_DEG: float = 18.0       # в ярости — веер из трёх
const ZAKHAR_FART_RADIUS: float = 26.0
const ZAKHAR_FART_DAMAGE: float = 4.0           # за каждый удар (с кулдауном неуязвимости игрока)
const ZAKHAR_FART_LIFETIME_SEC: float = 3.5
const ZAKHAR_KICK_RANGE: float = 70.0
const ZAKHAR_KICK_WINDUP_SEC: float = 0.45      # замах — мигает жёлтым
const ZAKHAR_KICK_SPEED: float = 280.0
const ZAKHAR_KICK_DURATION_SEC: float = 0.25

# --- Боссы: Миньон-ебанат ---
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
const MINION_STRAFE_SPEED: float = 45.0         # «ебанутые» дёрганья в стороны
const PROJECTILE_BOSS_LIFETIME_SEC: float = 3.0

# --- Отдача от попаданий ---
const ENEMY_KNOCKBACK_SPEED: float = 120.0   # импульс, который враг получает от попадания
const KNOCKBACK_DECAY: float = 600.0         # px/с² — как быстро гаснет отдача
const PLAYER_HIT_SHAKE: float = 4.0          # px — тряска камеры при уроне по игроку
const SHAKE_DECAY: float = 28.0              # px/с — затухание тряски

# --- Арена и камера ---
const ARENA_BORDER_THICKNESS: float = 64.0  # проволока (16) + зона редких декораций (48) за краем арены
const BORDER_DECOR_CHANCE: float = 0.3   # шанс декорации на каждые 48 px границы
const WIRE_SHOCK_DAMAGE: float = 5.0     # удар током/огнём от проволоки
const ENEMY_PLAYER_MIN_DISTANCE: float = 10.0  # ближе враг не подходит — игрок его расталкивает
const GROUND_DECAL_AREA_PX2: float = 9000.0  # одна декаль пола на столько px² арены
const CAMERA_ZOOM: float = 1.0  # только целое: дробный зум рвёт пиксели (виден шум); «дальше» = больше viewport

# --- Предметы ---
# «Обосранные портки Supreme»: шанс, что враг в контакте охуевает от вони и не подходит (реализация — шаг с предметами).
const ITEM_STINKY_PANTS_REPEL_CHANCE: float = 0.15

# --- Забег ---
const MAX_ENEMIES_ON_SCREEN: int = 500  # CONVENTIONS.md

# --- XP / уровни ---
const XP_FIRST_LEVEL: int = 5           # порог первого уровня (TASKS.md, Шаг 2)
const XP_LEVEL_GROWTH: float = 1.5      # каждый следующий порог +50%
const LEVEL_UP_CHOICES: int = 3

# --- Враги: hp, damage, speed, xp, coins (GDD) ---
const ENEMIES: Dictionary = {
	&"squid_gopnik": {"hp": 20.0, "damage": 5.0, "speed": 60.0, "xp": 2, "coins": 1},
	&"microbe": {"hp": 30.0, "damage": 3.0, "speed": 40.0, "xp": 3, "coins": 1},
	&"npc_bot": {"hp": 15.0, "damage": 4.0, "speed": 50.0, "xp": 2, "coins": 1},
	&"cockroach": {"hp": 5.0, "damage": 10.0, "speed": 140.0, "xp": 1, "coins": 2},
	&"wifi_ghost": {"hp": 25.0, "damage": 6.0, "speed": 70.0, "xp": 4, "coins": 2},
	# Босс-заглушка Шага 3 (особое поведение — позже); radius — размер тела в px.
	&"boss_mega_hamster": {"hp": 600.0, "damage": 12.0, "speed": 35.0, "xp": 30, "coins": 20, "radius": 16.0},
	&"boss_zakhar": {"hp": 900.0, "damage": 10.0, "speed": 45.0, "xp": 40, "coins": 25, "radius": 14.0,
			"brain": "res://scripts/enemies/brains/boss_zakhar_brain.gd"},
	&"boss_minion": {"hp": 700.0, "damage": 8.0, "speed": 70.0, "xp": 40, "coins": 25, "radius": 11.0,
			"brain": "res://scripts/enemies/brains/boss_minion_brain.gd"},
}

# --- Боссы (GDD) ---
const BOSS_MEGA_HAMSTER_SPAWN_SEC: float = 300.0
const BOSS_MEGA_HAMSTER_SPLIT_COUNT: int = 8  # микробов при смерти
const BOSS_UNCLE_VITYA_SPAWN_SEC: float = 600.0
const BOSS_UNCLE_VITYA_AURA_RADIUS: float = 100.0
const BOSS_UNCLE_VITYA_AURA_DPS: float = 2.0
const BOSS_BLUE_WHALE_SPAWN_SEC: float = 900.0
const BOSS_BLUE_WHALE_TEARS_COUNT: int = 5  # веер снарядов

# --- Оружие: damage, cooldown (GDD) ---
const WEAPONS: Dictionary = {
	&"lighter": {"damage": 9.0, "cooldown": 0.35, "burn_dps": 2.0, "burn_duration": 3.0},
	&"sock": {"damage": 12.0, "cooldown": 1.0, "radius": 60.0},
	&"slingshot": {"damage": 8.0, "cooldown": 0.6, "ricochets": 2, "ricochet_range": 110.0},
	&"laser_pointer": {"damage": 4.0, "cooldown": 0.15},
	&"mop": {"damage": 14.0, "cooldown": 0.8, "knockback": 240.0, "reach": 52.0, "arc_deg": 140.0},
	&"slipper": {"damage": 25.0, "cooldown": 2.5, "aoe_radius": 40.0},
	&"condensed_milk": {"damage": 3.0, "cooldown": 0.5, "slow_factor": 0.5, "slow_duration": 2.0},
}

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
