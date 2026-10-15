#!/usr/bin/env python3
"""Новые спрайты врагов (2 кадра по горизонтали, у каждого свой размер). python3 tools/redraw_enemies.py [--apply] [имена...]"""
import os, sys, random
from PIL import Image
sys.path.insert(0, "tools")
from pix import *

N = 24  # базовый холст обычного врага


def squid_gopnik(t):
    c = Canvas(N, N); b = t  # покачивание
    for i, x in enumerate((5, 9, 14, 18)):  # щупальца
        sw = (1 if (i + t) % 2 else -1)
        c.line(x, 15 + b, x + sw, 22, PINK, 2); c.px(x + sw, 22, YELLOW)
    c.ell(12, 10 + b, 8, 8, PINK, dither=(255, 120, 245))
    c.rect(8, 15 + b, 16, 17 + b, PINK)
    c.rect(4, 3 + b, 20, 6 + b, RED); c.rect(13, 6 + b, 22, 7 + b, RED); c.pts([(11, 4 + b), (12, 4 + b), (11, 5 + b)], YELLOW)  # кепка с гербом
    c.eye(8, 10 + b, 3, (1, 1)); c.eye(16, 9 + b, 3, (-1, 1))
    c.line(5, 7 + b, 10, 8 + b, BLACK); c.line(19, 6 + b, 14, 8 + b, BLACK)  # злые брови
    c.teeth(8, 16, 14 + b, h=2)
    c.rect(17, 15 + b, 21, 15 + b, WHITE); c.px(22, 15 + b, ORANGE); c.px(23, 14 + b - t, GREY)  # бычок
    c.rect(7, 18 + b, 9, 18 + b, WHITE); c.rect(15, 18 + b, 17, 18 + b, WHITE)  # адидас-лампасы
    return c.finish(PURPLE, YELLOW)


