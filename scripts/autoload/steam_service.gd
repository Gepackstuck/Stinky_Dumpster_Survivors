extends Node
## Steam через GodotSteam (GDExtension в addons/godotsteam). Autoload: SteamService.
## Нет Steam (не установлен, не запущен, нет App ID, тесты/бот) - всё тихо работает как раньше: available = false.
## Достижения: Achievements.unlock -> set_achievement. Таблицы: ежедневка и Бесконечная помойка.

## App ID игры в Steamworks. 0 - Steam не трогаем (пока нет страницы игры). Для проверки можно 480 (Spacewar).
const APP_ID: int = 0
const BOARD_DAILY_PREFIX: String = "daily_"     # таблица на каждый день: daily_20261102
const BOARD_ENDLESS: String = "endless_mode"

var available: bool = false
var _steam: Object = null
var _pending_score: Dictionary = {}   # таблица -> очки, ждём find_leaderboard


func _ready() -> void:
	if APP_ID <= 0 or Profile.sandbox or DisplayServer.get_name() == "headless" or not Engine.has_singleton(&"Steam"):
		return
	_steam = Engine.get_singleton(&"Steam")
	var res: Variant = _steam.call(&"steamInitEx", APP_ID, true)
	var status: int = int(res.get("status", 1)) if res is Dictionary else 1
	available = status == 0
	if not available:
		print("Steam: нет (", res, ") - играем без него")
		return
	_steam.connect(&"leaderboard_find_result", _on_board_found)
	print("Steam: ок, пользователь ", _steam.call(&"getPersonaName"))


func _process(_delta: float) -> void:
	if available:
		_steam.call(&"run_callbacks")


## Достижение в Steam (id = API name, как в Achievements / docs/ACHIEVEMENTS.md).
func set_achievement(id: StringName) -> void:
	if not available:
		return
	_steam.call(&"setAchievement", String(id))
	_steam.call(&"storeStats")


## Отправить очки в таблицу (лучший результат хранит Steam).
func submit_score(board: String, score: int) -> void:
	if not available:
		return
	_pending_score[board] = score
	_steam.call(&"findOrCreateLeaderboard", board, 2, 1)   # по убыванию, числом


func _on_board_found(handle: int, found: int) -> void:
	if found == 0 or _pending_score.is_empty():
		return
	var board: String = _pending_score.keys()[0]
	var score: int = _pending_score[board]
	_pending_score.erase(board)
	_steam.call(&"uploadLeaderboardScore", score, true, PackedInt32Array(), handle)
