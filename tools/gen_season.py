#!/usr/bin/env python3
"""Погода на весь забег (идея 6): частицы и значки сезонов.
Запуск из корня: PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_season.py
-> assets/sprites/fx_season_*.png, assets/ui/hud_season_<id>.png, превью tools/_preview/season.png"""
import math, os
import numpy as np
from PIL import Image
from pix import *

LBLUE = (170, 220, 255); MUD = (120, 80, 30); RUST = (200, 90, 20)


def to_img(a): return Image.fromarray(a)


def snow(t):
    c = Canvas(5, 5)
    if t == 0: c.pts([(2, 1), (1, 2), (2, 2), (3, 2), (2, 3)], WHITE)
    else: c.pts([(1, 1), (3, 1), (2, 2), (1, 3), (3, 3)], LBLUE)
    return c.finish(LBLUE, WHITE, outline=False)


def leaf(t):
    c = Canvas(7, 7)
    col = [ORANGE, RUST, YELLOW, MUD][t]
    shapes = [[(1, 3), (2, 2), (3, 2), (4, 3), (5, 4), (3, 3), (2, 4)],
              [(3, 1), (3, 2), (4, 3), (3, 4), (2, 3), (3, 5)],
              [(1, 4), (2, 3), (3, 3), (4, 2), (5, 2), (3, 4), (4, 4)],
              [(2, 2), (3, 2), (3, 3), (4, 4), (2, 3), (4, 5)]][t]
    c.pts(shapes, col); c.px(3, 3, BROWN)
    return c.finish(BROWN, YELLOW, outline=False)


def rain(t):
    c = Canvas(4, 7)
    if t == 0: c.line(3, 0, 1, 6, LBLUE)
    else: c.pts([(0, 6), (1, 5), (2, 6), (3, 5)], LBLUE)     # брызги
    return c.finish(BLUE, WHITE, outline=False)


def heat(t):
    c = Canvas(5, 5)
    if t == 0: c.pts([(2, 0), (2, 1), (2, 3), (2, 4), (0, 2), (1, 2), (3, 2), (4, 2)], YELLOW)
    else: c.pts([(1, 1), (3, 1), (2, 2), (1, 3), (3, 3)], ORANGE)
    return c.finish(ORANGE, WHITE, outline=False)


def icon_summer():
    c = Canvas(16, 16)
    for (x0, y0, x1, y1) in ((8, 0, 8, 2), (8, 13, 8, 15), (0, 8, 2, 8), (13, 8, 15, 8), (2, 2, 3, 3), (12, 12, 13, 13), (12, 3, 13, 2), (2, 13, 3, 12)):
        c.line(x0, y0, x1, y1, ORANGE)
    c.ell(8, 8, 5, 5, YELLOW, dither=ORANGE)
    c.rect(4, 6, 12, 7, BLACK); c.rect(5, 8, 7, 8, BLACK); c.rect(9, 8, 11, 8, BLACK)   # очки
    c.line(6, 11, 10, 11, RED)
    return c.finish(RED, WHITE)


def icon_autumn():
    c = Canvas(16, 16)
    c.ell(8, 7, 6, 5, ORANGE, dither=RUST); c.line(8, 2, 8, 14, BROWN); c.line(8, 7, 4, 4, BROWN); c.line(8, 9, 12, 6, BROWN)
    c.ell(11, 13, 3, 2, MUD); c.px(11, 11, MUD)       # куча на листе
    c.eye(5, 8, 1, (0, 0), blood=False); c.eye(10, 9, 2, (0, 1))
    return c.finish(BROWN, YELLOW)


def icon_winter():
    c = Canvas(16, 16)
    for (x0, y0, x1, y1) in ((8, 0, 8, 15), (0, 8, 15, 8), (2, 2, 13, 13), (13, 2, 2, 13)):
        c.line(x0, y0, x1, y1, LBLUE)
    c.ell(8, 8, 4, 4, WHITE, dither=LBLUE)
    c.eye(6, 7, 1, (1, 0), blood=False); c.eye(10, 8, 2, (-1, 0)); c.line(6, 11, 10, 10, BLUE)
    return c.finish(BLUE, WHITE)


def icon_spring():
    c = Canvas(16, 16)
    c.ell(8, 10, 5, 5, CYAN, dither=BLUE); c.pts([(8, 2), (7, 4), (9, 4), (6, 6), (10, 6)], CYAN)
    c.rect(7, 3, 9, 6, CYAN)
    c.eye(6, 10, 2, (0, 1)); c.eye(11, 9, 1, (0, 1), blood=False); c.line(6, 13, 10, 13, BLACK)
    c.pts([(1, 14), (2, 15), (14, 15), (13, 14)], MUD)   # грязь
    return c.finish(BLUE, WHITE)


