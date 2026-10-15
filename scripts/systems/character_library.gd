class_name CharacterLibrary
extends RefCounted
## Каталог персонажей кладбища: имена, подписи, описания. Числа - в Balance.CHARACTERS.

const _NAMES: Dictionary[StringName, String] = {
	&"hobo": "БОМЖ ВАСЯ", &"squid": "ГОПНИК-КАЛЬМАР", &"clerk": "ОФИСНЫЙ ПЛАНКТОН",
	&"janitor": "ДВОРНИК ПАЛЫЧ", &"uncle_vitya": "ДЯДЯ ВИТЯ", &"blogger": "ЗОМБИ-БЛОГЕР",
	&"granny": "БАБКА С ЛАВОЧКИ", &"courier": "КУРЬЕР-ПОПРЫГУН", &"pigeon": "ГОЛУБЬ-МУТАНТ", &"punk": "КРЫС-ПАНК",
	&"shawarma": "ШАУРМИСТ ЭДИК", &"guard": "ОХРАННИК САНЫЧ", &"student": "СТУДЕНТ-ДОЛЖНИК",
	&"plumber": "САНТЕХНИК ВАЛЕРА", &"dacha": "ТЁТЯ ЗИНА С ДАЧИ", &"skater": "СКЕЙТЕР-ВЕЧНИК",
}
const _SHORT: Dictionary[StringName, String] = {
	&"hobo": "ВАСЯ", &"squid": "КАЛЬМАР", &"clerk": "ПЛАНКТОН", &"janitor": "ПАЛЫЧ", &"uncle_vitya": "ДЯДЯ ВИТЯ", &"blogger": "БЛОГЕР",
	&"granny": "БАБКА", &"courier": "КУРЬЕР", &"pigeon": "ГОЛУБЬ", &"punk": "ПАНК",
	&"shawarma": "ЭДИК", &"guard": "САНЫЧ", &"student": "СТУДЕНТ", &"plumber": "ВАЛЕРА", &"dacha": "ТЁТЯ ЗИНА", &"skater": "СКЕЙТЕР",
}
const _TAGLINES: Dictionary[StringName, String] = {
	&"hobo": "КЛАССИКА ПОМОЙКИ. ВСЕГО ПОНЕМНОГУ, ОРУЖИЕ ВЫБЕРЕШЬ САМ.",
	&"squid": "СЕМКИ, АДИДАС И ШВАБРА. БЬЁТ ПЕРВЫМ, ХП НЕ ЖАЛКО.",
	&"clerk": "РОГАТКА ИЗ СКРЕПОК. ХРУПКИЙ, ЗАТО МЕТКИЙ И БЫСТРЫЙ.",
	&"janitor": "ВИДЕЛ ВСЁ. ТОЛСТЫЙ, МЕДЛЕННЫЙ, С НОСКОМ НАПЕРЕВЕС.",
	&"uncle_vitya": "ВЫПИЛ - ЗНАЧИТ ЖИВ. ПЬЯНЫЙ УВОРОТ И ПОДЖИГАТЕЛЬ.",
	&"blogger": "ДОНАТЫ РЕШАЮТ. ЛАЗЕРНАЯ УКАЗКА И ЖАДНЫЕ ПОДПИСЧИКИ.",
	&"granny": "ВСЮ ЖИЗНЬ СИДЕЛА У ПОДЪЕЗДА. ТАПОК И КЛЮКА: КТО ТРОНЕТ, ТОТ ПОЛУЧИТ.",
	&"courier": "ДОСТАВИТ ДО ДВЕРИ И ДО ГРОБА. БЫСТРЫЙ, ЖАДНЫЙ, СТЕКЛА НЕ БЬЁТ.",
	&"pigeon": "ГАДИТ НА ВСЁ, ЧТО ДВИГАЕТСЯ. ЛЁГКИЙ, ЮРКИЙ, ПИТАЕТСЯ ВРАГАМИ.",
	&"punk": "НЕ ПОДДАЛСЯ СИСТЕМЕ. СКОВОРОДКА, ИРОКЕЗ И КРЫСА В ПОДДЕРЖКУ.",
	&"shawarma": "ТРИ ДНЯ НЕ МЫЛ ВЕРТЕЛ. ТОЛСТЫЙ, ЖАДНЫЙ, СКАКАЛКОЙ ПО ЛБУ.",
	&"guard": "ВИДЕЛ ВСЁ, НИЧЕГО НЕ ЗАПИСАЛ. МЕДЛЕННЫЙ, ЗАТО МОСИНКА И БРОНЯ.",
	&"student": "ДОЛГ ПО ДВУМ ПРЕДМЕТАМ И ТРЕМ ЭНЕРГЕТИКАМ. БЫСТРЫЙ, НО ХРУПКИЙ.",
	&"plumber": "ЛЮБАЯ ПРОБЛЕМА ЭТО ТРУБА. БЬЁТ СИЛЬНО, ХОДИТ МЕДЛЕННО.",
	&"dacha": "ВСЁ ТАЩИТ В ВЕДРО. ЖИВУЧАЯ, НЕТОРОПЛИВАЯ, ПРИТЯГИВАЕТ ХЛАМ.",
	&"skater": "ЕДЕТ, ПАДАЕТ, ВСТАЁТ. ОЧЕНЬ БЫСТРЫЙ, ЛЕГКО ПРОМАХНУТЬСЯ.",
}


const _QUIPS: Dictionary[StringName, String] = {
	&"hobo": "Я ТУТ ЖИВУ.", &"squid": "СЕМКИ ЕСТЬ?", &"clerk": "ЭТО НЕ В МОЕЙ ЗОНЕ.", &"janitor": "ЧИСТО НЕ БУДЕТ.",
	&"uncle_vitya": "ПО ПЯТЬДЕСЯТ!", &"blogger": "ЛАЙК И ПОДПИСКА!", &"granny": "А ВОТ В МОЁ ВРЕМЯ...", &"courier": "ЗАКАЗ ЖДАТЬ НЕ БУДЕТ.",
	&"pigeon": "КУРР-КУРР.", &"punk": "СИСТЕМА, ДЕРЖИСЬ.", &"shawarma": "С ОСТРЫМ ИЛИ С ОЧЕНЬ?", &"guard": "СТОЯТЬ. НЕ ДВИГАТЬСЯ.",
	&"student": "ДО СЕССИИ УСПЕЮ.", &"plumber": "ТРУБА ВСЕГДА ВИНОВАТА.", &"dacha": "РАССАДА СГОРИТ!", &"skater": "ЕДУ-ЕДУ, ПАДАЮ.",
}


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


## Плюсы и минусы построчно (как у предметов).
static func stat_lines(id: StringName) -> PackedStringArray:
	return ItemLibrary.describe(Balance.CHARACTERS[id]).split("\n", false)


static func hat_icon(id: StringName) -> Texture2D:
	return ItemLibrary.icon(Balance.CHARACTERS[id]["hat"])


static func unlock_text(id: StringName) -> String:
	var data: Dictionary = Balance.CHARACTERS[id]
	var kind: StringName = data["unlock"]
	var need: int = data["need"]
	match kind:
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
	if data["unlock"] == &"open" or data["unlock"] == &"wins":
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
