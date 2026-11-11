extends Node
## Стиль рисовки: «pixel» (как было) или «real» (детальная мрачная отрисовка из assets/hd/).
## Картинка нового стиля лежит по тому же пути под assets/hd/ и описана в assets/hd/manifest.json:
## {"sprites/enemy_x.png": {"h": 12, "v": 1, "scale": 0.25, "fps": 12, "rows": {...}}}.
## Нет картинки нового стиля - берётся пиксельная. Autoload: ArtStyle. Смена стиля применяется при загрузке сцены.

const ROOT: String = "res://assets/"
const HD_ROOT: String = "res://assets/hd/"
const HD_THEME: String = "res://assets/hd/ui/theme_hd.tres"
const MANIFEST: String = "res://assets/hd/manifest.json"

var _manifest: Dictionary = {}
var _pixel_theme: Theme = null   # копия пиксельной темы, чтобы вернуть её при переключении
var _cache: Dictionary[String, Texture2D] = {}


func _ready() -> void:
	if FileAccess.file_exists(MANIFEST):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
		if parsed is Dictionary:
			_manifest = parsed
	apply_ui()


## Шрифт и цвета интерфейса текущего стиля (вызывать после смены стиля в настройках). Меняем саму тему проекта:
## тема на корневом окне не доходит до элементов внутри CanvasLayer.
func apply_ui() -> void:
	var theme: Theme = ThemeDB.get_project_theme()
	if theme == null:
		return
	if _pixel_theme == null:
		_pixel_theme = theme.duplicate() as Theme
	var from: Theme = load(HD_THEME) as Theme if is_hd() else _pixel_theme
	theme.default_font = from.default_font
	for key: StringName in [&"font_color", &"font_shadow_color"]:
		theme.set_color(key, &"Label", from.get_color(key, &"Label"))
	get_tree().root.canvas_item_default_texture_filter = (Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_LINEAR if is_hd()
			else Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_NEAREST)   # гладкий шрифт и картинки в детальном стиле


func is_hd() -> bool:
	return Settings.art_style == "real"


## Описание картинки нового стиля ({} - её нет или включён пиксельный стиль).
func info(path: String) -> Dictionary:
	if not is_hd():
		return {}
	return _manifest.get(path.trim_prefix(ROOT), {})


func has_hd(path: String) -> bool:
	return not info(path).is_empty()


## Текстура по пути пиксельной картинки: в новом стиле - её детальная версия, если нарисована.
func tex(path: String) -> Texture2D:
	var real: String = HD_ROOT + path.trim_prefix(ROOT) if has_hd(path) else path
	if not _cache.has(real):
		_cache[real] = load(real) as Texture2D
	return _cache[real]


## Поставить спрайту картинку в текущем стиле: текстура, сетка кадров, сглаживание.
## Возвращает масштаб текселя (1.0 у пиксельной; у детальной - доля мировой единицы на тексель).
func apply(sprite: Sprite2D, path: String) -> float:
	var d: Dictionary = info(path)
	sprite.texture = tex(path)
	if d.is_empty():
		sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		return 1.0
	sprite.frame = 0
	sprite.hframes = int(d.get("h", 1))
	sprite.vframes = int(d.get("v", 1))
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	return float(d.get("scale", 0.25))
