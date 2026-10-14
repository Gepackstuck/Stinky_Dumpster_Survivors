# CHANGELOG

Формат: [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/).
Версии: SemVer.

## [Unreleased]

### Added

- Граница арены: ряд проволоки (8 видов: колючая, в говне, егоза, кишки/глаза, тряпки, слизь, под током, горящая — случайно каждый забег; ток и огонь бьют игрока) + редкие декорации за ней (34 вида) на тёмной земле; невидимые стены.
- Пол: земля двух тонов + случайные декали (~50 видов) в каждом забеге (`ground.gd`).
- Выбор перка клавишами A/D/стрелки + пробел, подсказка на экране.
- MP2 Живой прототип (Шаг 2): XP-пиксели с врагов (`xp_pickup`, `PickupSpawner`), магнит игрока,
  уровни (порог 5, далее ×1.5), экран выбора перка (3 карточки, пауза, клавиши 1/2/3),
  4 перка (Скорость, Регенерация, Двойной выстрел, Лут-Гоблин; `PerkLibrary`), HUD (HP/XP/уровень/убийства),
  экран смерти со случайными фразами (`FlavorText`) и рестартом «Ещё раз».
- Рисованный арт в стиле «Кислотный Кринж»: игрок, враг, снаряд, XP, пол, UI, шрифт, тема; генератор `tools/gen_art.py`.
- `FrameAnimatorComponent` (покадровая анимация 8 fps), перк-статы в `GameState`, `HealthComponent.heal()`.
- Идея предмета «Обосранные портки Supreme» записана в бэклог, число шанса в `Balance`.
- MP1 Core Loop (Шаг 1): игрок (`player.tscn`, `player_controller.gd`) с движением WASD/стрелки
  и `Camera2D` (zoom 1, лимиты по арене 2000x2000).
- Враг `enemy_base.tscn` / `enemy_base.gd`: идёт к игроку, бьёт при контакте.
- Спавнер `spawner.gd`: держит 20 врагов вокруг игрока, пополняет погибших раз в секунду.
- Автоатака `weapon_base.gd` + `projectile.tscn`: стреляет по ближайшему врагу (статы `lighter`).
- Компоненты `HealthComponent`, `HurtboxComponent`, `HitboxComponent`.
- `PoolManager` реализован (пулы врагов и снарядов), `GameState.reset_run()`.
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