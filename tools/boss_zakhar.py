"""Захар из Морковска: ходьба, бросок морковки, пук, пинок, ярость, веерный бросок."""
from boss_kit import *
W, H, OX, OY = 124, 156, 10, 32
ROWS = ["walk", "throw", "fart", "kick", "enrage", "fan"]
FUR = WHITE; FUR2 = (200, 200, 210)


def carrot(c, hand, ang, glow=False, big=1.0):
    """Морковь-дубина: хват у руки, острие вниз, ботва наверху; ang=0 — стоймя."""
    a = math.radians(ang); dx, dy = math.sin(a), -math.cos(a)
    def at(s, w): # s вдоль оси от руки, w поперёк
        return (hand[0] + dx * s - dy * w, hand[1] + dy * s + dx * w)
    top = 36 * big; tip = -26 * big
    pts = [at(tip, 0), at(tip + 10, 3), at(top, 8), at(top, -8), at(tip + 10, -3)]
    c.poly(pts, ORANGE, dither=(255, 170, 40) if not glow else YELLOW)
    for s in range(int(tip + 8), int(top), 9):
        p, q = at(s, -7), at(s + 2, 7); c.line(p[0], p[1], q[0], q[1], RED)
    for w2, l in ((-8, 18), (0, 22), (8, 16)):
        p, q = at(top, w2 * 0.6), at(top + l, w2 * 1.6); c.line(p[0], p[1], q[0], q[1], GREEN, 3)
    if glow:
        for k in range(6): p = at(-20 + k * 11, 10 if k % 2 else -10); c.px(p[0], p[1], YELLOW)


