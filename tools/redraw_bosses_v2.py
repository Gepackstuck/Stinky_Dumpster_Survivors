#!/usr/bin/env python3
"""Огромные боссы. python3 tools/redraw_bosses.py [--apply]"""
import sys, math, random
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
GOLD = (255, 200, 0)


def hamster(t):
    c = Canvas(104, 84); b = [0, 1, 0, 1][t]; w = [0, 1, 2, 1][t]
    c.ell(14, 14 + b, 11, 11, BROWN); c.ell(14, 14 + b, 7, 7, PINK, dither=(255, 120, 245))      # уши
    c.ell(88, 14 + b, 11, 11, BROWN); c.ell(88, 14 + b, 7, 7, PINK, dither=(255, 120, 245))
    c.rect(26, 70, 40, 82, BROWN); c.rect(62, 70, 76, 82, BROWN)                                      # лапы
    for x in (27, 31, 35): c.line(x, 78, x, 83, BLACK, 1)
    for x in (63, 67, 71): c.line(x, 78, x, 83, BLACK, 1)
    c.ell(52, 48 + b, 40, 28, BROWN, dither=(150, 90, 40))                                           # туша
    c.ell(52, 54 + b, 26, 20, YELLOW, dither=(255, 230, 150))                                        # пузо
    c.ell(52, 30 + b, 38, 24, BROWN, dither=(150, 90, 40))                                           # голова
    c.ell(18, 38 + b, 15, 12, BROWN, dither=ORANGE); c.ell(86, 38 + b, 15, 12, BROWN, dither=ORANGE)  # щёки-запасы
    for (x, y) in ((12, 44), (20, 46), (84, 46), (92, 44), (16, 50), (88, 50)):                       # семечки вываливаются
        c.ell(x, y + b, 3, 2, BLACK); c.px(x, y + b, WHITE)
    c.line(30, 20, 44, 28, BLACK, 3); c.line(74, 20, 60, 28, BLACK, 3)                                # злые брови
    c.eye(36, 31 + b, 8, (2, 2)); c.eye(68, 29 + b, 9, (-2, 2))                                       # разные глаза
    c.ell(36, 31 + b, 8, 8, WHITE) if False else None
    c.ell(52, 40 + b, 5, 3, PINK); c.px(51, 39 + b, WHITE)                                           # нос
    m = 4 + 3 * w
    c.rect(36, 46 + b, 68, 46 + b + m, BLACK)
    c.rect(44, 46 + b, 50, 56 + b + m // 2, WHITE); c.rect(54, 46 + b, 60, 56 + b + m // 2, WHITE); c.line(52, 46 + b, 52, 56 + b + m // 2, BLACK)  # резцы
    for x in range(37, 68, 3):
        if not 44 <= x <= 60: c.px(x, 46 + b + m, WHITE)
    c.ell(52, 54 + b + m, 8, 3, PINK)
    c.line(66, 52 + b, 66, 62 + b + w * 2, GREEN, 2); c.line(40, 54 + b, 40, 60 + b, GREEN)
    c.rect(22, 64 + b, 82, 67 + b, GREEN)                                                              # ошейник
    for x in range(24, 82, 6): c.line(x, 64 + b, x, 61 + b, GOLD, 1); c.px(x, 60 + b, WHITE)          # шипы
    c.ell(52, 72 + b, 5, 5, GOLD); c.px(51, 71 + b, WHITE); c.px(53, 73 + b, RED)                     # медальон
    c.line(30, 20, 26, 26, BLACK); c.line(28, 18, 24, 24, BLACK)                                      # шрамы
    c.pts([(10, 6), (90, 6), (96, 24), (6, 28), (50, 4)], YELLOW)                                      # мухи
    c.line(52, 6, 49, 0 + w * 2, BLACK); c.line(55, 6, 58, 1, BLACK)                                  # вихор
    return c.finish(PURPLE, YELLOW, lim=0.1)


def zakhar(t):
    c = Canvas(104, 124); b = [0, 1, 0, 1][t]; w = [0, 1, 2, 1][t]
    # уши
    c.ell(34, 24 + b, 11, 24, WHITE, dither=(200, 200, 210)); c.ell(34, 26 + b, 6, 19, PINK, dither=(255, 120, 245))
    c.ell(70, 22 + b, 11, 22, WHITE, dither=(200, 200, 210)); c.ell(70, 24 + b, 6, 17, PINK)
    c.line(62, 14 + b, 58, 6 + b, BLACK, 2); c.rect(64, 20 + b, 77, 24 + b, BLACK, dither=RED)       # рваное ухо
    # туша
    c.rect(24, 108, 40, 122, WHITE); c.rect(60, 108, 76, 122, WHITE)
    for x in (26, 31, 36): c.line(x, 118, x, 123, BLACK)
    for x in (62, 67, 72): c.line(x, 118, x, 123, BLACK)
    c.ell(50, 84 + b, 32, 30, WHITE, dither=(200, 200, 210))
    c.ell(50, 90 + b, 20, 20, PINK, dither=(255, 120, 245)); c.ell(50, 90 + b, 9, 9, YELLOW, dither=ORANGE)   # пузо с кругом
    c.pts([(46, 88 + b), (50, 85 + b), (54, 88 + b), (50, 93 + b)], BLACK)
    c.ell(50, 48 + b, 28, 24, WHITE, dither=(200, 200, 210))                                          # голова
    c.line(26, 30, 40, 38, BLACK, 3); c.line(74, 30, 60, 38, BLACK, 3)
    c.eye(38, 44 + b, 7, (2, 2)); c.eye(62, 42 + b, 8, (-2, 2))
    c.ell(62, 42 + b, 9, 9, RED, dither=BLACK) if False else None
    c.ell(50, 54 + b, 4, 3, PINK)
    m = 4 + 2 * w
    c.rect(38, 60 + b, 62, 60 + b + m, BLACK)
    c.rect(41, 60 + b, 45, 66 + b + m // 2, WHITE); c.rect(55, 60 + b, 59, 66 + b + m // 2, WHITE)
    c.px(43, 62 + b, GOLD); c.px(43, 63 + b, GOLD)                                                      # золотой зуб
    for x in (47, 50, 53): c.px(x, 60 + b, WHITE)
    c.line(48, 60 + b + m, 48, 68 + b + m + w * 2, GREEN, 2)
    # руки
    c.ell(18, 80 + b, 7, 12, WHITE, dither=(200, 200, 210))
    arm = -w * 5
    c.ell(84, 80 + b + arm // 2, 7, 12, WHITE, dither=(200, 200, 210))
    # морковь-дубина
    cx, cy = 90, 66 + arm
    c.line(cx, cy + 40, cx - 2, cy - 22, ORANGE, 14)
    for yy in range(-18, 40, 8): c.line(cx - 6, cy + yy, cx + 6, cy + yy + 2, RED, 1)
    c.line(cx - 4, cy - 22, cx - 12, cy - 38 - w * 2, GREEN, 3); c.line(cx, cy - 22, cx + 2, cy - 42, GREEN, 3); c.line(cx + 3, cy - 22, cx + 14, cy - 36, GREEN, 3)
    c.ell(cx - 1, cy + 38, 4, 5, ORANGE)
    c.ell(84, 80 + b + arm // 2, 6, 6, WHITE)
    c.line(20, 40, 16, 34, BLACK); c.pts([(8, 10), (96, 12), (12, 70), (92, 100), (30, 6)], YELLOW)
    c.pts([(22, 96), (80, 108)], GREEN); c.rect(34, 100, 66, 100, BLACK, dither=GREEN)
    return c.finish(CYAN, YELLOW, lim=0.12)


def minion(t):
    c = Canvas(84, 96); b = [0, 1, 0, 1][t]; w = [0, 1, 2, 1][t]
    for i in range(7):                                         # готический ёж на голове
        x = 14 + i * 9; h = 14 + (i % 3) * 5
        c.line(x, 20 + b, x + (i - 3) * 2, 20 - h + b, BLACK, 3)
    c.rect(18, 86, 34, 94, BLACK); c.rect(50, 86, 66, 94, BLACK); c.rect(18, 92, 34, 94, YELLOW); c.rect(50, 92, 66, 94, YELLOW)
    c.rect(20, 60, 64, 88, BLUE, dither=(80, 80, 255))                                                  # комбез
    c.rect(18, 22, 66, 62, YELLOW, dither=ORANGE)                                                       # капсула тела
    c.ell(42, 22 + b, 24, 18, YELLOW, dither=ORANGE); c.rect(18, 22, 66, 58, YELLOW)
    c.rect(18, 34, 66, 38, BLACK)                                                                       # ремешок
    c.ell(28, 36 + b, 12, 12, WHITE); c.ell(56, 36 + b, 10, 10, WHITE)                                  # очки
    c.ell(28, 36 + b, 12, 12, GREY, dither=WHITE) if False else None
    c.eye(28, 36 + b, 9, (3, 2)); c.eye(56, 36 + b, 8, (-3, 3))
    c.line(16, 24, 38, 30, BLACK, 3); c.line(68, 24, 48, 31, BLACK, 3)
    m = 3 + 2 * w
    c.rect(26, 50 + b, 58, 50 + b + m, BLACK)
    for x in range(27, 58, 4): c.rect(x, 50 + b, x + 1, 52 + b, WHITE); c.rect(x + 2, 50 + b + m - 2, x + 3, 50 + b + m, WHITE)
    c.rect(34, 52 + b + m, 52, 54 + b + m, PINK)
    c.rect(28, 66, 56, 78, BLUE); c.rect(30, 68, 36, 74, CYAN); c.pts([(32, 70), (34, 72)], BLACK)       # карман
    c.rect(14, 60, 18, 78, BLUE); c.rect(66, 60, 70, 78, BLUE)
    # булава
    ar = -w * 6
    c.ell(8, 66 + b, 6, 7, YELLOW)
    c.line(8, 70, 8, 4 + ar // 2 + 4, DGREY, 4); c.ell(8, 8 + ar // 2, 11, 11, GREY, dither=WHITE)
    for k in range(8):
        ang = k * math.pi / 4
        c.line(8 + math.cos(ang) * 9, 8 + ar // 2 + math.sin(ang) * 9, 8 + math.cos(ang) * 16, 8 + ar // 2 + math.sin(ang) * 16, RED, 2)
    c.ell(76, 68 + b, 6, 7, YELLOW)
    c.pts([(60, 4), (74, 10), (80, 40), (4, 90)], PINK)
    c.pts([(30, 2), (50, 4)], CYAN)
    return c.finish(PURPLE, WHITE, lim=0.1)


BOSSES = {"boss_mega_hamster": hamster, "boss_zakhar": zakhar, "boss_minion": minion}

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    k = 3; x = 6
    imgs = []
    for n, fn in BOSSES.items():
        im = sheet([fn(i) for i in range(4)]); imgs.append(im)
        im.save(f"tools/_preview/enemies_v2/enemy_{n}.png")
        if apply: im.save(f"assets/sprites/enemy_{n}.png")
    W = sum(i.width * k // 2 + 12 for i in imgs) + 6; H = max(i.height for i in imgs) * k + 12
    prev = Image.new("RGBA", (W, H), (45, 30, 20, 255))
    for im in imgs:
        fr = im.crop((0, 0, im.width // 4, im.height)).resize((im.width // 4 * k, im.height * k), Image.NEAREST)
        prev.paste(fr, (x, 6), fr); x += fr.width + 12
    prev.save("tools/_preview/bosses_v2.png")
