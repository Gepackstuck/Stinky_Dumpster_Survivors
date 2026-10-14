extends Node
## Все балансные числа игры (источник: GDD.md, CONVENTIONS.md, TASKS.md).
## Autoload: Balance. Числа не хардкодить в сценах — брать отсюда.

# --- Арена (Шаг 1) ---
const ARENA_SIZE: float = 2000.0        # квадрат ARENA_SIZE x ARENA_SIZE, старт в центре

# --- Игрок (Шаг 1; в GDD чисел нет — стартовые значения) ---
const PLAYER_MOVE_SPEED: float = 100.0
const PLAYER_MAX_HP: float = 100.0
const PLAYER_HURT_COOLDOWN_SEC: float = 0.5  # неуязвимость после попадания

# --- Спавн врагов (Шаг 1: простой хардкод-спавнер) ---
const ENEMY_TARGET_COUNT: int = 20
const ENEMY_SPAWN_RADIUS_MIN: float = 200.0  # за пределами экрана (половина диагонали ~184)
const ENEMY_SPAWN_RADIUS_MAX: float = 240.0
const ENEMY_RESPAWN_INTERVAL_SEC: float = 1.0

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

# --- Предметы ---
# «Обосранные портки Supreme»: шанс, что враг в контакте охуевает от вони и не подходит (реализация — шаг с предметами).
const ITEM_STINKY_PANTS_REPEL_CHANCE: float = 0.15

# --- Забег ---
const RUN_DURATION_SEC: float = 900.0   # 15 минут до победы (GDD)
const WAVE_INTERVAL_SEC: float = 30.0
const BOSS_INTERVAL_SEC: float = 300.0  # босс каждые 5 минут
const BOSS_TIMES_SEC: Array[float] = [300.0, 600.0, 900.0]
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
	&"lighter": {"damage": 5.0, "cooldown": 0.4, "burn_dps": 2.0, "burn_duration": 3.0},
	&"sock": {"damage": 12.0, "cooldown": 1.0, "radius": 60.0},
	&"slingshot": {"damage": 8.0, "cooldown": 0.6, "ricochets": 2},
	&"laser_pointer": {"damage": 4.0, "cooldown": 0.15},
	&"mop": {"damage": 10.0, "cooldown": 0.9, "knockback": 80.0},
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