def chaser(t):
    c = Canvas(N, 20)
    up = 0 if t == 0 else 3
    c.ell(5, 6 + up // 2, 5, 4, (140, 255, 255), dither=WHITE); c.ell(19, 6 + up // 2, 5, 4, (140, 255, 255), dither=WHITE)  # крылья
    c.ell(5, 7 + up, 4, 2, CYAN); c.ell(19, 7 + up, 4, 2, CYAN)
    c.ell(12, 13, 5, 5, BLUE, dither=(60, 60, 255)); c.rect(9, 14, 15, 14, YELLOW); c.rect(9, 17, 15, 17, YELLOW)
    c.ell(12, 8, 5, 4, RED)
    c.eye(10, 8, 2, (0, 1)); c.eye(14, 8, 2, (0, 1))
    c.pts([(11, 11), (12, 11), (13, 11)], BLACK); c.px(12, 12, WHITE)
    c.line(9, 4, 6, 1, BLACK); c.line(15, 4, 18, 1, BLACK)
    c.pts([(10, 19), (14, 19)], BLACK)
    return c.finish(PINK, WHITE)


def charger(t):
    c = Canvas(34, 26)
    lg = 2 * t
    for x, off in ((7, lg), (11, -lg), (21, -lg), (25, lg)):  # ноги
        c.rect(x, 18, x + 2, 22 + off // 2, BLACK); c.rect(x, 22 + off // 2, x + 3, 23 + off // 2, YELLOW)
    c.ell(16, 13, 12, 7, WHITE, dither=(200, 200, 200))
    c.ell(11, 11, 3, 3, BLACK); c.ell(20, 15, 3, 2, BLACK); c.ell(17, 9, 2, 2, BLACK)  # пятна
    c.ell(28, 11, 5, 5, WHITE, dither=(200, 200, 200))  # башка
    c.line(25, 6, 22, 1, PINK, 2); c.line(30, 6, 33, 2, GREEN, 2)  # рога
    c.eye(27, 10, 2, (1, 0)); c.eye(31, 10, 2, (1, 0))
    c.rect(29, 13, 33, 15, PINK); c.pts([(30, 14), (32, 14)], BLACK); c.pts([(31, 16), (31, 17)], YELLOW)  # кольцо в носу
    c.line(3, 10, 0, 7 + t * 2, WHITE, 2); c.px(0, 6, RED)  # хвост
    c.pts([(33, 18), (31, 20 - t)], WHITE)
    for i in range(3): c.line(1, 11 + i * 2, 5 + t, 11 + i * 2, YELLOW)  # полосы скорости
    return c.finish(PINK, YELLOW)


def spitter(t):
    c = Canvas(28, N)
    c.ell(14, 14, 11, 8, GREEN, dither=YELLOW)
    c.ell(7, 6, 4, 4, GREEN, dither=YELLOW); c.ell(21, 6, 4, 4, GREEN, dither=YELLOW)
    c.eye(7, 6, 3, (1, 1)); c.eye(21, 6, 3, (-1, 1))
    m = 3 + 2 * t
    c.rect(5, 13, 23, 13 + m, BLACK); c.rect(7, 13, 21, 14, WHITE, dither=YELLOW)
    for x in range(6, 23, 3): c.px(x, 13 + m, WHITE); c.px(x, 12, WHITE)
    c.rect(9, 15 + m // 2, 19, 16 + m // 2, PINK)  # язык
    c.line(24, 14 + m, 24, 18 + m + t, GREEN); c.px(24, 19 + m + t, WHITE)  # слюна
    c.rect(4, 20, 8, 21, BROWN); c.rect(20, 20, 24, 21, BROWN)
    c.pts([(14, 4), (15, 3), (13, 3)], CYAN)
    return c.finish(PURPLE, WHITE)


def cockroach(t):
    c = Canvas(30, 22)
    for i, x in enumerate((8, 14, 20)):  # ноги
        d = 1 if (i + t) % 2 else -1
        c.line(x, 11, x - 4, 17 + d, BROWN); c.line(x, 11, x + 4, 17 - d, BROWN)
        c.pts([(x - 5, 18 + d), (x + 5, 18 - d)], BLACK)
    c.ell(14, 11, 9, 6, BROWN, dither=(160, 90, 40)); c.ell(14, 10, 7, 4, YELLOW, dither=ORANGE)  # панцирь
    c.line(14, 5, 14, 15, BROWN)
    c.ell(25, 10, 4, 4, BROWN)
    c.eye(25, 8, 2, (1, 0)); c.eye(27, 11, 1, (0, 0), blood=False)
    c.line(26, 6, 29, 1 + t, BLACK); c.line(24, 6, 22, 1 - t, BLACK)  # усы
    c.pts([(1, 10), (2, 11)], GREEN); c.px(3, 12, GREEN)
    c.pts([(10, 8), (16, 12)], RED)
    return c.finish(GREEN, YELLOW)


def npc_bot(t):
    c = Canvas(N, 28)
    c.line(12, 0, 12, 4, DGREY); c.ell(12, 1, 2, 2, RED if t == 0 else YELLOW)
    c.rect(5, 4, 19, 14, GREY, dither=WHITE)
    c.rect(7, 7, 10, 10, BLACK); c.rect(14, 7, 17, 10, BLACK); c.rect(8, 8, 9, 9, RED); c.rect(15, 8, 16, 9, RED if t == 0 else YELLOW)
    c.rect(8, 12, 16, 13, BLACK)
    for x in range(8, 17, 2): c.px(x, 12, WHITE)
    c.rect(4, 15, 20, 22, DGREY, dither=GREY)
    c.rect(9, 17, 15, 20, BLACK); c.pts([(10, 18), (12, 18), (14, 18)], GREEN); c.pts([(11, 19), (13, 19)], PINK)
    ar = t * 2
    c.rect(0, 15 + ar, 3, 22 + ar, GREY); c.rect(21, 15 - ar, 24, 22 - ar, GREY)
    c.pts([(1, 23 + ar), (22, 23 - ar)], YELLOW)
    c.rect(7, 23, 10, 26, DGREY); c.rect(14, 23, 17, 26, DGREY)
    c.line(5, 5, 3, 3, YELLOW); c.line(19, 5, 21, 3, YELLOW)
    return c.finish(PINK, WHITE)


def bruiser(t):
    c = Canvas(38, 38); b = t
    c.rect(10, 31, 16, 36, BROWN); c.rect(22, 31, 28, 36, BROWN)
    c.ell(19, 22 + b, 15, 11, BLUE, dither=(80, 80, 255))
    c.rect(8, 27 + b, 30, 28 + b, WHITE)  # ремень-тельняшка
    for x in range(8, 31, 4): c.rect(x, 17 + b, x + 1, 25 + b, WHITE)
    c.ell(19, 24 + b, 4, 3, PINK); c.px(19, 24 + b, YELLOW)  # пряжка
    c.ell(4, 22 + b * 2, 4, 5, BLUE); c.ell(34, 22 - b * 2 + 2, 4, 5, BLUE)  # кулаки-кувалды
    c.ell(4, 28 + b * 2, 4, 3, SKIN); c.ell(34, 28 - b * 2 + 2, 4, 3, SKIN)
    c.ell(19, 9 + b, 8, 7, SKIN, dither=(220, 160, 120))
    c.rect(10, 3 + b, 28, 5 + b, PINK); c.rect(13, 0 + b, 25, 3 + b, PINK)  # кепка
    c.eye(15, 9 + b, 2, (1, 1)); c.eye(23, 9 + b, 2, (-1, 1)); c.line(11, 6 + b, 17, 8 + b, BLACK, 1); c.line(27, 6 + b, 21, 8 + b, BLACK, 1)
    c.teeth(14, 24, 13 + b, h=2); c.px(17, 16 + b, GREEN); c.px(17, 17 + b, GREEN)
    return c.finish(PURPLE, YELLOW)


def glutton(t):
    c = Canvas(30, 26)
    c.rect(9, 21, 12, 23, BROWN); c.rect(18, 21, 21, 23, BROWN)
    c.ell(15, 13, 13, 10, YELLOW, dither=ORANGE)
    m = 5 + 2 * t
    c.ell(15, 15, 9, m, BLACK); c.rect(7, 15 - m // 2 - 1, 23, 15 - m // 2, WHITE); c.rect(7, 15 + m // 2, 23, 16 + m // 2, WHITE)
    for x in range(7, 24, 3): c.line(x, 15 - m // 2, x, 17 - m // 2, BLACK); 
    c.ell(15, 17 + t, 5, 2, PINK)
    c.eye(8, 6, 3, (1, 1)); c.eye(22, 6, 3, (-1, 1))
    c.line(4, 2, 11, 4, BLACK); c.line(26, 2, 19, 4, BLACK)
    c.pts([(2, 12), (3, 14), (27, 12), (26, 15)], GREEN)  # слюни
    c.line(6, 22, 6, 25, GREEN)
    return c.finish(RED, WHITE)


def healer(t):
    c = Canvas(26, 30)
    c.rect(7, 25, 10, 28, BROWN); c.rect(15, 25, 18, 28, BROWN)
    c.rect(4, 12, 21, 25, WHITE, dither=(200, 255, 200))
    c.rect(10, 15, 15, 16, RED); c.rect(12, 13, 13, 18, RED); c.rect(11, 14, 14, 17, RED)  # крест
    c.ell(12, 7, 7, 6, SKIN); c.rect(4, 0, 20, 3, WHITE); c.rect(10, 0, 14, 2, RED)  # шапочка
    c.eye(9, 7, 2, (1, 0)); c.eye(15, 7, 2, (-1, 0))
    c.rect(6, 4, 18, 4, BLACK) if False else None
    c.rect(8, 11, 16, 11, BLACK); c.pts([(9, 10), (13, 10)], WHITE)
    c.rect(0, 14 - t * 2, 3, 20 - t * 2, WHITE)
    c.line(21, 13, 25, 7 - t, CYAN, 2); c.px(25, 6 - t, WHITE); c.pts([(26, 5 - t)], GREEN)  # шприц
    c.pts([(22, 18), (22, 20)], GREEN)
    return c.finish(GREEN, WHITE)


def looter(t):
    c = Canvas(30, 24)
    lg = t * 2
    c.rect(11, 17, 13, 21 - lg // 2, PINK); c.rect(17, 17, 19, 21 + lg // 2 - 1, PINK)
    c.ell(14, 12, 7, 6, PINK, dither=(255, 120, 245))
    c.ell(7, 8, 7, 7, BROWN, dither=YELLOW); c.rect(5, 1, 9, 2, YELLOW)  # мешок на спине
    c.pts([(6, 7), (7, 7), (7, 8), (6, 9), (7, 9)], BLACK)  # знак $
    c.ell(21, 8, 5, 5, WHITE); c.eye(22, 7, 2, (1, 0)); c.rect(19, 3, 26, 4, BLACK)  # маска вора
    c.pts([(25, 10), (26, 10), (26, 11)], YELLOW); c.rect(22, 12, 25, 12, BLACK)
    c.line(18, 12, 24, 14 + t, YELLOW, 2)  # лапа с монеткой
    c.ell(25, 15 + t, 2, 2, YELLOW)
    return c.finish(CYAN, YELLOW)


def mamka(t):
    c = Canvas(42, 42); b = t
    c.rect(11, 36, 18, 40, BROWN); c.rect(23, 36, 30, 40, BROWN)  # тапки
    c.ell(21, 26 + b, 17, 13, PINK, dither=(255, 120, 245))
    c.ell(13, 28 + b, 3, 3, WHITE); c.ell(27, 30 + b, 3, 3, WHITE); c.ell(21, 22 + b, 2, 2, YELLOW)  # горох
    c.ell(21, 12 + b, 8, 8, SKIN, dither=(220, 160, 120)); c.ell(21, 5 + b, 9, 4, PINK); c.ell(21, 1 + b, 4, 3, PINK)  # пучок
    c.pts([(10, 9 + b), (11, 12 + b), (32, 9 + b), (31, 12 + b)], PINK)
    c.eye(17, 12 + b, 3, (1, 1)); c.eye(25, 12 + b, 3, (-1, 1)); c.line(12, 8 + b, 19, 10 + b, BLACK); c.line(30, 8 + b, 23, 10 + b, BLACK)
    c.ell(21, 18 + b, 4, 3, BLACK); c.pts([(19, 17 + b), (23, 17 + b)], WHITE)  # орущий рот
    ar = t * 3
    c.line(36, 20 + b, 41, 8 - ar + 4, BROWN, 3); c.ell(40, 8 - ar + 4, 2, 3, BROWN)  # скалка
    c.ell(6, 24 + b, 4, 4, SKIN)
    return c.finish(CYAN, YELLOW)


def microbe(t):
    c = Canvas(26, 26)
    r = 8 + t
    for k in range(8):
        import math
        ang = k * math.pi / 4 + t * 0.4
        c.line(13, 13, 13 + math.cos(ang) * (r + 4), 13 + math.sin(ang) * (r + 4), GREEN); c.px(13 + math.cos(ang) * (r + 5), 13 + math.sin(ang) * (r + 5), YELLOW)
    c.ell(13, 13, r, r, GREEN, dither=(150, 255, 100))
    c.ell(9, 10, 2, 2, DGREEN); c.ell(16, 16, 3, 3, DGREEN); c.ell(17, 9, 1, 1, YELLOW)
    c.eye(10, 12, 3, (1, 0)); c.eye(17, 12, 2, (-1, 1))
    c.rect(9, 17, 16, 17, BLACK); c.pts([(10, 16), (13, 16), (15, 16)], WHITE)
    return c.finish(PURPLE, WHITE)


def egg(t):
    c = Canvas(24, 28)
    w = t
    c.ell(12, 15, 9 + w, 11, WHITE, dither=YELLOW)
    c.ell(12, 14, 7, 8, YELLOW, dither=WHITE)
    c.line(5, 8, 9, 11, BLACK); c.line(9, 11, 8, 14, BLACK); c.line(8, 14, 13, 16, BLACK)  # трещина
    c.eye(12, 14, 4, (0, 1)); c.pts([(8, 9), (17, 9), (18, 20)], GREEN)
    c.rect(10, 20, 14, 21, BLACK); c.pts([(11, 20), (13, 20)], WHITE)
    c.pts([(12 + w, 3), (5, 5 - w), (19, 4)], CYAN)
    return c.finish(PINK, WHITE)


def trash_bin(t, kind=0):
    c = Canvas(34, 38)
    r = t % 2
    c.rect(7, 13, 27, 34, GREY, dither=DGREY)                                  # корпус (мятый металл)
    for x in range(10, 27, 4): c.line(x, 14, x, 33, DGREY)                      # рёбра жёсткости
    c.rect(6, 16, 28, 17, DGREY); c.rect(6, 29, 28, 30, DGREY)                  # обручи
    c.rect(7, 13, 8, 34, WHITE, dither=GREY)                                    # блик
    c.pts([(14, 22), (15, 23), (20, 25), (21, 25), (12, 28)], BROWN)            # ржавчина и подтёки
    c.line(22, 18, 22, 22, GREEN); c.line(11, 31, 11, 33, GREEN)
    c.rect(8, 35, 11, 37, BLACK); c.rect(23, 35, 26, 37, BLACK)                 # колёсики
    c.ell(9, 37, 2, 1, DGREY); c.ell(25, 37, 2, 1, DGREY)
    c.rect(4, 8 + r, 30, 12, BLUE, dither=CYAN)                                 # крышка, чуть подпрыгивает
    c.rect(4, 8 + r, 30, 8 + r, WHITE); c.rect(14, 5 + r, 20, 7 + r, DGREY)    # ручка
    c.line(5, 12, 3, 15, BLUE)                                                  # вмятина-перекос
    c.rect(2, 20, 5, 22, DGREY); c.rect(29, 20, 32, 22, DGREY)                 # боковые ручки
    junk = [lambda: (c.line(10, 8 + r, 6, 1, WHITE), c.pts([(5, 0), (7, 1), (4, 2)], WHITE), c.line(22, 8 + r, 25, 3, YELLOW)),   # кость, банан
            lambda: (c.ell(10, 5, 4, 3, YELLOW), c.line(13, 5, 17, 1, YELLOW), c.px(9, 4, BROWN), c.rect(24, 4 + r, 26, 8, GREEN)),  # шкурка, бутылка
            lambda: (c.rect(22, 1 + r, 25, 7, CYAN), c.rect(23, 0 + r, 24, 1, WHITE), c.line(9, 8, 6, 3, PINK, 2)),                 # бутылка, носок
            lambda: (c.line(24, 8, 28, 2 + r, PINK, 2), c.line(27, 3, 30, 1, PINK), c.ell(10, 5, 3, 2, WHITE), c.px(10, 4, BLACK))][kind]  # перчатка, пакет
    junk()
    for i in range(2): c.px(5 + (t * 7 + i * 17) % 24, 3 + (t * 3 + i * 5) % 9, YELLOW)   # мухи
    c.pts([(15, 24), (16, 24), (17, 24), (16, 25)], BLACK)                       # дырка-пробоина
    return c.finish(PURPLE, YELLOW, lim=0.1)


def wifi_ghost(t):
    c = Canvas(26, 30)
    c.ell(13, 14, 10, 11, CYAN, dither=WHITE)
    for k, x in enumerate((4, 8, 12, 16, 20)):
        c.rect(x, 20, x + 3, 25 + ((k + t) % 2) * 3, CYAN, dither=WHITE)
    c.eye(9, 13, 3, (0, 1)); c.eye(17, 13, 3, (0, 1))
    c.ell(13, 20, 3, 2, BLACK)
    c.line(13, 3, 13, 0, YELLOW)
    c.px(13, 0 if t == 0 else 1, YELLOW); c.line(9, 3 - t, 13, 1, YELLOW); c.line(17, 3 - t, 13, 1, YELLOW)  # антенна-вайфай
    c.pts([(2, 12), (24, 15), (5, 6)], PINK)
    return c.finish(BLUE, WHITE)


ENEMIES = {"squid_gopnik": squid_gopnik, "chaser": chaser, "charger": charger, "spitter": spitter,
           "cockroach": cockroach, "npc_bot": npc_bot, "bruiser": bruiser, "glutton": glutton,
           "healer": healer, "looter": looter, "mamka": mamka, "microbe": microbe, "egg": egg, "trash_bin": trash_bin,
           "wifi_ghost": wifi_ghost}


def build(name):
    fn = ENEMIES[name]
    rng = random.Random(hash(name) % 997)
    frames = [fn(0), fn(1)]
    return sheet(frames)


def build_bin_variants():
    for k in range(4):
        sheet([trash_bin(0, k), trash_bin(1, k)]).save(f"tools/_preview/enemies_new/enemy_trash_bin_{k}.png")
        if APPLY: sheet([trash_bin(0, k), trash_bin(1, k)]).save(f"assets/sprites/enemy_trash_bin_{k}.png")


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    APPLY = apply
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ENEMIES)
    os.makedirs("tools/_preview/enemies_new", exist_ok=True)
    k = 6; x = 6
    imgs = [(n, build(n)) for n in names]
    W = sum(i.width // 2 * k + 14 for _, i in imgs) + 6
    H = max(i.height for _, i in imgs) * k + 12
    prev = Image.new("RGBA", (W, H), (45, 30, 20, 255))
    for n, im in imgs:
        im.save(f"tools/_preview/enemies_new/enemy_{n}.png")
        if apply: im.save(f"assets/sprites/enemy_{n}.png")
        fr = im.crop((0, 0, im.width // 2, im.height)).resize((im.width // 2 * k, im.height * k), Image.NEAREST)
        prev.paste(fr, (x, 6), fr); x += im.width // 2 * k + 14
    if "trash_bin" in names: build_bin_variants()
    prev.save("tools/_preview/enemies_new.png")
