extends Node
## Текущее состояние забега. Autoload: GameState.

var hp: float = 0.0
var max_hp: float = 0.0
var xp: int = 0
var xp_to_next: int = 0
var level: int = 1
var coins: int = 0
var kills: int = 0
var wave: int = 0
var wave_time_left: float = 0.0   # обратный отсчёт текущей волны (как в Brotato)
var wave_kind: StringName = &"normal"  # normal / elite / horde / boss
var wave_note: String = ""       # подпись для баннера (имена боссов и т.п.)
var special_waves: Dictionary = {}  # номер волны -> elite/horde/boss (бросается в начале забега)
var time: float = 0.0
var run_active: bool = false

# Перки и производные статы (пересчитываются в _recompute_perk_stats()).
var perk_stacks: Dictionary[StringName, int] = {}
var move_speed_mult: float = 1.0
var pickup_radius_mult: float = 1.0
var extra_projectiles: int = 0
var projectile_damage_mult: float = 1.0
var regen_hp: float = 0.0


func _ready() -> void:
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_died.connect(_on_player_died)
	EventBus.xp_collected.connect(_on_xp_collected)


## Сбросить состояние перед новым забегом.
func reset_run() -> void:
	max_hp = Balance.PLAYER_MAX_HP
	hp = max_hp
	xp = 0
	xp_to_next = Balance.XP_FIRST_LEVEL
	level = 1
	coins = 0
	kills = 0
	wave = 0
	wave_time_left = 0.0
	wave_kind = &"normal"
	wave_note = ""
	special_waves = {}
	time = 0.0
	run_active = true
	perk_stacks.clear()
	_recompute_perk_stats()
	EventBus.run_started.emit()


func get_perk_stacks(perk_id: StringName) -> int:
	return perk_stacks.get(perk_id, 0)


## Применить выбранный перк (+1 стак) и пересчитать статы.
func apply_perk(perk_id: StringName) -> void:
	perk_stacks[perk_id] = get_perk_stacks(perk_id) + 1
	_recompute_perk_stats()
	EventBus.perk_chosen.emit(perk_id)


func _recompute_perk_stats() -> void:
	var speed: int = get_perk_stacks(PerkLibrary.SPEED)
	var goblin: int = get_perk_stacks(PerkLibrary.LOOT_GOBLIN)
	var shots: int = get_perk_stacks(PerkLibrary.DOUBLE_SHOT)
	var regen: int = get_perk_stacks(PerkLibrary.REGEN)
	move_speed_mult = (1.0 + Balance.PERK_SPEED_BONUS * speed) * pow(Balance.PERK_LOOT_GOBLIN_MOVE_SPEED_MULT, goblin)
	pickup_radius_mult = 1.0 + (Balance.PERK_LOOT_GOBLIN_PICKUP_RADIUS_MULT - 1.0) * goblin
	extra_projectiles = Balance.PERK_DOUBLE_SHOT_EXTRA_PROJECTILES * shots
	projectile_damage_mult = pow(Balance.PERK_DOUBLE_SHOT_DAMAGE_MULT, shots)
	regen_hp = Balance.PERK_REGEN_HP * regen


func _on_enemy_died(_enemy_id: StringName, _position: Vector2) -> void:
	kills += 1


func _on_xp_collected(amount: int) -> void:
	if not run_active:
		return
	xp += amount
	while xp >= xp_to_next:
		xp -= xp_to_next
		level += 1
		xp_to_next = ceili(xp_to_next * Balance.XP_LEVEL_GROWTH)
		EventBus.player_leveled_up.emit(level)


func _on_player_died() -> void:
	run_active = false
	EventBus.run_ended.emit()
