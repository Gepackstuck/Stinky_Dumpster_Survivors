#!/usr/bin/env python3
"""Модификаторы волн: значки 32×32 (+_s 16×16) и мусоровоз 48×28 (2 кадра колёс).
python3 tools/gen_wave_mods.py --apply  (превью tools/_preview/wave_mods.png)"""
import sys
sys.path.insert(0, "tools")
from icon_kit import *

I = {}
def ic(sh=PURPLE, hi=WHITE, lim=0.4):
    def d(f): I[f.__name__] = (f, sh, hi, lim); return f
    return d

@ic(DGREEN, YELLOW, 0.5)
def mod_acid_rain(c):   # грязная туча с глазами, кислотные капли и дымящаяся лужа
    for (x, y, r) in [(8, 7, 6), (15, 5, 7), (21, 8, 5)]:
        c.ell(x, y, r, r * 0.8, GREY, dither=DGREY)
    c.eye(11, 7, 2, (0, 1)); c.eye(18, 6, 1.5, (0, 1))
    for (x, y) in [(6, 15), (13, 18), (20, 14), (9, 22), (17, 23)]:
        poly(c, [(x, y - 3), (x + 2, y + 1), (x, y + 2), (x - 2, y + 1)], GREEN)
    c.ell(14, 26, 10, 1.6, LGREEN, dither=GREEN); c.pts([(5, 25), (23, 24)], YELLOW)

@ic(DGREY, YELLOW, 0.4)
def mod_darkness(c):   # разбитая лампочка, из темноты пялятся глаза
    c.rect(0, 0, 27, 27, (20, 18, 28), dither=(30, 26, 40))
    c.ell(14, 10, 6, 7, (220, 220, 160), dither=(180, 180, 120)); c.rect(11, 16, 17, 21, GREY, dither=DGREY)
    c.line(11, 6, 15, 12, BLACK); c.line(15, 12, 13, 15, BLACK); c.px(17, 8, BLACK)
    c.eye(4, 22, 1.5, (1, 0), iris=RED); c.eye(23, 21, 2, (-1, 0), iris=RED); c.eye(24, 4, 1, (-1, 1), iris=RED)

@ic(DBROWN, YELLOW, 0.4)
def mod_garbage_truck(c):   # морда мусоровоза с клыками
    c.rect(2, 6, 25, 21, GREEN, dither=DGREEN); c.rect(4, 8, 23, 12, (150, 220, 255), dither=CYAN)
    c.eye(9, 10, 2, (1, 1)); c.eye(18, 10, 3, (-1, 1))
    c.rect(4, 15, 23, 19, BLACK); c.teeth(5, 22, 15, WHITE, BLACK, 3)
    c.ell(6, 23, 3, 3, BLACK); c.ell(21, 23, 3, 3, BLACK); c.px(6, 23, GREY); c.px(21, 23, GREY)
    c.pts([(1, 3), (4, 2), (25, 2), (27, 4)], BROWN); c.pts([(13, 1), (14, 0)], GREEN)

@ic(BLUE, WHITE, 0.4)
def mod_ice(c):   # жирная лужа, на ней скользит ботинок
    c.ell(14, 20, 13, 6, (120, 200, 255), dither=(200, 240, 255)); c.ell(10, 19, 4, 1.5, WHITE)
    poly(c, [(7, 6), (16, 6), (19, 11), (21, 13), (21, 16), (8, 16)], BROWN, dither=DBROWN)
    c.rect(8, 15, 21, 16, BLACK); c.pts([(2, 9), (4, 9), (1, 12), (3, 12)], CYAN); c.pts([(24, 22), (26, 21)], YELLOW)

@ic(DBROWN, YELLOW, 0.5)
def mod_payday(c):   # мешок с говном и знаком денег, мухи
    c.ell(14, 17, 10, 9, (190, 150, 90), dither=(160, 120, 70)); c.rect(11, 5, 17, 9, (190, 150, 90)); c.rect(10, 8, 18, 9, RED)
    c.ell(14, 17, 4, 4.5, BROWN); c.rect(13, 11, 15, 23, YELLOW); c.rect(11, 13, 17, 14, YELLOW); c.rect(11, 20, 17, 21, YELLOW)
    for (x, y) in [(4, 4), (24, 6), (25, 25)]:
        c.px(x, y, BLACK); c.px(x - 1, y - 1, LG); c.px(x + 1, y - 1, LG)


