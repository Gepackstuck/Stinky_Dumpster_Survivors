shader_type canvas_item;
render_mode unshaded;
// Фильтры модификаторов волн поверх мира (под HUD). Мягкие: угрозы должны оставаться читаемыми.
// mode: 1 - дискотека (цветные пятна-прожекторы), 2 - канализация (зелёная жижа снизу), 3 - похмелье (двоится, плывёт).
uniform int mode = 0;
uniform float strength = 0.0;
uniform float time = 0.0;
uniform vec2 screen_px = vec2(480.0, 270.0);
uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;

float dither(vec2 p) {
	vec2 c = floor(p);
	return mod(c.x + c.y, 2.0) * 0.5 + mod(c.y, 2.0) * 0.25;
}

void fragment() {
	vec2 p = UV * screen_px;
	vec4 base = texture(screen_tex, SCREEN_UV);
	vec4 outc = base;
	if (mode == 1) {
		vec3 acc = vec3(0.0);
		vec3 cols[3] = vec3[](vec3(1.0, 0.06, 0.94), vec3(0.22, 1.0, 0.08), vec3(0.0, 0.94, 1.0));
		for (int i = 0; i < 3; i++) {
			float fi = float(i);
			vec2 c = vec2(0.5 + 0.38 * sin(time * (0.7 + fi * 0.3) + fi * 2.1), 0.5 + 0.35 * cos(time * (0.5 + fi * 0.25) + fi));
			float d = distance(UV * vec2(1.78, 1.0), c * vec2(1.78, 1.0));
			float spot = step(dither(p) * 0.6, 1.0 - smoothstep(0.12, 0.3, d));
			acc += cols[i] * spot;
		}
		outc.rgb = base.rgb + acc * 0.16 * strength;
	} else if (mode == 2) {
		float level = 0.62 + 0.03 * sin(UV.x * 18.0 + time * 2.0);
		float wet = step(level, UV.y) * step(dither(p) * 0.5, 0.5);
		outc.rgb = mix(base.rgb, base.rgb * vec3(0.55, 0.95, 0.35), 0.35 * strength);
		outc.rgb = mix(outc.rgb, vec3(0.3, 0.55, 0.1), wet * 0.22 * strength);
	} else if (mode == 3) {
		vec2 off = vec2(sin(time * 1.3) * 3.0, cos(time * 0.9) * 2.0) / screen_px;
		vec4 ghost = texture(screen_tex, SCREEN_UV + off);
		outc.rgb = mix(base.rgb, ghost.rgb, 0.3 * strength);
		outc.rgb *= mix(1.0, 0.85 + 0.15 * sin(time * 2.0), strength);
	}
	COLOR = vec4(outc.rgb, 1.0);
}
