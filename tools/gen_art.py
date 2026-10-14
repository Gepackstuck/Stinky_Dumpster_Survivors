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
    """Бесшовная тайловая земля: только грязь двух тонов. Пятна крови/слизи/кишки/кости
    рассыпает скрипт ground.gd случайно в каждом забеге (см. draw_decals)."""
    rng = random.Random(seed)
    img = Image.new("RGBA", (size, size), BROWN + (255,))

    def region(fn):
        m = new_mask(size, size)
        for dx in (-size, 0, size):
            for dy in (-size, 0, size):
                fn(m, dx, dy)
        return m

    DARK = (74, 42, 20)
    LIGHT = (128, 78, 40)
    for col, n in ((DARK, 20), (LIGHT, 14)):
        for _ in range(n):
            cx, cy = rng.randrange(size), rng.randrange(size)
            r, r2 = rng.randint(5, 12), rng.randint(3, 6)
            m = region(lambda m, dx, dy: blob(m, cx + dx, cy + dy, r, r2, rng, 1.2, 12))
            dither(img, m, col, rng.choice(["dots", "dots_off", "checker"]))
    for _ in range(40):
        img.putpixel((rng.randrange(size), rng.randrange(size)), rng.choice([DARK, LIGHT]) + (255,))
    return img.convert("RGBA")



# ---------------------------------------------------------------- проволока и декали
WIRE_W, WIRE_H = 48, 16


