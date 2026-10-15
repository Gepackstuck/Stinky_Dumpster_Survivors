extends RefCounted
## Загрузка картинки: обычным путём, а если редактор ещё не импортировал новый PNG - прямо из файла.


static func load_tex(path: String) -> Texture2D:
	if ResourceLoader.exists(path):
		return load(path) as Texture2D
	var image: Image = Image.load_from_file(ProjectSettings.globalize_path(path))
	return ImageTexture.create_from_image(image) if image != null else null
