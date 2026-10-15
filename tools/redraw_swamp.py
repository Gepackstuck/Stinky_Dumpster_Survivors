#!/usr/bin/env python3
"""Огромные болотные объекты (4 кадра в ряд): assets/sprites/border_swamp_N.png"""
import sys, random, math
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
FR = 4


def ripple(c, cx, cy, rx, ry, t, col=WHITE, n=4):
    for k in range(n):
        r = (t + k * 1.3) % 4
        c.ell(cx + math.cos(k * 2.1) * rx * 0.5, cy + math.sin(k * 1.7) * ry * 0.4, 1 + r, max(1, (1 + r) // 2), col) if False else None


def lake(t):
    W, H = 236, 64
    c = Canvas(W, H); rng = random.Random(1)
    c.ell(W // 2, 40, 112, 22, GREEN, dither=DGREEN); c.ell(W // 2, 38, 96, 17, YELLOW, dither=GREEN); c.ell(W // 2, 36, 70, 11, GREEN, dither=YELLOW)
    for k in range(9):
        bx = 30 + k * 22; by = 38 + math.sin(k * 1.7) * 8
        c.ell(bx, by - (t * 2 + k * 3) % 8, 2 + k % 2, 2 + k % 2, WHITE); c.px(bx - 1, by - 1 - (t * 2 + k * 3) % 8, GREEN)
    c.line(40, 42, 76, 44, WHITE, 2)                                                       # скелет гигантской рыбы
    for x in range(44, 74, 4): c.line(x, 38, x + 1, 46, WHITE)
    c.ell(80, 43, 6, 5, WHITE); c.eye(80, 43, 2, (0, 0))
    c.rect(150, 32, 156, 38 - t % 2, RED); c.rect(170, 34 - t % 2, 178, 41, CYAN)          # плавающие бутылки
    c.ell(120, 30, 14, 6, BLACK); c.pts([(116, 29), (124, 29)], RED)                       # что-то смотрит из воды
    for x in (20, 214): c.line(x, 38, x + 3, 10, DGREEN, 2); c.rect(x + 1, 6, x + 5, 12, BROWN)
    c.pts([(60, 6 + t), (190, 10), (110, 4)], YELLOW)
    return c, (CYAN, WHITE)


def forest(t):
    W, H = 200, 112
    c = Canvas(W, H); rng = random.Random(2)
    c.ell(100, 98, 96, 12, DGREEN, dither=BROWN)
    for (x, h, th) in ((30, 80, 6), (62, 98, 8), (100, 70, 5), (140, 104, 8), (172, 76, 6)):
        c.line(x, 98, x + (x % 3 - 1) * 3, 98 - h, BROWN, th)
        for b in range(4):                                              # кривые ветки
            by = 98 - h + b * 14; dx = (-1) ** b * (10 + b * 3)
            c.line(x, by + 10, x + dx, by - 4, BROWN, 3); c.line(x + dx, by - 4, x + dx + (-1) ** b * 6, by - 12 + t % 2, BROWN, 2)
        for m in range(3):                                              # свисающий мох
            mx = x + (m - 1) * 8; c.line(mx, 98 - h + 12, mx, 98 - h + 24 + (t + m) % 3 * 2, GREEN, 2)
        c.eye(x, 98 - h * 0.45, 4, [(0, 0), (1, 0), (0, 1), (-1, 0)][(t + x // 31) % 4])                # глаз в стволе
    for k in range(10): c.px(8 + (k * 19 + t * 5) % 184, 20 + (k * 11) % 60, YELLOW)                      # светлячки
    c.ell(100, 104, 40, 5, GREEN, dither=YELLOW)
    return c, (PURPLE, YELLOW)


def monster(t):
    W, H = 188, 96
    c = Canvas(W, H)
    c.ell(94, 88, 90, 10, GREEN, dither=DGREEN)
    b = [0, 2, 4, 2][t]
    c.ell(94, 54 - b, 62, 44, GREEN, dither=(20, 160, 20)); c.ell(94, 60 - b, 44, 26, YELLOW, dither=GREEN)
    c.eye(60, 36 - b, 14, [(2, 3), (3, 3), (2, 4), (1, 3)][t]); c.eye(128, 34 - b, 16, [(-2, 3), (-3, 3), (-2, 4), (-1, 3)][t])
    c.line(40, 16 - b, 78, 26 - b, BLACK, 4); c.line(150, 14 - b, 112, 26 - b, BLACK, 4)
    m = 10 + 6 * (t % 2)
    c.rect(54, 62 - b, 134, 62 - b + m, BLACK)
    for x in range(56, 134, 8): c.rect(x, 62 - b, x + 3, 70 - b, WHITE); c.rect(x + 4, 62 - b + m - 7, x + 7, 62 - b + m, WHITE)
    c.ell(94, 62 - b + m, 18, 6, PINK)
    c.line(70, 62 - b + m, 70, 82 + t * 2, GREEN, 3); c.line(122, 62 - b + m, 122, 78 + (t % 2) * 4, GREEN, 3)
    for sx in (24, 164):
        for j in range(18): c.ell(sx + math.sin(j * 0.5 + t * 1.6) * 6, 80 - j * 3, 4 - j * 0.15, 3, PINK)    # щупальца
    c.pts([(10, 10), (176, 14), (94, 4)], YELLOW)
    return c, (PINK, WHITE)


def wreck(t):
    W, H = 224, 84
    c = Canvas(W, H)
    c.ell(112, 74, 108, 10, GREEN, dither=DGREEN)
    c.rect(18, 40, 206, 74, DGREY, dither=(40, 40, 50)); c.rect(14, 32, 210, 40, RED, dither=(150, 0, 30))
    for k in range(14): c.rect(24 + k * 13, 48, 31 + k * 13, 60, CYAN if (k + t) % 5 else BLACK, dither=WHITE if (k + t) % 5 else None)
    c.rect(40, 14, 120, 32, DGREY); c.rect(50, 18, 110, 28, CYAN, dither=WHITE)
    c.line(150, 32, 150, 2, DGREY, 3); c.line(150, 4, 176, 12, DGREY, 2); c.line(176, 12, 176, 22 + t * 2, GREY); c.ell(176, 24 + t * 2, 3, 3, GREY)
    c.ell(112, 74, 70, 6, GREEN, dither=YELLOW)                                       # ватерлиния слизи
    for k in range(5): c.ell(30 + k * 40, 70 - (t + k) % 3 * 2, 3, 3, WHITE)
    c.eye(85, 22, 3, [(0, 0), (1, 0), (0, 1), (-1, 0)][t]); c.pts([(30, 6), (200, 10)], PINK)
    return c, (PURPLE, YELLOW)


def reeds(t):
    W, H = 168, 80
    c = Canvas(W, H)
    c.ell(84, 70, 80, 9, DGREEN, dither=GREEN)
    for x in range(8, 160, 4):
        h = 30 + (x * 13) % 40; sw = [0, 1, 2, 1][(t + x // 4) % 4] - 1
        c.line(x, 72, x + sw * 2, 72 - h, GREEN, 2); c.rect(x + sw * 2 - 1, 68 - h, x + sw * 2 + 1, 74 - h, BROWN)
        if x % 16 == 0: c.px(x + sw * 2, 66 - h, YELLOW)
    c.ell(84, 72, 14, 5, YELLOW, dither=GREEN); c.eye(84, 71, 3, [(0, 0), (1, 0), (0, 1), (-1, 0)][t])
    return c, (PURPLE, YELLOW)


SWAMP = [lake, forest, monster, wreck, reeds]

if __name__ == "__main__":
    for i, fn in enumerate(SWAMP):
        frames = []
        for t in range(FR):
            c, (shade, hi) = fn(t)
            frames.append(c.finish(shade, hi, glitch=(8 if t == 3 else 0), rng=random.Random(i * 10 + t), lim=0.22))
        w = max(f.shape[1] for f in frames); h = max(f.shape[0] for f in frames)
        out = Image.new("RGBA", (w * FR, h), (0, 0, 0, 0))
        for t, f in enumerate(frames):
            im = Image.fromarray(f, "RGBA"); out.paste(im, (t * w + (w - im.width) // 2, h - im.height), im)
        out.save(f"assets/sprites/border_swamp_{i}.png"); print(i, w, h)
    prev = Image.new("RGBA", (1000, 620), (22, 48, 40, 255))
    for i in range(len(SWAMP)):
        im = Image.open(f"assets/sprites/border_swamp_{i}.png"); w = im.width // FR
        fr = im.crop((w, 0, 2 * w, im.height)); prev.paste(fr, (4 + (i % 3) * 330, 4 + (i // 3) * 140), fr)
    prev.save("tools/_preview/swamp_big.png")
