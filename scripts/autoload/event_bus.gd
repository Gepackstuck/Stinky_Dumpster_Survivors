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

# --- Враги ---
@warning_ignore("unused_signal")
signal enemy_died(enemy_id: StringName, position: Vector2)

# --- Подбираемое ---
@warning_ignore("unused_signal")
signal xp_collected(amount: int)
@warning_ignore("unused_signal")
signal coin_collected(amount: int)

# --- Забег ---
@warning_ignore("unused_signal")
signal wave_started(wave_number: int)
@warning_ignore("unused_signal")
signal run_started
@warning_ignore("unused_signal")
signal run_ended
