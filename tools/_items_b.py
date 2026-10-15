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
def hot_dog(c):   # хот-дог
    poly(c, [(1, 10), (26, 10), (26, 15), (1, 15)], (230, 70, 50)); c.ell(1.5, 12.5, 2.5, 2.5, (230, 70, 50)); c.ell(26, 12.5, 2.5, 2.5, (230, 70, 50)); c.rect(3, 11, 25, 11, (255, 135, 115))
    poly(c, [(3, 6), (25, 6), (27, 12), (1, 12)], (240, 185, 100), dither=(205, 140, 70)); c.ell(14, 7, 12, 3.5, (240, 185, 100)); poly(c, [(2, 15), (26, 15), (24, 22), (4, 22)], (240, 185, 100), dither=(205, 140, 70))
    c.pts([(4, 11), (6, 9), (8, 11), (10, 9), (12, 11), (14, 9), (16, 11), (18, 9), (20, 11), (22, 9), (24, 11)], YELLOW); c.pts([(5, 13), (8, 12), (11, 13), (14, 12), (17, 13), (20, 12), (23, 13)], YELLOW)
    c.pts([(7, 7), (17, 6), (22, 20), (9, 19)], GREEN); c.pts([(6, 4), (10, 3)], WHITE)
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
def scarf(c):   # шарф
    poly(c, [(2, 5), (14, 2), (26, 5), (26, 12), (14, 15), (2, 12)], PINK, dither=(200, 0, 190)); c.rect(2, 8, 26, 9, WHITE); poly(c, [(15, 12), (24, 14), (26, 25), (17, 26)], PINK, dither=(200, 0, 190)); c.rect(16, 17, 25, 18, WHITE)
    for x in range(17, 27, 2): c.rect(x, 26, x, 27, WHITE)
    c.pts([(6, 6), (10, 12), (19, 6)], YELLOW); c.line(4, 4, 12, 3, WHITE)
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
