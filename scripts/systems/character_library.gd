class_name CharacterLibrary
extends RefCounted
## Каталог персонажей кладбища: имена, подписи, описания. Числа - в Balance.CHARACTERS.

const _NAMES: Dictionary[StringName, String] = {
	&"hobo": "БОМЖ ВАСЯ", &"squid": "ГОПНИК-КАЛЬМАР", &"clerk": "ОФИСНЫЙ ПЛАНКТОН",
	&"janitor": "ДВОРНИК ПАЛЫЧ", &"uncle_vitya": "ДЯДЯ ВИТЯ", &"blogger": "ЗОМБИ-БЛОГЕР",
	&"granny": "БАБКА С ЛАВОЧКИ", &"courier": "КУРЬЕР-ПОПРЫГУН", &"pigeon": "ГОЛУБЬ-МУТАНТ", &"punk": "КРЫС-ПАНК",
	&"shawarma": "ШАУРМИСТ ЭДИК", &"guard": "ОХРАННИК САНЫЧ", &"student": "СТУДЕНТ-ДОЛЖНИК",
	&"plumber": "САНТЕХНИК ВАЛЕРА", &"dacha": "ТЁТЯ ЗИНА С ДАЧИ", &"skater": "СКЕЙТЕР-ВЕЧНИК", &"slime": "СЛИЗЕНЬ ГРИША",
	&"gopnik_jock": "ГОПНИК-КАЧОК ЖОРА", &"cat": "КОТ-ПОМОЕЧНИК",
}
const _SHORT: Dictionary[StringName, String] = {
	&"hobo": "ВАСЯ", &"squid": "КАЛЬМАР", &"clerk": "ПЛАНКТОН", &"janitor": "ПАЛЫЧ", &"uncle_vitya": "ДЯДЯ ВИТЯ", &"blogger": "БЛОГЕР",
	&"granny": "БАБКА", &"courier": "КУРЬЕР", &"pigeon": "ГОЛУБЬ", &"punk": "ПАНК",
	&"shawarma": "ЭДИК", &"guard": "САНЫЧ", &"student": "СТУДЕНТ", &"plumber": "ВАЛЕРА", &"dacha": "ТЁТЯ ЗИНА", &"skater": "СКЕЙТЕР", &"gopnik_jock": "ЖОРА", &"cat": "КОТ", &"slime": "ГРИША",
}
const _TAGLINES: Dictionary[StringName, String] = {
	&"hobo": "КЛАССИКА ПОМОЙКИ. ОРУЖИЕ ВЫБЕРЕШЬ САМ.",
	&"squid": "СЕМКИ, АДИДАС И ШВАБРА. БЬЁТ ПЕРВЫМ.",
	&"clerk": "РОГАТКА ИЗ СКРЕПОК. ХРУПКИЙ, ЗАТО МЕТКИЙ.",
	&"janitor": "ВИДЕЛ ВСЁ. ТОЛСТЫЙ, МЕДЛЕННЫЙ, С НОСКОМ.",
	&"uncle_vitya": "ВЫПИЛ - ЗНАЧИТ ЖИВ. ПЬЯНЫЙ УВОРОТ И ОГОНЬ.",
	&"blogger": "ДОНАТЫ РЕШАЮТ. УКАЗКА И ЖАДНЫЕ ПОДПИСЧИКИ.",
	&"granny": "ТАПОК-МИНА И КЛЮКА: КТО ТРОНЕТ, ТОТ ПОЛУЧИТ.",
	&"courier": "ДОСТАВИТ ДО ДВЕРИ И ДО ГРОБА. БЫСТРЫЙ, ЖАДНЫЙ.",
	&"pigeon": "ГАДИТ НА ВСЁ, ЧТО ДВИГАЕТСЯ. ЛЁГКИЙ, ЮРКИЙ.",
	&"punk": "СКОВОРОДКА, ИРОКЕЗ И КРЫСА В ПОДДЕРЖКУ.",
	&"shawarma": "ТРИ ДНЯ НЕ МЫЛ ВЕРТЕЛ. СКАЛКОЙ ПО ЛБУ.",
	&"guard": "ВИДЕЛ ВСЁ, НИЧЕГО НЕ ЗАПИСАЛ. МОСИНКА И БРОНЯ.",
	&"student": "ДОЛГ ПО ДВУМ ПРЕДМЕТАМ. БЫСТРЫЙ, НО ХРУПКИЙ.",
	&"plumber": "ЛЮБАЯ ПРОБЛЕМА ЭТО ТРУБА. БЬЁТ СИЛЬНО.",
	&"dacha": "ВСЁ ТАЩИТ В ВЕДРО. ЖИВУЧАЯ, ПРИТЯГИВАЕТ ХЛАМ.",
	&"skater": "ЕДЕТ, ПАДАЕТ, ВСТАЁТ. ОЧЕНЬ БЫСТРЫЙ.",
	&"slime": "ИЗ КАНАЛИЗАЦИИ ЗА ШАУРМОЙ. НЕ ЧЕЛОВЕК, НЕ ЖАБА.",
	&"gopnik_jock": "ТУРНИК, СЕМКИ, ЗАТОЧКА. ТАРАНОМ СКВОЗЬ ТОЛПУ.",
	&"cat": "ДЕВЯТЬ ЖИЗНЕЙ, НО КАЖДЫЙ УДАР - МИНУС ЖИЗНЬ.",
}


