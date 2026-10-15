#!/usr/bin/env python3
"""Декорации за проволокой: 16 видов × 4 кадра анимации по 48×32, с запечённым глитчем. -> assets/sprites/arena_border.png"""
import sys, random, math
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
W, H, FR = 46, 30, 4
FIRE = [RED, ORANGE, YELLOW]


def fire(c, x, y, t, s=1):
    for i, dx in enumerate((-2, 0, 2)):
        h = (4 + (t + i) % 3 * 2) * s
        c.line(x + dx, y, x + dx + (1 if (t + i) % 2 else -1), y - h, FIRE[(t + i) % 3], 2)
    c.px(x + (t % 2) * 3 - 1, y - 11 * s, YELLOW)


def smoke(c, x, y, t, col=GREY):
    for k in range(3):
        c.ell(x + (k + t) % 3 - 1, y - k * 3 - t, 2, 2, col, dither=DGREY)


def barrel(t):
    c = Canvas(W, H)
    c.rect(14, 12, 32, 28, DGREY, dither=GREY); c.rect(14, 16, 32, 17, BLACK); c.rect(14, 24, 32, 25, BLACK)
    c.rect(13, 10, 33, 12, GREY); fire(c, 23, 11, t, 2)
    c.pts([(10 + t * 3, 4 - t), (36 - t * 2, 2 + t), (30, 6)], YELLOW)
    c.pts([(18, 20), (28, 22)], RED); c.eye(23, 21, 2, (0, 1))
    return c, (PURPLE, YELLOW)


def dumpster(t):
    c = Canvas(W, H)
    c.rect(6, 12, 40, 27, GREEN, dither=DGREEN); lid = [0, 1, 3, 1][t]
    c.rect(4, 8 - lid, 42, 12 - lid, BLUE, dither=CYAN)
    for x in range(10, 38, 6): c.line(x, 14, x, 26, DGREEN)
    c.rect(12, 18, 34, 19, DGREEN); c.pts([(20, 22), (26, 24), (14, 25)], BROWN); c.line(30, 14, 30, 18, GREEN)
    c.rect(8, 28, 12, 29, BLACK); c.rect(34, 28, 38, 29, BLACK)
    for i in range(3): c.px(10 + ((t * 5 + i * 11) % 30), 4 + (i + t) % 4, YELLOW)
    c.line(20, 9 - lid, 18, 3, GREEN); c.line(26, 9 - lid, 29, 4 - (t % 2), PINK)
    return c, (PURPLE, YELLOW)


def tv(t):
    c = Canvas(W, H)
    c.rect(8, 6, 38, 26, DGREY); c.rect(11, 9, 35, 23, BLACK)
    rng = random.Random(t)
    for _ in range(40): c.px(rng.randint(11, 35), rng.randint(9, 23), rng.choice([WHITE, GREY, CYAN, PINK]))
    if t % 2 == 0:
        c.eye(19, 14, 3, (0, 1)); c.eye(28, 14, 3, (0, 1)); c.rect(18, 19, 29, 21, BLACK); c.teeth(18, 29, 19, h=2)
    c.line(18, 6, 12, 0 + t % 2 * 2, GREY); c.line(28, 6, 34, 1, GREY)
    c.rect(12, 26, 16, 28, BLACK); c.rect(30, 26, 34, 28, BLACK); c.px(36, 12, RED if t < 2 else GREEN)
    return c, (CYAN, WHITE)


