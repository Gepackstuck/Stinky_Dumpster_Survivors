"""Королева крыс (элита): ходьба, призыв стаи (визжит, поднимает скипетр), таран (пригнулась), удар хвостом, ярость.
python3 tools/boss_rat_queen.py --apply -> assets/sprites/enemy_boss_rat_queen.png"""
from boss_kit import *
W, H, OX, OY = 104, 92, 6, 10
ROWS = ["walk", "summon", "charge", "tail", "enrage"]
FUR = (120, 120, 135); FUR2 = (90, 90, 105); BELLY = (190, 175, 175)


def queen(c, b=0, lean=0, m=3, tail=0, eyes="n", arm=0, rage=False, legs=(0, 0)):
    by = 60 - b
    # хвост: розовый шнурок с узлами
    tx = [(78, 70), (90, 66 - tail), (98, 54 - tail * 2), (96, 40 - tail * 2)]
    for (x0, y0), (x1, y1) in zip(tx, tx[1:]): c.line(x0, y0, x1, y1, PINK, 3)
    for x, y in tx[1:]: c.ell(x, y, 2, 2, (220, 90, 160))
    # ноги
    for xo, lift in ((30, legs[0]), (58, legs[1])):
        c.rect(xo + lean, 72 + lift, xo + 10 + lean, 80 + lift, FUR2); c.pts([(xo + 1 + lean, 80 + lift), (xo + 5 + lean, 80 + lift), (xo + 9 + lean, 80 + lift)], PINK)
    # туша в мантии из пакета
    c.ell(46 + lean, by, 30, 22, FUR, dither=FUR2)
    c.poly([(18 + lean, by - 6), (74 + lean, by - 6), (80 + lean, by + 20), (12 + lean, by + 20)], (40, 40, 50), dither=(25, 25, 35))   # мусорный пакет-мантия
    c.line(14 + lean, by + 4, 78 + lean, by + 4, (90, 90, 110))
    c.ell(46 + lean, by + 6, 14, 10, BELLY, dither=(160, 150, 150))
    # голова
    hx, hy = 46 + lean * 2, by - 26
    c.ell(hx - 14, hy - 12, 8, 8, FUR); c.ell(hx - 14, hy - 12, 5, 5, PINK)
    c.ell(hx + 14, hy - 12, 8, 8, FUR); c.ell(hx + 14, hy - 12, 5, 5, PINK)
    c.ell(hx, hy, 18, 14, FUR, dither=FUR2)
    c.poly([(hx - 8, hy + 6), (hx + 8, hy + 6), (hx, hy + 18)], FUR)   # морда
    c.ell(hx, hy + 17, 3, 2, PINK)
    for k in (-1, 1): c.line(hx + k * 4, hy + 14, hx + k * 18, hy + 12 + k, LGREY); c.line(hx + k * 4, hy + 16, hx + k * 17, hy + 18, LGREY)
    if rage or eyes == "angry":
        c.line(hx - 12, hy - 6, hx - 3, hy - 2, BLACK, 2); c.line(hx + 12, hy - 6, hx + 3, hy - 2, BLACK, 2)
        c.ell(hx - 7, hy + 1, 4, 4, RED); c.ell(hx + 7, hy, 5, 5, RED); c.px(hx - 7, hy + 1, YELLOW); c.px(hx + 7, hy, YELLOW)
    else:
        c.eye(hx - 7, hy + 1, 4, (1, 1), iris=RED); c.eye(hx + 7, hy, 5, (-1, 1), iris=RED)
    c.rect(hx - 4, hy + 8, hx + 4, hy + 8 + m, BLACK); c.rect(hx - 3, hy + 8, hx - 1, hy + 12 + m, YELLOW); c.rect(hx + 1, hy + 8, hx + 3, hy + 12 + m, YELLOW)
    # корона из пивных крышек
    for k, x in enumerate(range(hx - 12, hx + 13, 6)):
        c.ell(x, hy - 18 - (k % 2) * 3, 3, 3, GOLD); c.px(x, hy - 18 - (k % 2) * 3, RED)
    c.rect(hx - 13, hy - 16, hx + 13, hy - 14, (200, 160, 20))
    # скипетр: вантуз с костью
    ax, ay = hx + 26, hy + 14 - arm
    c.line(ax, ay, ax + 4, ay - 22, BROWN, 2); c.ell(ax + 5, ay - 25, 5, 3, RED); c.ell(ax - 1, ay + 1, 3, 3, FUR)


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    if st == "walk":
        queen(c, b=[0, 2, 0, 2][t], legs=[(0, 0), (-3, 0), (0, 0), (0, -3)][t], tail=[0, 2, 4, 2][t], m=[3, 4, 3, 4][t])
        c.pts([(4, 8 + t), (96, 10 - t)], BLACK)
    elif st == "summon":
        queen(c, b=-2 * min(t, 2), arm=[0, 8, 14, 10][t], m=[4, 8, 12, 10][t], eyes="angry", tail=t * 2)
        for k in range(t + 1):   # визг: дуги звука
            c.ring(70, 26, 8 + k * 6, YELLOW if k % 2 else WHITE)
        if t >= 2:
            for x in (6, 16, 84, 92): c.ell(x, 82, 4, 2, FUR); c.px(x - 2, 81, RED)   # крысы лезут из-под мантии
    elif st == "charge":
        queen(c, lean=[-2, -5, 4, 8][t], b=[0, -2, 2, 4][t], eyes="angry", m=[2, 4, 8, 10][t], tail=[0, -2, 6, 8][t], legs=[(0, 0), (2, 2), (-4, 0), (0, -4)][t])
        if t >= 2:
            for k in range(4): c.line(0, 40 + k * 10, 10 + t * 2, 40 + k * 10, WHITE if k % 2 else YELLOW)
    elif st == "tail":
        queen(c, tail=[0, 10, 20, 6][t], eyes="angry", m=[3, 5, 8, 4][t], b=[0, 1, 2, 0][t])
        if t == 2:
            c.ring(46, 60, 40, PINK); c.ring(46, 60, 34, (220, 90, 160))
    elif st == "enrage":
        queen(c, b=[0, 2, 0, 2][t], rage=True, m=[8, 10, 8, 12][t], tail=[2, 6, 2, 6][t], arm=[6, 10, 6, 10][t])
        for k, x in enumerate(range(16, 90, 7)):
            h = 4 + ((k + t) % 3) * 2; c.line(x, 82, x + ((k + t) % 2) - 1, 82 - h, ORANGE if k % 2 else RED)
    return cv.finish(PURPLE, YELLOW, lim=0.1)


def build():
    return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_rat_queen.png")
    if "--apply" in sys.argv: im.save("assets/sprites/enemy_boss_rat_queen.png")
    print(im.size)
