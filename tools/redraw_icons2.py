#!/usr/bin/env python3
"""Иконки 32×32: статы, перки, предметы. python3 tools/redraw_icons2.py [--apply] [имя ...]"""
import sys
sys.path.insert(0, "tools")
from icon_kit import *
I = {}
def ic(sh=PURPLE, hi=WHITE, lim=0.35, tall=False):
    def d(f): I[f.__name__] = (f, sh, hi, lim, tall); return f
    return d

# ============ СТАТЫ ============
@ic(DRED, PINK, 0.5)
def stat_max_hp(c):
    c.ell(8.5, 9, 6.5, 6, RED); c.ell(19.5, 9, 6.5, 6, RED)
    poly(c, [(2, 11), (26, 11), (14, 26)], RED); c.rect(3, 9, 25, 12, RED)
    c.rect(12, 7, 15, 20, WHITE); c.rect(8, 11, 19, 15, WHITE)                       # белый крест
    c.rect(5, 5, 8, 6, PINK); c.rect(4, 7, 5, 9, PINK); c.px(6, 4, WHITE)           # блик
    c.pts([(22, 14), (21, 17), (19, 20)], DRED)
@ic(GREEN, WHITE, 0.5)
def stat_regen(c):   # пластырь
    poly(c, [(2, 21), (6, 25), (25, 6), (21, 2)], (235, 195, 150), dither=(250, 220, 185))
    poly(c, [(8, 17), (11, 20), (20, 11), (17, 8)], WHITE); poly(c, [(11, 15), (13, 17), (17, 13), (15, 11)], (225, 120, 120))
    for p in [(5, 19), (7, 21), (20, 6), (22, 8), (4, 22), (23, 5)]: c.px(*p, (200, 150, 110))
    c.line(2, 21, 21, 2, (200, 150, 110)); c.line(6, 25, 25, 6, (200, 150, 110))
    c.rect(22, 15, 23, 25, GREEN); c.rect(18, 19, 27, 20, GREEN); c.rect(3, 1, 3, 7, GREEN); c.rect(0, 4, 6, 4, GREEN)   # плюсики
@ic(DRED, ORANGE, 0.5)
def stat_damage(c):   # злая рожа с рогами
    poly(c, [(2, 2), (8, 7), (6, 10)], WHITE); poly(c, [(26, 2), (20, 7), (22, 10)], WHITE)
    c.ell(14, 15, 11, 10, RED); c.rect(4, 11, 24, 22, RED)
    poly(c, [(5, 10), (12, 15), (12, 18), (5, 14)], BLACK); poly(c, [(23, 10), (16, 15), (16, 18), (23, 14)], BLACK)    # брови
    c.rect(7, 15, 11, 18, YELLOW); c.rect(17, 15, 21, 18, YELLOW); c.rect(9, 16, 10, 18, BLACK); c.rect(18, 16, 19, 18, BLACK)
    c.rect(7, 21, 20, 25, BLACK)
    for x in range(8, 20, 3): poly(c, [(x, 21), (x + 2, 21), (x + 1, 24)], WHITE)
    c.pts([(5, 19), (23, 19)], DRED); c.px(10, 12, PINK)
@ic(ORANGE, YELLOW, 0.5)
def stat_attack_speed(c):   # очередь пуль
    for i, y in enumerate((3, 11, 19)):
        x0 = 9 + (i % 2) * 3
        c.rect(x0, y, x0 + 9, y + 5, (255, 200, 60)); c.rect(x0, y, x0 + 9, y + 1, YELLOW); c.rect(x0 + 10, y + 1, x0 + 11, y + 4, ORANGE); poly(c, [(x0 + 12, y + 1), (x0 + 16, y + 3), (x0 + 12, y + 5)], RED)
        c.rect(x0, y + 3, x0 + 1, y + 5, DBROWN); c.px(x0 + 2, y, WHITE)
        c.rect(0, y + 1, x0 - 3, y + 1, WHITE); c.rect(2, y + 4, x0 - 2, y + 4, CYAN)
@ic(CYAN, WHITE, 0.5)
def stat_speed(c):   # кроссовок с крылом
    poly(c, [(7, 5), (16, 5), (16, 14), (26, 17), (26, 23), (5, 23), (5, 12)], WHITE, dither=LG)
    c.rect(5, 21, 26, 24, BLACK); c.rect(5, 19, 26, 20, RED); poly(c, [(9, 7), (14, 7), (14, 12), (9, 12)], GREY)
    c.line(16, 15, 26, 18, GREY); c.pts([(18, 17), (20, 18), (22, 19)], DGREY)
    poly(c, [(5, 12), (0, 6), (2, 14), (-1, 12), (3, 19), (5, 17)], CYAN); c.line(0, 6, 5, 12, WHITE)
    c.rect(0, 22, 3, 22, CYAN); c.rect(0, 25, 5, 25, CYAN); c.rect(21, 3, 27, 3, CYAN); c.rect(24, 7, 27, 7, CYAN)
@ic(MG, WHITE, 0.5)
def stat_armor(c):   # клёпаный стальной щит
    poly(c, [(3, 2), (25, 2), (25, 14), (14, 26), (3, 14)], MG, dither=LG)
    poly(c, [(6, 5), (22, 5), (22, 13), (14, 22), (6, 13)], (110, 115, 130)); poly(c, [(8, 7), (20, 7), (20, 12), (14, 19), (8, 12)], STEEL)
    c.rect(13, 7, 14, 19, DGREY); c.rect(8, 11, 20, 12, DGREY); c.ell(14, 11.5, 3, 3, YELLOW); c.px(13, 10, WHITE)
    for p in [(4, 3), (23, 3), (4, 12), (23, 12), (14, 24)]: c.rect(p[0], p[1], p[0] + 1, p[1] + 1, WHITE)
    c.rect(3, 2, 25, 3, WHITE); c.pts([(9, 8), (10, 9)], WHITE)
@ic(CYAN, WHITE, 0.5)
def stat_dodge(c):   # бегущий человечек с остаточными образами
    def man(ox, col, bold):
        t = 3 if bold else 2
        c.ell(15 + ox, 5, 3.2, 3.2, col)
        c.line(14 + ox, 9, 12 + ox, 17, col, t)                    # торс
        c.line(13 + ox, 10, 19 + ox, 13, col, t); c.line(13 + ox, 10, 8 + ox, 14, col, t)   # руки
        c.line(12 + ox, 17, 18 + ox, 21, col, t); c.line(18 + ox, 21, 17 + ox, 26, col, t)  # нога вперёд
        c.line(12 + ox, 17, 8 + ox, 22, col, t); c.line(8 + ox, 22, 4 + ox, 21, col, t)    # нога назад
    man(-8, (70, 100, 135), False); man(-4, (130, 165, 200), False); man(3, WHITE, True)
    c.rect(0, 5, 5, 5, CYAN); c.rect(0, 12, 3, 12, CYAN); c.rect(1, 25, 6, 25, CYAN)