W, H = 480, 270
_r = np.random.default_rng(11)


def edge_dist(c):
    """Расстояние каждого пикселя до ближайшего края экрана, с рваным шумом."""
    d = np.minimum(np.minimum(c.xx, W - 1 - c.xx), np.minimum(c.yy, H - 1 - c.yy)).astype(float)
    wob = 1.5 * np.sin(c.xx / 9.0) + 1.2 * np.sin(c.yy / 7.0 + 1.3) + 1.0 * np.sin((c.xx + c.yy) / 13.0)
    return d + wob


def band(c, d, width, col, dith, alpha_mul=1.0):
    """Кромка по краю экрана: плотная у края, к центру - дизеринг и пропадает."""
    m_full = d < width * 0.45
    m_dith = (d >= width * 0.45) & (d < width) & ((c.xx + c.yy) % 2 == 0)
    m_spk = (d >= width) & (d < width * 1.5) & ((c.xx * 7 + c.yy * 13) % 11 == 0)
    c.a[m_full] = (*col, int(235 * alpha_mul)); c.a[m_dith] = (*dith, int(200 * alpha_mul)); c.a[m_spk] = (*dith, int(160 * alpha_mul))


def frame_winter():
    c = Canvas(W, H); d = edge_dist(c)
    band(c, d, 9, WHITE, LBLUE)
    for x in range(6, W - 6, 11):                     # сосульки сверху
        L = int(_r.integers(4, 11)); w = int(_r.integers(1, 3))
        for k in range(L):
            ww = max(int(w * (1 - k / L)), 0)
            c.a[k + 3, max(x - ww, 0):x + ww + 1] = (*(LBLUE if k % 3 else WHITE), 235)
    for cx in range(0, W, 60):                        # сугробы снизу
        c.ell(cx + int(_r.integers(0, 30)), H - 1, int(_r.integers(12, 24)), int(_r.integers(4, 7)), WHITE, dither=LBLUE)
    c.a[c.a[:, :, 3] > 0, 3] = np.minimum(c.a[c.a[:, :, 3] > 0, 3], 235)
    return c.a


def frame_summer():
    c = Canvas(W, H); d = edge_dist(c)
    band(c, d, 7, ORANGE, YELLOW, 0.75)
    rr = np.hypot(c.xx - (W - 1), c.yy)             # солнечный ожог в углу
    for r, col in ((16, WHITE), (26, YELLOW), (38, ORANGE)):
        m = (rr < r) & (c.a[:, :, 3] == 0) & (((c.xx + c.yy) % 2 == 0) if r > 16 else True)
        c.a[m] = (*col, 210 if r == 16 else 170)
    for k in range(10):                               # лучи
        ang = math.radians(100 + k * 8)
        for t in range(40, 66):
            x = int(W - 1 + t * math.cos(ang)); y = int(t * math.sin(ang))
            if 0 <= x < W and 0 <= y < H and t % 3: c.a[y, x] = (*YELLOW, 150)
    return c.a


def frame_autumn():
    c = Canvas(W, H); d = edge_dist(c)
    band(c, d, 6, (70, 90, 120), LBLUE, 0.8)
    cols = [ORANGE, RUST, YELLOW, (150, 70, 20)]
    for corner in ((0, H), (W, H), (0, 0), (W, 0)):    # кучи листьев по углам (снизу больше)
        n = 260 if corner[1] == H else 80
        for _ in range(n):
            r = abs(_r.normal(0, 12 if corner[1] == H else 8))
            a = _r.uniform(0, math.pi / 2)
            sx = 1 if corner[0] == 0 else -1; sy = 1 if corner[1] == 0 else -1
            x = int(corner[0] + sx * r * math.cos(a) * 2.2); y = int(corner[1] + sy * r * math.sin(a))
            col = cols[int(_r.integers(0, 4))]
            for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0)):
                if 0 <= x + dx < W and 0 <= y + dy < H: c.a[y + dy, x + dx] = (*col, 235)
    return c.a


def frame_spring():
    c = Canvas(W, H); d = edge_dist(c)
    band(c, d, 6, (90, 160, 90), (190, 255, 190), 0.7)
    for x in range(4, W, 9):                           # подтёки сверху
        L = int(_r.integers(3, 12))
        for k in range(L):
            c.a[k, x] = (*(LBLUE if k < L - 2 else WHITE), 200)
        c.a[L:L + 2, x - 1:x + 2] = (*LBLUE, 200)
    for cx in range(20, W, 85):                        # лужи снизу
        c.ell(cx + int(_r.integers(0, 30)), H - 2, int(_r.integers(10, 16)), 3, (60, 110, 200), dither=LBLUE)
        c.ell(cx + 6, H - 3, 3, 1, WHITE)
    return c.a


