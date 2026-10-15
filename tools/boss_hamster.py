"""Мега-хомяк: ходьба, плевок семечками, прыжок-раздавливание, перекат шаром, ярость."""
from boss_kit import *
W, H, OX, OY = 124, 110, 10, 24
ROWS = ["walk", "spit", "slam", "roll", "enrage"]
FUR = BROWN; FUR2 = (150, 90, 40)


def seed(c, x, y, ang=0):
    c.ell(x, y, 3, 2, BLACK); c.px(x, y, WHITE)


def body(c, b=0, sx=0, sy=0, cheek=(15, 12), m=4, eyes="n", dy=0, legs=(0, 0), tongue=True, blush=False, rage=False, steam=0, wob=0):
    """Базовый хомяк. sx/sy — раздувание тела, dy — смещение вверх(-)/вниз(+), m — раскрытие пасти."""
    bottom = 76 + dy
    ry = 28 + sy; rx = 40 + sx
    cy = bottom - ry - b          # низ тела фиксирован, bob сдвигает вверх
    top = cy - ry
    hy = top + 10                  # центр головы
    # ноги
    for xo, lift in ((26, legs[0]), (62, legs[1])):
        c.rect(xo + wob, 70 + dy + lift, xo + 14 + wob, 82 + dy + lift, FUR)
        for x in (xo + 1, xo + 5, xo + 9): c.line(x + wob, 78 + dy + lift, x + wob, 83 + dy + lift, BLACK)
    # уши
    ey = hy - 16
    for ex in (14 - sx // 3, 88 + sx // 3):
        c.ell(ex, ey, 11, 11, FUR); c.ell(ex, ey, 7, 7, PINK, dither=(255, 120, 245))
        if rage: c.ell(ex, ey, 7, 7, RED, dither=PINK)
    # туша
    c.ell(52 + wob, cy, rx, ry, FUR, dither=FUR2)
    c.ell(52 + wob, bottom - 22 - b, 26 + sx * 0.6, 20 + sy * 0.7, YELLOW, dither=(255, 230, 150))
    c.ell(52 + wob, hy, 38 + sx * 0.8, 24 + sy * 0.4, FUR, dither=FUR2)
    # щёки-запасы
    cw, ch = cheek
    c.ell(18 - (cw - 15), hy + 8, cw, ch, FUR, dither=ORANGE); c.ell(86 + (cw - 15), hy + 8, cw, ch, FUR, dither=ORANGE)
    if blush: c.ell(18 - (cw - 15), hy + 8, cw - 3, ch - 3, (255, 90, 110), dither=FUR); c.ell(86 + (cw - 15), hy + 8, cw - 3, ch - 3, (255, 90, 110), dither=FUR)
    for (x, y) in ((12, 44), (20, 46), (84, 46), (92, 44), (16, 50), (88, 50)):
        sxo = -(cw - 15) if x < 52 else (cw - 15)
        seed(c, x + sxo, hy + (y - 30), 0)
    # брови и глаза
    if eyes == "angry" or rage:
        c.line(30, hy - 10, 44, hy - 2, BLACK, 3); c.line(74, hy - 10, 60, hy - 2, BLACK, 3)
        if rage:
            c.ell(36, hy + 1, 8, 8, RED, dither=(255, 120, 0)); c.ell(68, hy - 1, 9, 9, RED, dither=(255, 120, 0)); c.rect(35, hy - 3, 37, hy + 5, YELLOW); c.rect(67, hy - 5, 69, hy + 5, YELLOW)
            c.pts([(34, hy - 6), (37, hy - 7), (66, hy - 8), (70, hy - 7)], RED)
        else: c.eye(36, hy + 1, 8, (2, 2)); c.eye(68, hy - 1, 9, (-2, 2))
    elif eyes == "squint":
        c.line(30, hy - 8, 44, hy - 2, BLACK, 3); c.line(74, hy - 8, 60, hy - 2, BLACK, 3)
        c.rect(30, hy, 42, hy + 2, WHITE); c.rect(62, hy - 2, 76, hy, WHITE); c.rect(34, hy, 36, hy + 2, BLACK); c.rect(70, hy - 2, 72, hy, BLACK)
    elif eyes == "wide":
        c.line(30, hy - 12, 44, hy - 6, BLACK, 3); c.line(74, hy - 12, 60, hy - 6, BLACK, 3)
        c.eye(36, hy + 1, 10, (0, 0)); c.eye(68, hy - 1, 11, (0, 0))
    else:
        c.line(30, hy - 10, 44, hy - 2, BLACK, 3); c.line(74, hy - 10, 60, hy - 2, BLACK, 3)
        c.eye(36, hy + 1, 8, (2, 2)); c.eye(68, hy - 1, 9, (-2, 2))
    c.ell(52, hy + 10, 5, 3, PINK); c.px(51, hy + 9, WHITE)
    # пасть
    my = hy + 16
    c.rect(36, my, 68, my + m, BLACK)
    c.rect(44, my, 50, my + 10 + m // 2, WHITE); c.rect(54, my, 60, my + 10 + m // 2, WHITE); c.line(52, my, 52, my + 10 + m // 2, BLACK)
    for x in range(37, 68, 3):
        if not 44 <= x <= 60: c.px(x, my + m, WHITE); c.px(x, my + 1, WHITE)
    if rage and m > 3:
        for x in (38, 41, 64, 67): c.line(x, my + 1, x, my + 5, WHITE)
    if tongue and m >= 4: c.ell(52, my + m, 8, 3, PINK)
    c.line(66, my + 6, 66, my + 16 + m // 3, GREEN, 2); c.line(40, my + 8, 40, my + 14, GREEN)
    # ошейник с шипами, медальон
    cy2 = bottom - 12 - b
    c.rect(22, cy2, 82, cy2 + 3, GREEN)
    for x in range(24, 82, 6): c.line(x, cy2, x, cy2 - 3, GOLD); c.px(x, cy2 - 4, WHITE)
    c.ell(52, cy2 + 8, 5, 5, GOLD); c.px(51, cy2 + 7, WHITE); c.px(53, cy2 + 9, RED)
    c.line(30, hy - 10, 26, hy - 4, BLACK); c.line(28, hy - 12, 24, hy - 6, BLACK)   # шрамы
    c.line(52, hy - 24, 49, hy - 30 - (b % 2) * 2, BLACK); c.line(55, hy - 24, 58, hy - 29, BLACK)   # вихор
    if steam:
        for k, ex in enumerate((10, 94)):
            for j in range(3): c.ell(ex + (j - 1) * 2 + (k * 2 - 1) * ((steam + j) % 3), ey - 12 - j * 6 - steam * 2, 3 + j, 2 + j, (230, 230, 240), dither=(180, 180, 200))
    return hy, bottom


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    # мухи и вонь вокруг — общая «мерзость»
    flies = [(10, 6), (90, 6), (96, 24), (6, 28)]
    if st == "walk":
        b = [0, 2, 0, 2][t]; legs = [(0, 0), (-4, 0), (0, 0), (0, -4)][t]; wob = [0, 1, 0, -1][t]
        body(c, b=b, legs=legs, wob=wob, m=[4, 5, 4, 5][t])
        # шлейф вони
        for k in range(3): c.pts([(30 + k * 20, -2 - (t + k) % 3)], GREEN)
    elif st == "spit":
        cw = [(15, 12), (18, 14), (21, 16), (13, 11)][t]; m = [3, 3, 4, 16][t]
        body(c, b=0, sy=[0, -1, -2, 2][t], sx=[0, 1, 2, -1][t], cheek=cw, m=m, eyes=["n", "squint", "squint", "wide"][t], blush=t in (1, 2), tongue=(t == 3))
        if t == 3:
            hy = 24 + 10 - 0
            for k, (dx, dyy) in enumerate(((-34, 14), (-20, 26), (0, 32), (20, 26), (34, 14))):
                seed(c, 52 + dx, 56 + dyy); c.line(52 + dx // 2, 52 + dyy // 2, 52 + dx * 0.8, 52 + dyy * 0.9, WHITE)
            c.ring(52, 54, 16, YELLOW)
        if t in (1, 2):
            for k in range(t + 1): c.pts([(8 - k * 2, 40 - k * 3), (96 + k * 2, 40 - k * 3)], YELLOW)   # дрожь
    elif st == "slam":
        if t == 0:   # присел
            body(c, sx=8, sy=-9, m=3, eyes="angry", legs=(0, 0)); c.rect(14, 82, 94, 83, BLACK) if False else None
        elif t == 1:  # взлёт, вытянулся
            body(c, sx=-5, sy=6, dy=-14, m=8, eyes="wide", legs=(-6, -6)); [c.line(30 + i * 18, 88, 30 + i * 18, 94 - i % 2 * 2, LGREY) for i in range(4)]
        elif t == 2:  # апекс, пузом вниз
            c.ell(52, 90, 30, 4, (30, 20, 10), dither=BLACK)    # тень на земле
            body(c, sx=2, sy=2, dy=-22, m=14, eyes="wide", legs=(-8, -8)); c.line(46, 26, 46, 36, LGREY); c.line(58, 26, 58, 36, LGREY)
        else:  # удар: сплющился + пыль + ударная волна
            body(c, sx=14, sy=-12, dy=2, m=10, eyes="angry", legs=(0, 0), tongue=True)
            for k, (dx, dyy, rr) in enumerate(((-52, 76, 8), (-40, 70, 6), (-60, 66, 5), (106, 76, 8), (94, 70, 6), (114, 66, 5))): c.ell(dx + 52 if dx < 0 else dx, dyy, rr, rr - 1, (190, 190, 200), dither=WHITE)
            c.line(0, 84, 104, 84, YELLOW); c.line(4, 82, 100, 82, WHITE)
            for x, y in ((8, 78), (20, 80), (84, 80), (96, 78)): c.line(x, y, x + (-4 if x < 50 else 4), y - 6, YELLOW)
            c.pts([(12, 18), (92, 18), (52, 2)], YELLOW)
    elif st == "roll":
        a = t * 90
        c.ell(52, 52, 34, 34, FUR, dither=FUR2)
        for k in range(4):   # вращающиеся полосы
            p1 = rot((52, 52 - 4), (52, 52), a + k * 90); p2 = rot((52, 52 - 33), (52, 52), a + k * 90)
            c.line(p1[0], p1[1], p2[0], p2[1], (250, 220, 150), 3)
        for k in range(2):   # торчащие уши-лопасти
            e = rot((52, 52 - 38), (52, 52), a + k * 180 + 20); c.ell(e[0], e[1], 8, 8, FUR); c.ell(e[0], e[1], 5, 5, PINK)
        c.ell(52, 52, 20, 20, YELLOW, dither=(255, 230, 150))
        # лицо в центре «шара» не крутится
        c.line(40, 42, 50, 48, BLACK, 3); c.line(64, 42, 54, 48, BLACK, 3)
        c.eye(44, 50, 6, (2, 1)); c.eye(60, 50, 6, (-2, 1))
        c.rect(44, 62, 60, 66, BLACK)
        for x in range(45, 60, 3): c.px(x, 62, WHITE); c.px(x, 66, WHITE)
        c.ell(52, 56, 3, 2, PINK)
        for k in range(5): c.line(0 + (t * 3 + k * 2) % 5, 34 + k * 9, 14 + (t + k) % 4 * 2, 34 + k * 9, YELLOW if k % 2 else WHITE)   # полосы скорости
        for k, (x, y) in enumerate(((-4, 92), (6, 96), (16, 90))): c.ell(x + (t * 4) % 8, y, 5, 3, (190, 190, 200), dither=WHITE)   # пыль
        c.pts([(100, 30 + t * 3), (104, 50 - t * 2)], YELLOW)
    elif st == "enrage":
        b = [0, 2, 0, 2][t]; legs = [(0, 0), (-5, 0), (0, 0), (0, -5)][t]
        body(c, b=b, legs=legs, wob=[0, 1, 0, -1][t], m=[9, 11, 9, 12][t], eyes="angry", rage=True, steam=t)
        # аура-огонь у лап
        for k, x in enumerate(range(16, 94, 6)):
            h = 4 + ((k + t) % 3) * 2; c.line(x, 84, x + ((k + t) % 2) - 1, 84 - h, ORANGE if k % 2 else RED)
        c.pts([(30, 36), (34, 34), (72, 32), (76, 34)], PINK)    # вздутые вены
    return cv.finish(PURPLE, YELLOW, lim=0.1)


def build():
    return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_hamster.png"); print(im.size)