def car(t):
    c = Canvas(W, H)
    c.rect(3, 15, 43, 25, RED, dither=(150, 0, 30)); c.rect(10, 8, 34, 15, RED); c.rect(13, 10, 21, 14, CYAN, dither=WHITE); c.rect(24, 10, 32, 14, CYAN, dither=WHITE)
    c.line(14, 10, 20, 14, BLACK); c.ell(11, 26, 5, 5, BLACK); c.ell(35, 26, 5, 5, BLACK); c.ell(11, 26, 2, 2, GREY); c.ell(35, 26, 2, 2, GREY)
    c.rect(40, 17, 43, 19, YELLOW if t % 2 == 0 else (120, 120, 0)); c.rect(3, 17, 5, 19, RED)
    smoke(c, 22, 8, t); c.eye(27, 20, 3, (-1, 0)); c.pts([(8, 20), (16, 21)], BLACK)
    return c, (PINK, YELLOW)


def toilet(t):
    c = Canvas(W, H)
    c.rect(14, 4, 32, 12, WHITE, dither=GREY); c.ell(23, 19, 15, 9, WHITE, dither=GREY); c.ell(23, 17, 11, 5, GREEN, dither=YELLOW)
    for i in range(3): c.ell(18 + i * 5, 14 - (t + i) % 3, 2, 2, GREEN)
    c.rect(18, 26, 28, 29, GREY); c.eye(23, 8, 2, (0, 1))
    c.line(33, 6, 38, 12, GOLD := (255, 200, 0), 2); c.rect(34, 2, 36, 5, GOLD)
    c.pts([(7, 20 + t % 2), (40, 24)], GREEN)
    return c, (CYAN, PINK)


def tires(t):
    c = Canvas(W, H)
    for (x, y) in ((12, 22), (28, 22), (20, 12), (38, 22)):
        c.ell(x, y, 8, 7, BLACK); c.ell(x, y, 3, 3, DGREY); c.ell(x, y, 8, 7, DGREY) if False else None
    c.ell(20, 12, 3, 3, GREY); c.eye(20, 12, 2, (0, 1)); smoke(c, 20, 6, t, DGREY)
    c.ell(12, 22, 3, 3, GREY); c.ell(28, 22, 3, 3, GREY)
    c.pts([(24 + t, 5), (10, 9 - t)], ORANGE); c.rect(34, 14, 36, 16, RED if t % 2 else YELLOW)
    return c, (GREEN, YELLOW)


def pipe(t):
    c = Canvas(W, H)
    c.rect(3, 4, 40, 12, DGREY, dither=GREY); c.rect(36, 2, 44, 14, GREY)
    for x in (8, 18, 28): c.rect(x, 4, x + 1, 12, BLACK)
    drip = [0, 5, 11, 16][t]
    c.rect(38, 14, 42, 16, GREEN); c.ell(40, 16 + drip, 2, 3, GREEN); c.pts([(40, 15)], WHITE)
    c.ell(40, 29, 6 + (t % 2), 2, GREEN, dither=YELLOW)
    c.eye(14, 8, 2, (1, 0)); c.pts([(25, 7)], GREEN)
    return c, (PINK, WHITE)


def rat(t):
    c = Canvas(W, H)
    c.ell(18, 24, 16, 5, BROWN, dither=GREEN); c.pts([(6, 22), (28, 21), (14, 20)], YELLOW)
    c.ell(24, 14, 10, 8, GREY, dither=WHITE); c.ell(36, 12, 6, 5, GREY, dither=WHITE)
    c.ell(30, 5, 3, 3, PINK); c.ell(36, 5, 3, 3, PINK)
    c.eye(34, 11, 2, (1, 0), blood=True) if t != 2 else c.rect(33, 11, 36, 11, BLACK)
    c.px(41, 13, PINK); c.teeth(36, 40, 16, h=1)
    c.line(14, 16, 4, 14 + [0, 3, 0, -3][t], PINK, 1); c.line(4, 14 + [0, 3, 0, -3][t], 2, 9, PINK)
    c.line(38, 14, 44, 13 + t % 2, BLACK)
    return c, (PINK, WHITE)


