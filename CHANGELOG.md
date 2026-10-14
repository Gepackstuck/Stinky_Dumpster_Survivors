# CHANGELOG

Формат: [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/).
Версии: SemVer.

## [Unreleased]

### Added

- MP1 Core Loop (Шаг 1): игрок (`player.tscn`, `player_controller.gd`) с движением WASD/стрелки
  и `Camera2D` (zoom 1, лимиты по арене 2000x2000).
- Враг `enemy_base.tscn` / `enemy_base.gd`: идёт к игроку, бьёт при контакте.
- Спавнер `spawner.gd`: держит 20 врагов вокруг игрока, пополняет погибших раз в секунду.
- Автоатака `weapon_base.gd` + `projectile.tscn`: стреляет по ближайшему врагу (статы `lighter`).
- Компоненты `HealthComponent`, `HurtboxComponent`, `HitboxComponent`.
- `PoolManager` реализован (пулы врагов и снарядов), `GameState.reset_run()`.
- `PlaceholderSprites` — программные заглушки спрайтов (игрок, враг, снаряд).
- Балансные числа Шага 1 в `Balance` (арена, игрок, спавн, снаряд).
- Имена слоёв физики 2D в `project.godot`.
- MP0 Bootstrap (Шаг 0): `project.godot` под Godot 4.7.2 / Forward+ (Metal на macOS),
  viewport 320×180, stretch `viewport` + `keep` + integer scale, окно 1280×720,
  фильтр текстур `nearest`, pixel snap 2D.
- Input map: `move_up` / `move_down` / `move_left` / `move_right` (WASD + стрелки).
- Autoloads-заглушки: `EventBus`, `GameState`, `Balance` (числа из GDD),
  `AudioManager`, `PoolManager` в `scripts/autoload/`.
- `scenes/levels/main.tscn` (ColorRect 320×180, `#E8E8E8`) — main scene проекта.
- Структура папок по `CONVENTIONS.md` (`.gitkeep` в пустых).
- `.gitignore` расширен до шаблона Godot 4 (+ macOS, mono, export credentials).
- AGENTS.md, MVP_PLAN.md, GDD.md, ART_STYLE.md, CONVENTIONS.md,
  TASKS.md, IDEAS.md, README.md.

### Changed

- Версия Godot приведена к единой: **4.7.2** во всех документах.
- TASKS.md переупорядочен: игрок и камера идут до спавнера врагов.
- В GDD.md удалены ошибочные иероглифы из таблицы врагов.
- Добавлен раздел «Definition of Done» в AGENTS.md.

### Fixed

- Расхождение версий Godot между файлами.
- Отсутствие дропа валюты в GDD (было только XP).