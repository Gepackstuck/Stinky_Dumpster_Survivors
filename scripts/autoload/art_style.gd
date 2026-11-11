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
## Если у детальной есть карта нормалей (<имя>_n.png, "n" в описании) - отдаётся CanvasTexture: свет ложится рельефно.
func tex(path: String) -> Texture2D:
	var d: Dictionary = info(path)
	var real: String = HD_ROOT + path.trim_prefix(ROOT) if not d.is_empty() else path
	if not _cache.has(real):
		var base: Texture2D = load(real) as Texture2D
		if d.get("n", false):
			var ct: CanvasTexture = CanvasTexture.new()
			ct.diffuse_texture = base
			ct.normal_texture = load(real.replace(".png", "_n.png")) as Texture2D
			ct.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
			if d.get("repeat", false):
				ct.texture_repeat = CanvasItem.TEXTURE_REPEAT_ENABLED
			base = ct
		_cache[real] = base
	return _cache[real]


## Мягкая тень под существом детального стиля (width - ширина тела, foot - от центра до подошвы; мировые единицы).
func shadow(host: Node2D, width: float, foot: float, cx: float = 0.0) -> Sprite2D:
	var sh: Sprite2D = host.get_node_or_null(^"HdShadow") as Sprite2D
	if sh == null:
		sh = Sprite2D.new()
		sh.name = "HdShadow"
		sh.texture = _shadow_tex()
		sh.show_behind_parent = true
		sh.z_index = -1
		host.add_child(sh)
		host.move_child(sh, 0)
	sh.visible = true
	sh.position = Vector2(cx, foot - width * 0.04)
	sh.scale = Vector2(width * Balance.HD_SHADOW_WIDTH / 64.0, width * Balance.HD_SHADOW_WIDTH * 0.42 / 64.0)
	return sh


var _shadow: GradientTexture2D = null


func _shadow_tex() -> Texture2D:
	if _shadow == null:
		var grad: Gradient = Gradient.new()
		grad.offsets = PackedFloat32Array([0.0, 0.55, 1.0])
		grad.colors = PackedColorArray([Color(0, 0, 0, Balance.HD_SHADOW_ALPHA), Color(0, 0, 0, Balance.HD_SHADOW_ALPHA * 0.7), Color(0, 0, 0, 0)])
		_shadow = GradientTexture2D.new()
		_shadow.gradient = grad
		_shadow.fill = GradientTexture2D.FILL_RADIAL
		_shadow.fill_from = Vector2(0.5, 0.5)
		_shadow.fill_to = Vector2(1.0, 0.5)
		_shadow.width = 64
		_shadow.height = 64
	return _shadow


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
