"""Шрифт реалистичного стиля: наши же буквы (assets/fonts/pixel_font) перерисованы гладкой «кистью»:
точки буквы соединяются толстыми скруглёнными мазками, край неровный, как краска пальцем. Метрики те же (x8),
поэтому вся вёрстка интерфейса остаётся на месте. Результат: assets/hd/fonts/horror_font.fnt + .png."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

S = 8            # пикселей нового шрифта на пиксель старого
PADG = 6         # поля вокруг глифа в атласе (мазок вылезает за клетку)
SRC_FNT = "assets/fonts/pixel_font.fnt"
SRC_PNG = "assets/fonts/pixel_font.png"
OUT_DIR = "assets/hd/fonts"


def parse(path: str):
    chars, common = [], {}
    for line in open(path, encoding="utf-8"):
        parts = dict(p.split("=", 1) for p in line.split()[1:] if "=" in p)
        if line.startswith("common"):
            common = parts
        elif line.startswith("char "):
            chars.append({k: int(v) for k, v in parts.items()})
    return chars, common


def brush(bits: np.ndarray, seed: int) -> np.ndarray:
    """bits - матрица 0/1 буквы. Возвращает альфу мазка (float 0..1) размером (h*S+2*PADG, w*S+2*PADG)."""
    h, w = bits.shape
    big = 4   # сглаживание: рисуем крупнее и уменьшаем
    im = Image.new("L", ((w * S + 2 * PADG) * big, (h * S + 2 * PADG) * big), 0)
    d = ImageDraw.Draw(im)

    def c(x, y):
        return ((x + 0.5) * S + PADG) * big, ((y + 0.5) * S + PADG) * big

    width = int(S * 0.98 * big)
    r = width / 2.0
    for y in range(h):
        for x in range(w):
            if not bits[y, x]:
                continue
            cx, cy = c(x, y)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
            if x + 1 < w and bits[y, x + 1]:
                d.line([c(x, y), c(x + 1, y)], fill=255, width=width)
            if y + 1 < h and bits[y + 1, x]:
                d.line([c(x, y), c(x, y + 1)], fill=255, width=width)
            for dx in (-1, 1):   # диагональ - только если нет соединения углом (иначе буква заплывает)
                if 0 <= x + dx < w and y + 1 < h and bits[y + 1, x + dx] and not bits[y, x + dx] and not bits[y + 1, x]:
                    d.line([c(x, y), c(x + dx, y + 1)], fill=255, width=width)
    a = np.asarray(im.resize((w * S + 2 * PADG, h * S + 2 * PADG), Image.LANCZOS)).astype(np.float32) / 255.0
    rng = np.random.default_rng(seed)
    noise = ndimage.gaussian_filter(rng.random(a.shape).astype(np.float32), 1.6)
    noise = (noise - noise.mean()) / (noise.std() + 1e-6)
    soft = ndimage.gaussian_filter(a, 1.2)
    return np.clip((soft + noise * 0.07 - 0.46) / 0.12, 0.0, 1.0)   # неровный, «рваный» край мазка


if __name__ == "__main__":
    chars, common = parse(SRC_FNT)
    src = np.asarray(Image.open(SRC_PNG).convert("RGBA"))
    glyphs = []
    for ch in chars:
        if ch["width"] == 0:
            glyphs.append(None)
            continue
        cell = src[ch["y"]:ch["y"] + ch["height"], ch["x"]:ch["x"] + ch["width"], 3] > 127
        glyphs.append(brush(cell, ch["id"]))
    gw = max(g.shape[1] for g in glyphs if g is not None)
    gh = max(g.shape[0] for g in glyphs if g is not None)
    cols = 16
    rows = (len(chars) + cols - 1) // cols
    atlas = np.zeros((rows * gh, cols * gw, 4), np.uint8)
    atlas[..., :3] = 255
    lines = ['info face="horror_font" size=%d bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0' % (int(common.get("lineHeight", 9)) * S - S),
             "common lineHeight=%d base=%d scaleW=%d scaleH=%d pages=1 packed=0" % (int(common["lineHeight"]) * S, int(common["base"]) * S, atlas.shape[1], atlas.shape[0]),
             'page id=0 file="horror_font.png"', "chars count=%d" % len(chars)]
    for i, (ch, g) in enumerate(zip(chars, glyphs)):
        x, y = (i % cols) * gw, (i // cols) * gh
        if g is None:
            lines.append("char id=%d x=0 y=0 width=0 height=0 xoffset=0 yoffset=0 xadvance=%d page=0 chnl=15" % (ch["id"], ch["xadvance"] * S))
            continue
        atlas[y:y + g.shape[0], x:x + g.shape[1], 3] = (g * 255).astype(np.uint8)
        lines.append("char id=%d x=%d y=%d width=%d height=%d xoffset=%d yoffset=%d xadvance=%d page=0 chnl=15" % (
            ch["id"], x, y, g.shape[1], g.shape[0], ch["xoffset"] * S - PADG, ch["yoffset"] * S - PADG, ch["xadvance"] * S))
    os.makedirs(OUT_DIR, exist_ok=True)
    Image.fromarray(atlas).save(os.path.join(OUT_DIR, "horror_font.png"))
    open(os.path.join(OUT_DIR, "horror_font.fnt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    # образец для просмотра глазами
    by_id = {ch["id"]: (ch, g) for ch, g in zip(chars, glyphs)}
    sample = ["ПОМОЙКА SURVIVORS 0123456789", "БЕЗ ЦАРАПИН: +50% ГОВНА", "ЖЩЫЮЯЁФЦЧШЪЬЭ ВОЛНА 3/15", "LET'S GO! FULLSCREEN: YEP"]
    im = np.zeros((len(sample) * 10 * S, 30 * 6 * S, 3), np.float32) + np.array([24, 14, 14], np.float32)
    for li, text in enumerate(sample):
        px = S
        for chv in text:
            ch, g = by_id.get(ord(chv), (None, None))
            if ch is None:
                continue
            if g is not None:
                y0, x0 = li * 10 * S + S + ch["yoffset"] * S - PADG, px + ch["xoffset"] * S - PADG
                reg = im[y0:y0 + g.shape[0], x0:x0 + g.shape[1]]
                reg[:] = reg * (1 - g[..., None]) + np.array([225, 215, 195], np.float32) * g[..., None]
            px += ch["xadvance"] * S
    Image.fromarray(im.astype(np.uint8)).save("tools/_preview/hd/01_пробы/шрифт_образец.png")
    print("font ok", len(chars), gw, gh)
