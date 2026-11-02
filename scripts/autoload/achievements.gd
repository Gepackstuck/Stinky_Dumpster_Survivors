extends Node
## Достижения. Autoload: Achievements. Каждое - стабильный id (под Steam: id = API name), название и условие.
## Проверки по событиям EventBus; открытые хранятся в Profile.achievements. Всплывашка «ДОСТИЖЕНИЕ!» сверху экрана.
## Steam: когда будет подключён GodotSteam - в _unlock() добавить Steam.setAchievement(id) + storeStats().
## Список на согласование: docs/ACHIEVEMENTS.md.

const CUP: Texture2D = preload("res://assets/ui/achievement_cup.png")
const TOAST_SEC: float = 2.6

## Простые достижения: id -> [название, описание]. Герои × опасность собираются отдельно (hero_<id>_d<n>).
const LIST: Dictionary = {
	&"first_blood": ["ПЕРВАЯ КРОВЬ", "Убей первого врага"],
	&"kills_1000": ["ТЫСЯЧА ТРУПОВ", "1000 убийств за всё время"],
	&"kills_10000": ["ГЕНОЦИД ПОМОЙКИ", "10000 убийств за всё время"],
	&"kills_100000": ["САНИТАР СВАЛКИ", "100000 убийств за всё время"],
	&"deaths_1": ["СДОХ КАК ЛОХ", "Умри в первый раз"],
	&"deaths_10": ["ПОСТОЯННЫЙ КЛИЕНТ", "Умри 10 раз"],
	&"deaths_50": ["ЛОХ ГОДА", "Умри 50 раз"],
	&"deaths_100": ["БЕССМЕРТНЫЙ ЛОХ", "Умри 100 раз. Кладбище тебя любит"],
	&"wave1_death": ["ДАЖЕ НЕ НАЧАЛ", "Умри на первой волне"],
	&"first_win": ["ВЫБРАЛСЯ", "Победи в первый раз"],
	&"win_danger5": ["СО ДНА ДНА", "Победи на опасности ДНО ДНА"],
	&"coins_10000": ["ЗОЛОТАРЬ", "Собери 10000 говна за всё время"],
	&"coins_hoard_999": ["ГОВНОКОПИТЕЛЬ", "Держи 999 говна одновременно"],
	&"boss_hamster": ["ХОМЯК ЛОПНУЛ", "Убей Мега-Хомяка"],
	&"boss_rat_queen": ["ЦАРЕУБИЙЦА", "Убей Королеву крыс"],
	&"boss_zakhar": ["МОРКОВКУ В ЗУБЫ", "Убей Захара из Морковска"],
	&"boss_minion": ["ПСИХ НЕ ПОМОГ", "Убей Миньона-психа"],
	&"boss_whale": ["КИТОБОЙ", "Убей Синего кита"],
	&"boss_roach_king": ["ДУСТ", "Убей Таракана-качка"],
	&"boss_golem": ["ВЫНЕС МУСОР", "Убей Мусорного голема"],
	&"boss_pigeon_papa": ["ОСИРОТИЛ ГОЛУБЕЙ", "Убей Голубиного папу"],
	&"clean_wave": ["НИ ЦАРАПИНЫ", "Пройди волну без урона"],
	&"clean_5": ["СКОЛЬЗКИЙ ТИП", "5 чистых волн за забег"],
	&"clean_all": ["НЕУЛОВИМЫЙ ГОВНЮК", "Победи, не получив урона ни в одной волне"],
	&"streak_60": ["МИНУТА СЛАВЫ", "Продержись 60 секунд без урона"],
	&"combo_any": ["АЛХИМИК ПОМОЙКИ", "Собери любое комбо предметов"],
	&"combo_all": ["ВСЕ РЕЦЕПТЫ", "Открой все 8 комбо"],
	&"cursed_3": ["ВОНЮЧКА СО СТАЖЕМ", "Держи 3 зловонных предмета с помойки одновременно"],
	&"cursed_win": ["ПОБЕДИЛ, ВОНЯЯ", "Победи с 3 зловонными предметами"],
	&"tier4": ["ЛЕГЕНДАРНЫЙ ХЛАМ", "Собери оружие IV тира"],
	&"tickets_50": ["ЛУДОМАН", "Сотри 50 лотерейных билетов"],
	&"ticket_jackpot": ["ДЖЕКПОТ", "Выиграй 100 говна в ГОВНОЛОТО"],
	&"card_10": ["ВИП-БОМЖ", "Заполни карту «Помойка+» 10 раз"],
	&"bottle_kicks_100": ["ФУТБОЛИСТ", "Пни 100 бутылок-гранат"],
	&"bottle_own_goal": ["АВТОГОЛ", "Подорвись своей же бутылкой"],
	&"evolution": ["ЭВОЛЮЦИЯ ГОВНА", "Эволюционируй любое оружие"],
	&"evolution_all": ["ДАРВИН С ПОМОЙКИ", "Открой все эволюции оружия"],
	&"six_same": ["ОДНООБРАЗИЕ", "6 одинаковых оружий в слотах"],
	&"set_6": ["ПОЛНЫЙ КОМПЛЕКТ", "Набор из 6 оружий одного класса"],
	&"dash_1000": ["ПРЫГУН", "1000 рывков за всё время"],
	&"bump_100": ["БАРАН", "Упрись рывком во врага 100 раз"],
	&"killed_truck": ["СБИТ МУСОРОВОЗОМ", "Умри под колёсами мусоровоза"],
	&"killed_lightning": ["ПРОВОДНИК", "Умри от молнии"],
	&"killed_acid": ["РАСТВОРИЛСЯ", "Умри в кислотной луже"],
	&"killed_wire": ["НАСАЖЕН НА ПРОВОЛОКУ", "Умри о колючку на краю арены"],
	&"killed_crate": ["ГУМАНИТАРНАЯ ПОМОЩЬ", "Умри от падающего ящика"],
	&"all_mods": ["ВИДЕЛ ВСЁ", "Пережми все 27 модификаторов волн"],
	&"daily_1": ["ЕЖЕДНЕВНЫЙ ЛОХ", "Сыграй ежедневку"],
	&"daily_10": ["ПО РАСПИСАНИЮ", "Сыграй 10 разных ежедневок"],
	&"endless_20": ["НЕ МОЖЕТ ОСТАНОВИТЬСЯ", "Доживи до 20-й волны в бесконечности"],
	&"endless_30": ["БЕСКОНЕЧНО ВОНЮЧИЙ", "Доживи до 30-й волны в бесконечности"],
	&"no_items_win": ["АСКЕТ", "Победи без единого предмета"],
	&"heroes_all": ["ВСЕХ ОТКОПАЛ", "Открой всех героев"],
	&"medals_hero": ["ЗОЛОТОЙ УНИТАЗ", "Собери все 6 медалей одного героя, до золотого унитаза"],
}