def zak(c, b=0, squat=0, legs=(0, 0), mouth=4, eyes="n", rarm=(88, 82), rang=4, larm=(16, 90), lean=0, rage=False, steam=0, glow=False,
        foot_r=None, foot_l=None, droop=0, blotch=False, second=None, club=True):
    dy = squat
    # ушки
    ex = lean
    c.ell(34 + ex, 24 + b + dy + droop, 11, 24 - droop * 2, FUR, dither=FUR2); c.ell(34 + ex, 26 + b + dy + droop, 6, 19 - droop, PINK, dither=(255, 120, 245))
    c.ell(70 + ex, 22 + b + dy + droop // 2, 11, 22, FUR, dither=FUR2); c.ell(70 + ex, 24 + b + dy + droop // 2, 6, 17, PINK)
    c.line(62 + ex, 14 + b + dy, 58 + ex, 6 + b + dy, BLACK, 2); c.rect(64 + ex, 20 + b + dy, 77 + ex, 24 + b + dy, BLACK, dither=RED)
    if rage:
        c.ell(34 + ex, 26 + b + dy, 6, 19, RED, dither=PINK)
    # ноги
    for i, (x0, lift) in enumerate(((24, legs[0]), (60, legs[1]))):
        foot = foot_l if i == 0 else foot_r
        if foot is None:
            c.rect(x0, 108 + lift, x0 + 16, 122 + lift, FUR)
            for x in (x0 + 2, x0 + 7, x0 + 12): c.line(x, 118 + lift, x, 123 + lift, BLACK)
        else:
            c.rect(x0, 108, x0 + 16, 112, FUR)     # бедро остаётся
            c.line(x0 + 8, 112, foot[0], foot[1], FUR, 10); c.ell(foot[0], foot[1], 8, 6, FUR, dither=FUR2)
            for k in (-4, 0, 4): c.px(foot[0] + k, foot[1] + 4, BLACK)
    # туша
    c.ell(50 + ex // 2, 84 + b + dy, 32, 30 - squat // 2, FUR, dither=FUR2)
    c.ell(50 + ex // 2, 90 + b + dy, 20, 20 - squat // 2, PINK, dither=(255, 120, 245)); c.ell(50 + ex // 2, 90 + b + dy, 9, 9, YELLOW, dither=ORANGE)
    c.pts([(46, 88 + b + dy), (50, 85 + b + dy), (54, 88 + b + dy), (50, 93 + b + dy)], BLACK)
    # голова
    hx = 50 + ex
    c.ell(hx, 48 + b + dy, 28, 24, FUR, dither=FUR2)
    if blotch:
        c.ell(hx - 18, 56 + b + dy, 7, 5, (255, 110, 120), dither=FUR); c.ell(hx + 18, 56 + b + dy, 7, 5, (255, 110, 120), dither=FUR)
    c.line(hx - 24, 30 + b + dy, hx - 10, 38 + b + dy, BLACK, 3); c.line(hx + 24, 30 + b + dy, hx + 10, 38 + b + dy, BLACK, 3)
    if rage:
        c.ell(hx - 12, 44 + b + dy, 7, 7, RED, dither=(255, 120, 0)); c.ell(hx + 12, 42 + b + dy, 8, 8, RED, dither=(255, 120, 0)); c.rect(hx - 13, 40 + b + dy, hx - 11, 48 + b + dy, YELLOW); c.rect(hx + 11, 38 + b + dy, hx + 13, 47 + b + dy, YELLOW)
    elif eyes == "cross":
        c.eye(hx - 12, 44 + b + dy, 7, (2, 0)); c.eye(hx + 12, 42 + b + dy, 8, (-2, 0))
    elif eyes == "squint":
        c.rect(hx - 18, 42 + b + dy, hx - 6, 46 + b + dy, WHITE); c.rect(hx + 6, 40 + b + dy, hx + 20, 45 + b + dy, WHITE); c.rect(hx - 13, 42 + b + dy, hx - 11, 46 + b + dy, BLACK); c.rect(hx + 12, 40 + b + dy, hx + 14, 45 + b + dy, BLACK)
    elif eyes == "wide":
        c.eye(hx - 12, 44 + b + dy, 8, (0, 0)); c.eye(hx + 12, 42 + b + dy, 9, (0, 0))
    else:
        c.eye(hx - 12, 44 + b + dy, 7, (2, 2)); c.eye(hx + 12, 42 + b + dy, 8, (-2, 2))
    c.ell(hx, 54 + b + dy, 4, 3, PINK)
    m = mouth
    c.rect(hx - 12, 60 + b + dy, hx + 12, 60 + b + dy + m, BLACK)
    c.rect(hx - 9, 60 + b + dy, hx - 5, 66 + b + dy + m // 2, WHITE); c.rect(hx + 5, 60 + b + dy, hx + 9, 66 + b + dy + m // 2, WHITE)
    c.px(hx - 7, 62 + b + dy, GOLD); c.px(hx - 7, 63 + b + dy, GOLD)
    for x in (hx - 3, hx, hx + 3): c.px(x, 60 + b + dy, WHITE)
    c.line(hx - 2, 60 + b + dy + m, hx - 2, 68 + b + dy + m, GREEN, 2)
    # руки
    sh_l, sh_r = (24 + ex // 2, 76 + b + dy), (78 + ex // 2, 76 + b + dy)
    c.line(sh_l[0], sh_l[1], larm[0], larm[1] + b + dy // 2, FUR, 9); c.ell(larm[0], larm[1] + b + dy // 2, 6, 6, FUR, dither=FUR2)
    rh = (rarm[0], rarm[1] + b + dy // 2)
    c.line(sh_r[0], sh_r[1], rh[0], rh[1], FUR, 9)
    if club: carrot(c, rh, rang, glow=glow)
    if second: carrot(c, (larm[0], larm[1] + b + dy // 2), second, glow=glow, big=0.9)
    c.ell(rh[0], rh[1], 6, 6, FUR); c.ell(larm[0], larm[1] + b + dy // 2, 6, 6, FUR)
    c.line(20, 40 + b + dy, 16, 34 + b + dy, BLACK)
    c.pts([(22, 96 + b), (80, 108 + b)], GREEN); c.rect(34, 100 + b + dy, 66, 100 + b + dy, BLACK, dither=GREEN)
    if steam:
        for k, xx in enumerate((26, 76)):
            for j in range(3): c.ell(xx + (j - 1) * 2 + ((steam + j) % 3) - 1, -2 - j * 6 - steam * 2 + b + dy, 3 + j, 2 + j, (235, 235, 245), dither=(180, 180, 200))


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    if st == "walk":
        b = [0, 2, 0, 2][t]; zak(c, b=b, legs=[(0, 0), (-5, 0), (0, 0), (0, -5)][t], larm=(16, [90, 86, 90, 94][t]), rarm=(88, [82, 80, 82, 84][t]), mouth=[4, 5, 4, 5][t])
    elif st == "throw":
        if t == 0: zak(c, rarm=(88, 76), rang=20, eyes="n", mouth=5)
        elif t == 1: zak(c, rarm=(96, 56), rang=70, lean=-2, larm=(14, 84), mouth=6, eyes="squint")
        elif t == 2:
            zak(c, rarm=(100, 40), rang=105, lean=-4, larm=(12, 80), mouth=8, eyes="wide", glow=True)
            for k in range(3): c.pts([(86 + k * 3, 10 - k * 4)], YELLOW)
        else:
            zak(c, rarm=(72, 68), rang=-70, lean=4, larm=(20, 94), mouth=10, eyes="angry" if False else "n")
            for k in range(4): c.line(70 - k * 4, 30 + k * 6, 40 - k * 6, 38 + k * 8, WHITE if k % 2 else YELLOW)
            carrot(c, (10, 54), -80, big=0.55)
            c.pts([(14, 40), (8, 46), (6, 60)], YELLOW)
    elif st == "fart":
        sq = [4, 10, 12, 8][t]
        zak(c, squat=sq, legs=(0, 0), mouth=[6, 10, 4, 8][t], eyes=["squint", "cross", "squint", "cross"][t], blotch=True, droop=[0, 2, 4, 3][t], rarm=(88, 86 + sq // 2), larm=(14, 90))
        if t >= 1:   # газ у зада
            n = t * 2 + 1
            for k in range(n):
                cx = 50 + (k - n // 2) * 12 + ((t * 5 + k * 3) % 5) - 2; cy = 122 - (k % 3) * 5 - t * 3
                c.ell(cx, cy, 7 + t, 5 + t // 2, STINK, dither=STINK2)
            for k in range(3): c.pts([(30 + k * 20, 110 - t * 6 - (k % 2) * 3), (31 + k * 20, 106 - t * 6), (30 + k * 20, 102 - t * 6)], STINK2)
            c.pts([(40, 124 + (t % 2)), (60, 124 - (t % 2))], BLACK)
    elif st == "kick":
        if t == 0: zak(c, lean=-4, mouth=6, eyes="squint", foot_l=(10, 120), rarm=(90, 84), rang=0)
        elif t == 1:
            zak(c, lean=-8, mouth=8, eyes="angry" if False else "wide", foot_l=(6, 108), rarm=(92, 88), rang=-10, glow=True)
            c.pts([(8, 96), (14, 92), (4, 100)], YELLOW)
        elif t == 2:
            zak(c, lean=2, mouth=10, eyes="n", foot_l=(46, 112), rarm=(88, 78), rang=14)
            for k in range(5): c.line(6 + k * 6, 124 - k * 3, 26 + k * 8, 100 - k * 2, WHITE if k % 2 else YELLOW)
        else:
            zak(c, lean=8, mouth=12, eyes="n", foot_l=(92, 98), rarm=(88, 78), rang=14)
            sx, sy = 108, 94
            for a in range(0, 360, 45): p = rot((sx + 14, sy), (sx, sy), a); c.line(sx, sy, p[0], p[1], YELLOW if a % 90 else WHITE, 2)
            c.ell(sx, sy, 5, 5, WHITE)
            c.line(0, 96, 28, 104, LGREY); c.line(0, 106, 22, 110, LGREY)
    elif st == "enrage":
        b = [0, 2, 0, 2][t]; zak(c, b=b, legs=[(0, 0), (-5, 0), (0, 0), (0, -5)][t], larm=(14, [90, 84, 90, 96][t]), rarm=(90, [80, 76, 80, 84][t]), rang=[8, 14, 8, 2][t], mouth=[10, 12, 10, 13][t], rage=True, steam=t, glow=True)
        for k, x in enumerate(range(10, 90, 6)):
            h = 4 + ((k + t) % 3) * 3; c.line(x, 124, x + ((k + t) % 2) - 1, 124 - h, ORANGE if k % 2 else RED)
        c.pts([(hx, 30) for hx in (40, 60)], PINK)
    elif st == "fan":
        if t == 0: zak(c, rarm=(88, 80), rang=6, larm=(14, 86), second=-6, mouth=6, rage=True)
        elif t == 1: zak(c, rarm=(98, 56), rang=40, larm=(4, 56), second=-40, mouth=9, rage=True, glow=True)
        elif t == 2:
            zak(c, rarm=(80, 30), rang=0, larm=(22, 30), second=0, mouth=12, rage=True, glow=True, steam=1)
            for k in range(5): c.pts([(22 + k * 14, 4 - (k % 2) * 3)], YELLOW)
        else:
            zak(c, rarm=(80, 74), rang=-50, larm=(22, 74), second=50, mouth=14, rage=True, glow=True, lean=0)
            for (px_, py_, ang_) in ((8, 10, -60), (52, -8, 0), (100, 10, 60)):
                carrot(c, (px_, py_), ang_, big=0.45)
            for k in range(6): c.line(30 + k * 10, 28, 30 + k * 10 + (k - 3) * 3, 14 - k % 2 * 4, WHITE if k % 2 else YELLOW)
    return cv.finish(CYAN, YELLOW, lim=0.12)


def build(): return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_zakhar.png"); print(im.size)
