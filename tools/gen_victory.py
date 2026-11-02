#!/usr/bin/env python3
"""Ролик победы (идея 19): за воротами - помойка ещё больше. Три слоя для параллакса:
небо (480x270), дальние горы мусора (720x120), ближняя помойка с дорогой (720x150).
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_victory.py -> assets/ui/victory_*.png, превью tools/_preview/victory.png"""
import math
import numpy as np
from PIL import Image
from pix import *

R = np.random.default_rng(19)
SKY_TOP = (60, 10, 80); SKY_MID = (200, 40, 120); SKY_LOW = (255, 160, 40)
MUD = (90, 55, 30); DMUD = (50, 30, 20); RUST = (170, 80, 30)


def sky():
    c = Canvas(480, 270)
    for y in range(270):
        t = y / 200.0
        a, b, k = (SKY_TOP, SKY_MID, t * 2) if t < 0.5 else (SKY_MID, SKY_LOW, (t - 0.5) * 2)
        k = min(max(k, 0), 1)
        col = tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))
        nxt = tuple(int(a[i] + (b[i] - a[i]) * min(k + 0.08, 1)) for i in range(3))
        c.a[y, :] = (*col, 255)
        c.a[y, (np.arange(480) + y) % 2 == 0] = (*nxt, 255)      # дизеринг полос
    c.ell(360, 150, 38, 38, YELLOW, dither=ORANGE)               # кислотное солнце садится в мусор
    for k in range(5): c.line(322, 140 + k * 7, 398, 140 + k * 7, SKY_MID)
    for _ in range(60): c.px(int(R.integers(0, 480)), int(R.integers(0, 90)), WHITE)
    for i in range(7):                                           # голуби/чайки на закате
        x, y = int(R.integers(30, 450)), int(R.integers(20, 100))
        c.pts([(x - 2, y - 1), (x - 1, y), (x, y), (x + 1, y), (x + 2, y - 1)], BLACK)
    return c.a


def ridge(w, h, base, amp, col, dith, junk):
    c = Canvas(w, h)
    xs = np.arange(w)
    top = base - amp * (0.6 * np.sin(xs / 37.0) + 0.3 * np.sin(xs / 13.0 + 1.7) + 0.2 * np.sin(xs / 5.0))
    for x in range(w):
        y0 = int(top[x])
        c.a[y0:, x] = (*col, 255)
        for y in range(y0, h):
            if (x + y) % 2 == 0 and (y - y0) < 3: c.a[y, x] = (*dith, 255)
    for _ in range(junk):                                        # торчащий хлам на склоне
        x = int(R.integers(0, w)); y = int(top[x]) + int(R.integers(0, 12))
        kind = int(R.integers(0, 5))
        if kind == 0: c.rect(x, y - 6, x + 5, y, GREY, dither=DGREY)                 # холодильник
        elif kind == 1: c.line(x, y, x + 7, y - 5, RUST, 2)                          # труба
        elif kind == 2: c.ell(x, y - 2, 3, 3, BLACK); c.px(x, y - 2, GREY)            # шина
        elif kind == 3: c.rect(x, y - 4, x + 3, y, BLUE)                             # бак
        else: c.pts([(x, y - 3), (x + 1, y - 4), (x + 2, y - 3)], GREEN)            # бутылки
    return c.a, top