@ic(ORANGE, YELLOW, 0.5)
def stat_pickup(c):   # цепкая рука + монета
    c.rect(7, 13, 19, 25, SKINC); c.rect(7, 25, 19, 26, DGREY)
    for x, y0 in ((7, 5), (11, 3), (15, 4), (19, 7)): c.rect(x, y0, x + 2, 14, SKINC); c.rect(x, y0, x + 2, y0, WHITE)
    poly(c, [(7, 17), (2, 13), (1, 16), (7, 22)], SKINC)
    for x in (9, 13, 17): c.px(x, 6 if x != 17 else 9, (200, 140, 100))
    c.pts([(10, 18), (12, 20), (15, 19), (17, 21)], (200, 140, 100))
    c.ell(23, 21, 3.5, 3.5, YELLOW); c.ell(23, 21, 1.5, 1.5, ORANGE); c.px(21, 19, WHITE); c.rect(22, 11, 23, 14, YELLOW); c.px(23, 8, YELLOW)
@ic(RED, YELLOW, 0.5)
def stat_crit(c):   # нож + вспышка + x2
    pts = []
    for i in range(20):
        r = 13.5 if i % 2 == 0 else 7; a = i * math.pi / 10
        pts.append((14 + math.cos(a) * r, 14 + math.sin(a) * r))
    poly(c, pts, RED, dither=ORANGE); c.ell(14, 14, 6, 6, YELLOW)
    poly(c, [(3, 3), (13, 11), (11, 15), (3, 5)], LG); c.line(3, 3, 12, 12, WHITE); poly(c, [(11, 11), (15, 11), (15, 15), (11, 15)], DGREY)
    poly(c, [(13, 14), (16, 12), (24, 24), (22, 26)], DBROWN); c.px(14, 13, WHITE)
    tri_font(c, 17, 3, "x2", WHITE)

# ============ ПЕРКИ ============
@ic(ORANGE, YELLOW, 0.5)
def perk_double_shot(c):   # две пули x2
    for y in (4, 16):
        c.rect(0, y, 5, y + 6, DGREY); c.rect(5, y, 17, y + 6, ORANGE); c.rect(5, y, 17, y + 1, YELLOW); poly(c, [(18, y), (24, y + 3), (18, y + 6)], RED); c.rect(0, y + 5, 3, y + 6, BLACK); c.px(7, y + 2, WHITE)
    tri_font(c, 20, 21, "x2", CYAN)
@ic(GREEN, WHITE, 0.5)
def perk_loot_goblin(c):
    poly(c, [(2, 9), (8, 12), (7, 15), (0, 14)], GREEN); poly(c, [(26, 9), (20, 12), (21, 15), (28, 14)], GREEN)
    c.ell(14, 15, 9, 9, GREEN, dither=(20, 180, 20)); c.rect(7, 13, 11, 16, YELLOW); c.rect(17, 13, 21, 16, YELLOW); c.rect(9, 13, 10, 16, BLACK); c.rect(19, 13, 20, 16, BLACK)
    c.rect(8, 21, 20, 23, BLACK); c.pts([(9, 21), (12, 21), (16, 21), (19, 21)], WHITE); poly(c, [(11, 17), (17, 17), (14, 20)], (20, 150, 20))
    c.ell(24, 24, 3, 3, YELLOW); c.px(23, 23, WHITE); c.px(24, 25, ORANGE)
@ic(GREEN, WHITE, 0.5)
def perk_regen(c): stat_regen(c)
@ic(CYAN, WHITE, 0.5)
def perk_speed(c): stat_speed(c)

# ============ ПРЕДМЕТЫ (А–Г) ============
@ic(PURPLE, WHITE)
def bandage(c):   # рулон грязного бинта
    c.ell(14, 14, 11, 11, (225, 215, 195), dither=(190, 180, 160)); c.ell(14, 14, 4, 4, BLACK)
    ringc(c, 14, 14, 7, (160, 150, 130), 1); ringc(c, 14, 14, 10, (160, 150, 130), 1)
    poly(c, [(20, 22), (27, 22), (27, 26), (18, 26)], (225, 215, 195)); c.rect(22, 23, 25, 24, (160, 150, 130))
    c.ell(9, 9, 2.5, 2, RED); c.pts([(10, 11), (10, 13), (17, 6), (18, 7)], RED); c.pts([(7, 5), (8, 4)], WHITE)
@ic(GREY, WHITE)
def barbed_wire(c):   # моток колючей проволоки
    for r, col in ((10, MG), (7, LG)): ringc(c, 14, 14, r, col, 2)
    for a in range(0, 360, 45):
        x = 14 + math.cos(math.radians(a)) * 10; y = 14 + math.sin(math.radians(a)) * 10
        for dx, dy in ((-2, -2), (2, -2), (-2, 2), (2, 2)): c.line(round(x), round(y), round(x) + dx, round(y) + dy, WHITE)
    ringc(c, 14, 14, 3.5, DGREY, 1); c.pts([(4, 14), (24, 14)], RED)
@ic(GREEN, WHITE)
def battery(c):   # батарейка из пульта
    c.rect(5, 6, 22, 24, DGREY); c.rect(5, 6, 22, 11, GREEN); c.rect(5, 6, 22, 7, LGREEN); c.rect(10, 2, 17, 5, MG); c.rect(11, 3, 12, 4, WHITE)
    c.rect(5, 12, 22, 24, (40, 40, 50), dither=DGREY); poly(c, [(15, 13), (10, 20), (14, 20), (12, 24), (19, 17), (15, 17), (17, 13)], YELLOW)
    c.pts([(7, 14), (7, 16), (7, 18)], WHITE); c.rect(8, 8, 19, 8, (20, 120, 20))
@ic(PURPLE, WHITE)
def binoculars(c):   # бинокль из труб
    for ox in (2, 15):
        c.rect(ox, 6, ox + 9, 22, DGREY, dither=MG); c.ell(ox + 4.5, 22, 5.5, 3.5, BLACK); c.ell(ox + 4.5, 22, 3.5, 2.2, CYAN); c.px(ox + 3, 21, WHITE)
        c.rect(ox, 3, ox + 9, 6, MG); c.rect(ox + 1, 4, ox + 3, 4, WHITE)
    c.rect(11, 9, 16, 17, DGREY); c.rect(12, 10, 15, 16, MG); c.pts([(5, 10), (5, 14), (19, 12)], (150, 70, 30)); c.rect(10, 20, 17, 20, BLACK)
