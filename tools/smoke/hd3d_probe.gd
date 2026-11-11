extends Node
## Проба 3D-вида: арена с рельефной землёй, камера под углом, свет и тени. Пока существа - картинки-билборды (модели ещё нет).
## Снимки: tools/_preview/hd/04_3d/угол_N.png. Оконный режим.

const ANGLES: Array[float] = [90.0, 60.0, 50.0]
const IDS: Array[String] = ["enemy_squid_gopnik", "enemy_spitter", "enemy_microbe", "enemy_chaser"]


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()


func _run() -> void:
	var env: WorldEnvironment = WorldEnvironment.new()
	var e: Environment = Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.03, 0.03, 0.04)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.35, 0.36, 0.45)
	e.ambient_light_energy = 0.6
	e.fog_enabled = true
	e.fog_light_color = Color(0.12, 0.13, 0.1)
	e.fog_density = 0.012
	e.glow_enabled = true
	env.environment = e
	add_child(env)
	var ground: MeshInstance3D = MeshInstance3D.new()
	var plane: PlaneMesh = PlaneMesh.new()
	plane.size = Vector2(80.0, 80.0)
	ground.mesh = plane
	var gm: StandardMaterial3D = StandardMaterial3D.new()
	gm.albedo_texture = load("res://assets/hd/sprites/ground_tile.png")
	gm.normal_enabled = true
	gm.normal_texture = load("res://assets/hd/sprites/ground_tile_n.png")
	gm.normal_scale = 1.4
	gm.uv1_scale = Vector3(8.0, 8.0, 1.0)
	gm.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	gm.roughness = 0.9
	ground.material_override = gm
	add_child(ground)
	var sun: DirectionalLight3D = DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-48.0, -35.0, 0.0)
	sun.light_color = Color(0.7, 0.78, 1.0)
	sun.light_energy = 0.9
	sun.shadow_enabled = true
	add_child(sun)
	var lamp: OmniLight3D = OmniLight3D.new()
	lamp.position = Vector3(0.0, 3.0, 0.0)
	lamp.light_color = Color(1.0, 0.8, 0.55)
	lamp.light_energy = 3.0
	lamp.omni_range = 16.0
	lamp.shadow_enabled = true
	add_child(lamp)
	for i: int in 22:
		var id: String = IDS[i % IDS.size()]
		var tex: Texture2D = load("res://assets/hd/sprites/%s.png" % id)
		var sp: Sprite3D = Sprite3D.new()
		sp.texture = tex
		sp.hframes = 12 if id != "enemy_chaser" else 8
		sp.vframes = 4
		sp.frame = 0
		sp.pixel_size = 0.022
		sp.billboard = BaseMaterial3D.BILLBOARD_FIXED_Y
		sp.shaded = true
		sp.alpha_cut = SpriteBase3D.ALPHA_CUT_OPAQUE_PREPASS
		sp.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		var ang: float = i * 0.9
		var r: float = 3.0 + (i % 7) * 1.1
		sp.position = Vector3(cos(ang) * r, 1.6, sin(ang) * r)
		add_child(sp)
	var cam: Camera3D = Camera3D.new()
	cam.fov = 40.0
	add_child(cam)
	for a: float in ANGLES:
		var rad: float = deg_to_rad(a)
		cam.position = Vector3(0.0, sin(rad) * 17.0, cos(rad) * 17.0 + 0.001)
		cam.look_at(Vector3(0.0, 0.0, 0.0), Vector3.UP if a < 89.0 else Vector3.FORWARD)
		await get_tree().create_timer(0.6).timeout
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(ProjectSettings.globalize_path("res://tools/_preview/hd/04_3d/угол_%d.png" % int(a)))
	print("3D PROBE DONE")
	get_tree().quit()