## Досье: как выглядит персонаж (экран выбора, клавиша E).
const _LORE: Dictionary[StringName, String] = {
	&"hobo": "БОРОДАЧ В УШАНКЕ И ДРАНОМ КИСЛОТНОМ ПАЛЬТО С ЗАПЛАТКАМИ. НОС КРАСНЫЙ, В РУКЕ БУТЫЛКА, В БОРОДЕ КРОШКИ ПРОШЛОГОДНИЕ.",
	&"squid": "СИНЯЯ ГОЛОВА, ЩУПАЛЬЦА ВМЕСТО БОРОДЫ, АДИДАС С ЛАМПАСАМИ И КЕПКА НАБЕКРЕНЬ. ВО РТУ БЫЧОК, В ГЛАЗАХ УВЕРЕННОСТЬ.",
	&"clerk": "БЕЛАЯ РУБАШКА, КРАСНЫЙ ГАЛСТУК, БЕЙДЖ С ДОЛЖНОСТЬЮ И ЗАПЛЫВШИЕ ОЧКИ. ВЗГЛЯД ЧЕЛОВЕКА, КОТОРЫЙ ПЕРЕЖИЛ ТРЕТИЙ КВАРТАЛ.",
	&"janitor": "КЕПКА С КОЗЫРЬКОМ, СЕДЫЕ УСЫ, ОРАНЖЕВЫЙ ЖИЛЕТ СО СВЕТООТРАЖАТЕЛЯМИ, САПОГИ И МЕТЛА. НА ЭТОМ ДВОРЕ ОН ЦАРЬ.",
	&"uncle_vitya": "МАЙКА-АЛКОГОЛИЧКА, РУМЯНЫЙ НОС, ЩЕТИНА И БУТЫЛКА В КАРМАНЕ. ШАТАЕТСЯ, НО ПАДАЕТ ТОЛЬКО ПО ПРАЗДНИКАМ.",
	&"blogger": "ЗЕЛЁНЫЙ ЗОМБИ С РОЗОВЫМИ ВОЛОСАМИ, ТЁМНЫМИ КРУГАМИ ПОД ГЛАЗАМИ И ЗОЛОТОЙ ЦЕПОЧКОЙ. ТЕЛЕФОН СВЕТИТСЯ ДАЖЕ В ГРОБУ.",
	&"granny": "ПЛАТОК С ГОРОШКОМ, ОЧКИ, ОСКАЛ, ХАЛАТ В ЦВЕТОЧЕК, КЛЮКА И АВОСЬКА С СЕМКАМИ. СИДЕЛА У ПОДЪЕЗДА, ПОКА ПОДЪЕЗД НЕ ЗАКОНЧИЛСЯ.",
	&"courier": "ЗЕЛЁНАЯ КУРТКА, КЕПКА И ОГРОМНЫЙ ЖЁЛТЫЙ КОРОБ ЗА СПИНОЙ С ЗАКАЗОМ, КОТОРЫЙ ДАВНО ОСТЫЛ.",
	&"pigeon": "СИЗОЕ ТЕЛО С БЕЛЫМИ ПОЛОСАМИ НА КРЫЛЬЯХ, ЗЕЛЁНО-ФИОЛЕТОВАЯ ШЕЯ, БЕШЕНЫЕ ГЛАЗА И ТРЕТИЙ, КРАСНЫЙ, НА ЛБУ.",
	&"punk": "КРЫСА С ЗЕЛЁНЫМ ИРОКЕЗОМ, РОЗОВЫМИ УШАМИ И ЖЁЛТЫМИ ЗУБАМИ В КОЖАНКЕ С ЗАКЛЁПКАМИ. ХВОСТ ТОРЧИТ КАК ПРОТЕСТ.",
	&"shawarma": "ПОВАРСКОЙ КОЛПАК, УСИЩИ, ЗОЛОТАЯ ЦЕПОЧКА И ФАРТУК В ПЯТНАХ НЕИЗВЕСТНОГО ПРОИСХОЖДЕНИЯ. ВЕРТЕЛ ПОМНИТ ВСЁ.",
	&"guard": "ТЁМНО-СИНЯЯ ФОРМА, ФУРАЖКА С КОКАРДОЙ, УСЫ И РЕМЕНЬ С ДУБИНКОЙ. СТОИТ НА ПОСТУ, ДАЖЕ КОГДА ПОСТ УЖЕ СНЕСЛИ.",
	&"student": "ФИОЛЕТОВЫЙ ХУДИ, ВСКЛОКОЧЕННАЯ ШЕВЕЛЮРА, КРУГИ ПОД ГЛАЗАМИ И БАНКА ЭНЕРГЕТИКА В КУЛАКЕ. СПИТ ТОЛЬКО НА ЛЕКЦИЯХ.",
	&"plumber": "КРАСНАЯ КЕПКА, ОГРОМНЫЕ УСЫ, СИНИЙ КОМБИНЕЗОН НА ЖЁЛТОЙ ФУТБОЛКЕ И ГАЕЧНЫЙ КЛЮЧ. ЛЮБАЯ ТРУБА ЕМУ ЗНАКОМА.",
	&"dacha": "СОЛОМЕННАЯ ШЛЯПА С ЦВЕТАМИ, РОЗОВОЕ ПЛАТЬЕ, БЕЛЫЙ ФАРТУК, РУМЯНЕЦ И ВЁДРО В РУКЕ. РАССАДА ВАЖНЕЕ ЖИЗНИ.",
	&"skater": "КРАСНЫЙ КОЗЫРЁК, ЖЁЛТАЯ ФУТБОЛКА, НАУШНИКИ И ДОСКА ПОД МЫШКОЙ. КОЛЕНИ В ЗЕЛЁНКЕ, КАРМА В ПЛЮСЕ.",
	&"gopnik_jock": "СИНЯЯ ОЛИМПИЙКА С ЛАМПАСАМИ, КЕПКА-ВОСЬМИКЛИНКА, ЗОЛОТАЯ ЦЕПЬ И ФИКСА. РУКИ ШИРЕ ПЛЕЧ, МОЗГ УЖЕ ПЛЕЧ.",
	&"cat": "СЕРЫЙ ПОЛОСАТЫЙ КОТ С НАДОРВАННЫМ УХОМ, ШРАМОМ И РАЗНЫМИ ГЛАЗАМИ. В СТАРЫХ САПОГАХ. ВИДЕЛ ДЕВЯТЬ СМЕРТЕЙ И ЕЩЁ ХОЧЕТ.",
	&"slime": "ЗЕЛЁНЫЙ КОМОК СЛИЗИ С ОГРОМНЫМИ ВЫПУЧЕННЫМИ ГЛАЗАМИ, ВЫСУНУТЫМ ЯЗЫКОМ И КОРИЧНЕВЫМИ НОЖКАМИ. ПАХНЕТ КАНАЛИЗАЦИЕЙ И ГОРДОСТЬЮ.",
}


