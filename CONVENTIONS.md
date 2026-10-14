# Соглашения по коду и проекту

## Версия Godot

**Godot 4.7.2** или новее. Если апгрейдишь версию — обнови её синхронно
в `AGENTS.md`, `README.md` и этом файле.

## Язык

GDScript. Всегда с типами. Никаких `Variant` без нужды.

## Структура папок

```text
scenes/
  player/
  enemies/
  weapons/
  ui/
  levels/
scripts/
  autoload/       — синглтоны (EventBus, GameState, Balance, AudioManager, PoolManager)
  components/     — переиспользуемые ноды (HealthComponent, HurtboxComponent, ...)
  systems/        — менеджеры (Spawner, WaveManager, PoolManager)
  player/ enemies/ weapons/ levels/ — скрипты сущностей, зеркалят scenes/
assets/
  sprites/
  sfx/
  music/
data/             — .tres ресурсы баланса (если перейдём с .gd на .tres)
shaders/          — .gdshader
addons/           — только по явному разрешению
tools/            — скрипты генерации placeholder-спрайтов
```

## Autoloads (синглтоны) — ровно 5, не больше

| Имя | Ответственность |
|---|---|
| `EventBus` | Глобальные сигналы (`enemy_died`, `player_hit`, `wave_started`, ...) |
| `GameState` | Текущее состояние забега (HP, XP, level, wave, time, run_active) |
| `Balance` | Все числа геймплея в одном месте (скорости, урон, HP, дропы) |
| `AudioManager` | Воспроизведение sfx/music, пул `AudioStreamPlayer` |
| `PoolManager` | Пулы для снарядов, врагов, XP-пикселей |

**Не создавать новые autoloads** без явного разрешения. Локальные менеджеры —
обычные ноды в сцене.

## Naming

| Что | Стиль | Пример |
|---|---|---|
| Классы | `PascalCase` | `PlayerController`, `EnemySquidGopnik` |
| Файлы сцен/скриптов | `snake_case` | `player_controller.gd`, `enemy_squid_gopnik.tscn` |
| Переменные/функции | `snake_case` | `move_speed`, `take_damage()` |
| Константы | `UPPER_SNAKE_CASE` | `MAX_ENEMIES_ON_SCREEN` |
| Приватные | `_` префикс | `_internal_counter`, `_on_enemy_died()` |
| Сигналы | past tense | `enemy_died`, `player_leveled_up` |

## Компонентный подход

Игрок и враги — это `CharacterBody2D` + набор компонентов (дочерних нод):

- `HealthComponent` — HP, получение урона, сигнал `died`.
- `HurtboxComponent` (`Area2D`) — область, куда прилетает урон.
- `HitboxComponent` (`Area2D`) — область, которой наносим урон.
- `MovementComponent` — движение к цели, скорость.
- `AttackComponent` — таймер атаки, спавн снаряда.

Компоненты общаются **только через сигналы** и не знают о своих владельцах
напрямую.

## Физика и слои коллизий

- Игрок и враги: `CharacterBody2D`.
- Снаряды, pickup, hitbox/hurtbox: `Area2D`.
- Стены: `StaticBody2D`.

| Layer | Имя | Кто использует |
|---|---|---|
| 1 | `player` | Игрок |
| 2 | `enemy` | Враги |
| 3 | `player_projectile` | Снаряды игрока |
| 4 | `enemy_projectile` | Снаряды врагов |
| 5 | `pickup` | XP, монеты, лут |
| 6 | `wall` | Стены, препятствия |

Столкновения настраиваются через `collision_layer` / `collision_mask`, не через
проверки в коде.

## Производительность

- Все снаряды и враги — **через пулы** (`PoolManager`).
- Никаких `await` в `_process` / `_physics_process`.
- Жёсткий лимит врагов на экране: **500** (сверх — не спавнить).
- `_physics_process` для движения и коллизий, `_process` для визуала.
- Никаких аллокаций (`new`, массивы) в hot-path (каждый кадр).

## Обработка ошибок

- Проверять `get_node()` / `$Path` через `has_node()` если путь динамический.
- Пропавшие ресурсы (спрайты, звуки) — `push_warning()`, не краш.
- Сигналы на «мёртвые» ноды — `is_instance_valid()` перед вызовом.

## Git

- Conventional Commits (`feat:`, `fix:`, `art:`, `refactor:`, `docs:`).
- Ветки: `main` (стабильно), `dev` (текущая работа).
- `.gitignore` — стандартный для Godot 4 (включая `.godot/`, `*.import`).

## Тестирование

- После каждого коммита: `godot --headless --quit --path .` — проверка парсинга.
- Никаких автотестов на старте. GUT добавим, если понадобится.
- Ручная проверка описана в `TASKS.md` для каждой задачи.

## Ввод
Всё в игре управляется в первую очередь с клавиатуры (WASD и стрелки), мышь — запасной вариант. Любой новый экран обязан работать без мыши и быть готов к геймпаду и Steam Deck (только InputMap-действия, никакой логики «только клик»).