@ic(RED, PINK)
def bloody_rag(c):   # окровавленная тряпка
    poly(c, [(2, 5), (10, 3), (19, 5), (26, 3), (25, 12), (27, 20), (21, 25), (13, 23), (5, 26), (3, 17), (4, 11)], (210, 200, 185), dither=(175, 165, 150))
    c.line(3, 8, 10, 7, (150, 140, 125)); c.line(14, 16, 24, 17, (150, 140, 125)); c.ell(13, 13, 5, 5, RED); c.ell(12, 12, 2, 2, PINK)
    c.pts([(13, 18), (13, 20), (13, 22), (20, 8), (21, 10), (7, 20), (6, 22)], RED); c.pts([(10, 3), (17, 5)], (150, 140, 125))
@ic(PURPLE, WHITE)
def bomber_pigeon(c):   # голубь с бомбой
    c.ell(13, 11, 9, 6.5, STEEL, dither=LG); c.ell(21, 7, 4, 4, (200, 205, 220)); poly(c, [(24, 7), (28, 8), (24, 9)], ORANGE); c.px(22, 6, BLACK); c.px(23, 6, RED)
    poly(c, [(5, 9), (-1, 4), (1, 11), (5, 13)], MG); poly(c, [(8, 8), (4, 1), (11, 6)], DGREY); c.rect(16, 11, 21, 12, (150, 255, 100)); c.pts([(10, 8), (11, 9), (12, 8)], WHITE)
    c.ell(14, 21, 5, 5, BLACK); c.rect(13, 14, 14, 16, DGREY); c.px(14, 13, YELLOW); c.px(15, 12, ORANGE); c.px(12, 19, WHITE); c.pts([(11, 11), (14, 11), (11, 12)], ORANGE)
    c.px(10, 14, ORANGE); c.px(15, 14, ORANGE)
@ic(PURPLE, WHITE)
def bone_club(c):   # дубина из бедра
    poly(c, [(5, 22), (9, 26), (22, 12), (18, 8)], (245, 240, 220), dither=(215, 205, 175))
    c.ell(22, 6, 4.5, 4.5, (245, 240, 220)); c.ell(25, 9, 3.5, 3.5, (245, 240, 220)); c.ell(18, 4, 3, 3, (245, 240, 220)); c.ell(3, 25, 3.5, 3.5, (245, 240, 220)); c.ell(6, 27, 3, 2.5, (245, 240, 220))
    c.pts([(21, 6), (24, 8)], (180, 170, 140)); c.rect(12, 15, 15, 16, RED); c.pts([(8, 20), (17, 11)], (190, 180, 150)); c.px(2, 24, WHITE); c.px(21, 3, WHITE)
@ic(ORANGE, YELLOW)
def bottle_cap(c):   # крышка от пива
    pts = []
    for i in range(48):
        a = i * math.pi * 2 / 48; r = 13 if i % 2 == 0 else 11
        pts.append((14 + math.cos(a) * r, 14 + math.sin(a) * r))
    poly(c, pts, YELLOW, dither=ORANGE); c.ell(14, 14, 8.5, 8.5, RED); ringc(c, 14, 14, 7.3, YELLOW, 1)
    poly(c, [(11, 8), (17, 8), (17, 11), (19, 14), (19, 21), (9, 21), (9, 14), (11, 11)], (255, 235, 130)); c.rect(10, 15, 18, 18, WHITE); c.rect(12, 16, 16, 17, RED); c.pts([(11, 9), (11, 12)], WHITE); c.pts([(5, 6), (6, 5)], WHITE)
@ic(GREEN, YELLOW)
def bottle_mine(c):   # мина из крышек
    c.ell(14, 20, 13, 6, DGREY); c.rect(1, 18, 26, 22, DGREY); c.ell(14, 17, 11, 4, MG, dither=LG)
    for x in (4, 8, 12, 16, 20, 24): c.rect(x, 22, x + 1, 24, YELLOW)
    c.rect(11, 8, 17, 15, BLACK); c.rect(12, 5, 16, 8, BLACK); c.rect(12, 9, 16, 14, GREEN); c.rect(13, 3, 15, 4, GREY); c.px(14, 1, YELLOW); c.px(15, 0, ORANGE); c.px(13, 2, ORANGE)
    c.rect(13, 17, 15, 18, RED); c.pts([(5, 16), (22, 16)], WHITE); c.rect(12, 9, 12, 13, LGREEN)