const _QUIPS: Dictionary[StringName, String] = {
	&"hobo": "Я ТУТ ЖИВУ.", &"squid": "СЕМКИ ЕСТЬ?", &"clerk": "ЭТО НЕ В МОЕЙ ЗОНЕ.", &"janitor": "ЧИСТО НЕ БУДЕТ.",
	&"uncle_vitya": "ПО ПЯТЬДЕСЯТ!", &"blogger": "ЛАЙК И ПОДПИСКА!", &"granny": "А ВОТ В МОЁ ВРЕМЯ...", &"courier": "ЗАКАЗ ЖДАТЬ НЕ БУДЕТ.",
	&"pigeon": "КУРР-КУРР.", &"punk": "СИСТЕМА, ДЕРЖИСЬ.", &"shawarma": "С ОСТРЫМ ИЛИ С ОЧЕНЬ?", &"guard": "СТОЯТЬ. НЕ ДВИГАТЬСЯ.",
	&"student": "ДО СЕССИИ УСПЕЮ.", &"plumber": "ТРУБА ВСЕГДА ВИНОВАТА.", &"dacha": "РАССАДА СГОРИТ!", &"skater": "ЕДУ-ЕДУ, ПАДАЮ.", &"gopnik_jock": "С КАКОГО РАЙОНА?", &"cat": "МЯУ. ДАЙ ПОЖРАТЬ.", &"slime": "ЧЛЮП. ЧЛЮП-ЧЛЮП.",
}


