#!/usr/bin/env python3
"""Враги v2: 4 кадра анимации, детали по названию. python3 tools/redraw_enemies_v2.py [--apply] [имена]
Лист: 4 кадра по горизонтали (в enemy_base.gd FRAMES указывает число кадров)."""
import os, sys
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
GOLD = (255, 200, 40); DGREEN = (20, 120, 30); LGREY = (190, 190, 200); RUST = (170, 80, 30)


def trash_bin(t, kind=0):
    c = Canvas(36, 40)
    lid = [0, 3, 5, 2][t]; sway = [0, 1, 0, -1][t]
    # колёса
    c.ell(10, 38, 3, 2, BLACK); c.ell(27, 38, 3, 2, BLACK); c.px(10, 38, GREY); c.px(27, 38, GREY)
    # корпус: мятый металл, рёбра, обручи, ржавчина
    c.rect(7, 15, 29, 36, GREY, dither=DGREY)
    for x in range(11, 29, 4): c.line(x, 16, x, 35, DGREY)
    c.rect(6, 19, 30, 20, DGREY); c.rect(6, 31, 30, 32, DGREY)
    c.rect(7, 15, 8, 36, WHITE, dither=GREY)
    c.pts([(14, 24), (15, 25), (21, 27), (22, 27), (12, 30), (25, 22), (26, 23)], RUST)
    c.line(22, 20, 22, 25 + t % 2, GREEN); c.line(11, 33, 11, 36, GREEN)
    # надпись «ТБО» и вмятина
    c.pts([(14, 28), (15, 28), (16, 28), (15, 29), (15, 30), (18, 28), (19, 28), (18, 30), (19, 30), (22, 28), (22, 29), (22, 30)], WHITE)
    c.line(26, 18, 29, 24, DGREY, 2)
    # тёмная щель под крышкой + злые глаза внутри
    c.rect(8, 12 - lid, 28, 15, BLACK)
    if lid > 1:
        c.rect(11, 13 - lid // 2, 14, 14, YELLOW); c.rect(22, 13 - lid // 2, 25, 14, YELLOW); c.px(12, 13 - lid // 2, RED); c.px(23, 13 - lid // 2, RED)
        c.pts([(15, 14), (17, 14), (19, 14), (21, 14)], WHITE)    # клыки
    # боковые ручки
    c.rect(3, 21, 6, 23, DGREY); c.rect(30, 21, 33, 23, DGREY)
    # крышка хлопает, как челюсть
    c.rect(5, 8 - lid, 31 + sway, 11 - lid, BLUE, dither=CYAN)
    c.rect(5, 8 - lid, 31 + sway, 8 - lid, WHITE); c.rect(15, 5 - lid, 21, 7 - lid, DGREY)
    c.line(6, 11 - lid, 4, 15 - lid, BLUE)
    # мусор торчит
    junk = [lambda: (c.line(11, 8 - lid, 8, 1 - lid // 2, WHITE), c.pts([(7, 0), (9, 1), (6, 2)], WHITE), c.line(25, 8 - lid, 28, 3 - lid // 2, YELLOW)),
            lambda: (c.ell(12, 5 - lid, 4, 3, YELLOW), c.line(15, 5 - lid, 19, 1, YELLOW), c.rect(26, 3 - lid, 28, 8 - lid, GREEN), c.px(27, 2 - lid, WHITE)),
            lambda: (c.rect(24, 1, 27, 7 - lid, CYAN), c.px(25, 0, WHITE), c.line(11, 8 - lid, 8, 3, PINK, 2)),
            lambda: (c.line(25, 8 - lid, 29, 2, PINK, 2), c.line(28, 3, 31, 1, PINK), c.ell(12, 5 - lid, 3, 2, WHITE), c.px(12, 4 - lid, BLACK))][kind]
    junk()
    # мухи кружат
    for i in range(3):
        a = (t * 90 + i * 120) % 360
        import math
        c.px(int(18 + 15 * math.cos(math.radians(a))), int(8 + 6 * math.sin(math.radians(a * 1.3))), BLACK)
    # струйки вони
    for k, x in enumerate((9, 18, 27)):
        yy = 3 - (t + k) % 4
        c.pts([(x, yy), (x + 1, yy - 1), (x, yy - 2)], GREEN) if yy > 1 else None
    return c.finish(PURPLE, YELLOW, lim=0.1)


def cockroach(t):
    c = Canvas(34, 24)
    step = [0, 1, 0, -1][t]
    # 6 ног: две тройки шагают поочерёдно
    for i, x in enumerate((11, 16, 21)):
        d = step if i % 2 == 0 else -step
        c.line(x, 13, x - 5, 18 + d, BROWN); c.line(x - 5, 18 + d, x - 7, 21, BROWN)
        c.line(x, 13, x + 5, 18 - d, BROWN); c.line(x + 5, 18 - d, x + 7, 21, BROWN)
        c.pts([(x - 7, 21), (x + 7, 21)], BLACK)
    # крылья-надкрылья (приоткрываются на кадре 2)
    open_ = 2 if t == 2 else 0
    c.ell(15, 12, 11, 7, BROWN, dither=(160, 90, 40))
    c.ell(15, 11, 9, 5, (255, 190, 60), dither=ORANGE)
    c.line(15, 5, 15, 17, BROWN)
    c.ell(11, 10 - open_, 4, 3, (255, 220, 120)); c.ell(19, 10 - open_, 4, 3, (255, 220, 120))
    if open_: c.ell(8, 6, 5, 2, WHITE, dither=CYAN); c.ell(22, 6, 5, 2, WHITE, dither=CYAN)
    c.pts([(9, 13), (13, 15), (18, 15), (21, 13)], BROWN)
    # голова с жвалами и усами-антеннами
    c.ell(28, 11, 5, 5, BROWN, dither=(160, 90, 40))
    c.eye(29, 9, 3, (1, 0)); c.eye(30, 13, 2, (1, 0), blood=False)
    c.line(32, 14, 33, 16, RED); c.line(30, 15, 31, 17, RED)   # жвалы
    wv = [0, 2, 0, -2][t]
    c.line(30, 6, 33, 1 + wv, BLACK); c.line(27, 6, 22, 1 - wv, BLACK)
    c.px(33, 1 + wv, YELLOW); c.px(22, 1 - wv, YELLOW)
    # слизь и пятна
    c.pts([(2, 12), (3, 13), (4, 14)], GREEN); c.pts([(12, 9), (17, 13)], RED)
    return c.finish(GREEN, YELLOW)


def mamka(t):
    c = Canvas(46, 44); b = [0, 1, 0, 1][t]
    # тапки
    c.ell(14, 41, 5, 2, BROWN); c.ell(30, 41, 5, 2, BROWN); c.rect(10, 38, 18, 40, BROWN); c.rect(26, 38, 34, 40, BROWN)
    c.pts([(12, 38), (13, 38)], PINK)   # помпоны
    # халат в цветочек
    c.ell(22, 28 + b, 17, 13, PINK, dither=(255, 120, 245))
    c.rect(20, 18 + b, 24, 38, PURPLE)                         # запах халата
    c.rect(8, 34, 36, 35, PURPLE)                              # пояс
    for p, col in (((12, 27), WHITE), ((30, 30), WHITE), ((24, 24), YELLOW), ((15, 33), YELLOW), ((33, 25), WHITE)): c.ell(p[0], p[1] + b, 2, 2, col); c.px(p[0], p[1] + b, RED)
    # голова
    c.ell(22, 12 + b, 9, 9, SKIN, dither=(220, 160, 120))
    # бигуди и пучок
    c.ell(22, 3 + b, 5, 3, PINK); c.ell(22, 0 + b, 3, 2, PINK)
    for x in (11, 15, 29, 33): c.rect(x, 4 + b, x + 2, 8 + b, CYAN); c.rect(x, 4 + b, x + 2, 4 + b, WHITE)
    c.pts([(11, 9 + b), (12, 12 + b), (33, 9 + b), (32, 12 + b)], PINK)
    # лицо: злые брови, орущий рот по кадрам
    c.eye(18, 12 + b, 3, (1, 1)); c.eye(26, 12 + b, 3, (-1, 1))
    c.line(13, 8 + b, 20, 10 + b, BLACK); c.line(31, 8 + b, 24, 10 + b, BLACK)
    mh = [2, 4, 5, 3][t]
    c.ell(22, 18 + b, 4, mh // 2 + 1, BLACK); c.rect(19, 17 + b, 25, 17 + b, WHITE)
    if t in (1, 2): c.pts([(21, 20 + b), (23, 20 + b)], RED)
    c.pts([(15, 15 + b), (29, 15 + b)], (255, 120, 140))     # румянец-злость
    # звуковые волны крика
    if t in (1, 2):
        for k in (1, 2): c.pts([(22 - 5 - k * 3, 17 + b - k), (22 + 5 + k * 3, 17 + b - k)], YELLOW)
    # скалка: замах по дуге
    ang = [(38, 22, 44, 12), (40, 20, 44, 6), (41, 24, 41, 36), (39, 28, 44, 20)][t]
    c.line(ang[0], ang[1] + b, ang[2], ang[3], BROWN, 3); c.ell(ang[2], ang[3], 2, 2, (150, 90, 40)); c.px(ang[0], ang[1] + b, YELLOW)
    # вторая рука подбоченилась
    c.ell(6, 26 + b, 4, 4, SKIN); c.line(7, 26 + b, 12, 30 + b, SKIN, 2)
    return c.finish(CYAN, YELLOW)


def spitter(t):
    c = Canvas(34, 28)
    m = [1, 4, 7, 3][t]; glow = [0, 0, 1, 0][t]
    c.ell(17, 17, 13, 8, GREEN, dither=YELLOW)
    c.ell(8, 8, 4, 4, GREEN, dither=YELLOW); c.ell(26, 8, 4, 4, GREEN, dither=YELLOW)   # выпученные глаза-бородавки
    c.eye(8, 8, 3, (1, 1)); c.eye(26, 8, 3, (-1, 1))
    c.pts([(14, 12), (19, 11), (22, 14), (11, 15)], DGREEN)                            # бородавки
    # пасть: раскрывается, видно горло и язык
    c.rect(6, 16, 28, 16 + m, BLACK)
    c.rect(7, 16, 27, 17, WHITE, dither=YELLOW)
    for x in range(7, 28, 3): c.px(x, 16 + m, WHITE); c.px(x, 18, WHITE)
    if m > 3: c.rect(11, 18 + m // 2, 23, 18 + m // 2 + 1, PINK); c.rect(14, 17, 20, 18, RED)
    if glow: c.ell(17, 17 + m // 2, 3, 2, (150, 255, 60)); c.pts([(17, 22), (16, 23), (18, 23)], WHITE)
    # слюна и летящий плевок
    c.line(8, 17 + m, 8, 20 + m + t % 2, GREEN); c.line(27, 17 + m, 27, 21 + m, GREEN)
    if t == 3: c.ell(32, 18, 1.5, 1.5, (150, 255, 60)); c.px(31, 18, WHITE)
    # лапы-перепонки
    c.rect(6, 25, 12, 26, BROWN); c.rect(22, 25, 28, 26, BROWN); c.pts([(6, 26), (9, 26), (12, 26)], BLACK)
    c.pts([(17, 4), (18, 3), (16, 3)], CYAN)
    return c.finish(PURPLE, WHITE)


import math

def squid_gopnik(t):
    c = Canvas(30, 28); b = [0, 1, 0, 1][t]
    # щупальца-ноги шагают, на концах присоски
    for i, x in enumerate((6, 11, 17, 22)):
        sw = [1, 0, -1, 0][(i + t) % 4]
        c.line(x, 18 + b, x + sw, 25, PINK, 2); c.px(x + sw, 26, YELLOW); c.px(x + sw + 1, 26, YELLOW)
    c.ell(15, 11 + b, 10, 10, PINK, dither=(255, 120, 245))
    c.rect(9, 17 + b, 21, 19 + b, PINK)
    # кепка набекрень с гербом, козырёк сбоку
    c.rect(5, 3 + b, 21, 6 + b, RED); c.rect(14, 6 + b, 28, 7 + b, RED); c.ell(15, 3 + b, 7, 2, RED)
    c.pts([(12, 4 + b), (13, 4 + b), (12, 5 + b)], YELLOW)
    # глаза-щёлки, злые брови
    c.eye(10, 11 + b, 3, (1, 1)); c.eye(20, 10 + b, 3, (-1, 1))
    c.line(6, 8 + b, 12, 9 + b, BLACK); c.line(24, 7 + b, 17, 9 + b, BLACK)
    c.teeth(10, 20, 15 + b, h=2)
    # бычок: тлеет, дым вьётся
    c.rect(17, 16 + b, 23, 16 + b, WHITE); c.px(24, 16 + b, ORANGE if t % 2 else RED)
    c.pts([(25, 14 + b - t), (26, 12 + b - t), (25, 10 + b - t)], GREY)
    # адидас: три полоски на боках
    for x in (7, 22): c.line(x, 14 + b, x, 17 + b, WHITE); c.line(x + 1, 14 + b, x + 1, 17 + b, WHITE)
    # семечки (шелуха) летит
    c.px(2, 22 + (t % 2), WHITE); c.px(27, 21, WHITE) if t == 2 else None
    return c.finish(PURPLE, YELLOW)


def chaser(t):
    """Назойливая муха-кусака: крылья жужжат, глаза-фасетки, хоботок."""
    c = Canvas(26, 22)
    wing = [0, 3, 5, 3][t]
    c.ell(6, 7 - wing // 2, 6, 3 + wing // 2, (200, 255, 255), dither=WHITE); c.ell(20, 7 - wing // 2, 6, 3 + wing // 2, (200, 255, 255), dither=WHITE)
    c.line(6, 7, 11, 11, CYAN); c.line(20, 7, 15, 11, CYAN)
    # брюшко в полоску
    c.ell(13, 15, 5, 5, BLUE, dither=(60, 60, 255)); c.rect(8, 14, 18, 14, YELLOW); c.rect(8, 17, 18, 17, YELLOW)
    c.pts([(13, 20), (12, 20), (14, 20)], BLACK)       # жало
    # голова с огромными глазами
    c.ell(13, 9, 6, 5, RED, dither=(255, 80, 80))
    c.ell(9, 8, 3, 3, (255, 60, 60)); c.ell(17, 8, 3, 3, (255, 60, 60))
    c.eye(9, 8, 2, (0, 1)); c.eye(17, 8, 2, (0, 1))
    c.pts([(9, 7), (17, 7)], WHITE)
    c.line(13, 12, 13, 15 + t % 2, BLACK)             # хоботок
    c.line(11, 4, 8, 1, BLACK); c.line(15, 4, 18, 1, BLACK)
    # лапки
    for x, d in ((9, 1), (13, 0), (17, -1)):
        c.line(x, 19, x + d * 2, 21, BLACK)
    return c.finish(PINK, WHITE)


def charger(t):
    """Бык-бодун: рога, кольцо в носу, пар из ноздрей, галоп."""
    c = Canvas(40, 28)
    g = [-2, 0, 2, 0][t]; b = [0, -1, 0, -1][t]
    # ноги галопируют
    for x, off in ((9, g), (14, -g), (25, -g), (30, g)):
        c.line(x, 19 + b, x + off, 24, WHITE); c.rect(x + off - 1, 24, x + off + 1, 25, BLACK)
    c.ell(18, 14 + b, 14, 8, WHITE, dither=(210, 210, 215))
    c.ell(11, 11 + b, 3, 3, BLACK); c.ell(21, 16 + b, 3, 2, BLACK); c.ell(17, 9 + b, 2, 2, BLACK)
    # горб-холка
    c.ell(24, 9 + b, 6, 5, WHITE, dither=(210, 210, 215))
    # башка
    c.ell(34, 13 + b, 6, 6, WHITE, dither=(210, 210, 215))
    # рога
    c.line(29, 8 + b, 25, 2 + b, YELLOW, 2); c.line(37, 8 + b, 40, 3 + b, YELLOW, 2); c.px(25, 1 + b, WHITE); c.px(40, 2 + b, WHITE)
    c.eye(32, 11 + b, 2, (1, 1)); c.eye(37, 11 + b, 2, (1, 1)); c.line(30, 9 + b, 34, 10 + b, BLACK)
    c.rect(33, 15 + b, 39, 18 + b, PINK); c.pts([(34, 16 + b), (37, 16 + b)], BLACK)
    c.ell(37, 20 + b, 2, 2, YELLOW); c.px(37, 20 + b, BLACK)     # кольцо в носу
    # пар из ноздрей
    if t % 2: c.pts([(40, 15 + b), (39, 13 + b)], WHITE)
    # хвост хлещет, полосы скорости
    c.line(4, 10 + b, 1, 6 + g, WHITE, 2); c.px(1, 5 + g, RED)
    for i in range(3): c.line(0, 12 + i * 3, 4 + t, 12 + i * 3, YELLOW)
    return c.finish(PINK, YELLOW)


def npc_bot(t):
    """Тупой НПС-робот: квадратная башка, мигающая антенна, 'ОШИБКА' на экране-груди."""
    c = Canvas(28, 32)
    ar = [0, 2, 0, -2][t]; blink = t % 2
    c.line(14, 0, 14, 4, DGREY); c.ell(14, 1, 2, 2, RED if blink else YELLOW)
    c.rect(6, 4, 22, 15, GREY, dither=WHITE)
    c.rect(8, 7, 12, 11, BLACK); c.rect(16, 7, 20, 11, BLACK)
    c.rect(9, 8, 11, 10, RED if blink else YELLOW); c.rect(17, 8, 19, 10, YELLOW if blink else RED)
    c.rect(9, 13, 19, 14, BLACK)
    for x in range(9, 20, 2): c.px(x, 13, WHITE)
    c.rect(11, 15, 17, 16, DGREY)                                   # шея
    c.rect(5, 17, 23, 25, DGREY, dither=GREY)
    c.rect(9, 19, 19, 23, BLACK)
    c.pts([(10, 20), (12, 20), (14, 20), (16, 20), (18, 20)], GREEN if blink else RED)   # строка ошибки
    c.pts([(11, 22), (13, 22), (15, 22)], PINK)
    c.rect(0, 17 + ar, 3, 25 + ar, GREY); c.rect(25, 17 - ar, 28, 25 - ar, GREY)
    c.pts([(1, 26 + ar), (26, 26 - ar)], YELLOW)                    # клешни
    c.rect(8, 26, 12, 30, DGREY); c.rect(16, 26, 20, 30, DGREY)
    c.rect(7, 30, 13, 31, BLACK); c.rect(15, 30, 21, 31, BLACK)
    c.line(6, 5, 3, 2, YELLOW); c.line(22, 5, 25, 2, YELLOW)        # болты
    c.pts([(23, 12 + blink)], CYAN)                                  # искра
    return c.finish(PINK, WHITE)


def bruiser(t):
    """Амбал в тельняшке: кулаки-кувалды, бычья шея, сломанный нос."""
    c = Canvas(44, 42); b = [0, 1, 0, 1][t]
    sw = [-2, 0, 2, 0][t]
    c.rect(11, 33, 18, 39, BROWN); c.rect(25, 33, 32, 39, BROWN)
    c.rect(10, 39, 19, 40, BLACK); c.rect(24, 39, 33, 40, BLACK)
    c.ell(22, 24 + b, 17, 12, BLUE, dither=(80, 80, 255))
    for x in range(9, 36, 4): c.rect(x, 17 + b, x + 1, 28 + b, WHITE)            # тельняшка
    c.rect(8, 29 + b, 36, 30 + b, BLACK)                                         # ремень
    c.rect(19, 29 + b, 25, 31 + b, GOLD); c.px(22, 30 + b, BLACK)
    # руки с кулаками
    c.line(9, 20 + b, 4, 26 + b * 2 + sw, SKIN, 5); c.ell(4, 28 + b * 2 + sw, 5, 5, SKIN, dither=(220, 160, 120))
    c.line(35, 20 + b, 40, 26 + b * 2 - sw, SKIN, 5); c.ell(40, 28 + b * 2 - sw, 5, 5, SKIN, dither=(220, 160, 120))
    c.pts([(2, 27 + b * 2 + sw), (4, 27 + b * 2 + sw), (38, 27 + b * 2 - sw), (40, 27 + b * 2 - sw)], BLACK)  # костяшки
    c.rect(6, 25 + b * 2 + sw, 7, 25 + b * 2 + sw, RED) if False else None
    # голова
    c.ell(22, 9 + b, 9, 8, SKIN, dither=(220, 160, 120)); c.rect(14, 15 + b, 30, 17 + b, SKIN)
    c.rect(12, 3 + b, 32, 5 + b, PINK); c.rect(15, 0 + b, 29, 3 + b, PINK); c.rect(12, 5 + b, 17, 6 + b, (200, 0, 190))  # кепка
    c.eye(17, 9 + b, 2, (1, 1)); c.eye(27, 9 + b, 2, (-1, 1)); c.line(13, 6 + b, 20, 8 + b, BLACK); c.line(31, 6 + b, 24, 8 + b, BLACK)
    c.pts([(22, 11 + b), (23, 12 + b), (22, 13 + b)], (200, 120, 100))            # нос сломан
    c.teeth(16, 28, 15 + b, h=2); c.px(19, 14 + b, GOLD)
    c.pts([(14, 11 + b), (30, 12 + b)], RED)                                      # синяк
    c.line(33, 14 + b, 36, 11 + b, SKIN) if False else None
    return c.finish(PURPLE, YELLOW)


def glutton(t):
    """Обжора: пасть-бездна, слюни, крошки летят."""
    c = Canvas(36, 30)
    m = [4, 6, 8, 6][t]; b = [0, 1, 0, 1][t]
    c.rect(9, 25, 14, 28, BROWN); c.rect(22, 25, 27, 28, BROWN)
    c.ell(18, 15, 16, 12, YELLOW, dither=ORANGE)
    c.ell(18, 17, 11, m, BLACK)
    c.rect(8, 17 - m - 1, 28, 17 - m, WHITE); c.rect(8, 17 + m, 28, 18 + m, WHITE)
    for x in range(9, 28, 3): c.line(x, 17 - m, x, 19 - m, BLACK); c.line(x, 17 + m, x, 15 + m, BLACK)
    c.ell(18, 19 + b, 6, 2, PINK)                        # язык
    c.ell(12, 6, 4, 4, WHITE); c.ell(24, 6, 4, 4, WHITE)  # глаза навыкате
    c.eye(12, 6, 3, (1, 1)); c.eye(24, 6, 3, (-1, 1))
    c.line(5, 2, 13, 3, BLACK); c.line(31, 2, 23, 3, BLACK)
    c.line(4, 15, 4, 20 + t, GREEN); c.line(32, 15, 32, 21 - t, GREEN); c.pts([(4, 22 + t), (32, 22 - t)], GREEN)   # слюни
    # крошки/кости летят
    c.pts([(2, 9 + t), (34, 11 - t), (1, 14), (33, 8)], WHITE)
    c.pts([(18, 4)], RED)
    return c.finish(RED, WHITE)


def healer(t):
    """Шаманка-медсестра: красный крест, огромный шприц, зелёное исцеление."""
    c = Canvas(32, 36)
    b = [0, 1, 0, 1][t]; pl = [0, 1, 2, 1][t]
    c.rect(9, 30, 13, 34, BROWN); c.rect(19, 30, 23, 34, BROWN)
    c.rect(8, 14 + b, 24, 31, WHITE, dither=(200, 255, 200)); c.rect(8, 14 + b, 24, 15 + b, LGREY)
    c.rect(14, 17 + b, 18, 24 + b, RED); c.rect(12, 19 + b, 20, 22 + b, RED)        # крест
    c.ell(16, 8 + b, 7, 7, SKIN)
    c.rect(7, 0 + b, 25, 4 + b, WHITE); c.rect(13, 0 + b, 19, 3 + b, RED); c.rect(15, -0, 17, 3 + b, WHITE) if False else None  # шапочка
    c.pts([(15, 1 + b), (16, 1 + b), (17, 1 + b), (16, 2 + b), (16, 0 + b)], WHITE)
    c.eye(13, 8 + b, 2, (1, 0)); c.eye(19, 8 + b, 2, (-1, 0)); c.pts([(11, 11 + b), (21, 11 + b)], (255, 150, 150))
    c.rect(11, 13 + b, 21, 13 + b, BLACK) if False else None
    c.rect(13, 12 + b, 19, 12 + b, (60, 20, 20))                                      # маска/рот
    c.line(6, 17 + b, 3, 24, SKIN, 3)                                                  # левая рука
    # шприц: огромный, поршень ходит
    c.line(24, 18 + b, 29, 10 - pl, LGREY, 3); c.rect(28, 8 - pl, 30, 11 - pl, GREEN); c.px(31, 6 - pl, WHITE); c.line(24, 18 + b, 24, 19 + b, BLACK)
    c.rect(27, 5 - pl, 31, 5 - pl, DGREY)
    # исцеляющие плюсики
    for k, (x, y) in enumerate(((28, 3), (4, 10), (30, 14))):
        if (k + t) % 3 == 0: c.pts([(x, y - 1), (x - 1, y), (x, y), (x + 1, y), (x, y + 1)], GREEN)
    return c.finish(GREEN, WHITE)


def looter(t):
    """Крыса-ворюга: маска, мешок с монетами, длинный хвост, жадные глаза."""
    c = Canvas(40, 30)
    lg = [-2, 0, 2, 0][t]; b = [0, 1, 0, 1][t]
    # хвост змеится
    c.line(4, 20, 1, 14 + lg, PINK, 2); c.line(1, 14 + lg, 4, 8 - lg, PINK, 2); c.px(5, 7 - lg, PINK)
    # лапы
    c.line(14, 23, 12 + lg, 27, GREY, 2); c.line(24, 23, 26 - lg, 27, GREY, 2); c.pts([(11 + lg, 28), (27 - lg, 28)], BLACK)
    c.ell(17, 17 + b, 11, 7, GREY, dither=WHITE)
    # мешок за спиной: узел, $ и торчащие монеты
    c.ell(9, 14 + b, 8, 9, BROWN, dither=YELLOW); c.rect(6, 4 + b, 11, 7 + b, BROWN); c.line(5, 6 + b, 12, 6 + b, RED)
    c.pts([(8, 11 + b), (9, 11 + b), (8, 12 + b), (9, 13 + b), (8, 14 + b), (9, 14 + b)], BLACK)
    c.ell(7, 3 + b, 2, 1, GOLD); c.px(10, 2 + b, GOLD) if t % 2 == 0 else c.px(5, 2 + b, GOLD)
    # голова-морда
    c.ell(29, 13 + b, 6, 5, GREY, dither=WHITE); c.ell(36, 15 + b, 4, 3, GREY)
    c.ell(26, 6 + b, 3, 3, PINK); c.ell(32, 6 + b, 3, 3, PINK)
    c.rect(24, 10 + b, 33, 11 + b, BLACK)                      # маска
    c.eye(28, 12 + b, 2, (1, 0)); c.eye(33, 12 + b, 1, (1, 0), blood=False)
    c.px(39, 15 + b, PINK); c.line(37, 17 + b, 40, 18 + b, WHITE); c.line(37, 14 + b, 40, 12 + b + t % 2, WHITE)
    c.rect(35, 18 + b, 37, 20 + b, YELLOW); c.px(36, 19 + b, WHITE)    # зубы
    c.line(22, 17 + b, 30, 20 + b, GREY, 2); c.ell(31, 21 + b, 2, 2, GOLD); c.px(31, 21 + b, YELLOW)   # лапка с монетой
    return c.finish(CYAN, YELLOW, lim=0.05)


def microbe(t):
    """Микроб-слизняк: жгутики, ядро, вакуоли, хищная ухмылка."""
    c = Canvas(30, 30)
    r = [9, 10, 9, 8][t]
    for k in range(10):
        ang = k * math.pi / 5 + t * 0.35
        c.line(15, 15, 15 + math.cos(ang) * (r + 4), 15 + math.sin(ang) * (r + 4), GREEN)
        c.px(15 + math.cos(ang) * (r + 5), 15 + math.sin(ang) * (r + 5), YELLOW)
    c.ell(15, 15, r, r - 1 + t % 2, GREEN, dither=(150, 255, 100))
    c.ell(11, 11, 2, 2, DGREEN); c.ell(19, 18, 3, 3, DGREEN); c.ell(20, 10, 1, 1, YELLOW); c.ell(10, 19, 2, 1, DGREEN)
    c.ell(15, 14, 3, 3, (200, 255, 100))                                                # ядро
    c.eye(11, 13, 3, (1, 0)); c.eye(20, 13, 2, (-1, 1))
    c.rect(10, 19, 20, 19, BLACK); c.pts([(11, 18), (14, 18), (17, 18), (19, 18)], WHITE)
    c.pts([(15, 24 + t % 2)], GREEN)                                                   # капает
    return c.finish(PURPLE, WHITE)


def egg(t):
    """Яйцо-вредитель: трещина, глаз-зрачок, из трещины лезет слизь; пульсирует."""
    c = Canvas(28, 32)
    w = [0, 1, 0, -1][t]; sh = [0, 1, 0, 0][t]
    c.ell(14 + sh, 17, 10 + w, 12, WHITE, dither=YELLOW)
    c.ell(14 + sh, 16, 8 + w, 9, YELLOW, dither=WHITE)
    # трещины, расширяются
    c.line(6, 9, 10, 12, BLACK); c.line(10, 12, 9, 16, BLACK); c.line(9, 16, 15, 18, BLACK); c.line(15, 18, 13, 22, BLACK)
    if t == 2: c.line(20, 8, 17, 12, BLACK); c.line(17, 12, 19, 15, BLACK)
    c.line(10, 12, 10, 14 + t, GREEN)
    # глаз в центре
    c.ell(15 + sh, 14, 5, 4, WHITE); c.eye(15 + sh, 14, 4, (0, 1))
    c.pts([(9, 10), (20, 10), (21, 22), (8, 21)], GREEN)       # плесень
    c.rect(12, 22, 17, 23, BLACK); c.pts([(13, 22), (15, 22), (17, 22)], WHITE)     # зубастый рот
    c.pts([(14 + w, 3), (6, 5 - sh), (22, 4)], CYAN)
    c.rect(10, 29, 18, 30, BLACK) if False else None
    return c.finish(PINK, WHITE)


def wifi_ghost(t):
    """Призрак роутера: полупрозрачный, сигнал над головой, 'нет сети'."""
    c = Canvas(30, 34)
    b = [0, 1, 0, -1][t]
    c.ell(15, 17 + b, 11, 12, CYAN, dither=WHITE)
    for k, x in enumerate((4, 9, 14, 19, 24)):
        c.rect(x, 24 + b, x + 3, 29 + b + ((k + t) % 2) * 3, CYAN, dither=WHITE)
    c.eye(10, 16 + b, 3, (0, 1)); c.eye(20, 16 + b, 3, (0, 1))
    c.ell(15, 23 + b, 3, 3, BLACK); c.px(15, 22 + b, RED)
    c.rect(15, 0, 15, 5, YELLOW)                              # антенна
    for k, r in enumerate((3, 5, 8)):
        if k <= (t + 1) % 4:
            for dx in range(-r, r + 1):
                yy = 4 - int((r * r - dx * dx) ** 0.5 * 0.7)
                if yy >= 0: c.px(15 + dx, yy, YELLOW)
    c.line(24, 20 + b, 28, 14 + b - t, CYAN, 2); c.line(4, 20 + b, 1, 14 + b + t, CYAN, 2)   # призрачные руки
    c.pts([(2, 12), (26, 11), (5, 6)], PINK)
    c.pts([(12, 14 + b), (18, 14 + b)], WHITE)
    return c.finish(BLUE, WHITE)


ENEMIES = {"squid_gopnik": squid_gopnik, "chaser": chaser, "charger": charger, "spitter": spitter, "cockroach": cockroach, "npc_bot": npc_bot, "bruiser": bruiser, "glutton": glutton, "healer": healer, "looter": looter, "mamka": mamka, "microbe": microbe, "egg": egg, "trash_bin": trash_bin, "wifi_ghost": wifi_ghost}
FR = 4


def build(fn, **kw): return sheet([fn(t, **kw) for t in range(FR)])


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ENEMIES)
    os.makedirs("tools/_preview/enemies_v2", exist_ok=True)
    k = 5; rows = []
    for n in names:
        im = build(ENEMIES[n]); rows.append((n, im))
        im.save(f"tools/_preview/enemies_v2/enemy_{n}.png")
        if apply: im.save(f"assets/sprites/enemy_{n}.png")
        if n == "trash_bin":
            for kk in range(4):
                v = build(trash_bin, kind=kk); v.save(f"tools/_preview/enemies_v2/enemy_trash_bin_{kk}.png")
                if apply: v.save(f"assets/sprites/enemy_trash_bin_{kk}.png")
    k = 3
    colw = max(im.width for _, im in rows) * k + 12; W = colw * 3; per = (len(rows) + 2) // 3
    H = max(sum(im.height * k + 8 for _, im in rows[i * per:(i + 1) * per]) for i in range(3)) + 8
    prev = Image.new("RGBA", (W, H), (45, 30, 20, 255))
    for ci in range(3):
        y = 6
        for n, im in rows[ci * per:(ci + 1) * per]:
            big = im.resize((im.width * k, im.height * k), Image.NEAREST); prev.paste(big, (6 + ci * colw, y), big); y += big.height + 8
    prev.save("tools/_preview/enemies_v2.png"); print(prev.size)
