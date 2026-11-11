extends Node
## Настройки игрока (user://settings.cfg): громкость звуков и музыки, полный экран, тряска экрана.
## Autoload: Settings. Сигнал changed - применить (AudioManager, камера).

signal changed

const PATH: String = "user://settings.cfg"

var sfx_volume: float = 0.8     # 0..1
var music_volume: float = 0.6
var fullscreen: bool = true
var screen_shake: bool = true
var victory_cutscene: bool = true
var damage_numbers: int = 1         # цифры урона: 0 - нет, 1 - только криты, 2 - все   # ролик победы за воротами (можно выключить)
var art_style: String = "pixel"   # pixel - классика, new - новая пиксельная (крупнее, детальнее, вид 3/4, свет; assets/hd)
const ART_STYLES: Array[String] = ["pixel", "new"]
var language: String = "ru"     # ru / en (строки - translations/ui.csv, через tr())
const LANGUAGES: Array[String] = ["ru", "en"]


func _ready() -> void:
	var cfg: ConfigFile = ConfigFile.new()
	if cfg.load(PATH) == OK:
		sfx_volume = float(cfg.get_value("audio", "sfx", sfx_volume))
		music_volume = float(cfg.get_value("audio", "music", music_volume))
		fullscreen = bool(cfg.get_value("video", "fullscreen", fullscreen))
		screen_shake = bool(cfg.get_value("video", "shake", screen_shake))
		victory_cutscene = bool(cfg.get_value("video", "victory_cutscene", victory_cutscene))
		damage_numbers = int(cfg.get_value("video", "damage_numbers", damage_numbers))
		language = str(cfg.get_value("general", "language", language))
		art_style = str(cfg.get_value("video", "art_style", art_style))
		if art_style == "real":   # старое имя убранного реалистичного стиля
			art_style = "new"
	TranslationServer.set_locale(language)
	_apply_window()


func save() -> void:
	var cfg: ConfigFile = ConfigFile.new()
	cfg.set_value("audio", "sfx", sfx_volume)
	cfg.set_value("audio", "music", music_volume)
	cfg.set_value("video", "fullscreen", fullscreen)
	cfg.set_value("video", "shake", screen_shake)
	cfg.set_value("video", "victory_cutscene", victory_cutscene)
	cfg.set_value("video", "damage_numbers", damage_numbers)
	cfg.set_value("general", "language", language)
	cfg.set_value("video", "art_style", art_style)
	TranslationServer.set_locale(language)
	cfg.save(PATH)
	_apply_window()
	changed.emit()


func _apply_window() -> void:
	if DisplayServer.get_name() == "headless" or OS.get_cmdline_args().has("--windowed"):
		return   # тесты и бот: окно не трогаем
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED)