static func lore(id: StringName) -> String:
	return _LORE.get(id, "")


static func quip(id: StringName) -> String:
	return _QUIPS.get(id, "")


static func ids() -> Array[StringName]:
	return Balance.CHARACTER_ORDER


static func title(id: StringName) -> String:
	return _NAMES[id]


static func short_title(id: StringName) -> String:
	return _SHORT[id]


static func tagline(id: StringName) -> String:
	return _TAGLINES[id]


static func weapon_line(id: StringName) -> String:
	var weapon: StringName = Balance.CHARACTERS[id]["weapon"]
	if weapon == &"":
		return "СТАРТ: ОРУЖИЕ НА ВЫБОР"
	return "СТАРТ: %s" % PerkLibrary.title(StringName("w_" + String(weapon)))


const _DASH_FX_TEXT: Dictionary = {
	&"slow": "ТОРМОЗИТ ВРАГОВ", &"sweep": "БЬЁТ ПО ПУТИ", &"knock": "РАСПИХИВАЕТ", &"ram": "ТАРАН СКВОЗЬ ТОЛПУ",
	&"trail": "СКОЛЬЗКИЙ СЛЕД", &"blink": "ТЕЛЕПОРТ", &"drunk": "КРИВОЙ, ДОЛЬШЕ НЕУЯЗВИМ",
	&"heal": "+1 ХП", &"fly": "ПЕРЕЛЁТ", &"pipe": "ЧЕРЕЗ ТРУБУ, СКВОЗЬ ВСЕХ",
}