def puddle(t):
    """Лужа осени: грязная вода, рябь от капель."""
    c = Canvas(34, 16)
    c.ell(17, 8, 16, 7, (50, 80, 150), dither=(70, 110, 190))
    c.ell(15, 7, 11, 4, (80, 130, 210))
    r = [2, 4, 6, 3][t]
    for k in range(-r, r + 1):
        c.px(22 + k, 6 - (1 if abs(k) < r else 0), LBLUE)
    c.pts([(6, 9), (7, 9), (27, 10)], WHITE)
    c.pts([(3, 6), (30, 8), (12, 13)], MUD)              # грязь по краю
    return c.finish(BLUE, WHITE)


def drift(t):
    """Сугроб: растёт по кадрам (0 - горстка, 3 - во весь рост), с жёлтым пятном."""
    c = Canvas(32, 20)
    h = [4, 7, 10, 13][t]
    c.ell(16, 19, 15, h, WHITE, dither=LBLUE)
    c.ell(11, 19 - h // 2, 6, max(h // 3, 1), WHITE)
    if t >= 2: c.ell(22, 17, 2, 1, YELLOW)                # кто-то пометил
    c.pts([(6, 18), (25, 17), (15, 19 - h + 1)], LBLUE)
    return c.finish(LBLUE, WHITE)


def snowdrop(t):
    """Подснежник: оттаявший старый ботинок, из него торчит цветочек."""
    c = Canvas(16, 16)
    b = [0, 1, 0, 1][t]
    c.rect(2, 9, 12, 14, BROWN, dither=MUD); c.rect(9, 5, 13, 10, BROWN); c.line(2, 14, 13, 14, BLACK)
    c.pts([(4, 11), (6, 11), (8, 11)], WHITE)             # шнурки
    c.line(11, 5, 11 - b, 1, DGREEN); c.ell(10 - b, 1, 2, 1, WHITE); c.px(10 - b, 2, WHITE)
    c.pts([(1, 15), (14, 15), (6, 15)], MUD)
    if t % 2: c.pts([(0, 3), (15, 6)], YELLOW)            # блестит - подбери
    return c.finish(MUD, YELLOW)


if __name__ == "__main__":
    out = {
        "assets/sprites/fx_season_snow": sheet([snow(t) for t in range(2)]),
        "assets/sprites/fx_season_leaf": sheet([leaf(t) for t in range(4)]),
        "assets/sprites/fx_season_rain": sheet([rain(t) for t in range(2)]),
        "assets/sprites/fx_season_heat": sheet([heat(t) for t in range(2)]),
        "assets/sprites/weather_puddle": sheet([puddle(t) for t in range(4)]),
        "assets/sprites/weather_drift": sheet([drift(t) for t in range(4)]),
        "assets/sprites/weather_snowdrop": sheet([snowdrop(t) for t in range(4)]),
        "assets/sprites/fx_weather_winter": to_img(frame_winter()),
        "assets/sprites/fx_weather_summer": to_img(frame_summer()),
        "assets/sprites/fx_weather_autumn": to_img(frame_autumn()),
        "assets/sprites/fx_weather_spring": to_img(frame_spring()),
        "assets/ui/hud_season_summer": to_img(icon_summer()),
        "assets/ui/hud_season_autumn": to_img(icon_autumn()),
        "assets/ui/hud_season_winter": to_img(icon_winter()),
        "assets/ui/hud_season_spring": to_img(icon_spring()),
    }
    for k, im in out.items():
        im.save(k + ".png")
    out = {k: v for k, v in out.items() if "fx_weather" not in k} | {}
    frames = [Image.open(f"assets/sprites/fx_weather_{n}.png") for n in ("winter", "summer", "autumn", "spring")]
    grid = Image.new("RGBA", (W * 2, H * 2), (110, 70, 40, 255))
    for i, f in enumerate(frames): grid.paste(f, ((i % 2) * W, (i // 2) * H), f)
    grid.save("tools/_preview/weather_frames.png")
    k = 6; pad = 8; x = pad
    W = sum(im.width * k + pad for im in out.values()) + pad; H = max(im.height for im in out.values()) * k + pad * 2
    prev = Image.new("RGBA", (W, H), (45, 30, 20, 255))
    for im in out.values():
        big = im.resize((im.width * k, im.height * k), Image.NEAREST); prev.paste(big, (x, pad), big); x += big.width + pad
    os.makedirs("tools/_preview", exist_ok=True); prev.save("tools/_preview/season.png"); print(prev.size)