@ic(PURPLE, WHITE, 0.4)
def mod_pigeon_raid(c):   # голубь пикирует с бомбой-какашкой
    c.ell(13, 9, 8, 5, GREY, dither=DGREY); poly(c, [(4, 6), (12, 4), (9, 11)], LG); poly(c, [(22, 6), (14, 4), (17, 11)], LG)
    c.ell(20, 8, 3.5, 3, (110, 60, 170)); c.eye(21, 7, 1.5, (1, 0), iris=RED); poly(c, [(24, 8), (27, 9), (24, 10)], ORANGE)
    c.ell(12, 20, 3.5, 3, BROWN); c.ell(12, 17, 2.5, 2, BROWN); c.ell(12, 15, 1.5, 1.2, (150, 90, 40)); c.pts([(9, 24), (15, 24), (12, 26)], BROWN)
@ic(DGREEN, YELLOW, 0.45)
def mod_sewer_flood(c):   # люк, из него хлещет жижа
    c.ell(14, 18, 12, 6, (120, 160, 40), dither=(90, 130, 30)); c.ell(14, 12, 8, 4, DGREY); c.ell(14, 12, 6, 3, GREY, dither=DGREY)
    for x in (10, 14, 18): c.rect(x, 3, x + 1, 9, (140, 190, 50))
    c.ell(14, 3, 4, 2, (160, 210, 60)); c.ell(6, 20, 2, 1.5, BROWN); c.ell(22, 21, 1.5, 1, BROWN); c.pts([(3, 14), (25, 15)], YELLOW)
@ic(DGREY, CYAN, 0.4)
def mod_wind(c):   # пакет летит по ветру, полосы ветра
    for y, x0, x1 in [(5, 2, 16), (13, 0, 10), (22, 3, 14)]: c.line(x0, y, x1, y, WHITE)
    poly(c, [(15, 6), (25, 9), (24, 20), (14, 22), (12, 12)], (235, 235, 245), dither=LG); c.rect(17, 4, 19, 7, LG)
    c.eye(18, 13, 2, (-1, 0)); c.line(16, 18, 20, 17, BLACK)
@ic(DRED, PINK, 0.45)
def mod_hangover(c):   # рожа зелёная, глаза в кучу, бутылка
    c.ell(12, 13, 9, 9, (170, 220, 120), dither=(140, 190, 100)); c.eye(9, 11, 2.5, (1, 0)); c.eye(15, 11, 2, (-1, 1))
    c.line(8, 18, 15, 17, BLACK); c.pts([(10, 19), (12, 20)], GREEN)
    poly(c, [(21, 9), (25, 9), (26, 26), (20, 26)], (100, 200, 120), dither=GREEN); c.rect(22, 5, 24, 9, (100, 200, 120))
    c.pts([(3, 4), (5, 2), (7, 4)], YELLOW)
@ic(DRED, ORANGE, 0.4)
def mod_giants(c):   # огромная рожа, маленький герой рядом
    c.ell(16, 12, 11, 11, RED, dither=DRED); c.eye(11, 9, 3, (0, 1)); c.eye(20, 10, 2, (0, 1)); c.rect(9, 16, 22, 19, BLACK); c.teeth(9, 22, 16, WHITE, BLACK, 3)
    c.ell(4, 23, 2, 3, SKINC); c.rect(3, 25, 5, 27, BLUE); c.px(4, 22, BLACK)
@ic(PURPLE, PINK, 0.4)
def mod_dwarfs(c):   # куча мелких рож
    for (x, y, col) in [(6, 6, RED), (16, 5, PINK), (22, 13, GREEN), (11, 15, ORANGE), (4, 22, CYAN), (17, 22, RED), (24, 23, YELLOW)]:
        c.ell(x, y, 3, 3, col); c.px(x - 1, y - 1, BLACK); c.px(x + 1, y - 1, BLACK); c.px(x, y + 1, WHITE)
@ic(DBROWN, YELLOW, 0.45)
def mod_poop_death(c):   # череп в луже какашек
    c.ell(14, 21, 12, 5, BROWN, dither=(130, 80, 40)); c.ell(14, 11, 7, 7, WHITE, dither=LG); c.rect(10, 15, 18, 19, WHITE)
    c.ell(11, 10, 2, 2.5, BLACK); c.ell(17, 10, 2, 2.5, BLACK); c.rect(12, 16, 12, 18, BLACK); c.rect(15, 16, 15, 18, BLACK)
    c.pts([(4, 16), (24, 15), (8, 26)], GREEN)