@ic(PURPLE, YELLOW, 0.35, True)
def bucket_turret(c):   # ведро-турель
    poly(c, [(4, 12), (24, 12), (21, 34), (7, 34)], MG, dither=LG); c.rect(3, 10, 25, 13, GREY); c.rect(3, 10, 25, 10, WHITE)
    for y in (17, 22, 27): c.rect(6 + (y - 17) // 5, y, 21 - (y - 17) // 5, y, DGREY)
    c.rect(7, 13, 9, 33, WHITE); c.rect(10, 7, 18, 11, DGREY); c.rect(18, 8, 27, 10, BLACK); c.rect(26, 7, 27, 11, DGREY); c.px(27, 9, RED); c.rect(6, 1, 8, 6, MG); c.line(5, 10, 3, 4, GREY); c.line(23, 10, 25, 4, GREY)
    c.ell(14, 22, 3, 3, (160, 70, 30)); c.pts([(12, 21), (16, 23)], (210, 110, 40)); c.px(14, 2, RED)
@ic(PURPLE, YELLOW, 0.35, True)
def cart_mortar(c):   # тележка-миномёт
    poly(c, [(2, 18), (26, 18), (23, 30), (5, 30)], STEEL, dither=DGREY); c.rect(1, 17, 27, 18, MG)
    for x in (7, 11, 15, 19): c.rect(x, 19, x, 29, DGREY)
    c.rect(4, 22, 24, 22, DGREY); c.rect(4, 26, 23, 26, DGREY); c.ell(7, 34, 3.5, 3.5, BLACK); c.ell(21, 34, 3.5, 3.5, BLACK); c.px(6, 33, GREY); c.px(20, 33, GREY)
    c.line(26, 18, 27, 9, MG, 2); poly(c, [(8, 17), (18, 17), (16, 5), (10, 5)], DGREY); c.rect(8, 4, 18, 6, GREY); c.ell(13, 12, 3, 3, BLACK)
    c.px(13, 2, ORANGE); c.px(14, 1, YELLOW); c.px(12, 3, RED); c.rect(10, 8, 11, 15, MG)
@ic(PURPLE, YELLOW)
def cigarette(c):   # бычок
    poly(c, [(2, 21), (4, 17), (22, 7), (24, 11)], WHITE, dither=(235, 225, 200)); poly(c, [(2, 21), (4, 17), (8, 15), (6, 19)], ORANGE); c.pts([(8, 16), (9, 17)], BROWN)
    poly(c, [(20, 8), (24, 11), (26, 9), (22, 5)], RED); c.rect(24, 5, 25, 6, YELLOW); c.px(26, 4, WHITE)
    c.pts([(23, 3), (22, 1), (24, 0), (22, -1)], GREY) if False else c.pts([(22, 2), (23, 1), (22, 0), (24, 0)], GREY); c.pts([(10, 14), (13, 12), (16, 10)], (210, 200, 175)); c.pts([(5, 20), (3, 23)], GREY)
@ic(RED, YELLOW)
def coupon(c):   # талон бомжа
    c.rect(2, 4, 25, 23, YELLOW, dither=(230, 230, 0))
    for y in range(4, 24, 3): c.px(1, y, BLACK); c.px(26, y, BLACK)
    c.rect(4, 6, 23, 10, RED); tri_font(c, 6, 7, "x2", WHITE) if False else None
    for x in range(5, 22, 2): c.px(x, 8, WHITE) if x % 4 == 1 else None
    c.rect(5, 13, 22, 14, BLACK); c.rect(5, 17, 17, 18, BLACK); c.rect(5, 20, 12, 21, BLACK); c.ell(21, 19, 3, 3, RED); c.px(20, 18, WHITE)
@ic(RED, WHITE)
def crowbar(c):   # лом
    poly(c, [(4, 24), (7, 27), (21, 11), (18, 8)], RED, dither=(190, 0, 40)); poly(c, [(18, 8), (21, 11), (25, 9), (27, 4), (22, 1), (19, 3), (23, 5), (22, 7)], RED)
    poly(c, [(4, 24), (7, 27), (3, 27), (1, 25)], RED); c.line(5, 23, 19, 9, WHITE); c.pts([(22, 2), (26, 4)], WHITE); c.rect(9, 20, 10, 21, BLACK); c.rect(14, 14, 15, 15, BLACK)
@ic(ORANGE, YELLOW)
def crown(c):   # корона из крышек
    poly(c, [(2, 24), (2, 10), (8, 15), (14, 5), (20, 15), (26, 10), (26, 24)], YELLOW, dither=ORANGE); c.rect(2, 21, 25, 25, ORANGE); c.rect(2, 21, 25, 22, YELLOW)
    for x, y, col in ((2, 8, RED), (14, 3, CYAN), (26, 8, GREEN)): c.ell(x, y, 2.2, 2.2, col); c.px(x - 1, y - 1, WHITE)
    for x in (6, 11, 16, 21): c.ell(x, 17, 2, 2, RED if x % 2 else CYAN); c.px(x - 1, 16, WHITE)
    c.pts([(5, 12), (9, 18)], WHITE)
@ic(PURPLE, WHITE)
def dead_rat(c):   # крыса-приятель
    c.ell(12, 18, 10, 6, MG, dither=DGREY); c.ell(22, 14, 5, 4, MG); poly(c, [(26, 13), (28, 15), (26, 16)], PINK); c.ell(20, 9, 2.2, 2.2, PINK); c.ell(24, 9, 2, 2, PINK)
    c.px(22, 13, BLACK); c.px(23, 12, RED); c.px(22, 12, WHITE); c.pts([(25, 15), (28, 14)], WHITE); c.line(2, 18, 0, 26, PINK); c.line(0, 26, 4, 27, PINK)
    for x in (7, 11, 15): c.rect(x, 23, x + 1, 25, PINK)
    c.pts([(6, 14), (10, 13)], DGREY); c.pts([(14, 15), (16, 15)], LG)
@ic(GREEN, YELLOW)
def diarrhea(c):   # взрывной понос
    poly(c, [(2, 25), (26, 25), (24, 19), (4, 19)], BROWN); poly(c, [(5, 19), (23, 19), (21, 13), (7, 13)], BROWN, dither=DBROWN); poly(c, [(8, 13), (20, 13), (18, 8), (10, 8)], BROWN); poly(c, [(11, 8), (17, 8), (14, 3)], BROWN)
    c.pts([(9, 22), (16, 22), (12, 16), (16, 11)], (150, 90, 40)); c.pts([(11, 10), (12, 9)], (150, 90, 40)); c.px(12, 20, BLACK) if False else None
    for p in [(1, 14), (26, 12), (2, 4), (25, 4), (0, 22)]: c.ell(p[0], p[1], 2, 2, GREEN); c.px(p[0] - 1, p[1] - 1, LGREEN)
    for p in [(22, 22), (5, 22)]: c.px(*p, YELLOW)
    c.rect(13, 0, 14, 1, YELLOW); c.px(15, 1, ORANGE)
@ic(CYAN, WHITE)
def dirty_glasses(c):   # грязные очки
    c.ell(7.5, 15, 6, 6, BLACK); c.ell(20.5, 15, 6, 6, BLACK); c.ell(7.5, 15, 4.5, 4.5, (60, 70, 70)); c.ell(20.5, 15, 4.5, 4.5, (60, 70, 70)); c.rect(12, 12, 15, 13, BLACK)
    c.line(1, 11, 0, 8, BLACK, 2); c.line(26, 11, 27, 8, BLACK, 2); c.pts([(5, 13), (6, 12), (18, 13), (19, 12)], CYAN); c.pts([(8, 18), (10, 17), (21, 19), (23, 17)], GREEN); c.pts([(6, 16), (22, 14)], BROWN)
    c.px(4, 12, WHITE); c.px(17, 12, WHITE)
@ic(ORANGE, YELLOW)
def dried_fish(c):   # вяленая рыба
    c.ell(13, 14, 11, 6, (235, 205, 70), dither=(190, 160, 30)); poly(c, [(21, 14), (28, 7), (27, 14), (28, 21)], ORANGE)
    c.ell(6, 13, 1.8, 1.8, WHITE); c.px(6, 13, BLACK); c.line(4, 17, 9, 18, BROWN); c.pts([(12, 8), (14, 7), (17, 9), (19, 8)], ORANGE); c.pts([(12, 20), (15, 21), (18, 20)], ORANGE)
    for x in (10, 13, 16): c.line(x, 10, x - 1, 18, (180, 140, 20)); c.pts([(4, 3), (5, 4)], BROWN) if False else None
    c.line(5, 0, 6, 8, BROWN); c.px(3, 0, BROWN); c.px(8, 0, BROWN)
@ic(GREEN, YELLOW)
def energy_can(c):   # энергетик
    c.rect(6, 3, 21, 25, (30, 30, 40)); c.rect(6, 3, 21, 5, MG); c.rect(6, 23, 21, 25, MG); c.rect(6, 6, 21, 6, WHITE); c.rect(8, 1, 19, 3, STEEL); c.rect(14, 1, 17, 2, DGREY)
    poly(c, [(16, 7), (9, 15), (13, 15), (11, 23), (19, 13), (15, 13), (17, 7)], YELLOW); c.rect(6, 8, 7, 22, GREEN); c.rect(20, 8, 21, 22, GREEN); c.pts([(8, 7), (8, 9)], WHITE); c.px(23, 5, CYAN)
@ic(CYAN, WHITE)
def foil_hat(c):   # шапка из фольги
    poly(c, [(14, 1), (24, 22), (4, 22)], STEEL, dither=WHITE); poly(c, [(14, 1), (15, 1), (19, 14), (14, 10), (9, 16)], LG)
    c.rect(2, 21, 26, 25, MG, dither=LG); c.pts([(10, 8), (18, 9), (7, 17), (21, 18), (12, 14)], DGREY); c.line(14, 1, 11, 20, WHITE); c.rect(3, 22, 25, 22, WHITE); c.pts([(14, -1), (22, 3), (8, 4)], CYAN) if False else c.pts([(24, 5), (26, 3), (3, 6), (1, 4)], CYAN)
@ic(CYAN, WHITE)
def ghost_drunk(c):   # дух друга-алкаша
    GH = (160, 235, 255)
    c.ell(13, 11, 9, 9, GH, dither=WHITE); c.rect(4, 11, 22, 23, GH, dither=WHITE)
    for x in (4, 9, 14, 19): poly(c, [(x, 22), (x + 5, 22), (x + 2, 27)], GH)
    c.rect(8, 9, 10, 12, BLACK); c.rect(15, 9, 17, 12, BLACK); c.px(9, 10, RED); c.px(16, 10, RED); c.rect(10, 15, 15, 17, BLACK); c.px(12, 16, PINK)
    poly(c, [(21, 14), (24, 14), (24, 25), (21, 25)], GREEN); c.rect(22, 11, 23, 13, GREEN); c.rect(21, 10, 24, 10, WHITE); c.px(22, 17, WHITE); c.pts([(2, 4), (1, 6)], CYAN)
@ic(PINK, WHITE)
def ghost_granny(c):   # дух бабки
    GH = (160, 235, 255)
    c.ell(13, 12, 9, 10, GH, dither=WHITE); c.rect(4, 13, 22, 23, GH, dither=WHITE)
    for x in (4, 9, 14, 19): poly(c, [(x, 22), (x + 5, 22), (x + 2, 27)], GH)
    poly(c, [(3, 6), (13, 0), (23, 6), (22, 11), (4, 11)], PINK, dither=(255, 120, 245)); c.rect(4, 11, 22, 12, (200, 0, 190)); c.pts([(8, 3), (14, 2), (19, 4)], WHITE)
    c.rect(8, 15, 10, 16, BLACK); c.rect(15, 15, 17, 16, BLACK); c.ell(9, 15.5, 3, 2.5, BLACK) if False else None; c.pts([(7, 14), (11, 14), (14, 14), (18, 14)], WHITE); c.rect(10, 20, 15, 20, BLACK); c.pts([(2, 12), (24, 12)], MG)
@ic(ORANGE, YELLOW)
def gold_tooth(c):   # золотой зуб
    c.ell(8, 8, 7, 6, YELLOW, dither=ORANGE); c.ell(20, 8, 7, 6, YELLOW, dither=ORANGE); c.rect(2, 8, 26, 15, YELLOW, dither=ORANGE)
    poly(c, [(3, 14), (12, 14), (10, 26), (6, 26)], YELLOW, dither=ORANGE); poly(c, [(16, 14), (25, 14), (22, 26), (18, 26)], YELLOW, dither=ORANGE)
    c.rect(6, 4, 8, 8, WHITE); c.rect(4, 7, 5, 11, WHITE); c.rect(13, 14, 14, 20, ORANGE); c.pts([(24, 2), (26, 0), (26, 4), (22, 0)], WHITE)
@ic(ORANGE, YELLOW)
def golden_toilet(c):   # золотой унитаз
    poly(c, [(2, 1), (11, 1), (11, 12), (2, 12)], YELLOW, dither=ORANGE); c.rect(1, 1, 12, 3, ORANGE); c.rect(5, 0, 8, 0, WHITE); c.ell(20, 3, 2, 1.5, YELLOW)
    poly(c, [(2, 13), (27, 13), (25, 19), (4, 19)], YELLOW, dither=ORANGE); c.rect(2, 12, 27, 13, WHITE); poly(c, [(5, 19), (24, 19), (21, 24), (8, 24)], YELLOW, dither=ORANGE); c.rect(8, 24, 22, 27, ORANGE); c.rect(6, 27, 24, 27, YELLOW)
    c.ell(16, 16, 8, 2, BLACK); c.pts([(14, 15), (18, 16)], BROWN); c.pts([(3, 4), (3, 9), (7, 14)], WHITE); c.px(26, 8, WHITE); c.px(25, 7, RED); c.px(6, 2, RED)
@ic(PINK, WHITE)
def gum(c):   # жвачка с асфальта
    c.rect(0, 18, 27, 27, DGREY, dither=MG); c.pts([(3, 20), (9, 24), (15, 21), (21, 25), (25, 20), (6, 26)], BLACK); c.pts([(4, 19), (13, 22), (24, 23)], MG)
    c.ell(10, 13, 8.5, 6.5, PINK, dither=(255, 120, 245)); c.ell(18, 14, 5.5, 4.5, PINK); c.ell(14, 8, 4, 3, PINK); c.pts([(6, 9), (7, 8), (8, 9)], WHITE); c.rect(5, 11, 6, 13, WHITE)
    poly(c, [(20, 11), (26, 3), (27, 4), (22, 13)], PINK); c.px(26, 1, (255, 150, 245)); c.pts([(12, 17), (18, 18), (6, 16)], (200, 0, 190)); c.pts([(8, 15), (14, 14)], (200, 0, 190))
# ============ ПРЕДМЕТЫ (Д–Я) ============
@ic(ORANGE, YELLOW)
def helmet(c):   # каска строителя
    c.ell(14, 17, 12.5, 11, YELLOW, dither=(230, 230, 0)); c.rect(1, 17, 26, 22, YELLOW); c.rect(0, 22, 27, 25, ORANGE); c.rect(0, 22, 27, 22, YELLOW)
    c.rect(11, 5, 16, 20, ORANGE); c.rect(12, 6, 13, 18, (255, 150, 60)); c.pts([(5, 11), (6, 9), (8, 8)], WHITE); c.rect(4, 12, 5, 14, WHITE); c.pts([(20, 14), (22, 16)], (200, 200, 0))
@ic(GREEN, WHITE)
def holey_sock(c):   # дырявый носок
    poly(c, [(6, 1), (17, 1), (17, 17), (26, 19), (26, 26), (6, 26)], WHITE, dither=LG)
    for y in (3, 7): c.rect(6, y, 17, y + 1, RED)
    c.rect(6, 12, 17, 13, RED); c.ell(10, 21, 3.5, 3, BLACK); c.pts([(8, 18), (10, 18), (12, 19), (7, 23), (12, 24)], BROWN); c.pts([(20, 21), (22, 22)], BROWN)
    c.pts([(20, 0), (21, -1)], GREEN) if False else c.pts([(21, 2), (22, 4), (21, 6), (23, 8)], GREEN); c.pts([(25, 4), (24, 6)], LGREEN); c.rect(15, 23, 25, 23, (210, 210, 195))
@ic(PURPLE, YELLOW)
def hot_dog(c):   # хот-дог: булка-лодочка и сосиска с горчицей
    poly(c, [(3, 14), (25, 14), (23, 24), (5, 24)], (240, 185, 100), dither=(205, 140, 70)); c.ell(14, 14, 11, 3, (240, 185, 100)); c.rect(5, 23, 23, 24, (205, 140, 70))
    c.ell(14, 11, 13.5, 3.6, (230, 70, 50)); c.ell(2, 11, 2.6, 3.6, (230, 70, 50)); c.ell(26, 11, 2.6, 3.6, (230, 70, 50)); c.rect(3, 8, 24, 9, (255, 135, 115)); c.pts([(2, 9), (26, 9)], (255, 135, 115))
    c.rect(4, 13, 23, 13, (200, 40, 30)); c.pts([(4, 10), (6, 7), (8, 10), (10, 7), (12, 10), (14, 7), (16, 10), (18, 7), (20, 10), (22, 7), (24, 10)], YELLOW)
    c.pts([(8, 17), (14, 19), (19, 17)], (200, 150, 80)); c.pts([(6, 5), (15, 4), (21, 4)], GREEN); c.pts([(4, 21)], WHITE)
@ic(PURPLE, WHITE)
def junk_backpack(c):   # рюкзак с хламом
    c.ell(14, 8, 10, 6, (140, 105, 60), dither=BROWN); poly(c, [(3, 10), (25, 10), (26, 26), (2, 26)], (140, 105, 60), dither=BROWN); c.rect(7, 16, 21, 24, BROWN); c.rect(11, 18, 17, 19, YELLOW); c.rect(13, 19, 14, 21, DGREY)
    c.line(3, 12, 1, 24, DGREY, 2); c.line(24, 12, 26, 24, DGREY, 2); c.pts([(10, 0), (11, 1), (17, 0)], GREEN); c.rect(8, 1, 9, 5, YELLOW); poly(c, [(15, 4), (19, 0), (21, 4)], RED); c.rect(5, 11, 22, 11, DGREY)
    c.pts([(9, 14), (18, 13), (7, 22), (21, 22)], (200, 150, 80)); c.px(6, 14, WHITE)
@ic(RED, PINK)
def junk_magnet(c):   # магнит
    poly(c, [(2, 2), (10, 2), (10, 13), (14, 17), (18, 13), (18, 2), (26, 2), (26, 15), (20, 24), (8, 24), (2, 15)], RED, dither=(190, 0, 40))
    c.rect(10, 3, 17, 13, BLACK) if False else None; c.rect(2, 2, 10, 8, WHITE); c.rect(18, 2, 26, 8, WHITE); c.rect(2, 9, 9, 10, DRED); c.rect(19, 9, 26, 10, DRED)
    c.rect(3, 3, 4, 7, (230, 230, 230)); c.pts([(5, 14), (4, 18)], PINK); c.pts([(8, 26), (14, 27), (20, 26)], GREEN) if False else None
    c.pts([(5, 0), (8, 0), (20, 0), (23, 0)], LG); c.px(12, 20, YELLOW); c.px(9, 21, GREEN); c.px(16, 21, CYAN)
@ic(RED, YELLOW)
def lighter(c):   # зажигалка
    poly(c, [(7, 10), (20, 10), (20, 26), (7, 26)], RED, dither=(190, 0, 40)); c.rect(7, 6, 20, 10, STEEL); c.rect(7, 6, 20, 7, WHITE); c.rect(10, 3, 16, 5, DGREY); c.rect(11, 2, 13, 3, WHITE)
    c.rect(9, 12, 10, 24, PINK); c.rect(12, 16, 17, 20, YELLOW); c.px(14, 18, BLACK)
    poly(c, [(18, 1), (22, 6), (20, 8), (16, 5)], ORANGE) if False else None; poly(c, [(13, 0), (11, -1), (14, -3)], YELLOW) if False else None
    c.ell(21, 3, 2.5, 3.5, ORANGE); c.ell(21, 3.5, 1.2, 2, YELLOW); c.px(21, 6, WHITE)
@ic(PURPLE, WHITE)
def nail_knuckles(c):   # кастет из гвоздей
    poly(c, [(2, 11), (26, 11), (26, 21), (2, 21)], DGREY, dither=MG)
    for x in (5, 10, 15, 20): c.rect(x - 1, 14, x + 2, 24, BLACK); c.rect(x, 15, x + 1, 21, MG)
    for x in (4, 9, 14, 19, 24): c.rect(x, 3, x + 1, 11, LG); poly(c, [(x - 1, 11), (x + 2, 11), (x, 12)], DGREY); c.px(x, 2, WHITE); c.px(x - 1, 3, MG) if False else None
    c.rect(2, 11, 26, 12, WHITE) if False else None; c.pts([(4, 13), (12, 13)], WHITE); c.pts([(6, 17), (16, 18), (24, 17)], (150, 70, 30))
@ic(PURPLE, WHITE)
def old_milk(c):   # тухлая сгущёнка (банка)
    c.rect(4, 5, 23, 24, TIN, dither=WHITE); c.rect(4, 3, 23, 5, MG); c.rect(4, 24, 23, 26, MG); c.rect(4, 7, 23, 22, BLUE); c.rect(4, 7, 23, 8, (80, 80, 255))
    c.ell(14, 14, 6, 5.5, WHITE); c.px(12, 12, BLACK); c.px(16, 12, BLACK); c.rect(12, 16, 16, 16, PINK) if False else None; c.ell(14, 16, 2.5, 1.6, PINK); c.px(12, 10, BLACK) if False else None
    poly(c, [(6, 10), (9, 8), (10, 12)], BLACK) if False else None; c.pts([(8, 18), (8, 20), (20, 19), (21, 21)], GREEN); c.rect(21, 3, 25, 3, GREEN) if False else None
    c.pts([(25, 8), (26, 10), (26, 13), (25, 15)], WHITE); c.ell(26, 18, 1.5, 2, WHITE); c.pts([(7, 0), (9, 1), (6, 2)], GREEN)
@ic(PURPLE, WHITE)
def plastic_bag(c):   # пакет
    poly(c, [(5, 8), (23, 8), (26, 26), (2, 26)], (235, 245, 252), dither=(190, 215, 235)); poly(c, [(5, 8), (8, 0), (11, 8)], (235, 245, 252)); poly(c, [(17, 8), (20, 0), (23, 8)], (235, 245, 252))
    c.rect(6, 13, 21, 20, RED); tri_font(c, 8, 14, "x2", WHITE) if False else None; c.rect(8, 15, 19, 16, WHITE); c.rect(8, 18, 15, 18, WHITE)
    c.pts([(4, 24), (22, 22), (9, 10)], (150, 190, 215)); c.px(8, 3, WHITE); c.pts([(24, 12), (25, 18)], (150, 190, 215))
@ic(PURPLE, YELLOW)
def poop_wallet(c):   # кошелёк с говном
    poly(c, [(2, 8), (26, 8), (26, 25), (2, 25)], DBROWN, dither=BROWN); c.rect(2, 8, 26, 10, BROWN); c.rect(18, 14, 26, 20, YELLOW); c.ell(21, 17, 2, 2, ORANGE); c.rect(24, 16, 25, 18, DGREY)
    poly(c, [(8, 8), (14, 8), (13, 4), (11, 2), (9, 4)], BROWN); c.px(11, 0, BROWN); c.px(10, 3, DBROWN); c.pts([(4, 24), (8, 26), (12, 26)], GREEN); c.pts([(4, 12), (10, 12)], (180, 120, 70)); c.px(5, 2, GREEN); c.px(15, 2, GREEN)
    c.pts([(3, 14), (3, 20)], DBROWN)
@ic(PURPLE, WHITE)
def pot(c):   # ржавая кастрюля
    poly(c, [(3, 9), (25, 9), (24, 25), (4, 25)], (150, 80, 45), dither=DGREY); c.rect(2, 7, 26, 9, MG); c.rect(2, 7, 26, 7, WHITE); c.rect(0, 11, 3, 14, DGREY); c.rect(24, 11, 27, 14, DGREY)
    c.ell(14, 4, 4, 2, DGREY); c.px(14, 2, WHITE); c.pts([(6, 14), (7, 16), (18, 20), (19, 22), (11, 12), (21, 14)], (215, 120, 45)); c.pts([(5, 11), (5, 20)], WHITE); c.pts([(12, 24), (16, 23)], DBROWN)
@ic(GREEN, LGREEN)
def rubber_boot(c):   # резиновый сапог
    poly(c, [(6, 1), (17, 1), (17, 17), (26, 19), (27, 26), (3, 26), (6, 17)], GREEN, dither=(20, 190, 20)); c.rect(5, 0, 18, 3, LGREEN); c.rect(3, 24, 27, 27, BLACK); c.rect(8, 6, 9, 14, WHITE)
    c.pts([(12, 9), (13, 10), (14, 9), (13, 13), (8, 22)], DGRN); c.pts([(1, 26), (2, 27), (0, 27)], BROWN); c.pts([(22, 22), (23, 22), (24, 21)], LGREEN); c.px(12, 20, BLACK)
@ic(PURPLE, WHITE)
def sandwich(c):   # тухлый сэндвич
    poly(c, [(2, 5), (25, 5), (27, 11), (1, 11)], (235, 180, 100), dither=(200, 140, 70)); c.rect(1, 12, 26, 13, GREEN); c.rect(3, 14, 24, 15, RED); c.rect(1, 16, 26, 18, YELLOW); c.rect(2, 19, 25, 19, (240, 150, 160))
    poly(c, [(1, 20), (26, 20), (24, 26), (3, 26)], (235, 180, 100), dither=(200, 140, 70)); c.pts([(7, 7), (12, 6), (19, 7), (22, 8)], WHITE); c.pts([(6, 22), (14, 23), (20, 22)], BROWN); c.pts([(8, 13), (17, 14), (10, 17), (21, 17)], GREEN) ; c.pts([(18, 3), (20, 2)], GREEN)
@ic(RED, WHITE)
def scarf(c):   # полосатый шарф: петля вокруг шеи и два свисающих конца с бахромой
    poly(c, [(1, 3), (8, 1), (20, 1), (27, 3), (26, 10), (20, 13), (8, 13), (2, 10)], PINK, dither=(200, 0, 190))
    c.ell(14, 8, 5, 3, BLACK)
    for x in range(2, 26, 5): c.rect(x, 2, x + 1, 12, WHITE)
    poly(c, [(6, 12), (13, 12), (12, 25), (4, 25)], PINK, dither=(200, 0, 190)); poly(c, [(15, 12), (22, 12), (24, 22), (16, 22)], PINK, dither=(200, 0, 190))
    for y in (15, 19): c.rect(5 if y == 15 else 4, y, 12 if y == 15 else 11, y + 1, WHITE)
    c.rect(16, 16, 23, 17, WHITE)
    for x in (4, 6, 8, 10): c.rect(x, 26, x, 28, WHITE)
    for x in (16, 18, 20, 22): c.rect(x, 23, x, 25, WHITE)
    c.pts([(3, 3), (24, 3)], YELLOW)
@ic(CYAN, WHITE)
def shawarma(c):   # шаурма
    poly(c, [(5, 25), (17, 6), (24, 10), (13, 27)], (240, 190, 110), dither=(205, 150, 75)); poly(c, [(6, 25), (3, 22), (5, 19)], (240, 190, 110)); c.line(9, 20, 17, 8, (205, 150, 75))
    poly(c, [(15, 5), (26, 9), (24, 12), (13, 8)], DBROWN); c.pts([(15, 3), (17, 1), (20, 3), (22, 1), (24, 4)], GREEN); c.pts([(18, 5), (22, 6)], RED); c.pts([(19, 7), (23, 8)], WHITE)
    poly(c, [(2, 26), (10, 22), (14, 27), (4, 28)], STEEL, dither=WHITE) ; c.pts([(10, 22), (6, 25)], DGREY); c.pts([(0, 8), (1, 6), (2, 4)], GREEN) if False else c.pts([(3, 6), (4, 4), (3, 2)], GREEN)
@ic(ORANGE, YELLOW)
def skateboard(c):   # скейт
    poly(c, [(0, 8), (3, 6), (25, 6), (28, 8), (27, 12), (1, 12)], YELLOW, dither=ORANGE); c.rect(2, 8, 25, 8, WHITE); c.rect(5, 9, 10, 10, RED); c.pts([(13, 9), (15, 10), (17, 9), (20, 10)], BLACK)
    c.rect(5, 13, 9, 15, DGREY); c.rect(19, 13, 23, 15, DGREY); c.ell(7, 19, 4, 4, DGREY); c.ell(21, 19, 4, 4, DGREY); c.ell(7, 19, 1.5, 1.5, WHITE); c.ell(21, 19, 1.5, 1.5, WHITE); c.px(5, 17, WHITE); c.px(19, 17, WHITE)
    c.pts([(1, 24), (3, 25), (25, 25), (27, 24)], CYAN) if False else None
@ic(GREEN, WHITE)
def stink_lamp(c):   # лампа-вонялка
    c.ell(14, 10, 9, 9, (210, 245, 210), dither=WHITE); c.ell(14, 11, 6, 6, GREEN); c.ell(14, 11, 3, 3, LGREEN); c.px(9, 6, WHITE); c.pts([(8, 8), (8, 9)], WHITE)
    poly(c, [(9, 18), (19, 18), (18, 22), (10, 22)], MG); c.rect(10, 19, 18, 19, DGREY); c.rect(8, 23, 20, 26, DGREY); c.rect(8, 23, 20, 23, STEEL); c.rect(12, 26, 16, 27, BLACK)
    c.pts([(1, 6), (2, 4), (1, 2), (2, 0), (26, 6), (25, 4), (26, 2), (25, 0)], GREEN); c.pts([(4, 14), (23, 15)], LGREEN)
@ic(GREEN, YELLOW)
def stinky_pants(c):   # обосранные штаны
    poly(c, [(3, 1), (25, 1), (25, 6), (3, 6)], (50, 90, 170)); poly(c, [(3, 6), (14, 6), (13, 26), (3, 26)], (50, 90, 170), dither=(40, 70, 135)); poly(c, [(14, 6), (25, 6), (25, 26), (15, 26)], (50, 90, 170), dither=(40, 70, 135))
    c.rect(3, 1, 25, 2, DGREY); c.rect(13, 6, 14, 26, BLACK); c.rect(3, 25, 12, 26, CREAM); c.rect(16, 25, 25, 26, CREAM); c.rect(11, 1, 12, 2, YELLOW); c.rect(15, 1, 16, 2, YELLOW)
    c.ell(8, 12, 4, 5, BROWN); c.ell(20, 10, 3, 4, BROWN); c.ell(12, 18, 2, 2, BROWN); c.px(7, 10, (150, 90, 40)); c.pts([(2, 12), (1, 16), (26, 14), (26, 18), (6, 28)], GREEN)
@ic(PURPLE, WHITE)
def ushanka(c):   # ушанка
    c.ell(14, 11, 11, 9, (160, 130, 90), dither=BROWN); c.rect(1, 12, 8, 26, BROWN, dither=DBROWN); c.rect(19, 12, 26, 26, BROWN, dither=DBROWN); c.rect(8, 14, 19, 18, DBROWN); c.ell(14, 3, 5, 2, (185, 155, 115))
    poly(c, [(14, 8), (16, 12), (21, 12), (17, 15), (19, 19), (14, 16), (9, 19), (11, 15), (7, 12), (12, 12)], RED); c.px(14, 13, YELLOW) if False else None; c.ell(14, 14, 1.5, 1.5, YELLOW)
    c.rect(1, 25, 8, 27, (215, 215, 195)); c.rect(19, 25, 26, 27, (215, 215, 195)); c.rect(8, 18, 19, 19, (215, 215, 195)); c.pts([(5, 6), (9, 4)], WHITE)
@ic(GREEN, WHITE)
def vodka(c):   # бутылка палёнки
    poly(c, [(8, 11), (19, 11), (20, 26), (7, 26)], (220, 245, 255), dither=WHITE); poly(c, [(11, 3), (16, 3), (16, 11), (11, 11)], (220, 245, 255)); c.rect(10, 0, 17, 3, RED); c.rect(10, 1, 17, 1, (255, 90, 90))
    c.rect(8, 15, 19, 22, WHITE); c.rect(9, 16, 18, 21, RED); c.ell(13.5, 18.5, 2.5, 2.5, WHITE); c.px(13, 18, BLACK); c.px(14, 18, BLACK); c.rect(8, 24, 19, 25, CYAN) ; c.pts([(9, 6), (9, 12), (8, 18)], CYAN) if False else None
    c.pts([(10, 5), (10, 8)], WHITE); c.pts([(22, 8), (23, 6), (22, 4)], GREEN); c.pts([(24, 12), (23, 10)], LGREEN)
@ic(GREEN, WHITE)
def stray_dog(c):   # пёс с помойки
    poly(c, [(2, 3), (8, 2), (9, 9), (4, 12)], DBROWN); poly(c, [(26, 3), (20, 2), (19, 9), (24, 12)], DBROWN)
    c.ell(14, 14, 10, 10, (170, 120, 70), dither=BROWN); c.ell(14, 19, 5.5, 4.5, (235, 225, 205)); c.ell(14, 17, 2.5, 1.8, BLACK); c.rect(13, 20, 14, 23, BLACK) if False else None
    c.rect(8, 11, 10, 13, BLACK); c.rect(18, 11, 20, 13, BLACK); c.px(9, 11, WHITE); c.px(19, 11, WHITE); c.rect(12, 22, 16, 25, PINK); c.rect(14, 22, 14, 24, (230, 80, 130))
    c.pts([(7, 7), (10, 6)], (200, 150, 100)); c.pts([(17, 4), (20, 6)], GREEN); c.px(21, 3, LGREEN); c.pts([(4, 16), (5, 18)], DBROWN)

def render(n):
    f, sh, hi, lim, tall = I[n]
    c = Canvas(N, 36) if tall else new(); f(c); return fin(c, sh, hi, lim, tall)

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(I)
    k = 5; cols = 9; cell = 34 * k
    prev = Image.new("RGBA", (cols * cell, ((len(names) + cols - 1) // cols) * (cell + 40)), (45, 30, 20, 255))
    for i, n in enumerate(names):
        a = render(n); im = Image.fromarray(a, "RGBA")
        if apply:
            base = "assets/ui/" + (n if n.startswith(("stat_", "perk_")) else "item_" + n)
            im.save(base + ".png"); Image.fromarray(small(a), "RGBA").save(base + "_s.png")
        b = im.resize((im.width * k, im.height * k), Image.NEAREST); x = (i % cols) * cell + 6; y = (i // cols) * (cell + 40) + 4
        prev.paste(b, (x, y), b)
        sm = Image.fromarray(small(a), "RGBA").resize((16 * 4, 16 * 4), Image.NEAREST); prev.paste(sm, (x + 32 * k - 64, y + im.height * k + 2), sm)
    prev.save("tools/_preview/icons2.png"); print(len(names), prev.size)