def far():
    a, _ = ridge(720, 120, 70, 30, (70, 25, 70), (100, 40, 90), 90)
    for x in (120, 380, 610):                                    # трубы мусоросжигателя с дымом
        c = Canvas(720, 120); c.a = a
        c.rect(x, 20, x + 6, 80, DGREY); c.rect(x, 20, x + 6, 22, RED)
        for k in range(6): c.ell(x + 3 + k * 4, 14 - k * 3, 4 + k, 3 + k // 2, (120, 100, 110))
    return a


def near():
    a, top = ridge(720, 150, 60, 22, MUD, (120, 75, 40), 160)
    c = Canvas(720, 150); c.a = a
    c.ell(520, int(top[520]) - 6, 16, 10, BROWN, dither=MUD)     # куча с сиянием на вершине
    c.ell(520, int(top[520]) - 16, 6, 4, GREEN, dither=YELLOW)
    for k in range(4): c.line(520, int(top[520]) - 22 - k * 3, 520 + (k - 2) * 6, int(top[520]) - 34 - k * 4, YELLOW)
    c.rect(200, int(top[200]) - 30, 202, int(top[200]), GREY)  # фонарь
    c.ell(204, int(top[200]) - 30, 3, 2, YELLOW)
    c.rect(600, int(top[600]) - 16, 640, int(top[600]) - 8, WHITE)   # табличка «ДОБРО ПОЖАЛОВАТЬ»
    c.rect(618, int(top[600]) - 8, 620, int(top[600]), BROWN)
    for i, x in enumerate(range(603, 638, 5)): c.rect(x, int(top[600]) - 13, x + 2, int(top[600]) - 11, RED)
    return a


def road():
    """Дорога от зрителя к кладбищу на горизонте (неподвижный слой поверх помойки)."""
    c = Canvas(480, 90)
    for y in range(90):
        k = y / 89.0                        # 0 - горизонт, 1 - у ног
        half = int(8 + k * 70)
        x0, x1 = 240 - half, 240 + half
        c.a[y, x0:x1] = (*DMUD, 255)
        c.a[y, x0:x1][(np.arange(x1 - x0) + y) % 3 == 0] = (*MUD, 255)
        if y % 12 < 6: c.a[y, 239:241] = (*YELLOW, 200)          # стёртая разметка
        c.a[y, max(x0 - 1, 0)] = (*BLACK, 255); c.a[y, min(x1, 479)] = (*BLACK, 255)
    for _ in range(40):                                          # мусор на обочине и лужи
        y = int(R.integers(8, 88)); k = y / 89.0; half = int(8 + k * 70)
        x = 240 + int(R.choice([-1, 1])) * int(half * R.uniform(0.3, 0.9))
        c.ell(x, y, max(1, int(k * 4)), max(1, int(k * 2)), (60, 100, 160) if R.random() < 0.4 else BROWN)
    return c.a


def yard():
    """Кладбище на горизонте: ограда, ворота-арка, кресты, фонарь - туда и идёт герой."""
    c = Canvas(120, 48)
    c.ell(60, 47, 62, 17, (60, 50, 45), dither=(80, 70, 60))   # холм-курган
    for x in range(2, 118, 4): c.line(x, 26, x, 34, DGREY)       # ограда
    c.line(0, 27, 119, 27, DGREY)
    c.rect(50, 14, 52, 34, DGREY); c.rect(67, 14, 69, 34, DGREY); c.line(50, 13, 69, 13, DGREY, 2)   # ворота
    c.pts([(55, 11), (58, 10), (61, 10), (64, 11)], DGREY)
    for (x, y) in ((10, 20), (24, 18), (36, 22), (84, 21), (96, 17), (108, 22)):   # кресты
        c.line(x, y, x, y + 10, (200, 190, 170)); c.line(x - 2, y + 3, x + 2, y + 3, (200, 190, 170))
    c.rect(78, 8, 79, 30, GREY); c.ell(80, 8, 2, 1, YELLOW)     # фонарь
    c.pts([(40, 6), (44, 4), (90, 5)], BLACK)                    # вороны
    return c.a


if __name__ == "__main__":
    Image.fromarray(road()).save("assets/ui/victory_road.png")
    Image.fromarray(yard()).save("assets/ui/victory_yard.png")
    Image.fromarray(sky()).save("assets/ui/victory_sky.png")
    Image.fromarray(far()).save("assets/ui/victory_far.png")
    Image.fromarray(near()).save("assets/ui/victory_near.png")
    s = Image.open("assets/ui/victory_sky.png").convert("RGBA")
    f = Image.open("assets/ui/victory_far.png"); n = Image.open("assets/ui/victory_near.png")
    s.paste(f, (-60, 120), f); s.paste(n, (-100, 140), n)
    r = Image.open("assets/ui/victory_road.png"); y = Image.open("assets/ui/victory_yard.png")
    s.paste(y, (180, 140), y); s.paste(n, (-100, 140), n); s.paste(r, (0, 180), r)
    s.save("tools/_preview/victory.png"); print("ok")
