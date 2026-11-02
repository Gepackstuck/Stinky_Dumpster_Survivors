"""Голубиный папа (финал): ходьба вразвалку, пике, бомбёжка помётом, веер перьев, ярость. --apply -> enemy_boss_pigeon_papa.png"""
from boss_kit import *
W, H, OX, OY = 112, 96, 6, 8
ROWS = ["walk", "dive", "bomb", "feathers", "enrage"]
GR = (130, 135, 150); GR2 = (100, 105, 120); NECK = (90, 160, 120); NECK2 = (130, 70, 170)


def pigeon(c, b=0, wing=0, lean=0, rage=False, m=0, poop=False):
    cy = 54 - b
    c.ell(46 + lean, cy + 8, 28, 22, GR, dither=GR2)   # туша
    for side in (-1, 1):   # крылья
        wx = 46 + side * 26 + lean; wy = cy - wing
        c.poly([(wx, wy), (wx + side * 24, wy - 10 - wing), (wx + side * 20, wy + 14), (wx, wy + 18)], GR2, dither=GR)
        for k in range(3): c.line(wx + side * (8 + k * 5), wy + 2 - k, wx + side * (10 + k * 5), wy + 14 - k * 2, WHITE)
    c.ell(46 + lean, cy - 14, 15, 13, NECK, dither=NECK2)   # переливчатая шея
    c.ell(48 + lean, cy - 30, 12, 10, GR)                     # голова
    c.poly([(58 + lean, cy - 32), (70 + lean, cy - 29), (58 + lean, cy - 26)], ORANGE)   # клюв
    c.rect(58 + lean, cy - 29, 66 + lean, cy - 29 + m, BLACK) if m else None
    if rage:
        c.ell(46 + lean, cy - 32, 4, 4, RED); c.px(46 + lean, cy - 32, YELLOW); c.ell(53 + lean, cy - 33, 2, 2, RED)
    else:
        c.eye(46 + lean, cy - 32, 4, (2, 0), iris=ORANGE); c.eye(53 + lean, cy - 33, 2, (1, 0), iris=ORANGE)
    c.rect(38 + lean, cy - 44, 56 + lean, cy - 40, BLACK); c.rect(41 + lean, cy - 50, 53 + lean, cy - 44, BLACK)   # кепка-котелок папы
    for x in (36, 54):   # лапы
        c.line(x + lean, cy + 28, x + lean, cy + 36, (220, 100, 120), 2); c.line(x - 4 + lean, cy + 36, x + 4 + lean, cy + 36, (220, 100, 120))
    if poop:
        c.ell(46 + lean, cy + 40, 4, 3, WHITE); c.ell(46 + lean, cy + 46, 3, 2, (230, 230, 220))


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    if st == "walk":
        pigeon(c, b=[0, 2, 0, 2][t], wing=[0, 2, 0, 2][t], lean=[0, 2, 0, -2][t])
    elif st == "dive":
        pigeon(c, b=[0, 6, 10, 2][t], wing=[0, 12, 16, -4][t], lean=[0, -2, 4, 8][t], m=[0, 2, 3, 3][t], rage=t >= 2)
        if t >= 2:
            for k in range(4): c.line(0, 34 + k * 10, 12, 34 + k * 10, WHITE)
    elif st == "bomb":
        pigeon(c, b=[4, 8, 8, 6][t], wing=[8, 14, 8, 14][t], poop=t % 2 == 1)
    elif st == "feathers":
        pigeon(c, wing=[0, 10, 18, 6][t], m=[0, 2, 4, 2][t])
        if t >= 2:
            for k in range(5): c.line(84, 40, 98 + k * 2, 20 + k * 10, WHITE)
    elif st == "enrage":
        pigeon(c, b=[0, 2, 0, 2][t], rage=True, wing=[4, 10, 4, 10][t], m=[2, 3, 2, 3][t])
        for k, x in enumerate(range(14, 96, 8)):
            h = 4 + ((k + t) % 3) * 2; c.line(x, 90, x + ((k + t) % 2) - 1, 90 - h, ORANGE if k % 2 else RED)
    return cv.finish(PURPLE, YELLOW, lim=0.1)


def build():
    return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_pigeon.png")
    if "--apply" in sys.argv: im.save("assets/sprites/enemy_boss_pigeon_papa.png")
    print(im.size)
