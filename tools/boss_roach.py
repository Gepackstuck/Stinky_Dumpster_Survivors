"""Таракан-качок (элита): ходьба, тройной рывок (пригнулся), кладка яиц, топот, ярость. --apply -> enemy_boss_roach_king.png"""
from boss_kit import *
W, H, OX, OY = 104, 88, 4, 8
ROWS = ["walk", "dash", "eggs", "stomp", "enrage"]
SH = (120, 70, 30); SH2 = (90, 50, 20); MUS = (150, 95, 45)


def roach(c, b=0, lean=0, legs=0, arms=0, rage=False, m=2, eggs=0, flat=0):
    cy = 52 - b + flat
    for k in range(3):   # лапки
        y = cy - 6 + k * 8; d = (legs + k) % 2 * 3
        c.line(22 + lean, y, 8 + lean - d, y + 6 + d, BLACK, 2); c.line(76 + lean, y, 90 + lean + d, y + 6 + d, BLACK, 2)
    c.ell(48 + lean, cy + 8, 26, 18 - flat, SH, dither=SH2)   # брюхо-панцирь
    c.line(48 + lean, cy - 8, 48 + lean, cy + 24 - flat, SH2, 2)
    c.ell(48 + lean, cy - 14, 22, 12, MUS, dither=SH)        # грудь-качок
    for x in (34, 62):   # бицепсы
        c.ell(x + lean, cy - 14 - arms, 9, 7, MUS, dither=SH); c.ell(x + lean, cy - 18 - arms, 4, 3, (190, 130, 70))
    c.ell(48 + lean, cy - 32, 12, 10, SH2)                   # голова
    c.line(42 + lean, cy - 40, 30 + lean, cy - 58, BLACK); c.line(54 + lean, cy - 40, 66 + lean, cy - 58, BLACK)   # усы
    if rage:
        c.ell(43 + lean, cy - 32, 4, 4, RED); c.ell(54 + lean, cy - 33, 5, 5, RED); c.px(43 + lean, cy - 32, YELLOW); c.px(54 + lean, cy - 33, YELLOW)
    else:
        c.eye(43 + lean, cy - 32, 4, (1, 1)); c.eye(54 + lean, cy - 33, 5, (-1, 1))
    c.rect(42 + lean, cy - 25, 54 + lean, cy - 25 + m, BLACK); c.teeth(42 + lean, 54 + lean, cy - 25, WHITE, BLACK, 2)
    c.rect(36 + lean, cy - 6, 60 + lean, cy - 3, RED); c.px(48 + lean, cy - 5, YELLOW)   # пояс чемпиона
    for k in range(eggs):
        c.ell(20 + k * 14, 84, 5, 4, (230, 220, 190), dither=(200, 190, 160)); c.px(20 + k * 14, 83, BROWN)


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    if st == "walk":
        roach(c, b=[0, 2, 0, 2][t], legs=t, arms=[0, 2, 0, 2][t])
    elif st == "dash":
        roach(c, lean=[-3, -6, 6, 10][t], b=[0, -2, 2, 4][t], legs=t * 2, m=[2, 4, 6, 6][t], rage=t >= 2)
        if t >= 2:
            for k in range(4): c.line(0, 30 + k * 10, 14, 30 + k * 10, WHITE if k % 2 else YELLOW)
    elif st == "eggs":
        roach(c, b=[0, -2, 0, -1][t], arms=t * 2, eggs=t, m=3)
    elif st == "stomp":
        roach(c, b=[0, -8, -12, 4][t], flat=[0, 0, 0, 5][t], arms=[0, 6, 8, 0][t], m=[2, 4, 6, 8][t])
        if t == 3:
            c.ring(48, 76, 40, YELLOW); c.line(4, 84, 92, 84, WHITE)
    elif st == "enrage":
        roach(c, b=[0, 2, 0, 2][t], rage=True, arms=[4, 8, 4, 8][t], m=[6, 8, 6, 9][t], legs=t)
        for k, x in enumerate(range(12, 92, 7)):
            h = 4 + ((k + t) % 3) * 2; c.line(x, 86, x + ((k + t) % 2) - 1, 86 - h, ORANGE if k % 2 else RED)
    return cv.finish(PURPLE, YELLOW, lim=0.1)


def build():
    return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_roach.png")
    if "--apply" in sys.argv: im.save("assets/sprites/enemy_boss_roach_king.png")
    print(im.size)
