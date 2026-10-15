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
def bottle_cap(c):   # крышка с зубчиками
    pts = []
    for i in range(48):
        a = i * math.pi * 2 / 48; r = 13 if i % 2 == 0 else 11
        pts.append((14 + math.cos(a) * r, 14 + math.sin(a) * r))
    poly(c, pts, YELLOW, dither=ORANGE); c.ell(14, 14, 8.5, 8.5, RED); c.ell(14, 14, 8, 8, (210, 20, 40)); ringc(c, 14, 14, 7, YELLOW, 1)
    tri_font(c, 8, 10, "x2", WHITE) if False else None
    poly(c, [(9, 15), (14, 8), (19, 15), (16, 15), (16, 19), (12, 19), (12, 15)], WHITE); c.pts([(5, 6), (6, 5)], WHITE)
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
