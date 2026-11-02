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
	&"boss_mother_in_law": ["ЗЯТЬ ГОДА", "Убей Тёщу"],
	&"boss_uk": ["КВИТАНЦИЯ ОПЛАЧЕНА", "Убей Управляющую компанию"],
	&"clean_wave": ["НИ ЦАРАПИНЫ", "Пройди волну без урона"],
	&"clean_5": ["СКОЛЬЗКИЙ ТИП", "5 чистых волн за забег"],
	&"clean_all": ["НЕУЛОВИМЫЙ ГОВНЮК", "Победи, не получив урона ни в одной волне"],
	&"streak_60": ["МИНУТА СЛАВЫ", "Продержись 60 секунд без урона"],
	&"combo_any": ["АЛХИМИК ПОМОЙКИ", "Собери любое комбо предметов"],
	&"combo_all": ["ВСЕ РЕЦЕПТЫ", "Открой все 8 комбо"],
	&"cursed_3": ["ВОНЮЧКА СО СТАЖЕМ", "Держи 3 зловонных предмета с помойки одновременно"],
	&"cursed_win": ["ПОБЕДИЛ, ВОНЯЯ", "Победи с 3 зловонными предметами"],
	&"tier4": ["ЛЕГЕНДАРНЫЙ ХЛАМ", "Собери оружие IV тира"],
	&"mode_endless_25": ["ПОМОЙКА БЕЗ ДНА", "Доживи до 25-й волны в Бесконечной помойке"],
	&"mode_endless_40": ["ВЕЧНЫЙ БОМЖ", "Доживи до 40-й волны в Бесконечной помойке"],
	&"closed_10": ["БЕЗ ЛАРЬКА ЖИВУ", "Доживи до 10-й волны с закрытым Ларьком"],
	&"closed_win": ["ЛАРЁК НА ЗАМКЕ", "Победи с закрытым Ларьком"],
	&"duel_played": ["КТО ЛОХ?", "Сыграй битву героев до конца"],
	&"dog_found": ["НАШЁЛ ДРУГА", "Подбери бездомного пса"],
	&"dog_level_10": ["ЛУЧШИЙ ДРУГ", "Раскорми пса до 10 уровня"],
	&"dog_fashion": ["МОДНЫЙ ПЁС", "Собери псу все шмотки"],
	&"quests_1": ["НА ПОБЕГУШКАХ", "Выполни записку от бомжа"],
	&"quests_10": ["ДРУГ БОМЖЕЙ", "Выполни 10 записок от бомжей"],
	&"deja_vu": ["ДЕЖАВЮ", "Сдохни тем же героем на той же волне, что и в прошлый раз"],
	&"thief_caught": ["ВЕРНИ БАБКИ", "Прибей щипача с полным мешком"],
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
	&"spend_1000": ["ПОКУПАТЕЛЬ ГОДА", "Потрать 1000 говна за забег"],
	&"stingy_win": ["ЖМОТ", "Победи, ни разу не потратив больше 50 говна за один Ларёк"],
	&"zombie_100": ["ЗОМБИ-ОХОТНИК", "Убей 100 вставших зомби"],
	&"pigeon_vs_pigeons": ["ГОЛУБЬ ПРОТИВ ГОЛУБЕЙ", "Сыграй голубем в Голубиный налёт"],
	&"truck_50": ["САМ СЕБЕ МУСОРОВОЗ", "Мусоровоз задавил 50 врагов за волну"],
	&"daily_week": ["НЕДЕЛЯ ПОМОЙКИ", "Сыграй ежедневку 7 дней подряд"],
	&"daily_top": ["ТОП ДНЯ", "Набери 50000 очков в ежедневке"],
	&"cursed_all": ["ЗЛОВОННЫЙ ДО КОСТЕЙ", "Собери все зловонные предметы за забег"],
	&"medals_hero": ["ЗОЛОТОЙ УНИТАЗ", "Собери все 6 медалей одного героя, до золотого унитаза"],
}

