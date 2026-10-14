class_name CharacterLibrary
extends RefCounted
## Каталог персонажей кладбища: имена, подписи, описания. Числа - в Balance.CHARACTERS.

const _NAMES: Dictionary[StringName, String] = {
	&"hobo": "БОМЖ ВАСЯ", &"squid": "ГОПНИК-КАЛЬМАР", &"clerk": "ОФИСНЫЙ ПЛАНКТОН",
	&"janitor": "ДВОРНИК ПАЛЫЧ", &"uncle_vitya": "ДЯДЯ ВИТЯ", &"blogger": "ЗОМБИ-БЛОГЕР",
}
const _SHORT: Dictionary[StringName, String] = {
	&"hobo": "ВАСЯ", &"squid": "КАЛЬМАР", &"clerk": "ПЛАНКТОН", &"janitor": "ПАЛЫЧ", &"uncle_vitya": "ДЯДЯ ВИТЯ", &"blogger": "БЛОГЕР",
}
const _TAGLINES: Dictionary[StringName, String] = {
	&"hobo": "КЛАССИКА ПОМОЙКИ. ВСЕГО ПОНЕМНОГУ, ОРУЖИЕ ВЫБЕРЕШЬ САМ.",
	&"squid": "СЕМКИ, АДИДАС И ШВАБРА. БЬЁТ ПЕРВЫМ, ХП НЕ ЖАЛКО.",
	&"clerk": "РОГАТКА ИЗ СКРЕПОК. ХРУПКИЙ, ЗАТО МЕТКИЙ И БЫСТРЫЙ.",
	&"janitor": "ВИДЕЛ ВСЁ. ТОЛСТЫЙ, МЕДЛЕННЫЙ, С НОСКОМ НАПЕРЕВЕС.",
	&"uncle_vitya": "ВЫПИЛ - ЗНАЧИТ ЖИВ. ПЬЯНЫЙ УВОРОТ И ПОДЖИГАТЕЛЬ.",
	&"blogger": "ДОНАТЫ РЕШАЮТ. ЛАЗЕРНАЯ УКАЗКА И ЖАДНЫЕ ПОДПИСЧИКИ.",
}


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