def _wire_base(kind, frame=0, seed=1):
    """Сегмент проволоки 48x16: два столба по краям и три провода между ними (низ смотрит на арену)."""
    rng = random.Random(seed)
    img = new_img(WIRE_W, WIRE_H)
    sil = new_mask(WIRE_W, WIRE_H)
    post_col = (120, 120, 126) if kind != "electric" else (60, 60, 70)
    for x in (0, 46):
        m = new_mask(WIRE_W, WIRE_H); rect(m, x, 1, x + 1, 15); sil = union(sil, m); paint(img, m, post_col)
        px(img, x, 1, YELLOW if kind == "electric" else BROWN)
    ys = (4, 8, 12)
    col = {"barbed": GREY, "poop": GREY, "electric": CYAN, "razor": (200, 200, 215), "guts": PINK, "rags": GREY, "slime": GREEN, "fire": (90, 90, 96)}[kind]
    for i, y in enumerate(ys):
        pts = [(2, y)]
        for x in range(6, 47, 6):
            pts.append((x, y + (1 if (x // 6 + i) % 2 == 0 else -1)))
        m = new_mask(WIRE_W, WIRE_H); line(m, pts, 1); sil = union(sil, m); paint(img, m, col)
    if kind == "barbed":
        for y in ys:
            for x in range(8, 44, 8):
                for (dx, dy) in ((0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)): px(img, x + dx, y + dy, BLACK if (dx or dy) else RED)
    elif kind == "poop":
        for y in ys:
            for x in range(4, 44, 5):
                if rng.random() < 0.7:
                    s = new_mask(WIRE_W, WIRE_H); blob(s, x + rng.randint(-1, 1), y, 2, 2, rng, 0.6, 8)
                    sil = union(sil, s); paint(img, s, BROWN); px(img, x, y - 1, BLACK)
        for x in (10, 22, 34, 41):
            for k in range(rng.randint(2, 5)): px(img, x, 5 + k, BROWN)
        for _ in range(5): px(img, rng.randint(3, 44), rng.randint(0, 14), BLACK)
        for x in (14, 30): px(img, x, 0, GREEN)
    elif kind == "razor":  # егоза: витки лезвий с кровью
        for x in range(4, 44, 4):
            m = new_mask(WIRE_W, WIRE_H); blob(m, x, 8, 3, 6, rng, 0.3, 10); sil = union(sil, m)
            px(img, x - 3, 8, WHITE); px(img, x + 3, 8, WHITE); px(img, x, 2, WHITE); px(img, x, 14, WHITE)
            if rng.random() < 0.4: px(img, x + 3, 8, RED); px(img, x, 14, RED)
        for _ in range(6): px(img, rng.randint(3, 44), rng.randint(2, 13), RED)
    elif kind == "guts":  # гирлянда из кишок и глаз
        for x in range(3, 45, 9):
            m = new_mask(WIRE_W, WIRE_H); line(m, [(x, 4), (x + 3, 11), (x + 6, 4)], 2); sil = union(sil, m); paint(img, m, PINK); dither(img, m, RED, "dots")
            e = stamp_eyeball(seed + x); img.paste(e, (x + 1, 8), e)
        for x in (6, 24, 40): px(img, x, 14, RED); px(img, x, 15, RED)
        for _ in range(4): px(img, rng.randint(3, 44), rng.randint(1, 5), BLACK)
    elif kind == "rags":  # тряпки и трусы на проволоке
        for x in range(5, 44, 10):
            c = rng.choice([WHITE, BLUE, PINK, YELLOW])
            m = new_mask(WIRE_W, WIRE_H); poly(m, [(x, 4), (x + 7, 4), (x + 6, 12), (x + 4, 10), (x + 3, 14), (x + 1, 12)]); sil = union(sil, m); paint(img, m, c); dither(img, m, BROWN, "dots_off")
            if c == WHITE: px(img, x + 3, 9, BROWN); px(img, x + 4, 10, BROWN)
        flies(img, rng, 4, 2, 45, 0, 14)
    elif kind == "slime":  # едкая слизь: капает, светится
        for x in range(5, 44, 6):
            m = new_mask(WIRE_W, WIRE_H); blob(m, x, 8, 3, 4, rng, 0.6, 8); sil = union(sil, m); paint(img, m, GREEN); dither(img, m, YELLOW, "dots")
            for k in range(rng.randint(2, 6)): px(img, x, 12 + k % 4, GREEN)
        for _ in range(4): px(img, rng.randint(3, 44), rng.randint(1, 13), WHITE)
    elif kind == "fire":  # горящая проволока: 2 кадра пламени
        frng = random.Random(500 + frame)
        for x in range(4, 44, 4):
            h = frng.randint(3, 8)
            for k in range(h):
                px(img, x + frng.randint(-1, 1), 10 - k, RED if k < h // 2 else (YELLOW if k < h - 1 else WHITE))
        for x in range(4, 44, 6): px(img, x, 12, BLACK)
    else:  # electric: два кадра с разными молниями
        frng = random.Random(100 + frame)
        for y in ys:
            for x in range(4, 44, 7):
                if frng.random() < 0.55:
                    px(img, x, y - 1, YELLOW); px(img, x + 1, y - 2, WHITE); px(img, x + 1, y + 1, YELLOW)
        x = frng.randint(10, 36)
        pts = [(x, 0)]
        for k in range(1, 6): pts.append((x + frng.randint(-3, 3), k * 3))
        m = new_mask(WIRE_W, WIRE_H); line(m, pts, 1); sil = union(sil, m); paint(img, m, YELLOW)
        px(img, 23, 6, RED); px(img, 24, 6, RED)  # знак «молния»-пятно
    out = new_img(WIRE_W, WIRE_H)
    paint(out, minus(dilate4(sil), sil), BORDER_OUTLINE)
    out.alpha_composite(img)
    return out


def draw_wire_sheet():
    # порядок = WireKind в arena_border.gd; у анимированных (ток, огонь) два кадра подряд
    cells = [_wire_base("barbed", 0, 1), _wire_base("poop", 0, 2), _wire_base("razor", 0, 4),
             _wire_base("guts", 0, 5), _wire_base("rags", 0, 6), _wire_base("slime", 0, 7),
             _wire_base("electric", 0, 3), _wire_base("electric", 1, 3),
             _wire_base("fire", 0, 8), _wire_base("fire", 1, 8)]
    sheet = new_img(WIRE_W * len(cells), WIRE_H)
    for i, c in enumerate(cells): sheet.paste(c, (i * WIRE_W, 0))
    return sheet


def _dc(w=24, h=24): return new_img(w, h), new_mask(w, h)


def decal_vomit(seed):
    rng = random.Random(seed); img, _ = _dc()
    m = new_mask(24, 24)
    for _ in range(4): blob(m, rng.randint(7, 17), rng.randint(8, 16), rng.randint(3, 6), rng.randint(2, 4), rng, 1, 10)
    paint(img, m, YELLOW); dither(img, m, GREEN, "dots")
    for _ in range(8): px(img, rng.randint(4, 20), rng.randint(5, 19), rng.choice([RED, WHITE, BROWN]))
    return img


def decal_splat(seed):
    rng = random.Random(seed); img, _ = _dc()
    m = new_mask(24, 24); blob(m, 12, 12, 4, 4, rng, 1, 10)
    for _ in range(9):
        a = rng.uniform(0, 6.28); r = rng.randint(5, 10)
        line(m, [(12, 12), (12 + int(r * math.cos(a)), 12 + int(r * math.sin(a)))], 1)
    paint(img, m, RED); dither(img, m, BLACK, "dots_off")
    for _ in range(10): px(img, rng.randint(1, 22), rng.randint(1, 22), RED)
    return img


def decal_footprints(seed):
    rng = random.Random(seed); img, _ = _dc()
    for k in range(4):
        x, y = 4 + k * 5, 6 + (k % 2) * 8
        m = new_mask(24, 24); blob(m, x, y, 2, 3, rng, 0.5, 8)
        paint(img, m, BLACK if k % 2 else BROWN)
        for dx in (-2, 0, 2): px(img, x + dx, y - 4, BLACK)
    return img


def decal_butts(seed):
    rng = random.Random(seed); img, _ = _dc()
    for _ in range(5):
        x, y = rng.randint(3, 19), rng.randint(3, 19)
        for k in range(3): px(img, x + k, y, WHITE)
        px(img, x + 3, y, YELLOW if rng.random() < 0.5 else RED)
    for _ in range(4): px(img, rng.randint(2, 21), rng.randint(2, 21), GREY)
    return img


def decal_can(seed):
    rng = random.Random(seed); img, _ = _dc()
    m = new_mask(24, 24); rect(m, 9, 8, 15, 16); paint(img, m, rng.choice([CYAN, YELLOW, PINK])); dither(img, m, WHITE, "stripes3")
    o = new_mask(24, 24); rect(o, 9, 7, 15, 7); rect(o, 9, 17, 15, 17); paint(img, o, GREY)
    px(img, 12, 12, BLACK); px(img, 13, 13, BLACK)
    for k in range(4): px(img, 16 + k, 14 + k % 2, BROWN)
    return img


def decal_teeth(seed):
    rng = random.Random(seed); img, _ = _dc()
    for _ in range(7):
        x, y = rng.randint(3, 19), rng.randint(3, 19)
        m = new_mask(24, 24); rect(m, x, y, x + 1, y + 2); paint(img, m, WHITE); px(img, x, y + 2, RED if rng.random() < 0.5 else WHITE)
    return img


def decal_glass(seed):
    rng = random.Random(seed); img, _ = _dc()
    for _ in range(9):
        x, y = rng.randint(3, 20), rng.randint(3, 20)
        px(img, x, y, CYAN); px(img, x + 1, y + 1, WHITE); px(img, x + 1, y, BLUE)
    return img


def decal_rat(seed):
    rng = random.Random(seed); img, _ = _dc()
    m = new_mask(24, 24); blob(m, 12, 12, 6, 3, rng, 0.6, 10); paint(img, m, GREY); dither(img, m, BLACK, "dots")
    l = new_mask(24, 24); line(l, [(18, 12), (23, 9)], 1); paint(img, l, PINK)
    px(img, 8, 11, RED); px(img, 7, 11, WHITE)
    for x in range(10, 16): px(img, x, 15, RED)
    return img


def decal_slime_trail(seed):
    rng = random.Random(seed); img, _ = _dc()
    pts = [(1, 12)]
    for x in range(5, 24, 4): pts.append((x, 12 + rng.randint(-4, 4)))
    m = new_mask(24, 24); line(m, pts, 2); paint(img, m, GREEN); dither(img, m, YELLOW, "dots")
    s = new_mask(24, 24); blob(s, 22, pts[-1][1], 2, 2, rng, 0.5, 8); paint(img, s, GREEN)
    return img


def decal_scorch(seed):
    rng = random.Random(seed); img, _ = _dc()
    m = new_mask(24, 24); blob(m, 12, 12, 8, 6, rng, 1.5, 12)
    paint(img, m, BLACK); dither(img, m, GREY, "dots_off")
    for _ in range(6): px(img, rng.randint(5, 18), rng.randint(6, 17), RED)
    return img


def decal_skull(seed):
    rng = random.Random(seed); img, _ = _dc()
    m = new_mask(24, 24); blob(m, 12, 11, 5, 5, rng, 0.5, 10); rect(m, 9, 14, 15, 17); paint(img, m, WHITE)
    for x in (10, 14): px(img, x, 10, BLACK); px(img, x, 11, BLACK)
    px(img, 12, 13, BLACK)
    for x in (10, 12, 14): px(img, x, 16, BLACK)
    return img


def decal_hair(seed):
    rng = random.Random(seed); img, _ = _dc()
    for _ in range(4):
        pts = [(rng.randint(4, 18), rng.randint(4, 18))]
        for _ in range(3): pts.append((pts[-1][0] + rng.randint(-3, 3), pts[-1][1] + rng.randint(-3, 3)))
        m = new_mask(24, 24); line(m, pts, 1); paint(img, m, rng.choice([BLUE, BLACK, PINK]))
    return img


def decal_pills(seed):
    rng = random.Random(seed); img, _ = _dc()
    for _ in range(6):
        x, y = rng.randint(3, 19), rng.randint(3, 19)
        px(img, x, y, rng.choice([PINK, YELLOW, CYAN, GREEN, RED])); px(img, x + 1, y, WHITE)
    return img


def decal_crack_goo(seed):
    rng = random.Random(seed); img, _ = _dc()
    pts = [(2, 4)]
    for _ in range(5): pts.append((pts[-1][0] + rng.randint(2, 5), pts[-1][1] + rng.randint(1, 4)))
    m = new_mask(24, 24); line(m, pts, 1); paint(img, m, BLACK)
    for (x, y) in pts[1:]: px(img, x, y + 1, GREEN)
    return img


def decal_tongue(seed):
    rng = random.Random(seed); img, _ = _dc()
    m = new_mask(24, 24); blob(m, 12, 12, 8, 3, rng, 0.8, 10); paint(img, m, PINK); dither(img, m, RED, "dots")
    l = new_mask(24, 24); line(l, [(5, 12), (19, 12)], 1); paint(img, l, RED)
    return img


_DECAL_FNS = (decal_vomit, decal_splat, decal_footprints, decal_butts, decal_can, decal_teeth, decal_glass,
              decal_rat, decal_slime_trail, decal_scorch, decal_skull, decal_hair, decal_pills, decal_crack_goo, decal_tongue)


DECAL_CELL = 24


def draw_decals():
    """Лист декалей пола 24x24: лужи, кишки, говно, кости, глаза, потроха. Скрипт рассыпает их случайно."""
    items = []
    for i, (c, g) in enumerate(((RED, WHITE), (RED, PINK), (GREEN, WHITE), (GREEN, YELLOW), (PINK, WHITE), (BLUE, CYAN))):
        items.append(stamp_puddle(100 + i, c, g))
    for i in range(5): items.append(stamp_guts(110 + i, 14 + i * 2))
    for i in range(4): items.append(stamp_poop(120 + i))
    for i in range(4): items.append(stamp_bone(130 + i))
    for i in range(4): items.append(stamp_eyeball(140 + i))
    for fn in _DECAL_FNS:
        items.append(fn(200 + len(items)))
        items.append(fn(300 + len(items)))
    sheet = new_img(DECAL_CELL * len(items), DECAL_CELL)
    for i, spr in enumerate(items):
        sheet.paste(spr, (i * DECAL_CELL + (DECAL_CELL - spr.width) // 2, (DECAL_CELL - spr.height) // 2), spr)
    return sheet


# ---------------------------------------------------------------- граница арены
SEG_W, SEG_H = 48, 32  # один сегмент границы (низ сегмента смотрит на арену)
GREY = (90, 90, 96)
DARKGREEN = (20, 120, 12)
BRICK = (150, 40, 30)


def _seg_base():
    return new_img(SEG_W, SEG_H), new_mask(SEG_W, SEG_H)


BORDER_OUTLINE = (44, 24, 12)  # тёмная земля вместо чёрной обводки


def _seg_finish(img, sil):
    out = new_img(*img.size)
    paint(out, minus(dilate4(sil), sil), BORDER_OUTLINE)
    out.alpha_composite(img)
    return out


def R(img, sil, x0, y0, x1, y1, col, dcol=None, kind="checker"):
    m = new_mask(SEG_W, SEG_H); rect(m, x0, y0, x1, y1)
    paint(img, m, col)
    if dcol: dither(img, m, dcol, kind)
    return union(sil, m)


def B(img, sil, cx, cy, rx, ry, rng, col, dcol=None, kind="dots", jit=1.0):
    m = new_mask(SEG_W, SEG_H); blob(m, cx, cy, rx, ry, rng, jit, 12)
    paint(img, m, col)
    if dcol: dither(img, m, dcol, kind)
    return union(sil, m)


def P(img, sil, pts, col, dcol=None, kind="checker"):
    m = new_mask(SEG_W, SEG_H); poly(m, pts)
    paint(img, m, col)
    if dcol: dither(img, m, dcol, kind)
    return union(sil, m)


def L(img, sil, pts, col, w=1):
    m = new_mask(SEG_W, SEG_H); line(m, pts, w)
    paint(img, m, col)
    return union(sil, m)


def flies(img, rng, n=6, x0=2, x1=45, y0=2, y1=20):
    for _ in range(n): px(img, rng.randint(x0, x1), rng.randint(y0, y1), BLACK)


def drips(img, rng, xs, y0, col=GREEN):
    for x in xs:
        for k in range(rng.randint(2, 6)): px(img, x, y0 + k, col)


def item_toilet(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 28, 6, 40, 16, WHITE, GREY, "dots")
    sil = B(img, sil, 20, 22, 11, 6, rng, WHITE, GREY)
    sil = B(img, sil, 19, 19, 7, 3, rng, GREEN, YELLOW)
    sil = R(img, sil, 14, 27, 26, 30, WHITE)
    eye(img, 19, 19, 2, 2, 0, 0, rng); drips(img, rng, [30, 36], 16, BROWN); flies(img, rng, 4)
    return _seg_finish(img, sil)


def item_cart(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = L(img, sil, [(6, 8), (12, 24), (38, 24), (42, 10)], GREY, 2)
    for x in range(10, 40, 4): sil = L(img, sil, [(x, 12), (x + 1, 24)], GREY)
    sil = L(img, sil, [(6, 8), (2, 6)], GREY, 2)
    sil = B(img, sil, 22, 14, 11, 4, rng, PINK, RED, "checker")
    sil = B(img, sil, 14, 28, 3, 3, rng, BLACK); sil = B(img, sil, 36, 28, 3, 3, rng, BLACK)
    eye(img, 26, 13, 2, 2, 0, 0, rng); flies(img, rng, 5)
    return _seg_finish(img, sil)


def item_tv(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 6, 8, 41, 29, GREY, BLACK, "dots")
    sil = R(img, sil, 9, 11, 32, 26, CYAN, WHITE, "stripes3")
    sil = L(img, sil, [(18, 8), (12, 1)], GREY); sil = L(img, sil, [(28, 8), (36, 1)], GREY)
    eye(img, 20, 18, 4, 2, 1, 0, rng)
    for y in range(11, 26, 2): px(img, 30, y, RED)
    for x in (35, 38): px(img, x, 14, GREEN); px(img, x, 18, YELLOW)
    return _seg_finish(img, sil)


def item_washer(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 9, 4, 38, 30, WHITE, GREY, "dots")
    sil = B(img, sil, 23, 18, 8, 8, rng, CYAN, BLUE, "checker", 0.4)
    sil = B(img, sil, 23, 18, 5, 5, rng, BLACK, GREEN, "dots_off", 0.4)
    for x in (12, 16): px(img, x, 8, RED)
    drips(img, rng, [12, 20, 33], 26, BROWN)
    return _seg_finish(img, sil)


def item_fridge(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 8, 2, 28, 30, WHITE, GREY, "dots")
    sil = P(img, sil, [(28, 2), (40, 5), (40, 28), (28, 30)], GREY, BLACK, "dots")
    sil = R(img, sil, 30, 8, 37, 24, GREEN, YELLOW, "checker")
    for y in (12, 20): sil = L(img, sil, [(8, y), (28, y)], GREY)
    drips(img, rng, [31, 34, 36], 24); eye(img, 33, 16, 2, 2, 0, 1, rng); flies(img, rng, 6, 8, 40, 0, 12)
    return _seg_finish(img, sil)


def item_mattress(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 3, 14, 44, 27, YELLOW, BROWN, "stripes3")
    for x in range(6, 42, 6): px(img, x, 16, BLACK); px(img, x, 25, BLACK)
    sil = B(img, sil, 20, 20, 8, 4, rng, RED, BROWN)
    for k in range(5): sil = L(img, sil, [(38 + k, 14), (38 + (k % 2) * 3, 8)], GREY)
    flies(img, rng, 5, 2, 45, 4, 14)
    return _seg_finish(img, sil)


def item_bags(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    for cx, cy, r in ((10, 22, 7), (23, 21, 8), (36, 23, 7), (17, 12, 6), (30, 11, 6)):
        sil = B(img, sil, cx, cy, r, r - 1, rng, BLACK, GREY, "dots_off")
        sil = L(img, sil, [(cx, cy - r), (cx - 1, cy - r - 2)], BLACK, 2)
    drips(img, rng, [8, 24, 33], 26); flies(img, rng, 8, 2, 45, 0, 10)
    for _ in range(6): px(img, rng.randint(6, 40), rng.randint(8, 28), rng.choice([GREEN, YELLOW, PINK]))
    return _seg_finish(img, sil)


def item_boxes(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 3, 16, 22, 30, (170, 120, 60), BROWN, "stripes")
    sil = R(img, sil, 24, 12, 44, 30, (170, 120, 60), BROWN, "checker")
    sil = R(img, sil, 9, 4, 24, 16, (170, 120, 60), BROWN, "dots")
    for (x0, x1, y) in ((3, 22, 22), (24, 44, 20), (9, 24, 9)): sil = L(img, sil, [(x0, y), (x1, y)], YELLOW)
    px(img, 14, 24, BLACK); px(img, 15, 24, BLACK); px(img, 34, 22, RED); px(img, 35, 23, RED)
    drips(img, rng, [12, 30], 28, BROWN)
    return _seg_finish(img, sil)


def item_bathtub(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 3, 12, 44, 26, WHITE, GREY, "dots")
    sil = R(img, sil, 5, 11, 42, 16, GREEN, YELLOW, "checker")
    for x in (7, 38): sil = R(img, sil, x, 26, x + 2, 30, GREY)
    sil = L(img, sil, [(40, 12), (40, 4), (46, 4)], GREY, 2)
    for _ in range(5): px(img, rng.randint(6, 40), rng.randint(8, 12), WHITE)
    eye(img, 20, 13, 2, 2, 0, 0, rng); eye(img, 28, 14, 2, 2, 1, 0, rng)
    drips(img, rng, [12, 24], 26, RED)
    return _seg_finish(img, sil)


def item_graves(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = B(img, sil, 24, 28, 22, 4, rng, BROWN, BLACK)
    sil = R(img, sil, 5, 12, 14, 28, GREY, BLACK, "dots"); sil = B(img, sil, 9, 12, 5, 4, rng, GREY, BLACK)
    sil = R(img, sil, 30, 10, 40, 28, GREY, BLACK, "dots_off"); sil = B(img, sil, 35, 10, 5, 4, rng, GREY)
    sil = R(img, sil, 21, 4, 24, 26, BROWN); sil = R(img, sil, 17, 9, 28, 12, BROWN)
    for x in (8, 10): px(img, x, 17, BLACK); px(img, x, 19, BLACK)
    drips(img, rng, [7, 33], 18, RED); px(img, 22, 7, RED)
    return _seg_finish(img, sil)


def item_hand(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = B(img, sil, 24, 28, 20, 5, rng, BROWN, BLACK)
    sil = R(img, sil, 21, 12, 27, 28, PINK, RED, "stripes3")
    sil = R(img, sil, 19, 6, 29, 13, PINK, RED, "dots")
    for x in (19, 22, 25, 28): sil = L(img, sil, [(x, 6), (x - 1 + (x % 3), 1)], PINK)
    sil = L(img, sil, [(30, 9), (35, 5)], PINK, 2)
    px(img, 24, 20, GREEN); px(img, 23, 22, BLACK); flies(img, rng, 5, 10, 38, 0, 8)
    return _seg_finish(img, sil)


def item_pipes(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    for y in (7, 15, 23):
        sil = R(img, sil, 2, y, 45, y + 5, GREY, BLACK, "stripes")
        for x in (10, 24, 38): sil = R(img, sil, x, y - 1, x + 2, y + 6, BLACK)
    drips(img, rng, [14, 30, 41], 12); drips(img, rng, [20], 20, BROWN); drips(img, rng, [8, 34], 28, RED)
    return _seg_finish(img, sil)


def item_cones(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    for cx in (11, 27):
        sil = P(img, sil, [(cx, 6), (cx - 6, 27), (cx + 6, 27)], RED, WHITE, "stripes3")
        sil = R(img, sil, cx - 8, 27, cx + 8, 30, BLACK)
    sil = B(img, sil, 38, 24, 7, 6, rng, BLACK, GREY); sil = B(img, sil, 38, 24, 3, 3, rng, BROWN)
    px(img, 11, 12, YELLOW); drips(img, rng, [26, 30], 14, GREEN); flies(img, rng, 4)
    return _seg_finish(img, sil)


def item_bottles(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    for i, x in enumerate(range(5, 42, 7)):
        col = (BLUE, GREEN, YELLOW)[i % 3]
        sil = R(img, sil, x, 14 + i % 2 * 4, x + 4, 28, col, WHITE, "dots_off")
        sil = R(img, sil, x + 1, 8 + i % 2 * 4, x + 3, 14 + i % 2 * 4, col)
    for _ in range(14): px(img, rng.randint(2, 45), rng.randint(26, 30), CYAN)
    drips(img, rng, [9, 30], 24, YELLOW)
    return _seg_finish(img, sil)


def item_gutpile(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    for cx, cy, rx, ry in ((14, 22, 11, 7), (30, 20, 12, 8), (22, 12, 9, 5)):
        sil = B(img, sil, cx, cy, rx, ry, rng, PINK, RED, "stripes")
    for _ in range(6):
        x = rng.randint(6, 38); y = rng.randint(10, 26)
        sil = L(img, sil, [(x, y), (x + rng.randint(-6, 6), y + rng.randint(-3, 3)), (x + rng.randint(-8, 8), y + rng.randint(-4, 5))], RED, 2)
    eye(img, 16, 19, 2, 2, 0, 0, rng); eye(img, 33, 17, 2, 2, 1, 0, rng); flies(img, rng, 8)
    return _seg_finish(img, sil)


def item_stove(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 6, 12, 41, 30, GREY, BLACK, "dots")
    sil = R(img, sil, 8, 16, 39, 28, BLACK, GREY, "dots_off")
    for x in (13, 23, 33): sil = B(img, sil, x, 12, 4, 2, rng, BLACK, GREY); 
    for x in (13, 33):
        for k in range(5): px(img, x + rng.randint(-1, 1), 10 - k, RED if k < 2 else YELLOW)
    eye(img, 23, 22, 3, 2, 0, 0, rng); drips(img, rng, [10, 37], 28, BROWN)
    return _seg_finish(img, sil)


def item_crates(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    for x0, y0, x1, y1 in ((3, 18, 20, 30), (22, 18, 40, 30), (12, 6, 30, 18)):
        sil = R(img, sil, x0, y0, x1, y1, (170, 120, 60), BROWN, "stripes")
        sil = L(img, sil, [(x0, y0), (x1, y1)], BLACK); sil = L(img, sil, [(x0, y1), (x1, y0)], BLACK)
    px(img, 8, 22, RED); px(img, 31, 24, GREEN); px(img, 20, 10, PINK)
    drips(img, rng, [14, 34], 28, GREEN); flies(img, rng, 4)
    return _seg_finish(img, sil)


def item_mannequin(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = B(img, sil, 14, 10, 5, 5, rng, PINK, WHITE, "dots")
    sil = R(img, sil, 8, 15, 20, 30, PINK, WHITE, "stripes3")
    sil = L(img, sil, [(28, 8), (40, 26)], PINK, 3); sil = L(img, sil, [(34, 24), (46, 20)], PINK, 3)
    sil = B(img, sil, 40, 10, 3, 3, rng, PINK, WHITE)
    eye(img, 12, 9, 1, 1, 0, 0, rng); eye(img, 17, 9, 2, 2, 0, 0, rng)
    drips(img, rng, [10, 16], 22, RED)
    return _seg_finish(img, sil)


def item_vending(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 12, 1, 36, 30, RED, BLACK, "dots")
    sil = R(img, sil, 14, 4, 28, 22, CYAN, BLUE, "stripes3")
    for y in (8, 14, 20):
        for x in (16, 21, 26): px(img, x, y, rng.choice([YELLOW, GREEN, PINK, WHITE]))
    sil = R(img, sil, 30, 6, 34, 18, BLACK); sil = R(img, sil, 14, 25, 34, 28, BLACK)
    drips(img, rng, [18, 25], 22, GREEN); eye(img, 32, 22, 1, 1, 0, 0, rng)
    return _seg_finish(img, sil)


def item_bike(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    for cx in (11, 36):
        sil = B(img, sil, cx, 22, 8, 8, rng, GREY, None, "dots", 0.3)
        sil = B(img, sil, cx, 22, 6, 6, rng, BLACK, None, "dots", 0.3)
        for a in range(0, 360, 60):
            sil = L(img, sil, [(cx, 22), (cx + int(6 * math.cos(math.radians(a))), 22 + int(6 * math.sin(math.radians(a))))], GREY)
    sil = L(img, sil, [(11, 22), (20, 10), (36, 22), (28, 10), (20, 10)], RED, 2)
    sil = L(img, sil, [(26, 8), (31, 8)], BLACK, 2)
    px(img, 20, 8, YELLOW); drips(img, rng, [30], 24, BROWN)
    return _seg_finish(img, sil)


def item_bigeye(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = L(img, sil, [(24, 30), (24, 12)], GREY, 3)
    sil = B(img, sil, 24, 10, 11, 9, rng, WHITE, None, "dots", 0.6)
    eye(img, 24, 10, 6, 4, 2, 1, rng)
    for (x, y) in ((16, 8), (30, 13), (20, 15), (28, 5)): px(img, x, y, RED)
    sil = L(img, sil, [(14, 6), (8, 2)], RED); sil = L(img, sil, [(34, 8), (40, 4)], RED)
    drips(img, rng, [24], 20, RED)
    return _seg_finish(img, sil)


def item_bigpoop(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = B(img, sil, 24, 25, 17, 5, rng, BROWN, BLACK, "dots")
    sil = B(img, sil, 24, 19, 12, 5, rng, BROWN, BLACK, "checker")
    sil = B(img, sil, 24, 14, 8, 4, rng, BROWN, BLACK, "dots_off")
    sil = P(img, sil, [(20, 11), (24, 3), (28, 11)], BROWN, BLACK, "dots")
    eye(img, 21, 18, 2, 2, 0, 0, rng); eye(img, 28, 18, 2, 2, 0, 0, rng)
    for x in (10, 38, 44): sil = L(img, sil, [(x, 14), (x + 2, 10), (x, 6), (x + 2, 2)], GREEN)
    flies(img, rng, 9)
    return _seg_finish(img, sil)


def item_sewer(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = R(img, sil, 8, 3, 40, 14, GREY, BLACK, "stripes")
    sil = B(img, sil, 24, 14, 9, 3, rng, BLACK)
    sil = R(img, sil, 16, 14, 32, 29, GREEN, YELLOW, "stripes3")
    sil = B(img, sil, 24, 28, 18, 3, rng, GREEN, WHITE, "dots")
    for x in (10, 38): sil = R(img, sil, x - 2, 1, x + 2, 16, BLACK)
    flies(img, rng, 6, 4, 44, 0, 10); eye(img, 24, 20, 2, 2, 0, 0, rng)
    return _seg_finish(img, sil)


def item_coffin(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = P(img, sil, [(6, 16), (12, 4), (36, 4), (42, 16), (36, 29), (12, 29)], BROWN, BLACK, "dots")
    sil = P(img, sil, [(10, 17), (14, 8), (34, 8), (38, 17), (34, 26), (14, 26)], BLACK, BROWN, "dots_off")
    sil = R(img, sil, 38, 3, 46, 8, BROWN, BLACK, "stripes")
    sil = L(img, sil, [(18, 17), (28, 17)], WHITE, 2); sil = L(img, sil, [(23, 12), (23, 24)], WHITE, 2)
    for x in (20, 26): px(img, x, 12, PINK)
    drips(img, rng, [14, 30], 26, RED); flies(img, rng, 4)
    return _seg_finish(img, sil)


def item_tentacles(seed):
    rng = random.Random(seed); img, sil = _seg_base()
    sil = B(img, sil, 24, 27, 16, 4, rng, BLACK, GREY, "dots_off")
    for x in (12, 20, 28, 36):
        pts = [(x, 28)]
        yy = 28
        for _ in range(4):
            yy -= rng.randint(5, 7); pts.append((x + rng.randint(-5, 5), yy))
        sil = L(img, sil, pts, PINK, 3)
        for (a, b) in pts[1:]: px(img, a, b, WHITE); px(img, a, b + 2, WHITE)
    eye(img, 24, 24, 2, 2, 0, 0, rng); drips(img, rng, [30], 22, GREEN)
    return _seg_finish(img, sil)



def seg_dumpster(seed=1):
    rng = random.Random(seed)
    img, sil = _seg_base()
    body = new_mask(SEG_W, SEG_H); rect(body, 4, 8, 43, 28)
    lid = new_mask(SEG_W, SEG_H); poly(lid, [(2, 8), (45, 6), (46, 11), (3, 12)])
    sil = union(body, lid)
    paint(img, body, GREEN); dither(img, body, DARKGREEN, "checker")
    paint(img, lid, BLACK); dither(img, lid, GREY, "stripes")
    for x in (10, 18, 26, 34):  # ребра
        line(sil, [(x, 13), (x, 27)], 1); px(img, x, 14, BLACK)
        for y in range(13, 28): px(img, x, y, BLACK)
    for y in range(18, 21):  # ржавая слизь
        for x in range(4, 44):
            if (x + y) % 3 == 0: px(img, x, y, BROWN)
    for x in (12, 30):  # колёса
        w = new_mask(SEG_W, SEG_H); blob(w, x, 28, 3, 3, rng, 0.5, 8)
        sil = union(sil, w); paint(img, w, BLACK)
    for _ in range(5):  # торчит мусор и руки
        x = rng.randrange(6, 40); px(img, x, 5 - rng.randint(0, 2), rng.choice([PINK, YELLOW, WHITE]))
    for x in (7, 22, 39):  # капли
        for k in range(rng.randint(2, 5)): px(img, x, 12 + k, GREEN)
    e = stamp_eyeball(seed); img.paste(e, (20, 14), e)
    return _seg_finish(img, sil)


def seg_car(seed=2):
    rng = random.Random(seed)
    img, sil = _seg_base()
    body = new_mask(SEG_W, SEG_H); poly(body, [(2, 26), (2, 17), (9, 15), (15, 8), (32, 8), (39, 15), (46, 17), (46, 26)])
    sil = body
    paint(img, body, BLACK); dither(img, body, GREY, "dots")
    win = new_mask(SEG_W, SEG_H); poly(win, [(16, 10), (24, 10), (24, 15), (12, 15)]); poly(win, [(26, 10), (31, 10), (36, 15), (26, 15)])
    paint(img, win, CYAN); dither(img, win, BLACK, "dots_off")
    for _ in range(14): px(img, rng.randint(3, 44), rng.randint(16, 25), rng.choice([BROWN, RED]))
    for x in (11, 36):  # колёса без шин
        w = new_mask(SEG_W, SEG_H); blob(w, x, 26, 4, 4, rng, 0.5, 8)
        sil = union(sil, w); paint(img, w, BLACK); px(img, x, 26, GREY)
    for fx in (14, 22, 30):  # огонь
        for k in range(rng.randint(4, 7)):
            px(img, fx + rng.randint(-1, 1), 8 - k, RED if k < 3 else YELLOW)
    return _seg_finish(img, sil)


def seg_corpses(seed=3):
    rng = random.Random(seed)
    img, sil = _seg_base()
    heap = new_mask(SEG_W, SEG_H)
    for cx, cy, rx, ry in ((12, 22, 10, 6), (28, 20, 11, 7), (38, 24, 7, 5), (22, 14, 9, 5)):
        blob(heap, cx, cy, rx, ry, rng, 1.5, 12)
    sil = heap
    paint(img, heap, PINK); dither(img, heap, GREEN, "stripes3"); dither(img, heap, RED, "dots_off")
    for _ in range(6):  # торчащие конечности
        x = rng.randint(6, 40); line(sil, [(x, 14), (x + rng.randint(-3, 3), 6)], 2)
    paint(img, sil, PINK); dither(img, sil, RED, "dots_off")
    for _ in range(18): px(img, rng.randint(4, 44), rng.randint(10, 28), rng.choice([RED, BLACK, YELLOW]))
    for (ex, ey) in ((10, 20), (26, 17), (36, 23)):
        eye(img, ex, ey, 2, 2, 0, 0, rng)
    return _seg_finish(img, sil)


def seg_fence(seed=4):
    rng = random.Random(seed)
    img, sil = _seg_base()
    sil = new_mask(SEG_W, SEG_H)
    x = 1
    while x < SEG_W - 4:
        w, top = rng.randint(4, 6), rng.randint(4, 10)
        plank = new_mask(SEG_W, SEG_H)
        poly(plank, [(x, 30), (x, top + 3), (x + w // 2, top), (x + w, top + 3), (x + w, 30)])
        sil = union(sil, plank)
        paint(img, plank, (170, 120, 60)); dither(img, plank, BROWN, "stripes")
        px(img, x + 1, rng.randint(14, 24), BLACK)  # гвоздь
        x += w + 1
    line(sil, [(0, 14), (47, 17)], 1); line(sil, [(0, 24), (47, 22)], 1)
    for y in (14, 24):
        for xx in range(0, SEG_W):
            px(img, xx, y + (xx % 5 == 0), GREY)
    for xx in range(2, SEG_W, 6): px(img, xx, 5, RED)  # колючка с кровью
    return _seg_finish(img, sil)


def seg_wall(seed=5):
    rng = random.Random(seed)
    img, sil = _seg_base()
    wall = new_mask(SEG_W, SEG_H); rect(wall, 0, 4, 47, 30)
    sil = wall
    paint(img, wall, BRICK); dither(img, wall, BLACK, "dots")
    for y in range(4, 30, 5):
        for xx in range(0, SEG_W): px(img, xx, y, BLACK)
        off = 0 if (y // 5) % 2 == 0 else 5
        for xx in range(off, SEG_W, 10):
            for k in range(5): px(img, xx, y + k, BLACK)
    for _ in range(3):  # выбитые кирпичи
        bx, by = rng.randrange(2, 40), rng.randrange(6, 24)
        m = new_mask(SEG_W, SEG_H); rect(m, bx, by, bx + 6, by + 3); paint(img, m, BLACK)
    for xx in range(8, 40, 7): px(img, xx, 5, GREEN)
    for k, ch in enumerate([(6, 14), (7, 15), (8, 16), (9, 15), (10, 14)]): px(img, ch[0] + 14, ch[1] + 4, PINK)  # граффити-каракуля
    for _ in range(10): px(img, rng.randint(1, 46), rng.randint(5, 29), RED)
    return _seg_finish(img, sil)


def seg_tires(seed=6):
    rng = random.Random(seed)
    img, sil = _seg_base()
    sil = new_mask(SEG_W, SEG_H)
    for cx, cy, r in ((9, 24, 7), (24, 25, 7), (38, 24, 7), (16, 15, 6), (31, 15, 6)):
        t_ = new_mask(SEG_W, SEG_H); blob(t_, cx, cy, r, r, rng, 0.6, 12)
        hole = new_mask(SEG_W, SEG_H); blob(hole, cx, cy, r // 2, r // 2, rng, 0.3, 8)
        sil = union(sil, t_)
        paint(img, t_, BLACK); dither(img, t_, GREY, "dots")
        paint(img, hole, BROWN)
    for _ in range(12): px(img, rng.randint(2, 45), rng.randint(8, 30), rng.choice([GREEN, YELLOW, WHITE]))
    for x in (14, 30):  # мусорный пакет
        b = new_mask(SEG_W, SEG_H); blob(b, x, 8, 5, 3, rng, 1, 8); sil = union(sil, b); paint(img, b, BLUE); dither(img, b, BLACK, "checker")
    return _seg_finish(img, sil)


def seg_barrels(seed=7):
    rng = random.Random(seed)
    img, sil = _seg_base()
    sil = new_mask(SEG_W, SEG_H)
    for cx in (9, 22, 36):
        b = new_mask(SEG_W, SEG_H); rect(b, cx - 4, 10, cx + 4, 29); sil = union(sil, b)
        paint(img, b, YELLOW); dither(img, b, GREEN, "checker")
        for y in (14, 24):
            for x in range(cx - 4, cx + 5): px(img, x, y, BLACK)
        for k in range(3): px(img, cx - 1 + k, 18 + k, BLACK)  # знак «череп» каракулей
        for k in range(rng.randint(3, 7)): px(img, cx + rng.randint(-4, 4), 29, GREEN)
        for y in range(10, 10 + rng.randint(4, 8)): px(img, cx + 5, y, GREEN)
    return _seg_finish(img, sil)


def seg_bones(seed=8):
    rng = random.Random(seed)
    img, sil = _seg_base()
    sil = new_mask(SEG_W, SEG_H)
    for _ in range(12):
        x, y = rng.randint(4, 40), rng.randint(10, 28)
        a = rng.uniform(0, math.pi)
        dx, dy = int(6 * math.cos(a)), int(4 * math.sin(a))
        m = new_mask(SEG_W, SEG_H); line(m, [(x, y), (x + dx, y + dy)], 2)
        sil = union(sil, m); paint(img, m, WHITE)
    s = new_mask(SEG_W, SEG_H); blob(s, 24, 18, 6, 6, rng, 1, 10)  # череп
    sil = union(sil, s); paint(img, s, WHITE)
    eye(img, 22, 17, 1, 1, 0, 0, rng); eye(img, 27, 17, 1, 1, 0, 0, rng)
    for _ in range(8): px(img, rng.randint(4, 44), rng.randint(10, 28), RED)
    return _seg_finish(img, sil)


def seg_sofa(seed=9):
    rng = random.Random(seed)
    img, sil = _seg_base()
    body = new_mask(SEG_W, SEG_H); rect(body, 3, 12, 44, 28)
    back = new_mask(SEG_W, SEG_H); rect(back, 5, 6, 42, 14)
    sil = union(body, back)
    paint(img, back, BLUE); dither(img, back, BLACK, "checker")
    paint(img, body, PINK); dither(img, body, BROWN, "dots")
    for x in (16, 30): 
        for y in range(14, 28): px(img, x, y, BLACK)
    for _ in range(14): px(img, rng.randint(4, 43), rng.randint(14, 27), rng.choice([BLACK, YELLOW, GREEN]))
    for k in range(4): px(img, 40 - k, 8 + k, BROWN)  # торчит пружина
    for x in (6, 40): px(img, x, 29, BLACK); px(img, x, 30, BLACK)
    return _seg_finish(img, sil)


_ITEMS = (item_toilet, item_cart, item_tv, item_washer, item_fridge, item_mattress, item_bags,
          item_boxes, item_bathtub, item_graves, item_hand, item_pipes, item_cones, item_bottles,
          item_gutpile, item_stove, item_crates, item_mannequin, item_vending, item_bike,
          item_bigeye, item_bigpoop, item_sewer, item_coffin, item_tentacles)
BORDER_SEGMENTS = (seg_dumpster, seg_car, seg_corpses, seg_fence, seg_wall, seg_tires,
                   seg_barrels, seg_bones, seg_sofa) + _ITEMS


def draw_border_sheet():
    sheet = new_img(SEG_W * len(BORDER_SEGMENTS), SEG_H)
    for i, fn in enumerate(BORDER_SEGMENTS):
        sheet.paste(fn(i + 1), (i * SEG_W, 0))
    return sheet



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


def draw_frame(w, h, ring, ring2, seed, chamfer=5, drips=4, eyes=True, clean=False, corner="eyes", ring_w=2, deco_n=0):
    """Кривая рамка: чёрный контур, кишечная полоса (ring/ring2), чёрная начинка с грязью."""
    rng = random.Random(seed)
    img = new_img(w, h)
    c = chamfer
    m0 = wobbly_mask(w, h, 0, c, rng)
    m1 = wobbly_mask(w, h, 1, max(c - 1, 1), rng)
    m2 = wobbly_mask(w, h, 1 + ring_w, max(c - 2, 1), rng)
    paint(img, m0, BLACK)
    paint(img, m1, ring)
    dither(img, m1, ring2, "stripes")
    paint(img, m2, BLACK)
    if not clean:
        dither(img, m2, BROWN, "dots_off")
        noise(img, m2, [GREEN, CYAN, PINK, YELLOW], max(3, w * h // 500), rng)
    for _ in range(drips):  # слизь капает сверху
        x = rng.randrange(8, w - 8)
        for k in range(rng.randint(2, 5)):
            px(img, x, 3 + k, GREEN)
    if deco_n:  # украшения вдоль рамки в случайных местах
        maker2 = {"eyes": stamp_eyeball, "bones": stamp_bone, "poop": stamp_poop, "guts": lambda s: stamp_guts(s, 8)}[corner]
        for _ in range(deco_n):
            s = maker2(rng.randint(0, 99))
            side = rng.randrange(4)
            if side == 0: pos = (rng.randint(10, w - 18), -2)
            elif side == 1: pos = (rng.randint(10, w - 18), h - s.height + 2)
            elif side == 2: pos = (-2, rng.randint(10, h - 18))
            else: pos = (w - s.width + 2, rng.randint(10, h - 18))
            img.paste(s, pos, s)
    if eyes and corner == "eyes":
        for (ex, ey) in ((-2, -2), (w - 7, -2)):
            e = stamp_eyeball(rng.randint(0, 99))
            img.paste(e, (ex, ey), e)
    elif eyes:
        maker = {"bones": stamp_bone, "poop": stamp_poop, "guts": lambda s: stamp_guts(s, 8)}[corner]
        for (ex, ey) in ((-2, -3), (w - 8, -3), (-2, h - 8), (w - 8, h - 8)):
            s = maker(rng.randint(0, 99))
            img.paste(s, (ex, ey), s)
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


CARD_W, CARD_H = 112, 150
# (кольцо, кольцо2, seed, скос, капли, украшение углов) — вариантов много: каждая карточка берёт случайный
CARD_VARIANTS = (
    (PINK, RED, 101, 7, 7, "eyes", 3, 5), (GREEN, YELLOW, 202, 5, 4, "bones", 2, 7), (CYAN, BLUE, 303, 9, 9, "poop", 4, 4),
    (RED, BLACK, 404, 6, 3, "eyes", 5, 6), (YELLOW, PINK, 505, 8, 8, "poop", 2, 8), (BLUE, CYAN, 606, 4, 6, "guts", 3, 5),
    (PINK, GREEN, 707, 7, 5, "bones", 4, 9), (WHITE, RED, 808, 10, 10, "guts", 3, 6),
)


def draw_card_frames():
    """Лист рамок карточек: верхний ряд — обычные, нижний — выбранные (жёлтое кольцо). Ячейка 112x150."""
    sheet = new_img(CARD_W * len(CARD_VARIANTS), CARD_H * 2)
    for i, (ring, ring2, seed, chamfer, drips, corner, rw, dn) in enumerate(CARD_VARIANTS):
        a = draw_frame(CARD_W, CARD_H, ring, ring2, seed, chamfer=chamfer, drips=drips, clean=True, corner=corner, ring_w=rw, deco_n=dn)
        b = draw_frame(CARD_W, CARD_H, YELLOW, ring, seed, chamfer=chamfer, drips=drips + 2, clean=True, corner=corner, ring_w=rw, deco_n=dn)
        sheet.paste(a, (i * CARD_W, 0))
        sheet.paste(b, (i * CARD_W, CARD_H))
    return sheet


def build_step2():
    glyphs = build_font()
    for name, fn in (("perk_speed", icon_speed), ("perk_regen", icon_regen),
                     ("perk_double_shot", icon_double), ("perk_loot_goblin", icon_goblin),
                     ("hud_heart", lambda: draw_heart(14))):
        fn().save(UI + name + ".png")
    draw_card_frames().save(UI + "card_frames.png")
    draw_frame(96, 22, RED, PINK, 202, chamfer=4, drips=3, eyes=False).save(UI + "button.png")
    draw_frame(96, 22, YELLOW, GREEN, 202, chamfer=4, drips=5, eyes=False).save(UI + "button_hover.png")
    bar_under(72, 10, PINK).save(UI + "hp_bar_under.png")
    bar_fill(68, 6, RED, PINK, 5).save(UI + "hp_bar_fill.png")
    bar_under(224, 10, GREEN).save(UI + "xp_bar_under.png")
    bar_fill(220, 6, GREEN, WHITE, 6).save(UI + "xp_bar_fill.png")
    draw_death_bg().save(UI + "death_bg.png")
    draw_dim().save(UI + "dim_checker.png")
    draw_border_sheet().save(SPRITES + "arena_border.png")
    draw_decals().save(SPRITES + "ground_decals.png")
    draw_wire_sheet().save(SPRITES + "arena_wire.png")
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