var _queue: Array[String] = []
var _layer: CanvasLayer = null
var _toast: Control = null
var _toast_label: Label = null
var _dashes: int = 0
var _boss_hit: Dictionary = {}     # босс -> бил ли он героя (ачивки «без урона»)
var _wave_mod: StringName = &""
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
	EventBus.boss_spawned.connect(func(id: StringName) -> void: _boss_hit[id] = false)
	EventBus.player_hit.connect(func(_d: float) -> void: _note_boss_hit.call_deferred())
	EventBus.wave_started.connect(func(_w: int) -> void:
		_wave_mod = GameState.wave_mod
		if _wave_mod == &"pigeon_raid" and GameState.character == &"pigeon":
			unlock(&"pigeon_vs_pigeons"))
	EventBus.run_started.connect(func() -> void: _boss_hit.clear())
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
		return TranslationServer.translate(LIST[id][0])
	var s: String = String(id)
	if s.begins_with("nohit_"):
		return TranslationServer.translate("БЕЗ ЦАРАПИН: %s") % EnemyNames.title(StringName(s.trim_prefix("nohit_")))
	if s.begins_with("kill500_"):
		return TranslationServer.translate("ГРОЗА: %s") % EnemyNames.title(StringName(s.trim_prefix("kill500_")))
	if s.begins_with("tier4_"):
		return TranslationServer.translate("IV ТИР: %s") % PerkLibrary.title(StringName("w_" + s.trim_prefix("tier4_")))
	if s.begins_with("set_win_"):
		return TranslationServer.translate("НАБОР: %s") % WeaponLibrary.class_title(StringName(s.trim_prefix("set_win_")))
	if s.begins_with("hero_") and s.contains("_d"):
		var hero: StringName = StringName(s.trim_prefix("hero_").get_slice("_d", 0))
		var d: int = int(s.get_slice("_d", s.count("_d")))
		if Balance.CHARACTERS.has(hero) and d < Balance.DANGER_LEVELS.size():
			return TranslationServer.translate("ПОБЕДА ЗА %s: %s") % [CharacterLibrary.title(hero), Balance.DANGER_LEVELS[d]["name"]]
	if s.begins_with("mod_clean_"):
		return TranslationServer.translate("ПЕРЕЖИЛ ЧИСТО: %s") % TranslationServer.translate(Balance.WAVE_MOD_DATA.get(StringName(s.trim_prefix("mod_clean_")), {}).get("title", "?"))
	return "ПОБЕДА: %s" % String(id)


func unlock(id: StringName, title: String = "") -> void:
	if Profile.sandbox or id in Profile.achievements:
		return
	Profile.achievements.append(id)
	Profile.save()
	_queue.append(title if title != "" else title_of(id))
	if not _toast.visible:
		_show_next()


## Источник урона выставляется после удара - смотрим отложенно, кто из боссов попал.
func _note_boss_hit() -> void:
	var src: StringName = GameState.last_damage_source
	if _boss_hit.has(src):
		_boss_hit[src] = true


func _on_enemy_died(id: StringName, _at: Vector2) -> void:
	unlock(&"first_blood")
	if _boss_hit.has(id) and not _boss_hit[id]:
		unlock(StringName("nohit_" + String(id)))
	if not String(id).begins_with("boss_") and Profile.killed(id) >= 500:
		unlock(StringName("kill500_" + String(id)))
	match id:
		&"boss_mega_hamster": unlock(&"boss_hamster")
		&"boss_rat_queen": unlock(&"boss_rat_queen")
		&"boss_zakhar": unlock(&"boss_zakhar")
		&"boss_minion": unlock(&"boss_minion")
		&"boss_blue_whale": unlock(&"boss_whale")
		&"boss_roach_king": unlock(&"boss_roach_king")
		&"boss_trash_golem": unlock(&"boss_golem")
		&"boss_pigeon_papa": unlock(&"boss_pigeon_papa")
		&"boss_mother_in_law": unlock(&"boss_mother_in_law")
		&"boss_uk": unlock(&"boss_uk")
	if GameState.coins >= 999:
		unlock(&"coins_hoard_999")


