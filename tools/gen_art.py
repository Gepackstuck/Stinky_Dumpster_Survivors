#!/usr/bin/env python3
"""Генератор арта «Кислотный Кринж» (см. ART_STYLE.md).

Рисует PNG от руки-кодом: кривые контуры (шум вершин), дизеринг, кислотная палитра.
Фиксированные seed → результат воспроизводим. Запуск из корня проекта:

    python3 tools/gen_art.py            # весь арт
    python3 tools/gen_art.py preview    # + превью в tools/_preview/art_preview.png (x8)

Требует Pillow и numpy.
"""
import math
import random
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw

# --- Палитра (ART_STYLE.md) ---
BLACK = (10, 10, 10)
GREEN = (57, 255, 20)
PINK = (255, 16, 240)
BROWN = (107, 62, 31)
YELLOW = (247, 255, 0)
RED = (255, 0, 51)
WHITE = (232, 232, 232)
BLUE = (30, 30, 255)
CYAN = (0, 240, 255)

SPRITES = "assets/sprites/"
UI = "assets/ui/"


# ---------------------------------------------------------------- примитивы
def new_img(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def new_mask(w, h):
    return Image.new("L", (w, h), 0)


def blob(mask, cx, cy, rx, ry, rng, jitter=0.8, n=16):
    """Кривой эллипс: радиус каждой вершины «дрожит»."""
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rng.uniform(-jitter, jitter) / max(rx, ry)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    ImageDraw.Draw(mask).polygon(pts, fill=255)


def rect(mask, x0, y0, x1, y1):
    ImageDraw.Draw(mask).rectangle([x0, y0, x1, y1], fill=255)


def poly(mask, pts):
    ImageDraw.Draw(mask).polygon(pts, fill=255)


def line(mask, pts, width=1):
    ImageDraw.Draw(mask).line(pts, fill=255, width=width)


def union(*masks):
    out = masks[0]
    for m in masks[1:]:
        out = ImageChops.lighter(out, m)
    return out


def minus(a, b):
    return ImageChops.subtract(a, b)


def inter(a, b):
    return ImageChops.darker(a, b)


def dilate4(mask):
    a = np.array(mask) > 0
    b = a.copy()
    b[1:] |= a[:-1]
    b[:-1] |= a[1:]
    b[:, 1:] |= a[:, :-1]
    b[:, :-1] |= a[:, 1:]
    return Image.fromarray((b * 255).astype("uint8"), "L")


def paint(img, mask, color):
    img.paste(color + (255,), (0, 0), mask.point(lambda v: 255 if v > 127 else 0))


def pattern(w, h, kind):
    """Маска дизеринг-шаблона на весь холст."""
    yy, xx = np.mgrid[0:h, 0:w]
    if kind == "checker":
        a = (xx + yy) % 2 == 0
    elif kind == "dots":
        a = (xx % 2 == 0) & (yy % 2 == 0)
    elif kind == "dots_off":
        a = (xx % 2 == 1) & (yy % 2 == 1)
    elif kind == "stripes":
        a = yy % 2 == 0
    elif kind == "stripes3":
        a = yy % 3 == 0
    else:
        raise ValueError(kind)
    return Image.fromarray((a * 255).astype("uint8"), "L")


def dither(img, region, color, kind="checker"):
    w, h = img.size
    paint(img, inter(region, pattern(w, h, kind)), color)


def px(img, x, y, color):
    if 0 <= x < img.size[0] and 0 <= y < img.size[1]:
        img.putpixel((x, y), color + (255,))


def noise(img, region, colors, count, rng):
    """«Грязные» одиночные пиксели внутри региона."""
    pts = np.argwhere(np.array(region) > 0)
    if len(pts) == 0:
        return
    for _ in range(count):
        y, x = pts[rng.randrange(len(pts))]
        px(img, int(x), int(y), rng.choice(colors))


def eye(img, cx, cy, r, pupil, pdx, pdy, rng):
    """Глаз из Paint: белок с чёрным кольцом и чёрный зрачок."""
    w, h = img.size
    ring = new_mask(w, h)
    blob(ring, cx, cy, r + 1, r + 1, rng, 0.3, 10)
    white = new_mask(w, h)
    blob(white, cx, cy, r, r, rng, 0.2, 10)
    paint(img, ring, BLACK)
    paint(img, white, WHITE)
    pm = new_mask(w, h)
    x0, y0 = cx + pdx - pupil // 2, cy + pdy - pupil // 2
    rect(pm, x0, y0, x0 + pupil - 1, y0 + pupil - 1)
    paint(img, pm, BLACK)


def finish(img, silhouette):
    """Чёрная обводка 1 px вокруг силуэта (рисуется ПОД заливкой)."""
    out = new_img(*img.size)
    paint(out, minus(dilate4(silhouette), silhouette), BLACK)
    out.alpha_composite(img)
    return out


# ---------------------------------------------------------------- игрок
def draw_player(frame, seed=7):
    """24x24: зелёный мутант: щупальце на голове, зубы, слюна, кишки из брюха."""
    rng = random.Random(seed)  # одинаковая «кривизна» в обоих кадрах
    w = h = 24
    bob = 1 if frame else 0
    body = new_mask(w, h)
    blob(body, 12, 12 + bob, 9, 8, rng, 1.3, 18)
    legs = new_mask(w, h)
    lx, rx = (8, 15) if not frame else (7, 16)
    rect(legs, lx, 19 + bob, lx + 2, 22)
    rect(legs, rx, 19 + bob, rx + 2, 22 - (1 if frame else 0))
    arms = new_mask(w, h)
    blob(arms, 3, 13 + (1 if frame else -1) + bob, 2, 3, rng, 0.4, 8)
    blob(arms, 21, 13 + (-1 if frame else 1) + bob, 2, 3, rng, 0.4, 8)
    # щупальце на голове (извивается)
    tent = new_mask(w, h)
    sway = 1 if frame else -1
    line(tent, [(12, 5 + bob), (12 + sway, 3 + bob), (12, 1 + bob), (12 - sway, 0)], 2)
    # кишки свисают из брюха
    guts = new_mask(w, h)
    gx = 11 + (1 if frame else 0)
    line(guts, [(gx, 17 + bob), (gx + 1, 20 + bob), (gx + (2 if frame else -1), 22)], 2)
    sil = union(body, legs, arms, tent, guts)

    img = new_img(w, h)
    paint(img, union(body, arms, tent), GREEN)
    paint(img, legs, BROWN)
    paint(img, guts, PINK)
    dither(img, guts, RED, "stripes")
    # тень справа-снизу
    yy, xx = np.mgrid[0:h, 0:w]
    sh = ((xx - 12) * 0.7 + (yy - 12 - bob)) > 6.0
    shade = Image.fromarray((sh * 255).astype("uint8"), "L")
    dither(img, inter(shade, union(body, arms)), BLACK, "checker")
    # присоски на щупальце, грязь, разрез на брюхе
    px(img, 12, 3 + bob, WHITE)
    noise(img, body, [BROWN, BROWN, YELLOW], 5, rng)
    m = new_mask(w, h)
    line(m, [(9, 16 + bob), (13, 17 + bob)], 1)
    paint(img, m, BLACK)
    # глаза: большой в прожилках и маленький злой
    eye(img, 8, 8 + bob, 3, 2, 1, 1, rng)
    px(img, 7, 6 + bob, RED)
    px(img, 6, 9 + bob, RED)
    eye(img, 16, 8 + bob, 2, 1, 0, 1, rng)
    # злые брови
    m = new_mask(w, h)
    line(m, [(5, 4 + bob), (10, 5 + bob)], 1)
    line(m, [(19, 5 + bob), (14, 5 + bob)], 1)
    paint(img, m, BLACK)
    # пасть с зубами и слюной
    m = new_mask(w, h)
    rect(m, 8, 13 + bob, 16, 14 + bob)
    paint(img, m, BLACK)
    for x in (9, 11, 13, 15):
        px(img, x, 13 + bob, WHITE)
    for x in (10, 12, 14):
        px(img, x, 14 + bob, WHITE)
    px(img, 15, 15 + bob, CYAN)
    return finish(img, sil)


# ---------------------------------------------------------------- враг: Гопник-Кальмар
def draw_squid(frame, seed=11):
    """16x16: мясной кальмар в красной кепке, глаз в прожилках, зубы, слюна, щупальца."""
    rng = random.Random(seed)
    w = h = 16
    dome = new_mask(w, h)
    blob(dome, 8, 6, 6, 5, rng, 0.7, 14)
    tent = new_mask(w, h)
    for i, x in enumerate((2, 5, 8, 11, 13)):
        sway = 1 if (i + frame) % 2 else 0
        rect(tent, x, 10, x + 1, 12)
        rect(tent, x + sway, 13, x + sway + (0 if i == 4 else 1), 14)
    cap = new_mask(w, h)
    rect(cap, 4, 1, 11, 3)
    rect(cap, 10, 3, 14, 4)  # козырёк
    sil = union(dome, tent, cap)

    img = new_img(w, h)
    paint(img, union(dome, tent), PINK)
    paint(img, cap, RED)
    low = new_mask(w, h)
    rect(low, 0, 9, 15, 15)
    dither(img, inter(low, tent), RED, "stripes")  # кровавые щупальца
    sh = new_mask(w, h)
    rect(sh, 11, 5, 14, 12)
    dither(img, minus(inter(sh, union(dome, tent)), cap), BLACK, "checker")
    # глаза: огромный в прожилках + маленький
    m = new_mask(w, h)
    rect(m, 3, 5, 6, 8)
    rect(m, 9, 6, 10, 7)
    paint(img, m, WHITE)
    for x, y in ((5, 6), (6, 6), (5, 7), (6, 7), (10, 7)):
        px(img, x, y, BLACK)
    px(img, 3, 5, RED)
    px(img, 4, 8, RED)
    px(img, 6, 5, RED)
    # злые брови
    for x, y in ((3, 4), (4, 4), (5, 5), (10, 5), (9, 5)):
        px(img, x, y, BLACK)
    # пасть с зубами и слюной
    m = new_mask(w, h)
    rect(m, 4, 9, 11, 9)
    paint(img, m, BLACK)
    for x in (4, 6, 8, 10):
        px(img, x, 9, WHITE)
    px(img, 7, 10, GREEN)
    px(img, 7, 11, GREEN) if frame else px(img, 6, 10, GREEN)
    # присоски
    for x in (2, 5, 8, 11):
        px(img, x, 11, WHITE)
    return finish(img, sil)


# ---------------------------------------------------------------- мелочи
def draw_projectile(frame):
    """4x4: жёлтая искра, на втором кадре мигает розовым."""
    img = new_img(4, 4)
    for y in range(4):
        for x in range(4):
            if (x in (0, 3)) and (y in (0, 3)):
                continue
            px(img, x, y, YELLOW)
    if frame:
        px(img, 1, 1, PINK)
        px(img, 2, 2, PINK)
    else:
        px(img, 2, 1, WHITE)
    return img


def draw_xp(frame):
    """4x4: зелёный пиксель XP с чёрной каймой, мигает белым."""
    img = new_img(4, 4)
    for y in range(4):
        for x in range(4):
            if (x in (0, 3)) and (y in (0, 3)):
                continue
            px(img, x, y, BLACK)
    for x, y in ((1, 1), (2, 1), (1, 2), (2, 2)):
        px(img, x, y, GREEN)
    px(img, 1 if frame else 2, 1 if frame else 2, WHITE)
    return img


# ---------------------------------------------------------------- пол: мерзкие стикеры
def stamp_poop(seed):
    """Куча говна с мухой и зелёной вонью. 10x13."""
    rng = random.Random(seed)
    w, h = 10, 13
    m1, m2, m3 = new_mask(w, h), new_mask(w, h), new_mask(w, h)
    blob(m1, 5, 10, 4, 2, rng, 0.5, 10)
    blob(m2, 5, 7, 3, 2, rng, 0.4, 8)
    blob(m3, 5, 5, 1.6, 1.6, rng, 0.3, 8)
    sil = union(m1, m2, m3)
    img = new_img(w, h)
    paint(img, sil, BROWN)
    yy, xx = np.mgrid[0:h, 0:w]
    sh = Image.fromarray((((xx + yy) > 14) * 255).astype("uint8"), "L")
    dither(img, inter(sh, sil), BLACK, "checker")
    px(img, 3, 9, YELLOW)
    px(img, 4, 6, YELLOW)
    for x, y in ((3, 0), (4, 1), (3, 2), (6, 0), (7, 1), (6, 2)):
        px(img, x, y, GREEN)
    out = finish(img, sil)
    px(out, 8, 3, BLACK)
    px(out, 9, 2, WHITE)
    return out


def stamp_guts(seed, length=18):
    """Извивающаяся кишка: розовая в красную полоску, с чёрным контуром."""
    rng = random.Random(seed)
    w, h = length + 6, 14
    x, y = 2, rng.randint(4, 9)
    pts = [(x, y)]
    while x < length:
        x += rng.randint(2, 4)
        y = max(2, min(h - 3, y + rng.randint(-3, 3)))
        pts.append((x, y))
    sil = new_mask(w, h)
    line(sil, pts, 3)
    for (a, b) in (pts[0], pts[-1]):
        blob(sil, a, b, 2, 2, rng, 0.3, 8)
    img = new_img(w, h)
    paint(img, sil, PINK)
    dither(img, sil, RED, "stripes")
    px(img, pts[1][0], pts[1][1], WHITE)
    return finish(img, sil)


def stamp_bone(seed):
    w, h = 9, 5
    sil = new_mask(w, h)
    rect(sil, 1, 2, 7, 2)
    for x in (0, 8):
        rect(sil, x, 1, x, 3)
    rect(sil, 1, 1, 1, 3)
    rect(sil, 7, 1, 7, 3)
    img = new_img(w, h)
    paint(img, sil, WHITE)
    px(img, 4, 2, YELLOW)
    return finish(img, sil)


def stamp_eyeball(seed):
    rng = random.Random(seed)
    w = h = 8
    sil = new_mask(w, h)
    blob(sil, 4, 4, 3, 3, rng, 0.3, 10)
    img = new_img(w, h)
    paint(img, sil, WHITE)
    for x, y in ((2, 2), (5, 3), (3, 6), (6, 5)):
        px(img, x, y, RED)
    m = new_mask(w, h)
    rect(m, 3, 3, 4, 4)
    paint(img, m, BLACK)
    px(img, 3, 3, GREEN)
    return finish(img, sil)


def stamp_puddle(seed, color, glow):
    rng = random.Random(seed)
    w, h = 24, 14
    sil = new_mask(w, h)
    blob(sil, 12, 7, 9, 4, rng, 1.3, 14)
    blob(sil, 8, 8, 5, 3, rng, 1.0, 10)
    img = new_img(w, h)
    paint(img, sil, color)
    dither(img, sil, BLACK, "dots")
    px(img, 9, 5, glow)
    px(img, 10, 5, glow)
    px(img, 15, 8, glow)
    return finish(img, sil)


def draw_ground(seed=5, size=128):
    """Бесшовная тайловая помойка: грязь, лужи крови и слизи, кишки, говно, кости, глаза."""
    rng = random.Random(seed)
    img = Image.new("RGBA", (size, size), BROWN + (255,))

    def region(fn):
        m = new_mask(size, size)
        for dx in (-size, 0, size):
            for dy in (-size, 0, size):
                fn(m, dx, dy)
        return m

    def put(spr, x, y):
        for dx in (-size, 0, size):
            for dy in (-size, 0, size):
                img.paste(spr, (x + dx, y + dy), spr)

    # тёмные пятна грязи (дизеринг)
    for _ in range(26):
        cx, cy = rng.randrange(size), rng.randrange(size)
        r, r2 = rng.randint(4, 9), rng.randint(2, 5)
        m = region(lambda m, dx, dy: blob(m, cx + dx, cy + dy, r, r2, rng, 1.2, 12))
        dither(img, m, BLACK, rng.choice(["dots", "dots", "checker"]))
    # трещины
    for _ in range(10):
        x, y = rng.randrange(size), rng.randrange(size)
        pts = [(x, y)]
        for _ in range(rng.randint(3, 5)):
            x += rng.randint(-3, 3)
            y += rng.randint(1, 3)
            pts.append((x, y))
        m = region(lambda m, dx, dy: line(m, [(a + dx, b + dy) for a, b in pts], 1))
        paint(img, m, BLACK)
    # лужи: кровь и ядовитая слизь
    put(stamp_puddle(1, RED, WHITE), 12, 20)
    put(stamp_puddle(2, RED, WHITE), 84, 96)
    put(stamp_puddle(3, GREEN, WHITE), 60, 40)
    put(stamp_puddle(4, GREEN, YELLOW), 20, 100)
    # кишки
    for i, (x, y) in enumerate(((30, 12), (88, 60), (8, 70), (70, 118))):
        put(stamp_guts(10 + i, rng.randint(14, 22)), x, y)
    # куски жизни
    for i, (x, y) in enumerate(((50, 86), (104, 24), (28, 52))):
        put(stamp_poop(20 + i), x, y)
    for i, (x, y) in enumerate(((100, 108), (40, 68), (118, 8), (72, 24))):
        put(stamp_bone(30 + i), x, y)
    for i, (x, y) in enumerate(((64, 70), (6, 110), (110, 78))):
        put(stamp_eyeball(40 + i), x, y)
    # мусор и мухи
    junk = [WHITE, YELLOW, CYAN, GREEN, BLUE]
    for _ in range(14):
        x, y = rng.randrange(size), rng.randrange(size)
        img.putpixel((x, y), rng.choice(junk) + (255,))
    for _ in range(36):
        img.putpixel((rng.randrange(size), rng.randrange(size)), BLACK + (255,))
    return img.convert("RGBA")


# ---------------------------------------------------------------- сборка
def sheet(frames):
    w, h = frames[0].size
    out = new_img(w * len(frames), h)
    for i, f in enumerate(frames):
        out.paste(f, (i * w, 0))
    return out


def build_step1():
    sheet([draw_player(0), draw_player(1)]).save(SPRITES + "player.png")
    sheet([draw_squid(0), draw_squid(1)]).save(SPRITES + "enemy_squid_gopnik.png")
    sheet([draw_projectile(0), draw_projectile(1)]).save(SPRITES + "projectile.png")
    sheet([draw_xp(0), draw_xp(1)]).save(SPRITES + "xp_pixel.png")
    draw_ground().save(SPRITES + "ground_tile.png")


def preview(paths, out="tools/_preview/art_preview.png", scale=8, bg=(150, 150, 150)):
    imgs = [Image.open(p).convert("RGBA") for p in paths]
    gap = 8
    W = sum(i.size[0] for i in imgs) * scale + gap * (len(imgs) + 1) * scale // 4
    H = max(i.size[1] for i in imgs) * scale + 2 * gap * scale // 4
    canvas = Image.new("RGBA", (W, H), bg + (255,))
    x = gap * scale // 4
    for i in imgs:
        big = i.resize((i.size[0] * scale, i.size[1] * scale), Image.NEAREST)
        canvas.alpha_composite(big, (x, gap * scale // 4))
        x += big.size[0] + gap * scale // 4
    canvas.save(out)


# ================================================================ ШАГ 2: шрифт, UI, иконки
FONTS = "assets/fonts/"

_G = {
    "A": ".###./#...#/#...#/#####/#...#/#...#/#...#",
    "B": "####./#...#/#...#/####./#...#/#...#/####.",
    "C": ".###./#...#/#..../#..../#..../#...#/.###.",
    "D": "####./#...#/#...#/#...#/#...#/#...#/####.",
    "E": "#####/#..../#..../####./#..../#..../#####",
    "F": "#####/#..../#..../####./#..../#..../#....",
    "G": ".###./#...#/#..../#.###/#...#/#...#/.###.",
    "H": "#...#/#...#/#...#/#####/#...#/#...#/#...#",
    "I": ".###./..#../..#../..#../..#../..#../.###.",
    "J": "..###/...#./...#./...#./...#./#..#./.##..",
    "K": "#...#/#..#./#.#../##.../#.#../#..#./#...#",
    "L": "#..../#..../#..../#..../#..../#..../#####",
    "M": "#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#",
    "N": "#...#/##..#/#.#.#/#..##/#...#/#...#/#...#",
    "O": ".###./#...#/#...#/#...#/#...#/#...#/.###.",
    "P": "####./#...#/#...#/####./#..../#..../#....",
    "Q": ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
    "R": "####./#...#/#...#/####./#.#../#..#./#...#",
    "S": ".####/#..../#..../.###./....#/....#/####.",
    "T": "#####/..#../..#../..#../..#../..#../..#..",
    "U": "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "V": "#...#/#...#/#...#/#...#/#...#/.#.#./..#..",
    "W": "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
    "X": "#...#/#...#/.#.#./..#../.#.#./#...#/#...#",
    "Y": "#...#/#...#/.#.#./..#../..#../..#../..#..",
    "Z": "#####/....#/...#./..#../.#.../#..../#####",
    "0": ".###./#...#/#..##/#.#.#/##..#/#...#/.###.",
    "1": "..#../.##../..#../..#../..#../..#../.###.",
    "2": ".###./#...#/....#/...#./..#../.#.../#####",
    "3": ".###./#...#/....#/..##./....#/#...#/.###.",
    "4": "...#./..##./.#.#./#..#./#####/...#./...#.",
    "5": "#####/#..../####./....#/....#/#...#/.###.",
    "6": ".###./#..../#..../####./#...#/#...#/.###.",
    "7": "#####/....#/...#./..#../.#.../.#.../.#...",
    "8": ".###./#...#/#...#/.###./#...#/#...#/.###.",
    "9": ".###./#...#/#...#/.####/....#/....#/.###.",
    ".": "...../...../...../...../...../.##../.##..",
    ",": "...../...../...../...../.##../..#../.#...",
    "!": "..#../..#../..#../..#../..#../...../..#..",
    "?": ".###./#...#/....#/...#./..#../...../..#..",
    ":": "...../.##../.##../...../.##../.##../.....",
    "-": "...../...../...../#####/...../...../.....",
    "+": "...../..#../..#../#####/..#../..#../.....",
    "/": "....#/....#/...#./..#../.#.../#..../#....",
    "%": "##..#/##..#/...#./..#../.#.../#..##/#..##",
    "(": "...#./..#../.#.../.#.../.#.../..#../...#.",
    ")": ".#.../..#../...#./...#./...#./..#../.#...",
    "'": "..#../..#../...../...../...../...../.....",
    '"': ".#.#./.#.#./...../...../...../...../.....",
    "*": "...../#.#.#/.###./#####/.###./#.#.#/.....",
    "=": "...../...../#####/...../#####/...../.....",
    "₽": "####./#...#/####./#...#/#..../###../#....",
    # кириллица (уникальные формы)
    "Б": "#####/#..../#..../####./#...#/#...#/####.",
    "Г": "#####/#..../#..../#..../#..../#..../#....",
    "Д": "..##./.#.#./.#.#./.#.#./.#.#./#####/#...#",
    "Ё": ".#.#./#####/#..../####./#..../#..../#####",
    "Ж": "#.#.#/#.#.#/.###./..#../.###./#.#.#/#.#.#",
    "З": ".###./#...#/....#/..##./....#/#...#/.###.",
    "И": "#...#/#...#/#..##/#.#.#/##..#/#...#/#...#",
    "Й": ".#.#./#...#/#..##/#.#.#/##..#/#...#/#...#",
    "Л": "..###/.#..#/.#..#/.#..#/.#..#/#...#/#...#",
    "П": "#####/#...#/#...#/#...#/#...#/#...#/#...#",
    "У": "#...#/#...#/.#.#./..#../..#../.#.../#....",
    "Ф": "..#../.###./#.#.#/#.#.#/.###./..#../..#..",
    "Ц": "#..#./#..#./#..#./#..#./#..#./#####/....#",
    "Ч": "#...#/#...#/#...#/.####/....#/....#/....#",
    "Ш": "#.#.#/#.#.#/#.#.#/#.#.#/#.#.#/#.#.#/#####",
    "Щ": "#.#.#/#.#.#/#.#.#/#.#.#/#.#.#/#####/....#",
    "Ъ": "##.../.#.../.#.../.###./.#..#/.#..#/.###.",
    "Ы": "#...#/#...#/#...#/###.#/#..##/#..##/###.#",
    "Ь": "#..../#..../#..../####./#...#/#...#/####.",
    "Э": ".###./#...#/....#/.####/....#/#...#/.###.",
    "Ю": "#..#./#.#.#/#.#.#/###.#/#.#.#/#.#.#/#..#.",
    "Я": ".####/#...#/#...#/.####/..#.#/.#..#/#...#",
}
_ALIAS = {"А": "A", "В": "B", "Е": "E", "К": "K", "М": "M", "Н": "H",
          "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X"}


def build_font(path_png=FONTS + "pixel_font.png", path_fnt=FONTS + "pixel_font.fnt"):
    """Пиксельный шрифт 5x7 (только заглавные; строчные рисуются теми же глифами) в формате BMFont."""
    glyphs = dict(_G)
    for cyr, lat in _ALIAS.items():
        glyphs[cyr] = glyphs[lat]
    names = sorted(glyphs.keys())
    cell_w, cell_h, cols = 6, 8, 16
    rows = (len(names) + cols - 1) // cols
    W, H = cols * cell_w, rows * cell_h
    atlas = new_img(W, H)
    pos = {}
    for i, ch in enumerate(names):
        cx, cy = (i % cols) * cell_w, (i // cols) * cell_h
        pos[ch] = (cx, cy)
        for y, row in enumerate(glyphs[ch].split("/")):
            for x, c in enumerate(row):
                if c == "#":
                    atlas.putpixel((cx + x, cy + y), (255, 255, 255, 255))
    atlas.save(path_png)
    codes = {}
    for ch in names:
        codes[ord(ch)] = pos[ch]
        if ch.lower() != ch:
            codes[ord(ch.lower())] = pos[ch]
    lines = [
        'info face="pixel_font" size=8 bold=0 italic=0 charset="" unicode=1 stretchH=100 smooth=0 aa=0 padding=0,0,0,0 spacing=0,0',
        f"common lineHeight=9 base=7 scaleW={W} scaleH={H} pages=1 packed=0",
        'page id=0 file="pixel_font.png"',
        f"chars count={len(codes) + 1}",
        "char id=32 x=0 y=0 width=0 height=0 xoffset=0 yoffset=0 xadvance=4 page=0 chnl=15",
    ]
    for code in sorted(codes):
        x, y = codes[code]
        adv = 3 if chr(code) in ".,!:'" else 6
        lines.append(f"char id={code} x={x} y={y} width=5 height=7 xoffset=0 yoffset=0 xadvance={adv} page=0 chnl=15")
    open(path_fnt, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return glyphs


def render_text(text, glyphs, color=WHITE, scale=1):
    """Превью-рендер строки шрифтом (для проверки читаемости)."""
    img = new_img(len(text) * 6 + 2, 9)
    x = 1
    for ch in text:
        g = glyphs.get(ch.upper())
        if g:
            for y, row in enumerate(g.split("/")):
                for xx, c in enumerate(row):
                    if c == "#":
                        px(img, x + xx, 1 + y, color)
        x += 4 if ch == " " else (3 if ch in ".,!:'" else 6)
    return img.resize((img.size[0] * scale, img.size[1] * scale), Image.NEAREST)


# ---------------------------------------------------------------- рамки и полоски
def wobbly_mask(w, h, inset, chamfer, rng, step=7, jit=1.0):
    x0, y0, x1, y1, c = inset, inset, w - 1 - inset, h - 1 - inset, chamfer
    base = [(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c),
            (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)]
    pts = []
    for i in range(len(base)):
        a, b = base[i], base[(i + 1) % len(base)]
        n = max(1, int(math.dist(a, b) // step))
        for k in range(n):
            tt = k / n
            x = a[0] + (b[0] - a[0]) * tt
            y = a[1] + (b[1] - a[1]) * tt
            if k > 0:
                x += rng.uniform(-jit, jit)
                y += rng.uniform(-jit, jit)
            pts.append((x, y))
    m = new_mask(w, h)
    poly(m, pts)
    return m


def draw_frame(w, h, ring, ring2, seed, chamfer=5, drips=4, eyes=True):
    """Кривая рамка: чёрный контур, кишечная полоса (ring/ring2), чёрная начинка с грязью."""
    rng = random.Random(seed)
    img = new_img(w, h)
    c = chamfer
    m0 = wobbly_mask(w, h, 0, c, rng)
    m1 = wobbly_mask(w, h, 1, max(c - 1, 1), rng)
    m2 = wobbly_mask(w, h, 3, max(c - 2, 1), rng)
    paint(img, m0, BLACK)
    paint(img, m1, ring)
    dither(img, m1, ring2, "stripes")
    paint(img, m2, BLACK)
    dither(img, m2, BROWN, "dots_off")
    noise(img, m2, [GREEN, CYAN, PINK, YELLOW], max(3, w * h // 500), rng)
    for _ in range(drips):  # слизь капает сверху
        x = rng.randrange(8, w - 8)
        for k in range(rng.randint(2, 5)):
            px(img, x, 3 + k, GREEN)
    if eyes:
        for (ex, ey) in ((-2, -2), (w - 7, -2)):
            e = stamp_eyeball(rng.randint(0, 99))
            img.paste(e, (ex, ey), e)
    return img


def bar_under(w, h, color):
    rng = random.Random(1)
    img = new_img(w, h)
    paint(img, wobbly_mask(w, h, 0, 2, rng, jit=0), BLACK)
    paint(img, wobbly_mask(w, h, 1, 1, rng, jit=0), color)
    paint(img, wobbly_mask(w, h, 2, 1, rng, jit=0), BLACK)
    return img


def bar_fill(w, h, color, light, seed):
    rng = random.Random(seed)
    img = new_img(w, h)
    full = new_mask(w, h)
    rect(full, 0, 0, w - 1, h - 1)
    paint(img, full, color)
    for x in range(0, w, 2):
        px(img, x, 0, light)
    low = new_mask(w, h)
    rect(low, 0, h - 2, w - 1, h - 1)
    dither(img, low, BLACK, "checker")
    noise(img, full, [BLACK, light], w // 6, rng)
    return img


# ---------------------------------------------------------------- иконки
def draw_heart(size=14, seed=3):
    rng = random.Random(seed)
    w = h = size
    m = new_mask(w, h)
    r = size // 4 + 1
    blob(m, r + 1, r + 1, r, r, rng, 0.3, 10)
    blob(m, size - r - 2, r + 1, r, r, rng, 0.3, 10)
    poly(m, [(1, r + 1), (size - 2, r + 1), (size // 2, size - 2)])
    img = new_img(w, h)
    paint(img, m, RED)
    sh = Image.fromarray((((np.mgrid[0:h, 0:w][1] + np.mgrid[0:h, 0:w][0]) > size) * 255).astype("uint8"), "L")
    dither(img, inter(sh, m), BLACK, "checker")
    px(img, 3, 3, WHITE)
    px(img, 4, 3, WHITE)
    s = new_mask(w, h)
    line(s, [(size // 2 - 1, 4), (size // 2 + 1, size - 5)], 1)
    paint(img, s, BLACK)  # шов
    for yy in (5, 7):
        px(img, size // 2 - 2, yy, BLACK)
        px(img, size // 2 + 1, yy, BLACK)
    return finish(img, m)


def icon_speed():
    """Кроссовок и зелёное облако пердежа."""
    rng = random.Random(21)
    w = h = 16
    foot = new_mask(w, h)
    rect(foot, 5, 9, 14, 12)
    rect(foot, 5, 3, 9, 9)
    cloud = new_mask(w, h)
    blob(cloud, 3, 11, 2, 2, rng, 0.5, 8)
    blob(cloud, 1, 8, 1.5, 1.5, rng, 0.4, 8)
    sil = union(foot, cloud)
    img = new_img(w, h)
    paint(img, foot, WHITE)
    paint(img, cloud, GREEN)
    dither(img, cloud, BLACK, "checker")
    rect(m := new_mask(w, h), 5, 11, 14, 12)
    paint(img, m, RED)
    for x in (11, 12, 13):
        px(img, x, 9, BLACK)
    m2 = new_mask(w, h)
    rect(m2, 6, 4, 8, 4)
    paint(img, m2, PINK)
    out = finish(img, sil)
    for y in (2, 5, 14):  # линии скорости
        for x in range(0, 3):
            px(out, x, y, YELLOW)
    return out


def icon_regen():
    """Сердце, заштопанное пластырем, с кишкой."""
    w = h = 16
    img = new_img(w, h)
    heart = draw_heart(14)
    img.paste(heart, (1, 0), heart)
    m = new_mask(w, h)
    rect(m, 6, 4, 10, 6)
    rect(m, 7, 3, 9, 7)
    paint(img, m, WHITE)
    for x, y in ((7, 5), (8, 5), (9, 5)):
        px(img, x, y, BLACK)
    px(img, 8, 4, BLACK)
    px(img, 8, 6, BLACK)
    g = new_mask(w, h)
    line(g, [(5, 13), (7, 15), (10, 14), (12, 15)], 1)
    paint(img, g, PINK)
    return img


def icon_double():
    """Две злые искры с хвостами."""
    w = h = 16
    img = new_img(w, h)
    for (cx, cy) in ((4, 4), (10, 10)):
        tail = new_mask(w, h)
        line(tail, [(cx - 3, cy - 3), (cx, cy)], 2)
        paint(img, tail, PINK)
        core = new_mask(w, h)
        rect(core, cx - 1, cy - 1, cx + 3, cy + 3)
        sil = union(core, tail)
        paint(img, core, YELLOW)
        out = finish(img, sil)
        px(out, cx + 1, cy + 1, RED)
        img = out
    return img


def icon_goblin():
    """Рожа лут-гоблина: зелёная, жадные жёлтые глаза, клыки."""
    rng = random.Random(33)
    w = h = 16
    head = new_mask(w, h)
    blob(head, 8, 9, 5, 5, rng, 0.6, 12)
    ears = new_mask(w, h)
    poly(ears, [(3, 7), (0, 3), (4, 5)])
    poly(ears, [(12, 5), (15, 3), (13, 7)])
    sil = union(head, ears)
    img = new_img(w, h)
    paint(img, sil, GREEN)
    sh = new_mask(w, h)
    rect(sh, 10, 6, 15, 14)
    dither(img, inter(sh, sil), BLACK, "checker")
    for (x, y) in ((6, 7), (10, 7)):
        m = new_mask(w, h)
        rect(m, x - 1, y - 1, x + 1, y + 1)
        paint(img, m, YELLOW)
        px(img, x, y, BLACK)
    m = new_mask(w, h)
    line(m, [(5, 11), (8, 12), (11, 11)], 1)
    paint(img, m, BLACK)
    px(img, 6, 12, WHITE)
    px(img, 10, 12, WHITE)
    px(img, 8, 13, CYAN)
    return finish(img, sil)


# ---------------------------------------------------------------- фон экрана смерти
def draw_corpse():
    rng = random.Random(55)
    w, h = 64, 40
    img = new_img(w, h)
    pud = stamp_puddle(5, RED, WHITE).resize((52, 26), Image.NEAREST)
    img.paste(pud, (6, 12), pud)
    body = new_mask(w, h)
    blob(body, 30, 18, 20, 10, rng, 1.5, 18)
    img2 = new_img(w, h)
    paint(img2, body, GREEN)
    yy, xx = np.mgrid[0:h, 0:w]
    sh = Image.fromarray((((xx * 0.5 + yy) > 30) * 255).astype("uint8"), "L")
    dither(img2, inter(sh, body), BLACK, "checker")
    noise(img2, body, [BROWN, YELLOW], 8, rng)
    # кишки наружу
    g = stamp_guts(77, 20)
    sil = body
    out = finish(img2, sil)
    out.paste(g, (28, 22), g)
    # глаза-крестики и язык
    eye(out, 20, 13, 4, 1, 0, 0, rng)
    eye(out, 32, 12, 3, 1, 0, 0, rng)
    for (cx, cy) in ((20, 13), (32, 12)):
        for d in (-1, 0, 1):
            px(out, cx + d, cy + d, BLACK)
            px(out, cx + d, cy - d, BLACK)
    m = new_mask(w, h)
    line(m, [(14, 20), (22, 22), (30, 20)], 1)
    paint(out, m, BLACK)
    for x in range(21, 25):
        for y in range(22, 25):
            px(out, x, y, PINK)
    img.alpha_composite(out)
    for (x, y) in ((8, 6), (50, 4), (44, 30)):
        px(img, x, y, BLACK)
        px(img, x + 1, y - 1, WHITE)
    return img


def draw_death_bg(seed=9):
    rng = random.Random(seed)
    W, H = 320, 180
    img = Image.new("RGBA", (W, H), BROWN + (255,))
    d = ImageDraw.Draw(img)
    for y in range(0, 72):  # небо: полосы, как в Paint
        if y < 22:
            c = YELLOW
        elif y < 50:
            c = YELLOW if y % 2 == 0 else WHITE
        else:
            c = PINK if y % 2 == 0 else YELLOW
        d.line([(0, y), (W, y)], fill=c)
    for y in range(62, 74):  # серая дизеринг-полоса горизонта
        for x in range(W):
            img.putpixel((x, y), (BLACK if (x + y) % 2 == 0 else WHITE) + (255,))
    ground = new_mask(W, H)
    rect(ground, 0, 74, W, H)
    dither(img, inter(ground, pattern(W, H, "stripes3")), BLACK, "dots")
    for y in range(74, 80):  # кровавая кромка
        for x in range(W):
            if (x + y) % 2 == 0:
                img.putpixel((x, y), RED + (255,))
    for _ in range(300):
        img.putpixel((rng.randrange(W), rng.randrange(74, H)), rng.choice([BLACK, BLACK, YELLOW, GREEN, WHITE]) + (255,))
    # солнце
    sun = new_mask(W, H)
    blob(sun, 38, 58, 13, 13, rng, 0.8, 18)
    paint(img, dilate4(sun), BLACK)
    paint(img, sun, WHITE)
    # чёрные клякса-«деревья»
    for (cx, cy, rx) in ((250, 70, 17), (140, 80, 10)):
        m = new_mask(W, H)
        blob(m, cx, cy - 7, rx, 5, rng, 1.2, 12)
        rect(m, cx - 1, cy - 4, cx + 1, cy + 6)
        paint(img, m, BLACK)
    # надгробие
    gm = new_mask(W, H)
    rect(gm, 262, 100, 288, 128)
    blob(gm, 275, 100, 13, 9, rng, 0.8, 12)
    paint(img, dilate4(gm), BLACK)
    paint(img, gm, WHITE)
    dither(img, gm, BLACK, "checker")
    cr = new_mask(W, H)
    rect(cr, 274, 96, 276, 112)
    rect(cr, 269, 101, 281, 103)
    paint(img, cr, RED)
    for x in (266, 280, 284):
        for k in range(rng.randint(3, 6)):
            px(img, x, 114 + k, RED)
    # труп игрока и мусор вокруг
    corpse = draw_corpse()
    img.paste(corpse, (110, 92), corpse)
    for i, (x, y) in enumerate(((60, 120), (200, 132), (30, 150), (300, 150))):
        b = stamp_bone(60 + i)
        img.paste(b, (x, y), b)
    for i, (x, y) in enumerate(((84, 108), (210, 104), (150, 140))):
        e = stamp_eyeball(70 + i)
        img.paste(e, (x, y), e)
    for i, (x, y) in enumerate(((20, 100), (230, 118))):
        pp = stamp_poop(80 + i)
        img.paste(pp, (x, y), pp)
    return img


def draw_dim():
    img = new_img(2, 2)
    px(img, 0, 0, BLACK)
    px(img, 1, 1, BLACK)
    return img


def build_step2():
    glyphs = build_font()
    for name, fn in (("perk_speed", icon_speed), ("perk_regen", icon_regen),
                     ("perk_double_shot", icon_double), ("perk_loot_goblin", icon_goblin),
                     ("hud_heart", lambda: draw_heart(14))):
        fn().save(UI + name + ".png")
    draw_frame(84, 112, PINK, RED, 101, chamfer=6, drips=5).save(UI + "card.png")
    draw_frame(84, 112, YELLOW, GREEN, 101, chamfer=6, drips=7).save(UI + "card_hover.png")
    draw_frame(96, 22, RED, PINK, 202, chamfer=4, drips=3, eyes=False).save(UI + "button.png")
    draw_frame(96, 22, YELLOW, GREEN, 202, chamfer=4, drips=5, eyes=False).save(UI + "button_hover.png")
    bar_under(72, 10, PINK).save(UI + "hp_bar_under.png")
    bar_fill(68, 6, RED, PINK, 5).save(UI + "hp_bar_fill.png")
    bar_under(224, 10, GREEN).save(UI + "xp_bar_under.png")
    bar_fill(220, 6, GREEN, WHITE, 6).save(UI + "xp_bar_fill.png")
    draw_death_bg().save(UI + "death_bg.png")
    draw_dim().save(UI + "dim_checker.png")
    return glyphs


def preview_ui(glyphs):
    S = 4
    gray = (90, 90, 90, 255)
    canvas = Image.new("RGBA", (330 * 3, 190 * 3), gray)
    def put(path, x, y, s=3):
        im = Image.open(path).convert("RGBA")
        im = im.resize((im.size[0] * s, im.size[1] * s), Image.NEAREST)
        canvas.alpha_composite(im, (x, y))
    put(UI + "card.png", 10, 10)
    put(UI + "card_hover.png", 270, 10)
    put(UI + "button.png", 540, 10)
    put(UI + "button_hover.png", 540, 90)
    x = 540
    for n in ("perk_speed", "perk_regen", "perk_double_shot", "perk_loot_goblin", "hud_heart"):
        put(UI + n + ".png", x, 180)
        x += 16 * 3 + 8 if n != "hud_heart" else 0
    put(UI + "hp_bar_under.png", 540, 260)
    put(UI + "hp_bar_fill.png", 546, 266)
    put(UI + "xp_bar_under.png", 10, 480)
    put(UI + "xp_bar_fill.png", 16, 486)
    lines = ["ТЫ УМЕР, КАК ЛОХ", "ЕЩЁ РАЗ  УБИТО: 17", "ДВОЙНОЙ ВЫСТРЕЛ +1 СНАРЯД", "ЛУТ-ГОБЛИН РАДИУС +100%", "ШЩЪЫЬЭЮЯ ЖЦЧФБГДЛПУЙ 0123456789"]
    y = 310
    for s in lines:
        im = render_text(s, glyphs, WHITE, 3)
        canvas.alpha_composite(im, (540, y))
        y += 34
    canvas.save("tools/_preview/ui_preview.png")
    bg = Image.open(UI + "death_bg.png")
    bg.resize((960, 540), Image.NEAREST).save("tools/_preview/death_bg_preview.png")


if __name__ == "__main__":
    build_step1()
    g = build_step2()
    if "preview" in sys.argv:
        preview([SPRITES + n for n in ("player.png", "enemy_squid_gopnik.png", "projectile.png", "xp_pixel.png")])
        gt = Image.open(SPRITES + "ground_tile.png").convert("RGBA")
        scene = Image.new("RGBA", (320, 180))
        for i in range(3):
            for j in range(2):
                scene.paste(gt, (i * 128 - 20, j * 128 - 30))
        pl = Image.open(SPRITES + "player.png").convert("RGBA").crop((0, 0, 24, 24))
        en = Image.open(SPRITES + "enemy_squid_gopnik.png").convert("RGBA")
        for k, (x, y) in enumerate(((40, 30), (250, 40), (60, 140), (230, 130), (100, 60), (200, 90))):
            f = en.crop(((k % 2) * 16, 0, (k % 2) * 16 + 16, 16))
            scene.paste(f, (x, y), f)
        scene.paste(pl, (148, 78), pl)
        scene.resize((960, 540), Image.NEAREST).save("tools/_preview/scene_mock.png")
        preview_ui(g)
    print("ok")
