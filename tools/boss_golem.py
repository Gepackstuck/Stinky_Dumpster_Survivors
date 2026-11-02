"""Мусорный голем (финал): ходьба, бросок мешка, удар кулаками в землю, зов баков, ярость. --apply -> enemy_boss_trash_golem.png"""
from boss_kit import *
W, H, OX, OY = 116, 104, 6, 6
ROWS = ["walk", "throw", "pound", "summon", "enrage"]
BAG = (40, 40, 50); BAG2 = (25, 25, 35); BAGL = (80, 80, 100)


def golem(c, b=0, arm_l=0, arm_r=0, rage=False, m=3, lean=0):
    by = 92 - b
    for xo in (30, 64):   # ноги-вёдра
        c.rect(xo + lean, by - 18, xo + 16 + lean, by, (150, 150, 160), dither=GREY); c.rect(xo + lean, by - 18, xo + 16 + lean, by - 16, DGREY)
    c.ell(52 + lean, by - 40, 30, 26, BAG, dither=BAG2)   # туловище - мешки
    for (x, y) in [(40, by - 52), (64, by - 46), (50, by - 30)]: c.ell(x + lean, y, 9, 7, BAGL, dither=BAG); c.line(x - 3 + lean, y - 6, x + 3 + lean, y - 8, YELLOW)
    c.ell(30 + lean, by - 34, 4, 3, (170, 90, 40)); c.ell(70 + lean, by - 28, 3, 2, (200, 60, 120)); c.line(56 + lean, by - 20, 66 + lean, by - 14, WHITE)
    for side, a in ((-1, arm_l), (1, arm_r)):   # руки-мешки
        x0 = 52 + side * 30 + lean; y0 = by - 52
        hx, hy = x0 + side * 10, y0 + 18 - a
        c.line(x0, y0, hx, hy, BAG, 6); c.ell(hx, hy, 9, 8, BAGL, dither=BAG)
    c.ell(52 + lean, by - 70, 14, 12, (60, 120, 60), dither=DGREEN)   # голова - бак
    c.rect(40 + lean, by - 80, 64 + lean, by - 77, (40, 160, 40))
    if rage:
        c.ell(46 + lean, by - 70, 4, 4, RED); c.ell(58 + lean, by - 71, 5, 5, RED); c.px(46 + lean, by - 70, YELLOW)
    else:
        c.eye(46 + lean, by - 70, 4, (1, 1)); c.eye(58 + lean, by - 71, 5, (-1, 1))
    c.rect(44 + lean, by - 63, 60 + lean, by - 63 + m, BLACK); c.teeth(44 + lean, 60 + lean, by - 63, WHITE, BLACK, 2)
    for (x, y) in [(10, 14), (100, 18), (92, 6)]: c.px(x, y, BLACK); c.px(x - 1, y - 1, LGREY); c.px(x + 1, y - 1, LGREY)


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    if st == "walk":
        golem(c, b=[0, 2, 0, 2][t], arm_l=[0, 3, 0, -3][t], arm_r=[0, -3, 0, 3][t])
    elif st == "throw":
        golem(c, arm_r=[0, 18, 28, -6][t], m=[3, 4, 6, 8][t], lean=[0, -2, -3, 3][t])
        if t == 3: c.ell(100, 20, 7, 6, BAGL, dither=BAG)
    elif st == "pound":
        golem(c, arm_l=[0, 22, 28, -14][t], arm_r=[0, 22, 28, -14][t], b=[0, -3, -5, 3][t], m=[3, 5, 8, 10][t])
        if t == 3:
            c.ring(52, 96, 46, YELLOW); c.line(0, 98, 104, 98, WHITE)
    elif st == "summon":
        golem(c, arm_l=[0, 10, 20, 20][t], arm_r=[0, 10, 20, 20][t], m=[3, 8, 12, 10][t])
        for k in range(t + 1): c.ring(52, 22, 6 + k * 5, GREEN if k % 2 else YELLOW)
    elif st == "enrage":
        golem(c, b=[0, 2, 0, 2][t], rage=True, arm_l=[4, 10, 4, 10][t], arm_r=[10, 4, 10, 4][t], m=[6, 9, 6, 10][t])
        for k, x in enumerate(range(14, 100, 8)):
            h = 4 + ((k + t) % 3) * 2; c.line(x, 98, x + ((k + t) % 2) - 1, 98 - h, ORANGE if k % 2 else RED)
    return cv.finish(PURPLE, YELLOW, lim=0.1)


def build():
    return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_golem.png")
    if "--apply" in sys.argv: im.save("assets/sprites/enemy_boss_trash_golem.png")
    print(im.size)