var _queue: Array[String] = []
var _layer: CanvasLayer = null
var _toast: Control = null
var _toast_label: Label = null
var _dashes: int = 0
var _bumps: int = 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build_toast()
	EventBus.enemy_died.connect(_on_enemy_died)
	EventBus.player_died.connect(func() -> void: _on_run_end(false))
	EventBus.run_won.connect(func() -> void: _on_run_end(true))
	EventBus.wave_ended.connect(_on_wave_ended)
	EventBus.item_combo.connect(func(_c: StringName) -> void:
		unlock(&"combo_any")
		if Profile.combos_found.size() >= Balance.ITEM_COMBOS.size():
			unlock(&"combo_all"))
	EventBus.items_changed.connect(_check_items)
	EventBus.weapon_evolved.connect(func(id: StringName) -> void:
		unlock(&"evolution")
		Profile.stat_add(StringName("evo_" + String(id)), 1)
		var all_done: bool = true
		for w: StringName in Balance.WEAPON_EVOLUTIONS:
			if Profile.stat(StringName("evo_" + String(w))) == 0:
				all_done = false
		if all_done:
			unlock(&"evolution_all"))
	EventBus.weapons_changed.connect(_check_weapons)
	EventBus.dash_used.connect(func(_at: Vector2) -> void:
		Profile.stat_add(&"dashes", 1)
		if Profile.stat(&"dashes") >= 1000:
			unlock(&"dash_1000"))
	EventBus.streak_changed.connect(func(_t: int, _b: float, _broken: bool) -> void:
		if GameState.nohit_sec >= 60.0:
			unlock(&"streak_60"))
	EventBus.wave_started.connect(func(_w: int) -> void:
		if GameState.wave_mod != &"":
			Profile.mark_mod_seen(GameState.wave_mod)
			if Profile.mods_seen.size() >= Balance.WAVE_MODS.size():
				unlock(&"all_mods"))


## id достижения «победил за героя на опасности N».
static func hero_id(hero: StringName, danger: int) -> StringName:
	return StringName("hero_%s_d%d" % [hero, danger])


static func title_of(id: StringName) -> String:
	if LIST.has(id):
		return LIST[id][0]
	return "ПОБЕДА: %s" % String(id)


func unlock(id: StringName, title: String = "") -> void:
	if Profile.sandbox or id in Profile.achievements:
		return
	Profile.achievements.append(id)
	Profile.save()
	_queue.append(title if title != "" else title_of(id))
	if not _toast.visible:
		_show_next()


func _on_enemy_died(id: StringName, _at: Vector2) -> void:
	unlock(&"first_blood")
	match id:
		&"boss_mega_hamster": unlock(&"boss_hamster")
		&"boss_rat_queen": unlock(&"boss_rat_queen")
		&"boss_zakhar": unlock(&"boss_zakhar")
		&"boss_minion": unlock(&"boss_minion")
		&"boss_blue_whale": unlock(&"boss_whale")
		&"boss_roach_king": unlock(&"boss_roach_king")
		&"boss_trash_golem": unlock(&"boss_golem")
		&"boss_pigeon_papa": unlock(&"boss_pigeon_papa")
	if GameState.coins >= 999:
		unlock(&"coins_hoard_999")