@ic(PURPLE, PINK, 0.5)
def mod_disco(c):   # диско-шар из мусора, лучи
    c.ell(14, 13, 9, 9, GREY, dither=WHITE)
    for x in range(7, 22, 4):
        for y in range(6, 21, 4): c.px(x, y, CYAN if (x + y) % 8 else PINK)
    c.rect(13, 1, 14, 4, DGREY); c.line(2, 24, 8, 18, PINK); c.line(26, 24, 20, 18, GREEN); c.line(14, 27, 14, 23, YELLOW)
@ic(DBROWN, YELLOW, 0.4)
def mod_airdrop(c):   # ящик на парашюте из пакета
    poly(c, [(4, 9), (14, 2), (24, 9)], (235, 235, 245), dither=LG); c.line(5, 9, 10, 16, BLACK); c.line(23, 9, 18, 16, BLACK)
    c.rect(8, 16, 20, 26, WOOD, dither=DBROWN); c.rect(13, 17, 15, 25, RED); c.rect(9, 20, 19, 22, RED); c.rect(8, 16, 20, 16, BROWN)
@ic(DBROWN, PINK, 0.4)
def mod_slipper_storm(c):   # три тапка летят
    for (x, y, col) in [(3, 4, PINK), (12, 12, BLUE), (6, 20, RED)]:
        poly(c, [(x, y + 2), (x + 13, y), (x + 15, y + 3), (x + 2, y + 6)], col); c.rect(x + 4, y + 1, x + 7, y + 3, WHITE)
        c.line(x - 3, y + 3, x - 1, y + 3, WHITE)
@ic(DRED, CYAN, 0.45)
def mod_magnet(c):   # подкова-магнит тянет какашки
    c.rect(4, 4, 9, 20, RED); c.rect(15, 4, 20, 20, RED); c.ell(12, 20, 8, 6, RED); c.ell(12, 19, 3, 3, (0, 0, 0)) if False else None
    c.rect(10, 4, 14, 19, (0, 0, 0, 0)) if False else None
    c.rect(4, 4, 9, 7, LG); c.rect(15, 4, 20, 7, LG)
    for (x, y) in [(24, 4), (25, 12), (23, 22)]: c.ell(x, y, 2, 1.5, BROWN)
    c.pts([(21, 9), (22, 15)], CYAN)
@ic(DRED, YELLOW, 0.5)
def mod_explosive(c):   # рожа-бомба с фитилём
    c.ell(13, 15, 10, 10, DGREY, dither=BLACK); c.eye(10, 13, 2.5, (1, 0), iris=RED); c.eye(17, 13, 2, (-1, 0), iris=RED)
    c.rect(9, 19, 17, 21, ORANGE); c.line(18, 6, 23, 2, WOOD); c.ell(24, 2, 2, 2, YELLOW); c.pts([(26, 4), (22, 1)], ORANGE)
@ic(DGREEN, GREEN, 0.4)
def mod_zombies(c):   # рука из могилы
    c.rect(2, 22, 25, 27, BROWN, dither=DBROWN); c.rect(10, 8, 16, 22, (150, 200, 120), dither=(120, 170, 100))
    for x in (9, 11, 13, 15, 17): c.rect(x, 3 + (x % 3), x, 9, (150, 200, 120))
    c.rect(10, 14, 16, 16, (90, 60, 140)); c.pts([(19, 20), (6, 21)], WHITE)
@ic(DGREY, ORANGE, 0.4)
def mod_smoke_break(c):   # бычок и облака дыма
    c.rect(3, 21, 20, 23, WHITE); c.rect(17, 21, 20, 23, ORANGE); c.px(21, 22, RED)
    for (x, y, r) in [(20, 15, 4), (16, 9, 5), (21, 4, 4)]: c.ell(x, y, r, r * 0.8, LG, dither=GREY)
@ic(BLUE, CYAN, 0.4)
def mod_slowmo(c):   # улитка с часами
    c.ell(15, 15, 8, 8, ORANGE, dither=(200, 100, 0)); c.ell(15, 15, 5, 5, WHITE); c.line(15, 15, 15, 11, BLACK); c.line(15, 15, 18, 15, BLACK)
    c.rect(2, 21, 22, 24, (170, 220, 120)); c.rect(1, 17, 4, 21, (170, 220, 120)); c.px(1, 16, BLACK); c.px(4, 16, BLACK)
@ic(DRED, YELLOW, 0.4)
def mod_fast_forward(c):   # перемотка >>
    poly(c, [(2, 5), (13, 14), (2, 23)], YELLOW); poly(c, [(13, 5), (24, 14), (13, 23)], YELLOW); c.rect(25, 5, 27, 23, YELLOW)
    c.pts([(5, 12), (16, 12)], ORANGE)
