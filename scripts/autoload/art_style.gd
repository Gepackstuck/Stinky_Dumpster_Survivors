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
var _pending: Array[WeakRef] = []
var _grade: CanvasLayer = null
var _pixel_theme: Theme = null   # копия пиксельной темы, чтобы вернуть её при переключении
var _cache: Dictionary[String, Texture2D] = {}


func _ready() -> void:
	if FileAccess.file_exists(MANIFEST):
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
		if parsed is Dictionary:
			_manifest = parsed
	apply_ui()
	get_tree().node_added.connect(_on_node_added)


## Шрифт и цвета интерфейса текущего стиля (вызывать после смены стиля в настройках). Меняем саму тему проекта:
## тема на корневом окне не доходит до элементов внутри CanvasLayer.
func apply_ui() -> void:
	var theme: Theme = ThemeDB.get_project_theme()
	if theme == null:
		return
	if _pixel_theme == null:
		_pixel_theme = theme.duplicate() as Theme
	var from: Theme = load(HD_THEME) as Theme   # новый шрифт - во всей игре, в обоих стилях
	theme.default_font = from.default_font
	for key: StringName in [&"font_color", &"font_shadow_color"]:
		theme.set_color(key, &"Label", from.get_color(key, &"Label"))
	get_tree().root.canvas_item_default_texture_filter = Viewport.DEFAULT_CANVAS_ITEM_TEXTURE_FILTER_LINEAR   # гладкий шрифт; спрайты сами ставят NEAREST
	_apply_grade()


## Мрачная цветокоррекция всего экрана (игра и интерфейс) в новом стиле; в классике убирается.
func _apply_grade() -> void:
	if is_hd() and _grade == null:
		_grade = CanvasLayer.new()
		_grade.layer = 120
		_grade.process_mode = Node.PROCESS_MODE_ALWAYS
		var rect: ColorRect = ColorRect.new()
		rect.set_anchors_preset(Control.PRESET_FULL_RECT)
		rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var mat: ShaderMaterial = ShaderMaterial.new()
		mat.shader = load("res://assets/shaders/horror_grade.gdshader") as Shader
		rect.material = mat
		_grade.add_child(rect)
		get_tree().root.add_child.call_deferred(_grade)
	elif not is_hd() and _grade != null:
		_grade.queue_free()
		_grade = null


## Подмена картинок в новом стиле «на лету»: любой узел с текстурой, у которой есть версия в assets/hd/, получает её.
## Так интерфейс, оружие в руках и снаряды меняются без правки сцен (картинка - тот же путь внутри assets/hd/).
func _on_node_added(n: Node) -> void:
	if not is_hd():
		return
	if n is TextureRect or n is TextureProgressBar or n is Sprite2D or n is NinePatchRect:
		_pending.append(weakref(n))


func _process(_delta: float) -> void:
	if _pending.is_empty():
		return
	var batch: Array[WeakRef] = _pending
	_pending = []
	for ref: WeakRef in batch:
		var obj: Object = ref.get_ref()
		if obj != null:
			_reskin(obj as Node)


func _reskin(n: Node) -> void:
	var cur: Texture2D = n.get(&"texture") if not (n is TextureProgressBar) else null
	if n is TextureProgressBar:
		var bar: TextureProgressBar = n as TextureProgressBar
		bar.texture_under = _swap(bar.texture_under)
		bar.texture_progress = _swap(bar.texture_progress)
		bar.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
		return
	if cur != null:
		var swapped: Texture2D = _swap(cur)
		if swapped != cur or cur is AtlasTexture:
			n.set(&"texture", swapped)
			(n as CanvasItem).texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST


func _swap(t: Texture2D) -> Texture2D:
	if t == null:
		return null
	if t is AtlasTexture:
		var at: AtlasTexture = t as AtlasTexture
		var repl: Texture2D = _swap(at.atlas)
		if repl != at.atlas:
			at.atlas = repl
		return t
	var path: String = t.resource_path
	if path.begins_with(ROOT) and has_hd(path):
		return tex(path)
	return t


func is_hd() -> bool:
	return Settings.art_style == "new"


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
			ct.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST if d.get("pixel", true) else CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
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
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST if d.get("pixel", true) else CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	return float(d.get("scale", 0.25))
