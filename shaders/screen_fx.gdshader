shader_type canvas_item;
// Поверх мира под HUD: тёмные углы (глубина, взгляд в центр) и красная пульсация краёв при уроне.
// Центр экрана не трогаем никогда - там бой, он должен читаться.
uniform float vignette = 0.22;
uniform float hurt = 0.0;          // 0..1, гаснет после удара
uniform vec2 screen_px = vec2(480.0, 270.0);

void fragment() {
	vec2 uv = UV - 0.5;
	uv.x *= screen_px.x / screen_px.y;
	float d = length(uv);
	float corner = smoothstep(0.55, 1.0, d);
	vec2 cell = floor(UV * screen_px);
	float dith = mod(cell.x + cell.y, 2.0) * 0.06;   // пиксельный дизеринг, без гладкого градиента
	float dark = clamp(corner * vignette + dith * corner, 0.0, 1.0);
	float red = smoothstep(0.45, 0.95, d) * hurt;
	COLOR = vec4(mix(vec3(0.02, 0.0, 0.03), vec3(0.9, 0.0, 0.1), red / max(dark + red, 0.001)), max(dark, red * 0.55));
}