@ic(DGREY, GREEN, 0.4)
def mod_manholes(c):   # открытый люк, из него руки и глаза
    c.ell(14, 17, 12, 7, BLACK); c.ell(14, 17, 12, 7, DGREY) if False else None
    c.eye(10, 16, 2, (0, -1), iris=RED); c.eye(18, 17, 2.5, (0, -1), iris=RED)
    c.rect(4, 8, 6, 15, (150, 200, 120)); c.rect(22, 9, 24, 15, (150, 200, 120)); c.ell(24, 6, 4, 2, GREY, dither=DGREY)
@ic(DBROWN, YELLOW, 0.5)
def mod_lottery(c):   # билет 777 и монеты-какашки
    c.rect(2, 6, 25, 18, (240, 230, 190), dither=CREAM); c.rect(2, 6, 25, 7, RED)
    for i, x in enumerate((5, 12, 19)): tri7 = [(x, 9), (x + 4, 9), (x + 2, 16)]; c.rect(x, 9, x + 4, 10, RED); c.line(x + 4, 10, x + 2, 16, RED)
    c.ell(7, 23, 3, 2.5, YELLOW); c.ell(15, 24, 3, 2.5, BROWN); c.ell(22, 23, 3, 2.5, YELLOW)
@ic(PURPLE, YELLOW, 0.5)
def mod_thunder(c):   # туча и молния в бак
    c.ell(14, 6, 11, 5, DGREY, dither=GREY); poly(c, [(15, 9), (10, 17), (14, 17), (11, 26), (19, 14), (15, 14), (18, 9)], YELLOW)
    c.rect(19, 21, 26, 27, GREEN, dither=DGREEN); c.pts([(20, 19), (25, 19)], WHITE)
@ic(DRED, ORANGE, 0.4)
def mod_crooked(c):   # кривой ствол буквой Г, пули врассыпную
    c.rect(3, 14, 12, 18, GREY, dither=DGREY); c.rect(10, 8, 13, 15, GREY); c.rect(5, 18, 8, 25, WOOD)
    for (x, y) in [(18, 3), (22, 9), (20, 15), (25, 19), (15, 2)]: c.rect(x, y, x + 1, y + 1, YELLOW)
@ic(DBROWN, ORANGE, 0.4)
def mod_roach_exodus(c):   # колонна тараканов с чемоданами
    for (x, y) in [(5, 6), (14, 12), (22, 19)]:
        c.ell(x, y, 4, 2.5, BROWN, dither=DBROWN); c.pts([(x - 4, y - 2), (x + 4, y - 3), (x - 3, y + 3), (x + 3, y + 3)], BLACK); c.rect(x - 1, y - 5, x + 2, y - 3, RED)
@ic(DRED, YELLOW, 0.4)
def mod_few_fat(c):   # одна жирная туша
    c.ell(14, 15, 12, 11, PINK, dither=(220, 0, 200)); c.eye(10, 11, 2, (0, 1)); c.eye(18, 12, 1.5, (0, 1)); c.ell(14, 19, 4, 2, BLACK)
    c.ell(5, 22, 3, 2, (230, 0, 200)); c.ell(23, 22, 3, 2, (230, 0, 200))

def crate_sprite():
    """Ящик гуманитарки 18×16: доски, красный крест, на боку подтёк."""
    c = Canvas(18, 16)
    c.rect(0, 1, 17, 15, WOOD, dither=DBROWN); c.rect(0, 1, 17, 2, (200, 130, 70))
    for y in (5, 10): c.rect(0, y, 17, y, DBROWN)
    c.rect(7, 3, 10, 13, RED); c.rect(3, 6, 14, 9, RED); c.rect(8, 4, 9, 12, WHITE) if False else None
    c.rect(2, 11, 3, 15, BROWN); c.px(15, 3, BLACK)
    return c.finish(DBROWN, YELLOW, lim=0.3)

