extends Node
## Глобальная шина событий. Только сигналы, никакой логики.
## Autoload: EventBus. См. CONVENTIONS.md.
## TODO(MP1+): добавлять сигналы по мере появления систем.

# --- Игрок ---
@warning_ignore("unused_signal")
signal player_hit(damage: float)
@warning_ignore("unused_signal")
signal player_died
@warning_ignore("unused_signal")
signal player_leveled_up(new_level: int)
@warning_ignore("unused_signal")
signal perk_chosen(perk_id: StringName)

@warning_ignore("unused_signal")
signal dash_state(charges: int, max_charges: int, recharge: float)   # рывок: заряды и прогресс перезарядки 0..1
@warning_ignore("unused_signal")
signal dash_used(at: Vector2)
@warning_ignore("unused_signal")
signal ult_state(charge: float)              # ульта: заряд 0..1
@warning_ignore("unused_signal")
signal ult_used(kind: StringName)
@warning_ignore("unused_signal")
signal parried(at: Vector2)
@warning_ignore("unused_signal")
signal streak_changed(tier: int, bonus: float, broken: bool)   # серия без урона: ступень, + доля говна; broken - сбили

@warning_ignore("unused_signal")
signal weapon_fired(sfx: StringName)      # оружие выстрелило/махнуло (звук: shoot, swing, explosion)
@warning_ignore("unused_signal")
signal shake_requested(amount: float)      # тряска экрана (взрыв, удар босса); игрок решает, учитывая настройки
@warning_ignore("unused_signal")
signal telegraph_shown                     # враг/модификатор показал зону удара (звук-предупреждение)

# --- Враги ---
@warning_ignore("unused_signal")
signal enemy_died(enemy_id: StringName, position: Vector2)

@warning_ignore("unused_signal")
signal xp_drop_requested(at: Vector2, value: int)   # враг просит уронить XP (обжора)

@warning_ignore("unused_signal")
signal bin_destroyed(at: Vector2)                   # бак разбит: на его месте остаётся мусор до конца забега

@warning_ignore("unused_signal")
signal item_combo(combo_id: StringName)              # два предмета слились в комбо
@warning_ignore("unused_signal")
signal items_changed                               # рюкзак предметов поменялся
signal weapon_evolved(weapon_id: StringName)       # оружие IV тира эволюционировало
@warning_ignore("unused_signal")
signal weapons_changed                              # набор оружия игрока поменялся (купил, скрестил, переработал)

# --- Подбираемое ---
@warning_ignore("unused_signal")
signal xp_collected(amount: int)
@warning_ignore("unused_signal")
signal coin_collected(amount: int)

# --- Забег ---
@warning_ignore("unused_signal")
signal wave_started(wave_number: int)
@warning_ignore("unused_signal")
signal boss_spawned(boss_id: StringName)
@warning_ignore("unused_signal")
signal wave_ended(wave_number: int)        # время волны вышло, враги убраны, материалы собраны
@warning_ignore("unused_signal")
@warning_ignore("unused_signal")
signal next_wave_requested                 # игрок нажал «Дальше» на экране между волнами
@warning_ignore("unused_signal")
signal run_won                             # убиты боссы 20-й волны
@warning_ignore("unused_signal")
signal endless_requested                   # после победы игрок выбрал «бесконечно»
@warning_ignore("unused_signal")
signal pile_stepped                        # герой вступил в кучу-лотерею
@warning_ignore("unused_signal")
signal roulette_requested                  # крутим рулетку модификатора (перед волной)
@warning_ignore("unused_signal")
signal roulette_done(mod: StringName)      # рулетка остановилась
@warning_ignore("unused_signal")
signal run_started
@warning_ignore("unused_signal")
signal run_ended
signal duel_round_over                       # Н31: игрок прошёл все волны раунда битвы героев
