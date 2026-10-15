#!/usr/bin/env python3
"""Огромные дома: по файлу на дом (4 кадра в ряд). assets/sprites/border_house_N.png"""
import sys, random, math
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
import importlib.util
spec = importlib.util.spec_from_file_location("rd", "tools/redraw_decor.py")
rd = importlib.util.module_from_spec(spec); spec.loader.exec_module(rd)
FR = 4; GOLD = (255, 200, 0)


def win(c, x, y, w, h, on, col, t, eye=False):
    c.rect(x, y, x + w, y + h, col if on else BLACK)
    if on:
        c.line(x + w // 2, y, x + w // 2, y + h, BLACK)
        if eye: c.eye(x + w // 2, y + h // 2, 2, [(0, 0), (1, 0), (0, 1), (-1, 0)][t], blood=True)
    c.rect(x - 1, y + h + 1, x + w + 1, y + h + 1, DGREY)


def panel(t):
    W, H = 214, 116
    c = Canvas(W, H); rng = random.Random(1)
    c.rect(8, 14, W - 8, H - 1, GREY, dither=DGREY)
    for y in range(26, H - 8, 20): c.line(8, y + 14, W - 8, y + 14, DGREY)
    c.rect(4, 8, W - 4, 14, DGREY); c.rect(4, 8, W - 4, 9, WHITE)
    for r in range(5):
        for k in range(11):
            x, y = 14 + k * 18, 20 + r * 18
            on = rng.random() < 0.55
            if on and rng.random() < 0.2 and (t + r + k) % 4 == 0: on = False
            win(c, x, y, 9, 11, on, [YELLOW, CYAN, PINK, (255, 200, 120)][(r + k) % 4], t, eye=(r == 2 and k == 5))
            if rng.random() < 0.12: c.line(x - 1, y + 14, x + 12, y + 15 + t % 2, WHITE)   # бельё на балконе
    c.rect(95, 92, 118, H - 1, BLACK); c.rect(95, 92, 118, 94, RED); c.pts([(100, 100)], YELLOW)
    for x in (20, 60, 100, 150, 190):
        c.line(x, 8, x, 0 + (x % 7), DGREY); c.line(x - 5, 3 + (x % 5), x + 6, 3 + (x % 5) + t % 2, DGREY)
    c.ell(176, 6, 10, 5, GREY, dither=WHITE); c.line(176, 6, 182, 0, DGREY)
    c.rect(20, 2, 26, 8, DGREY); smoke(c, 23, 0, t, GREY) if False else None
    c.pts([(6, 40 + t * 3), (W - 6, 70 - t * 2), (30, 30)], YELLOW)
    c.line(10, 20, 6, 60, GREEN); c.line(W - 10, 30, W - 7, 80, PINK)                                # граффити-подтёки
    return c, (PURPLE, CYAN)


def brick(t):
    W, H = 196, 108
    c = Canvas(W, H); rng = random.Random(2)
    c.rect(10, 34, W - 10, H - 1, RED, dither=(150, 0, 30))
    for y in range(36, H - 2, 5): c.line(10, y, W - 10, y, (110, 0, 20))
    c.rect(4, 22, W - 4, 34, BROWN, dither=ORANGE); c.rect(24, 8, W - 24, 22, BROWN, dither=ORANGE)
    c.rect(36, 0, 46, 22, DGREY); c.rect(150, 0, 160, 22, DGREY)
    for x in (41, 155):
        for k in range(3): c.ell(x + (k + t) % 3 - 1, -k * 4 + 10 - t * 2 + 8, 3, 3, GREY if k else WHITE, dither=DGREY)
    for r in range(2):
        for k in range(6):
            x, y = 22 + k * 28, 44 + r * 28
            win(c, x, y, 12, 15, rng.random() < 0.6, [YELLOW, PINK, CYAN][(k + r) % 3], t, eye=(r == 0 and k == 3))
    c.rect(86, 70, 112, H - 1, BROWN); c.rect(90, 74, 108, H - 1, (60, 30, 10)); c.px(106, 90, YELLOW)
    c.rect(80, 64, 118, 68, DGREY)
    for x in range(14, W - 14, 12): c.pts([(x, 31 + (x // 12) % 3)], GREEN)
    c.line(30, 34, 30, 40 + t * 2, GREEN, 2)
    c.pts([(12, 14 + t), (W - 14, 24)], YELLOW)
    return c, (CYAN, YELLOW)


def shack(t):
    W, H = 176, 92
    c = Canvas(W, H)
    c.rect(14, 30, W - 14, H - 1, BROWN, dither=(140, 90, 40))
    for x in range(16, W - 14, 6): c.line(x, 30, x, H - 1, (60, 30, 10))
    c.line(4, 32, 88, 4, DGREY, 4); c.line(88, 4, W - 4, 34, DGREY, 4); c.rect(8, 28, W - 8, 34, DGREY)
    for (x, y, w) in ((20, 14, 20), (140, 18, 24), (96, 10, 14)):
        c.rect(x, y, x + w, y + 3, RED if (x + t) % 2 else ORANGE)    # залатки на крыше
    c.rect(110, 0, 120, 20, DGREY); [c.ell(115 + (k + t) % 3 - 1, 14 - k * 4 - t, 3, 3, WHITE if k == 0 else GREY, dither=DGREY) for k in range(3)]
    c.rect(36, 52, 66, H - 1, BLACK if t % 3 else (60, 60, 0)); c.eye(46, 70, 3, [(1, 0), (0, 1), (-1, 0), (0, 0)][t]); c.eye(58, 70, 3, [(1, 0), (0, 1), (-1, 0), (0, 0)][t])
    win(c, 100, 50, 24, 20, True, CYAN, t); win(c, 134, 50, 20, 20, t != 2, YELLOW, t)
    c.line(20, H - 1, 12, 70, GREEN, 2); c.line(W - 20, H - 1, W - 12, 74, GREEN, 2)
    c.rect(78, 80, 96, H - 1, DGREY); c.ell(87, 76, 8, 4, GOLD)                                        # ржавая бочка у входа
    return c, (PINK, YELLOW)


def garages(t):
    W, H = 236, 78
    c = Canvas(W, H)
    c.rect(4, 12, W - 4, H - 1, GREY, dither=DGREY); c.rect(0, 6, W, 14, DGREY); c.rect(0, 6, W, 7, WHITE)
    for i in range(5):
        x = 10 + i * 45; op = [0, 6, 12, 6][t] if i == 2 else 0
        c.rect(x, 20, x + 38, H - 1, ORANGE, dither=BROWN)
        for y in range(24, H - 1, 4): c.line(x, y, x + 38, y, (150, 70, 0))
        if i == 2:
            c.rect(x, 20, x + 38, H - 1, BLACK); c.rect(x, 20, x + 38, 56 - op, ORANGE)
            for e in (14, 28): c.eye(x + e, 66, 3, [(1, 0), (0, 1), (-1, 0), (0, 0)][t])
        else:
            c.pts([(x + 6, 30), (x + 30, 50)], BLACK); c.rect(x + 17, 44, x + 21, 46, DGREY)
        c.rect(x + 8, 10, x + 30, 14, YELLOW if (i + t) % 3 else DGREY)
    c.pts([(20, 2), (180, 0 + t), (120, 3)], YELLOW)
    c.line(W - 14, 10, W - 6, 0, DGREY, 2)
    return c, (CYAN, YELLOW)


def tower(t):
    W, H = 150, 138
    c = Canvas(W, H); rng = random.Random(5)
    c.rect(24, 16, W - 24, H - 1, DGREY, dither=BLACK); c.rect(18, 8, W - 18, 16, GREY); c.rect(30, 0, W - 30, 8, DGREY)
    for r in range(6):
        for k in range(4):
            x, y = 32 + k * 22, 28 + r * 16
            win(c, x, y, 10, 9, rng.random() < 0.5 and (t + r) % 4 != 0, [RED, PINK][(r + k) % 2], t)
    c.ell(75, 22, 14, 10, WHITE); c.eye(75, 22, 9, [(0, 0), (2, 0), (0, 2), (-2, 0)][t])             # гигантский глаз-окно
    c.rect(60, 112, 90, H - 1, BLACK); c.rect(60, 110, 90, 112, RED)
    c.line(75, 0, 75, -0, GREY); c.ell(122, 12, 14, 8, GREY, dither=WHITE); c.line(122, 12, 132, 2, DGREY)
    c.line(8, 40 + t, 24, 60, YELLOW); c.line(W - 8, 60, W - 24, 90 - t, CYAN)
    c.pts([(12, 20), (W - 14, 40), (30, 100)], PINK)
    return c, (GREEN, PINK)


HOUSES = [panel, brick, shack, garages, tower]

if __name__ == "__main__":
    for i, fn in enumerate(HOUSES):
        frames = []
        for t in range(FR):
            c, (shade, hi) = fn(t)
            frames.append(c.finish(shade, hi, glitch=(8 if t == 3 else 0), rng=random.Random(i * 10 + t), lim=0.22))
        w = max(f.shape[1] for f in frames); h = max(f.shape[0] for f in frames)
        out = Image.new("RGBA", (w * FR, h), (0, 0, 0, 0))
        for t, f in enumerate(frames):
            im = Image.fromarray(f, "RGBA"); out.paste(im, (t * w + (w - im.width) // 2, h - im.height), im)
        out.save(f"assets/sprites/border_house_{i}.png"); print(i, w, h)
    prev = Image.new("RGBA", (1000, 620), (60, 44, 34, 255)); y = 4
    for i in range(len(HOUSES)):
        im = Image.open(f"assets/sprites/border_house_{i}.png"); w = im.width // FR
        fr = im.crop((w, 0, 2 * w, im.height)); prev.paste(fr, (4 + (i % 3) * 330, 4 + (i // 3) * 300), fr)
    prev.save("tools/_preview/houses_big.png")