def truck_frame(k):
    """Мусоровоз сбоку 92×52 (едет вправо): ржавый контейнер с мусором, кабина-морда с клыками и глазами,
    жижа капает, мухи, колёса крутятся (k = 0/1)."""
    import random
    rng = random.Random(5)
    c = Canvas(92, 52)
    RUST = (170, 90, 40); DRUST = (120, 60, 25)
    # контейнер
    c.rect(2, 10, 58, 38, GREEN, dither=DGREEN); c.rect(2, 10, 58, 12, LGREEN)
    for x in range(7, 56, 8): c.rect(x, 14, x + 2, 34, DGREEN)
    for _ in range(14):   # ржавчина пятнами
        x, y = rng.randint(4, 54), rng.randint(14, 36); c.ell(x, y, rng.uniform(1, 2.6), rng.uniform(1, 2), RUST, dither=DRUST)
    c.rect(2, 36, 58, 38, DGREY)
    # мусор горой сверху
    for (x, y, r, col) in [(10, 8, 5, BROWN), (20, 6, 6, (150, 90, 40)), (31, 7, 5, GREY), (42, 6, 6, (200, 60, 120)), (52, 8, 4, BROWN)]:
        c.ell(x, y, r, r * 0.7, col)
    c.line(24, 2, 30, 6, WHITE); c.ell(37, 3, 2, 2, YELLOW); c.pts([(16, 2), (47, 1), (45, 2)], LGREEN)
    c.eye(20, 6, 1.5, (1, 0))   # из мусора кто-то смотрит
    # кабина-морда
    poly(c, [(60, 16), (80, 16), (88, 26), (88, 40), (60, 40)], YELLOW, dither=ORANGE)
    poly(c, [(64, 19), (78, 19), (84, 27), (64, 27)], (150, 220, 255), dither=CYAN)
    c.eye(70, 23, 3, (2, 0)); c.eye(79, 24, 2, (1, 0))
    c.rect(72, 32, 89, 39, BLACK); c.teeth(72, 89, 32, WHITE, BLACK, 4)
    c.rect(86, 28, 89, 31, RED); c.rect(60, 30, 62, 39, DGREY)
    c.rect(56, 40, 90, 42, DGREY); c.rect(88, 41, 91, 44, GREY)   # бампер
    # жижа капает и лужица
    for x in (6, 18, 33, 47):
        c.rect(x, 38, x + 1, 41 + rng.randint(0, 3), (120, 160, 40))
    # колёса
    for wx in (14, 44, 76):
        c.ell(wx, 44, 7, 7, BLACK); c.ell(wx, 44, 4, 4, DGREY); c.ell(wx, 44, 2, 2, GREY)
        for a in range(4):
            import math
            ang = math.pi / 2 * a + (math.pi / 4 if k else 0.0)
            c.px(int(wx + math.cos(ang) * 5), int(44 + math.sin(ang) * 5), WHITE)
    # мухи
    for (x, y) in [(5, 4), (58, 3), (66, 10)]:
        fx = x + (1 if k else 0)
        c.px(fx, y, BLACK); c.px(fx - 1, y - 1, (190, 190, 230)); c.px(fx + 1, y - 1, (190, 190, 230))
    return c.finish(DGREEN, YELLOW, lim=0.35)

def render(n):
    f, sh, hi, lim = I[n]; c = new(); f(c); return fin(c, sh, hi, lim)

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    k = 3; cols = 9; rows = (len(I) + cols - 1) // cols
    prev = Image.new("RGBA", (cols * 34 * k, rows * (34 * k + 36) + 170), (45, 30, 20, 255))
    for i, n in enumerate(I):
        a = render(n); im = Image.fromarray(a); sm = Image.fromarray(small(a))
        if apply: im.save("assets/ui/%s.png" % n); sm.save("assets/ui/%s_s.png" % n)
        x = (i % cols) * 34 * k; y = (i // cols) * (34 * k + 36)
        b = im.resize((32 * k, 32 * k), Image.NEAREST); prev.paste(b, (x, y), b)
        s2 = sm.resize((32, 32), Image.NEAREST); prev.paste(s2, (x + 32, y + 32 * k + 2), s2)
    frames = [Image.fromarray(truck_frame(j)) for j in (0, 1)]
    w, h = frames[0].size; sheet = Image.new("RGBA", (w * 2, h))
    for j, fr in enumerate(frames): sheet.paste(fr, (j * w, 0))
    if apply: sheet.save("assets/sprites/garbage_truck.png"); Image.fromarray(crate_sprite()).save("assets/sprites/airdrop_crate.png")
    big = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST); prev.paste(big, (10, rows * (34 * k + 36) + 4), big)
    cr = Image.fromarray(crate_sprite()).resize((72, 64), Image.NEAREST); prev.paste(cr, (420, rows * (34 * k + 36) + 20), cr)
    prev.save("tools/_preview/wave_mods.png"); print("ok", sheet.size)
