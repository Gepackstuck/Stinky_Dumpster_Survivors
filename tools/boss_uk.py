"""Н25 Управляющая компания (финал): будка-окошко на курьих ножках, внутри тётка в очках со штампом.
Ряды: ходьба, штамп (квитанции-мины), телефон (вызов аварийки), счета веером, ОБЕД (шторка). --apply -> enemy_boss_uk.png, proj_bill.png"""
from boss_kit import *
W, H, OX, OY = 100, 110, 6, 6
ROWS = ["walk", "stamp", "phone", "bills", "lunch"]
BOOTH = (90, 120, 170); BOOTH2 = (60, 85, 130); GLASS = (170, 220, 240); HAIR = (180, 60, 40); PAPER = (240, 235, 210); LEG = (240, 200, 60)


def booth(c, b=0, step=0, shutter=0, arm=0, phone=False, stamp=0, rage=False):
    cy = 20 - b
    for side, s in ((-1, step), (1, -step)):                       # курьи ножки
        x = 44 + side * 14
        c.line(x, cy + 62, x + s, cy + 78, LEG, 3); c.line(x + s - 4, cy + 80, x + s + 4, cy + 80, LEG, 2)
    c.rect(16, cy + 6, 74, cy + 64, BOOTH, dither=BOOTH2)              # будка
    c.rect(14, cy + 2, 76, cy + 8, BOOTH2); c.rect(24, cy - 6, 66, cy + 2, WHITE)   # вывеска
    for k, x in enumerate(range(28, 64, 6)): c.rect(x, cy - 4, x + 3, cy, RED if k % 2 else BLUE)   # «УК»-буквы-кракозябры
    c.rect(24, cy + 14, 66, cy + 44, GLASS, dither=WHITE)              # окошко
    # тётка внутри
    c.ell(45, cy + 30, 11, 10, SKIN); c.ell(45, cy + 20, 12, 6, HAIR)
    if rage:
        c.ell(40, cy + 29, 3, 3, RED); c.ell(50, cy + 29, 3, 3, RED)
    else:
        c.ring(40, cy + 29, 3, BLACK); c.ring(50, cy + 29, 3, BLACK); c.px(40, cy + 29, BLACK); c.px(50, cy + 29, BLACK)   # очки
    c.line(42, cy + 36, 48, 36 + cy, (150, 40, 40))
    c.rect(24, cy + 44, 66, cy + 47, (120, 90, 60))                    # прилавок
    if phone:
        c.rect(56, cy + 24, 60, cy + 34, BLACK); c.line(56, cy + 24, 52, cy + 28, BLACK)
    if stamp:
        c.rect(30 - arm, cy + 40 - stamp, 36 - arm, cy + 44 - stamp, RED); c.rect(32 - arm, cy + 34 - stamp, 34 - arm, cy + 40 - stamp, BROWN)
    if shutter:                                                         # шторка «ОБЕД»
        c.rect(24, cy + 14, 66, cy + 14 + shutter, (200, 200, 205), dither=GREY)
        for y in range(cy + 16, cy + 14 + shutter, 4): c.line(24, y, 66, y, DGREY)
        if shutter >= 30:
            c.rect(32, cy + 24, 58, cy + 34, WHITE); c.pts([(35, 28), (36, 29), (40, 28), (44, 29), (48, 28), (52, 29), (55, 28)], RED)
    c.rect(70, cy + 50, 74, cy + 62, PAPER); c.line(70, cy + 54, 74, cy + 54, DGREY)   # стопка квитанций сбоку


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    if st == "walk":
        booth(c, b=[0, 2, 0, 2][t], step=[-4, 0, 4, 0][t])
    elif st == "stamp":
        booth(c, b=[0, 0, 2, 0][t], stamp=[8, 4, 0, 4][t], arm=[0, 2, 4, 2][t])
    elif st == "phone":
        booth(c, b=[0, 1, 0, 1][t], phone=True)
        if t % 2: c.pts([(66, 10), (70, 8), (74, 12)], YELLOW)
    elif st == "bills":
        booth(c, b=[0, 2, 4, 2][t], rage=t >= 2)
        for k in range(t + 1): c.rect(76 + k * 4, 30 - k * 6, 82 + k * 4, 36 - k * 6, PAPER)
    else:
        booth(c, shutter=[10, 20, 30, 30][t])
    return cv.finish(BOOTH2, WHITE)


def bill():
    c = Canvas(10, 8)
    c.rect(1, 1, 8, 6, PAPER); c.rect(1, 1, 8, 2, RED); c.pts([(3, 4), (5, 4), (7, 4), (2, 5)], DGREY)
    return c.finish(BLACK, WHITE)


def build():
    return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_uk.png")
    if "--apply" in sys.argv:
        im.save("assets/sprites/enemy_boss_uk.png")
        Image.fromarray(bill()).save("assets/sprites/proj_bill.png")
    print(im.size)