func _on_wave_ended(_w: int) -> void:
	if _wave_mod != &"" and GameState.wave_damage_taken <= 0.0:
		unlock(StringName("mod_clean_" + String(_wave_mod)))
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
	var have: int = 0
	var total: int = 0
	for id: StringName in Balance.ITEMS:
		if ItemLibrary.is_cursed(id):
			total += 1
			have += 1 if GameState.item_count(id) > 0 else 0
	if total > 0 and have >= total:
		unlock(&"cursed_all")


func _check_weapons() -> void:
	var ids: Dictionary = {}
	for w: Dictionary in GameState.weapons:
		if w["tier"] >= 4:
			unlock(&"tier4")
			unlock(StringName("tier4_" + String(w["id"])))
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
		if GameState.run_score(won) >= 50000: unlock(&"daily_top")
		if _daily_streak() >= 7: unlock(&"daily_week")
		if p.daily_best.size() >= 10: unlock(&"daily_10")
	if won:
		unlock(&"first_win")
		unlock(hero_id(GameState.character, GameState.danger), "ПОБЕДА ЗА %s: %s" % [CharacterLibrary.title(GameState.character), Balance.DANGER_LEVELS[GameState.danger]["name"]])
		if GameState.danger >= 5: unlock(&"win_danger5")
		if GameState.clean_waves >= Balance.WAVE_COUNT: unlock(&"clean_all")
		if GameState.items.keys().all(func(k: StringName) -> bool: return k == ItemLibrary.SHOES): unlock(&"no_items_win")   # обувь не считается
		if GameState.max_shop_spent <= 50: unlock(&"stingy_win")
		var counts: Dictionary = WeaponLibrary.class_counts(GameState.weapons)
		for c: StringName in counts:
			if counts[c] >= 6: unlock(StringName("set_win_" + String(c)))
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


## Сколько дней подряд (до сегодня) сыграна ежедневка.
func _daily_streak() -> int:
	var days: Dictionary = {}
	for key: String in Profile.daily_best:
		var v: int = int(key)
		var unix: int = Time.get_unix_time_from_datetime_dict({"year": v / 10000, "month": (v / 100) % 100, "day": v % 100})
		days[unix / 86400] = true
	var today: int = Time.get_unix_time_from_datetime_dict(Time.get_date_dict_from_system()) / 86400
	var streak: int = 0
	while days.has(today - streak):
		streak += 1
	return streak


## Все id достижений (для Steam и документа): общие, «без царапин» на боссах, гроза каждого врага,
## IV тир каждого оружия, набор каждого класса, каждый модификатор без урона, победы героев на каждой опасности.
static func all_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for id: StringName in LIST:
		out.append(id)
	for b: StringName in Balance.ELITE_POOL + Balance.FINAL_BOSS_POOL:
		out.append(StringName("nohit_" + String(b)))
	for e: StringName in Balance.ENEMIES:
		if not String(e).begins_with("boss_") and not Balance.ENEMIES[e].get("neutral", false):
			out.append(StringName("kill500_" + String(e)))
	for w: StringName in Balance.WEAPONS:
		if not Balance.WEAPONS[w].get("structure", false):
			out.append(StringName("tier4_" + String(w)))
	for c: StringName in Balance.WEAPON_CLASSES:
		out.append(StringName("set_win_" + String(c)))
	for m: StringName in Balance.WAVE_MODS:
		out.append(StringName("mod_clean_" + String(m)))
	for h: StringName in Balance.CHARACTER_ORDER:
		for d: int in Balance.DANGER_LEVELS.size():
			out.append(hero_id(h, d))
	return out