## Рывок героя одной строкой: «РЫВОК: ОЛЛИ, 2 ЗАРЯДА, ДАЛЕКО».
static func dash_line(id: StringName) -> String:
	var p: Dictionary = DashComponent.profile(id)
	var parts: Array[String] = []
	if _DASH_FX_TEXT.has(p["fx"]):
		parts.append(_DASH_FX_TEXT[p["fx"]])
	if p.get("old", false):
		parts.append("СТАРЫЙ: КОРОТКИЙ, %d%% ПЕРДИТ" % roundi(float(p["fart"]) * 100.0))
	if int(p["charges"]) > 1:
		parts.append("%d ЗАРЯДА" % int(p["charges"]))
	if parts.is_empty():
		parts.append("ДАЛЕКО И ЧАСТО" if float(p["dist"]) >= 85.0 else ("ЧАСТО" if float(p["cd"]) <= 1.3 else "ОБЫЧНЫЙ"))
	var ult: Array = Balance.HERO_ULT.get(id, ["?", &""])
	return "РЫВОК: %s (%s)   УЛЬТА: %s" % [String(p.get("name", "РЫВОК")), ", ".join(parts), ult[0]]


## Плюсы и минусы построчно (как у предметов).
static func stat_lines(id: StringName) -> PackedStringArray:
	return ItemLibrary.describe({"mods": Balance.CHARACTERS[id].get("mods", {})}).split("\n", false)


## Фишки героя (fx) одной строкой: «ФИШКА: ПИРОЖКИ: +3 ХП В НАЧАЛЕ ВОЛНЫ, ...».
static func trait_line(id: StringName) -> String:
	var fx: Dictionary = Balance.CHARACTERS[id].get("fx", {})
	if fx.is_empty():
		return ""
	return "ФИШКА: " + ItemLibrary.describe({"fx": fx}).replace("\n", ". ")


static func hat_icon(id: StringName) -> Texture2D:
	return ItemLibrary.icon_small(Balance.CHARACTERS[id]["hat"])


static func unlock_text(id: StringName) -> String:
	var data: Dictionary = Balance.CHARACTERS[id]
	var kind: StringName = data["unlock"]
	var need: int = data["need"]
	match kind:
		&"ach":
			return TranslationServer.translate("ДОСТИЖЕНИЕ: %s") % Achievements.title_of(data["ach"])
		&"kills":
			return "УБЕЙ %d ВРАГОВ" % need
		&"coins":
			return "СОБЕРИ %d ГОВНА" % need
		&"deaths":
			return "СДОХНИ ХОТЯ БЫ РАЗ" if need <= 1 else "СДОХНИ %d РАЗ" % need
		&"wins":
			return "ПРОЙДИ ИГРУ"
	return ""


static func progress_text(id: StringName) -> String:
	var data: Dictionary = Balance.CHARACTERS[id]
	if data["unlock"] == &"open" or data["unlock"] == &"wins" or data["unlock"] == &"ach":
		return ""
	return "(%d/%d)" % [mini(Profile.counter(data["unlock"]), data["need"]), data["need"]]


## Лист спрайтов героя (4x3 кадра); нет своего - общий.
static func sprite_sheet(id: StringName) -> Texture2D:
	var path: String = "res://assets/sprites/player_%s.png" % id
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	var image: Image = Image.load_from_file(ProjectSettings.globalize_path(path))
	return ImageTexture.create_from_image(image) if image != null else null


## Текстура по пути; если редактор ещё не импортировал свежий PNG - читаем файл напрямую.
static func load_texture(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	var image: Image = Image.load_from_file(ProjectSettings.globalize_path(path))
	return ImageTexture.create_from_image(image) if image != null else null


## Шапка-трофей героя: за самую высокую опасность, на которой он победил (как медаль). null - побед нет.
static func trophy_hat(id: StringName) -> Texture2D:
	var won: Array = Profile.hero_wins.get(id, [])
	if won.is_empty():
		return null
	var best: int = 0
	for d: Variant in won:
		best = maxi(best, int(d))
	return load("res://assets/sprites/trophy_hat_%d.png" % clampi(best, 0, 5)) as Texture2D