def fridge(t):
    c = Canvas(W, H)
    c.rect(10, 2, 30, 28, WHITE, dither=GREY); c.rect(12, 5, 28, 12, GREY); c.rect(12, 15, 28, 26, BLACK if t % 3 == 2 else (30, 30, 10))
    c.rect(27, 6, 28, 10, DGREY)
    sw = [0, 3, 6, 3][t]
    c.line(20, 22, 20 + sw, 16 - sw // 2, GREEN, 3); c.line(24, 22, 28 - sw, 13, PINK, 2); c.eye(20 + sw, 15 - sw // 2, 2, (0, 1))
    c.px(34, 20, YELLOW); c.rect(32, 14, 36, 14, YELLOW if t != 2 else BLACK)
    return c, (CYAN, YELLOW)


def grave(t):
    c = Canvas(W, H)
    c.ell(20, 12, 10, 9, GREY, dither=WHITE); c.rect(10, 12, 30, 27, GREY, dither=WHITE)
    c.line(20, 6, 20, 14, BLACK); c.line(16, 9, 24, 9, BLACK)
    c.rect(4, 27, 38, 29, BROWN, dither=GREEN)
    h = [0, 2, 4, 2][t]
    c.rect(35, 15 - h, 38, 27, GREEN); c.ell(36, 13 - h, 3, 3, GREEN)
    for k in range(3): c.line(34 + k * 2, 11 - h, 34 + k * 2, 14 - h, GREEN)
    c.pts([(12, 3 + t % 2), (30, 5)], CYAN)
    return c, (PURPLE, CYAN)


def lamp(t):
    c = Canvas(W, H)
    c.rect(22, 8, 24, 28, DGREY); c.rect(16, 28, 30, 29, DGREY); c.line(23, 6, 36, 4, DGREY, 2)
    on = [1, 1, 0, 1][t]
    c.ell(37, 7, 5, 4, YELLOW if on else DGREY, dither=WHITE if on else None)
    if on:
        c.ell(37, 18, 8, 8, (80, 80, 0), dither=None) if False else None
        for k in range(3): c.line(33 + k * 4, 11, 31 + k * 6, 24, (120, 120, 0))
    c.pts([(30 + t * 2, 6 + t), (40 - t * 3, 14 - t)], WHITE); c.eye(23, 16, 2, (0, 1))
    return c, (PINK, YELLOW)


def cart(t):
    c = Canvas(W, H)
    c.line(6, 6, 12, 6, GREY, 2); c.line(10, 6, 14, 20, GREY, 2); c.rect(14, 8, 40, 20, GREY, dither=WHITE)
    for x in range(16, 40, 4): c.line(x, 8, x, 20, BLACK)
    c.line(14, 14, 40, 14, BLACK); c.line(14, 20, 38, 20, DGREY, 2)
    for x in (18, 36):
        c.ell(x, 25, 4, 4, BLACK); k = t % 4
        c.px(x + [0, 2, 0, -2][k], 25 + [-2, 0, 2, 0][k], YELLOW)
    c.eye(26, 12, 3, (1, 1)); c.eye(34, 12, 3, (-1, 1))
    c.rect(24, 15, 36, 16, BLACK); c.pts([(26, 15), (30, 15), (34, 15)], WHITE)
    c.pts([(20, 2 + t % 2), (40, 4)], PINK)
    return c, (PINK, YELLOW)


def bottles(t):
    c = Canvas(W, H)
    cols = [GREEN, CYAN, YELLOW, PINK]
    for row, n in enumerate((4, 3, 2)):
        for i in range(n):
            x = 8 + i * 9 + row * 4; y = 22 - row * 8
            c.rect(x, y, x + 5, y + 6, cols[(i + row) % 4]); c.rect(x + 2, y - 4, x + 3, y, cols[(i + row) % 4]); c.px(x + 1, y + 1, WHITE)
    for k in range(3): c.ell(14 + k * 9, 6 - (t * 2 + k * 3) % 8, 1, 1, WHITE)
    c.eye(20, 10, 2, (0, 1)); c.rect(4, 28, 42, 29, BROWN)
    return c, (PURPLE, WHITE)


def dummy(t):
    c = Canvas(W, H)
    c.rect(18, 14, 28, 26, SKIN, dither=(220, 160, 120)); c.rect(10, 14, 36, 17, SKIN); c.ell(23, 8, 6, 6, SKIN)
    c.rect(22, 26, 24, 29, DGREY); c.rect(16, 29, 30, 29, DGREY)
    c.eye(21, 7, 2, (1, 0)); c.eye(26, 7, 2, (-1, 0)); c.rect(22, 11, 26, 11, BLACK)
    c.rect(27, 11, 32, 11, WHITE); c.px(33, 11, ORANGE if t % 2 else RED)
    smoke(c, 34, 10, t, WHITE)
    c.pts([(14, 20), (30, 22)], PINK); c.line(18, 18, 28, 24, RED)
    return c, (CYAN, YELLOW)


def radbarrel(t):
    c = Canvas(W, H)
    c.rect(14, 8, 32, 28, YELLOW, dither=ORANGE); c.rect(14, 12, 32, 13, BLACK); c.rect(14, 24, 32, 25, BLACK)
    c.ell(23, 19, 4, 4, BLACK); c.pts([(23, 19), (20, 17), (26, 17), (23, 23)], YELLOW)
    c.ell(23, 4, 9 + t % 2 * 2, 5, GREEN, dither=YELLOW)
    for k in range(4): c.px(12 + k * 8, 26 - (t * 3 + k * 5) % 20, GREEN)
    c.line(32, 26, 40, 28, GREEN, 2)
    return c, (GREEN, WHITE)


def pigeons(t):
    c = Canvas(W, H)
    c.ell(24, 25, 18, 5, BROWN, dither=GREEN)
    for (x, y, ph) in ((12, 17, 0), (24, 14, 1), (35, 18, 2)):
        d = (t + ph) % 4 // 2
        c.ell(x, y + d, 5, 4, GREY, dither=WHITE); c.ell(x + 4, y - 3 + d, 3, 3, GREY); c.px(x + 5, y - 3 + d, RED); c.line(x + 7, y - 3 + d, x + 9, y - 2 + d, YELLOW)
        c.line(x - 5, y + d, x - 8, y + 2 + d + (t % 2), GREY)
    c.pts([(6, 10), (40, 8 + t)], YELLOW)
    return c, (PINK, WHITE)


def piano(t):
    c = Canvas(W, H)
    c.rect(4, 8, 42, 20, BLACK, dither=DGREY); c.rect(4, 20, 42, 24, WHITE)
    for x in range(6, 42, 3): c.line(x, 20, x, 24, BLACK)
    c.rect(10 + t * 2, 20, 12 + t * 2, 25, PINK)
    c.rect(6, 24, 9, 29, BLACK); c.rect(37, 24, 40, 29, BLACK); c.rect(8, 4, 38, 8, DGREY)
    c.pts([(14 + t * 6, 3 - t % 2), (30, 2 + t)], YELLOW); c.pts([(20, 14), (21, 13), (22, 14)], WHITE)
    return c, (PINK, YELLOW)


def couch(t):
    c = Canvas(W, H)
    c.rect(4, 8, 42, 22, PINK, dither=(200, 0, 190)); c.rect(2, 14, 8, 26, PINK); c.rect(38, 14, 44, 26, PINK)
    c.rect(10, 16, 36, 24, (255, 90, 245)); c.line(22, 16, 22, 24, BLACK)
    c.rect(5, 26, 8, 29, BLACK); c.rect(38, 26, 41, 29, BLACK)
    sp = [0, 2, 4, 2][t]
    c.line(28, 16, 31, 8 - sp, GREY); c.line(31, 8 - sp, 27, 4 - sp, GREY); c.ell(26, 3 - sp, 3, 2, WHITE)   # пружина и вата
    smoke(c, 14, 8, t, WHITE); c.pts([(33, 18), (14, 20)], BROWN)
    return c, (CYAN, YELLOW)


def washer(t):
    c = Canvas(W, H)
    c.rect(10, 2, 36, 28, WHITE, dither=GREY); c.rect(12, 4, 20, 6, DGREY); c.pts([(32, 5)], RED)
    c.ell(23, 17, 9, 9, DGREY); c.ell(23, 17, 7, 7, CYAN, dither=WHITE)
    a = t * math.pi / 2
    c.ell(23 + math.cos(a) * 3, 17 + math.sin(a) * 3, 2, 2, PINK); c.ell(23 - math.cos(a) * 3, 17 - math.sin(a) * 3, 2, 2, YELLOW)
    for k in range(3): c.ell(34 + k, 8 - (t + k) % 3 * 3, 2, 2, WHITE)
    c.rect(10, 28, 14, 29, BLACK); c.rect(32, 28, 36, 29, BLACK)
    return c, (PINK, WHITE)


def bath(t):
    c = Canvas(W, H)
    c.ell(23, 16, 20, 10, WHITE, dither=GREY); c.ell(23, 13, 17, 6, GREEN, dither=YELLOW)
    for k in range(3): c.ell(14 + k * 8, 11 - (t + k) % 3, 2, 2, GREEN)
    c.ell(30, 10 - t % 2, 4, 3, YELLOW); c.px(33, 9 - t % 2, ORANGE); c.px(31, 8 - t % 2, BLACK)    # уточка
    c.rect(6, 26, 10, 29, GREY); c.rect(36, 26, 40, 29, GREY); c.line(5, 8, 5, 3, GREY, 2); c.line(5, 3, 10, 3, GREY, 2)
    c.pts([(5, 10 + t * 3)], CYAN)
    return c, (CYAN, WHITE)


def skulls(t):
    c = Canvas(W, H)
    for (x, y, r) in ((12, 22, 6), (26, 21, 7), (36, 23, 5), (19, 14, 5)):
        c.ell(x, y, r, r, WHITE, dither=GREY); c.ell(x - 2, y, 1, 2, BLACK); c.ell(x + 2, y, 1, 2, BLACK); c.px(x, y + 2, BLACK)
    c.line(4, 28, 40, 26, WHITE, 2)
    c.rect(24, 8, 26, 14, YELLOW); fire(c, 25, 8, t, 1)
    c.pts([(8, 8), (40, 12)], PINK)
    return c, (PURPLE, CYAN)


def tentacle(t):
    c = Canvas(W, H)
    c.rect(8, 24, 38, 29, DGREY); 
    for x in range(10, 38, 4): c.line(x, 24, x, 29, BLACK)
    for k, base in enumerate((16, 26, 34)):
        for j in range(14):
            x = base + math.sin((j * 0.6) + t * 1.5 + k) * (2 + j * 0.3); y = 24 - j
            c.ell(x, y, 3 - j * 0.12, 2, PINK if k != 1 else GREEN)
        c.px(base + math.sin(14 * 0.6 + t * 1.5 + k) * 6, 9, YELLOW)
    return c, (CYAN, WHITE)


def arcade(t):
    c = Canvas(W, H)
    c.rect(12, 2, 34, 28, BLUE, dither=(80, 80, 255)); c.rect(14, 5, 32, 15, BLACK)
    rng = random.Random(t * 3)
    for _ in range(16): c.px(rng.randint(15, 31), rng.randint(6, 14), rng.choice([GREEN, PINK, YELLOW, CYAN]))
    c.rect(14, 18, 32, 21, DGREY); c.ell(18, 19, 2, 2, RED); c.ell(26, 19, 2, 2, YELLOW); c.ell(30, 19, 1, 1, GREEN)
    c.rect(18, 24, 28, 28, BLACK); c.px(23, 26, YELLOW if t % 2 else BLACK)
    c.pts([(10, 6), (36, 10 + t)], PINK)
    return c, (PINK, WHITE)


def mailbox(t):
    c = Canvas(W, H)
    c.rect(10, 8, 34, 24, BLUE, dither=CYAN); c.ell(22, 8, 12, 4, BLUE); c.rect(20, 24, 24, 29, DGREY)
    c.rect(36, 10, 38, 16, RED); c.rect(34, 10, 38, 12, RED)
    c.rect(12, 14, 32, 18, BLACK)
    for k in range(3):
        y = 2 + (t * 3 + k * 5) % 12
        c.rect(14 + k * 9, 8 - y // 3, 19 + k * 9, 10 - y // 3, WHITE); c.px(16 + k * 9, 9 - y // 3, RED)
    return c, (PINK, YELLOW)


def dish(t):
    c = Canvas(W, H)
    c.line(22, 28, 22, 14, DGREY, 3); c.rect(14, 28, 30, 29, DGREY)
    a = [0, 1, 2, 1][t]
    c.ell(22 + a, 11, 14, 8, GREY, dither=WHITE); c.ell(22 + a, 13, 12, 6, WHITE, dither=GREY)
    c.line(22 + a, 13, 28 + a, 3, DGREY); c.ell(28 + a, 3, 2, 2, RED if t % 2 else YELLOW)
    for k in range(3): c.px(8 + k * 4 + t, 2 + k, CYAN)
    c.pts([(10, 4), (36, 6)], YELLOW)
    return c, (PINK, YELLOW)


def slippers(t):
    c = Canvas(W, H)
    for (x, y) in ((10, 22), (22, 24), (33, 21), (16, 14)):
        c.ell(x, y, 7, 4, BROWN, dither=ORANGE); c.rect(x - 4, y - 5, x + 3, y - 2, BROWN)
    c.ell(22, 24, 2, 2, RED if t % 2 == 0 else BLACK); c.px(22, 24, WHITE)         # мигающая мина
    c.rect(8, 9, 12, 9, YELLOW); c.pts([(30, 10), (31, 9), (32, 10)], GREEN)
    smoke(c, 40, 20, t, GREEN)
    return c, (PINK, YELLOW)


def monitors(t):
    c = Canvas(W, H)
    for (x, y, w, h) in ((6, 16, 14, 11), (20, 18, 14, 10), (13, 5, 14, 11), (28, 8, 12, 9)):
        c.rect(x, y, x + w, y + h, DGREY, dither=GREY); c.rect(x + 2, y + 2, x + w - 2, y + h - 2, BLACK)
    rng = random.Random(t)
    for (x, y) in ((8, 18), (22, 20), (15, 7), (30, 10)):
        for _ in range(8): c.px(x + rng.randint(0, 9), y + rng.randint(0, 6), rng.choice([GREEN, CYAN, WHITE]))
    c.line(10, 28, 36, 28, BLACK); c.line(34, 12, 40, 2, BLACK)
    return c, (PINK, YELLOW)


def carriage(t):
    c = Canvas(W, H)
    c.ell(20, 14, 14, 9, PINK, dither=(255, 120, 245)); c.rect(6, 14, 34, 20, PINK); c.line(32, 14, 40, 6, DGREY, 2)
    for (x, r) in ((12, 5), (30, 5)):
        c.ell(x, 24, r, r, BLACK); k = t % 4
        c.px(x + [0, 3, 0, -3][k], 24 + [-3, 0, 3, 0][k], WHITE); c.ell(x, 24, 1, 1, GREY)
    c.eye(19, 12, 3, [(0, 0), (1, 0), (0, 1), (-1, 0)][t]); c.pts([(8, 10), (30, 12)], YELLOW)
    return c, (CYAN, YELLOW)


def pole(t):
    c = Canvas(W, H)
    c.rect(21, 4, 24, 29, BROWN); c.rect(10, 7, 36, 9, BROWN); c.rect(14, 13, 32, 14, BROWN)
    for x in (10, 22, 36): c.rect(x, 5, x + 1, 7, WHITE)
    for k in range(3):
        sx = [11, 23, 36][k]
        y1 = 10 + (t + k) % 3 * 3
        c.line(sx, 7, sx + (-1) ** k * 4, y1 + 6, YELLOW); c.line(sx + (-1) ** k * 4, y1 + 6, sx + (-1) ** k * 2, y1 + 12, CYAN)
    c.pts([(26, 12 + t), (18, 16 - t)], WHITE)
    return c, (PINK, YELLOW)


def bike(t):
    c = Canvas(W, H)
    for x in (11, 34):
        c.ell(x, 20, 8, 8, BLACK); c.ell(x, 20, 6, 6, None or (0, 0, 0)) if False else None
        a = t * math.pi / 4
        for k in range(4):
            ang = a + k * math.pi / 4
            c.line(x - math.cos(ang) * 6, 20 - math.sin(ang) * 6, x + math.cos(ang) * 6, 20 + math.sin(ang) * 6, GREY)
    c.line(11, 20, 21, 10, RED, 2); c.line(21, 10, 34, 20, RED, 2); c.line(21, 10, 29, 10, RED, 2); c.line(29, 10, 34, 20, RED, 2); c.line(26, 8, 31, 6, BLACK, 2)
    c.pts([(20, 6), (38, 8)], YELLOW)
    return c, (CYAN, YELLOW)


def vending(t):
    c = Canvas(W, H)
    c.rect(12, 2, 34, 28, RED, dither=(150, 0, 30)); c.rect(15, 5, 31, 18, BLACK if t % 3 == 2 else (30, 40, 60))
    for r in range(2):
        for k in range(4): c.rect(16 + k * 4, 6 + r * 6, 18 + k * 4, 9 + r * 6, [CYAN, GREEN, YELLOW, PINK][(k + r + t) % 4])
    c.rect(15, 21, 31, 24, DGREY); c.rect(17, 25 + t % 2, 22, 27, CYAN)
    c.px(33, 8, GREEN if t < 2 else RED); c.pts([(36, 6), (8, 14)], YELLOW)
    return c, (CYAN, WHITE)

KINDS = [barrel, dumpster, tv, car, toilet, tires, pipe, rat, fridge, grave, lamp, cart, bottles, dummy, radbarrel, pigeons,
         piano, couch, washer, bath, skulls, tentacle, arcade, mailbox, dish, slippers, monitors, carriage, pole, bike, vending]

if __name__ == "__main__":
    out = Image.new("RGBA", (48 * FR * len(KINDS), 32), (0, 0, 0, 0))
    for ki, fn in enumerate(KINDS):
        for t in range(FR):
            c, (shade, hi) = fn(t)
            a = c.finish(shade, hi, glitch=(5 if t == 3 else 0), rng=random.Random(ki * 31 + t), lim=0.05)
            im = Image.fromarray(a, "RGBA")
            out.paste(im, ((ki * FR + t) * 48 + (48 - im.width) // 2, 32 - im.height), im)
    out.save("assets/sprites/arena_border.png")
    k = 3
    prev = Image.new("RGBA", (48 * FR * 4 * k // 1 // 1, 32 * 4 * k + 8), (60, 34, 16, 255))
    for ki in range(len(KINDS)):
        fr = out.crop((ki * FR * 48, 0, ki * FR * 48 + 48 * FR, 32)).resize((48 * FR * 2, 64), Image.NEAREST)
        prev.paste(fr, ((ki % 4) * 48 * FR * 2 // 2 * 1, (ki // 4) * 66), fr)
    prev = prev.crop((0, 0, 4 * 48 * FR * 1, 4 * 66))
    prev.save("tools/_preview/decor_new.png")
