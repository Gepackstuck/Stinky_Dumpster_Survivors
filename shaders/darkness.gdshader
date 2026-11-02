shader_type canvas_item;
// Тьма модификатора «ОТРУБИЛИ СВЕТ»: всё чёрное, кроме пятна вокруг героя; край пятна - пиксельный дизеринг.
uniform vec2 center = vec2(0.5, 0.5);   // центр пятна в UV экрана
uniform float radius_px = 70.0;          // радиус в пикселях вьюпорта
uniform vec2 screen_px = vec2(480.0, 270.0);
uniform float strength = 0.0;            // 0..1 - плавное включение

void fragment() {
	vec2 p = UV * screen_px;
	float d = distance(p, center * screen_px);
	float edge = 14.0;
	float t = clamp((d - radius_px) / edge, 0.0, 1.0);
	vec2 cell = floor(p);
	float dither = mod(cell.x + cell.y, 2.0) * 0.5 + mod(cell.y, 2.0) * 0.25;   // шахматка: рваный край
	float dark = step(dither, t) * 0.96;
	COLOR = vec4(0.02, 0.01, 0.03, dark * strength);
}