func _on_wave_ended(_w: int) -> void:
	if GameState.last_clean_bonus > 0:
		unlock(&"clean_wave")
	if GameState.clean_waves >= 5:
		unlock(&"clean_5")
	if GameState.endless and GameState.wave >= 20:
		unlock(&"endless_20")
	if GameState.endless and GameState.wave >= 30:
		unlock(&"endless_30")


func _check_items() -> void:
	var cursed: int = 0
	for id: StringName in GameState.items:
		if ItemLibrary.is_cursed(id):
			cursed += GameState.items[id]
	if cursed >= 3:
		unlock(&"cursed_3")


func _check_weapons() -> void:
	var ids: Dictionary = {}
	for w: Dictionary in GameState.weapons:
		if w["tier"] >= 4:
			unlock(&"tier4")
		ids[w["id"]] = ids.get(w["id"], 0) + 1
	for id: StringName in ids:
		if ids[id] >= 6:
			unlock(&"six_same")
	for c: StringName in WeaponLibrary.class_counts(GameState.weapons):
		if WeaponLibrary.class_counts(GameState.weapons)[c] >= 6:
			unlock(&"set_6")


func _on_run_end(won: bool) -> void:
	if GameState.endless:
		return
	var p: Node = Profile
	if p.total_kills + GameState.kills >= 1000: unlock(&"kills_1000")
	if p.total_kills + GameState.kills >= 10000: unlock(&"kills_10000")
	if p.total_kills + GameState.kills >= 100000: unlock(&"kills_100000")
	if p.total_coins + GameState.run_coins_earned >= 10000: unlock(&"coins_10000")
	if GameState.daily:
		unlock(&"daily_1")
		if p.daily_best.size() >= 10: unlock(&"daily_10")
	if won:
		unlock(&"first_win")
		unlock(hero_id(GameState.character, GameState.danger), "ПОБЕДА ЗА %s: %s" % [CharacterLibrary.title(GameState.character), Balance.DANGER_LEVELS[GameState.danger]["name"]])
		if GameState.danger >= 5: unlock(&"win_danger5")
		if GameState.clean_waves >= Balance.WAVE_COUNT: unlock(&"clean_all")
		if GameState.items.is_empty(): unlock(&"no_items_win")
		var cursed: int = 0
		for id: StringName in GameState.items:
			if ItemLibrary.is_cursed(id): cursed += 1
		if cursed >= 3: unlock(&"cursed_win")
		if Profile.hero_wins.get(GameState.character, []).size() >= Balance.DANGER_LEVELS.size(): unlock(&"medals_hero")
	else:
		var deaths: int = p.deaths + 1
		if deaths >= 1: unlock(&"deaths_1")
		if deaths >= 10: unlock(&"deaths_10")
		if deaths >= 50: unlock(&"deaths_50")
		if deaths >= 100: unlock(&"deaths_100")
		if GameState.wave <= 1: unlock(&"wave1_death")
		match GameState.last_damage_source:
			&"garbage_truck": unlock(&"killed_truck")
			&"thunder": unlock(&"killed_lightning")
			&"acid_rain": unlock(&"killed_acid")
			&"wire": unlock(&"killed_wire")
			&"airdrop": unlock(&"killed_crate")


# ---------------------------------------------------------------- всплывашка

func _build_toast() -> void:
	_layer = CanvasLayer.new()
	_layer.layer = 50
	add_child(_layer)
	_toast = Panel.new()
	var box: StyleBoxFlat = StyleBoxFlat.new()
	box.bg_color = Color(0.05, 0.03, 0.02, 0.95)
	box.border_color = Color(1.0, 0.84, 0.0)
	box.set_border_width_all(2)
	_toast.add_theme_stylebox_override(&"panel", box)
	_toast.position = Vector2(140.0, -30.0)
	_toast.size = Vector2(200.0, 26.0)
	_toast.visible = false
	_layer.add_child(_toast)
	var cup: TextureRect = TextureRect.new()
	cup.texture = CUP
	cup.position = Vector2(5.0, 5.0)
	_toast.add_child(cup)
	var head: Label = Label.new()
	head.text = "ДОСТИЖЕНИЕ!"
	head.position = Vector2(26.0, 1.0)
	head.add_theme_color_override(&"font_color", Color(1.0, 0.84, 0.0))
	_toast.add_child(head)
	_toast_label = Label.new()
	_toast_label.position = Vector2(26.0, 11.0)
	_toast_label.size = Vector2(170.0, 12.0)
	_toast_label.clip_text = true
	_toast_label.add_theme_color_override(&"font_color", Color.WHITE)
	_toast.add_child(_toast_label)


func _show_next() -> void:
	if _queue.is_empty():
		_toast.visible = false
		return
	_toast_label.text = _queue.pop_front()
	_toast.visible = true
	AudioManager.play_sfx(&"combo")
	var tw: Tween = create_tween()
	tw.tween_property(_toast, "position:y", 4.0, 0.2)
	tw.tween_interval(TOAST_SEC)
	tw.tween_property(_toast, "position:y", -30.0, 0.2)
	tw.tween_callback(_show_next)
