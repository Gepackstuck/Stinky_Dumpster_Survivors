"""Синий кит (финальный босс): ползёт по мусору, веер слёз, прыжок-плюх, фонтан, ярость.
python3 tools/boss_whale.py --apply -> assets/sprites/enemy_boss_blue_whale.png"""
from boss_kit import *
W, H, OX, OY = 128, 96, 6, 12
ROWS = ["walk", "tears", "flop", "spout", "enrage"]
SKIN = (40, 90, 200); SKIN2 = (25, 60, 150); BELLY = (170, 200, 240)


def whale(c, b=0, dy=0, sx=0, sy=0, cry=0, m=2, rage=False, tailup=0, spout=0):
    cx, cy = 54, 54 + dy - b
    # хвост
    c.poly([(8, cy - 2 - tailup), (22, cy - 6), (22, cy + 6), (8, cy + 10 - tailup)], SKIN, dither=SKIN2)
    c.ell(6, cy - 4 - tailup, 6, 4, SKIN); c.ell(6, cy + 12 - tailup, 6, 4, SKIN)
    # туша
    c.ell(cx + 6, cy, 46 + sx, 26 + sy, SKIN, dither=SKIN2)
    c.ell(cx + 10, cy + 12 + sy // 2, 34 + sx, 12, BELLY, dither=(140, 170, 220))
    for x in range(cx - 14, cx + 36, 6): c.line(x, cy + 6 + sy // 2, x + 2, cy + 20 + sy // 2, (120, 150, 200))   # складки брюха
    # мусор, налипший на спину
    for (x, y, r, col) in [(cx - 6, cy - 24, 4, BROWN), (cx + 8, cy - 26, 3, GREY), (cx + 20, cy - 23, 4, (200, 60, 120))]: c.ell(x, y - sy, r, r * 0.7, col)
    c.line(cx - 20, cy - 18 - sy, cx - 14, cy - 22 - sy, WHITE)
    # глаз огромный и рыдающий + маленький
    ex, ey = cx + 34, cy - 6
    if rage:
        c.line(ex - 8, ey - 10, ex + 6, ey - 6, BLACK, 3); c.ell(ex, ey, 7, 7, RED); c.px(ex, ey, YELLOW); c.ell(ex - 16, ey - 2, 3, 3, RED)
    else:
        c.eye(ex, ey, 7, (2, 1)); c.eye(ex - 16, ey - 2, 3, (1, 1))
    for k in range(cry):   # слёзы ручьём
        c.line(ex + 2, ey + 6, ex + 4 - k, ey + 14 + k * 4, CYAN, 2)
    # пасть
    c.rect(cx + 28, cy + 6, cx + 50, cy + 6 + m, BLACK); c.teeth(cx + 29, cx + 50, cy + 6, WHITE, BLACK, 2)
    # дыхало
    c.ell(cx + 6, cy - 26 - sy, 3, 1.5, BLACK)
    for k in range(spout):
        c.ell(cx + 6 + (k % 2) * 3 - 1, cy - 32 - sy - k * 6, 3 + k, 2 + k // 2, CYAN, dither=WHITE)


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    if st == "walk":
        whale(c, b=[0, 2, 0, 2][t], cry=1 + t % 2, tailup=[0, 3, 0, -3][t])
        c.ell(60, 84, 40, 4, (30, 20, 10), dither=BLACK)
    elif st == "tears":
        whale(c, cry=2 + t, m=[2, 4, 8, 6][t], sy=[0, 1, 2, 1][t])
        if t >= 2:
            for k in range(5): c.line(100, 50, 112 + k * 2, 30 + k * 10, CYAN)
    elif st == "flop":
        if t == 0: whale(c, sy=-4, sx=6, cry=1)
        elif t == 1: whale(c, dy=-14, sy=4, cry=2, tailup=6); c.ell(60, 86, 34, 3, (30, 20, 10), dither=BLACK)
        elif t == 2: whale(c, dy=-24, sy=2, cry=3, tailup=8); c.ell(60, 86, 26, 2, (30, 20, 10), dither=BLACK)
        else:
            whale(c, dy=4, sx=10, sy=-8, cry=1, m=6)
            for x, y in ((6, 80), (18, 84), (100, 84), (112, 80)): c.ell(x, y, 5, 3, CYAN, dither=WHITE)
            c.line(0, 86, 120, 86, CYAN)
    elif st == "spout":
        whale(c, spout=[1, 3, 5, 4][t], cry=1, sy=[0, -2, -3, -1][t])
    elif st == "enrage":
        whale(c, b=[0, 2, 0, 2][t], rage=True, cry=4, m=[6, 8, 6, 9][t], tailup=[4, -4, 4, -4][t])
        for k, x in enumerate(range(14, 110, 8)):
            h = 4 + ((k + t) % 3) * 2; c.line(x, 86, x + ((k + t) % 2) - 1, 86 - h, ORANGE if k % 2 else RED)
    return cv.finish(PURPLE, YELLOW, lim=0.1)


def build():
    return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_whale.png")
    if "--apply" in sys.argv: im.save("assets/sprites/enemy_boss_blue_whale.png")
    print(im.size)
