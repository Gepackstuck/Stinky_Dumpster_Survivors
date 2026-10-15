"""Миньон-псих: дёрганая ходьба, ключи, говно, ярость, вихрь булавой."""
from boss_kit import *
W, H, OX, OY = 120, 124, 16, 20
ROWS = ["walk", "wrench", "poop", "rage", "whirl"]
YEL = (255, 220, 0); YEL2 = (255, 150, 0)


def mace(c, shoulder, ang, glow=False, ln=64):
    """Булава на длинной ручке от руки: ang=0 — вертикально вверх."""
    a = math.radians(ang); dx, dy = math.sin(a), -math.cos(a)
    hx, hy = shoulder
    ex, ey = hx + dx * ln, hy + dy * ln
    c.line(hx - dx * 8, hy - dy * 8, ex, ey, DGREY, 4)
    c.ell(ex, ey, 11, 11, GREY, dither=WHITE)
    for k in range(8):
        r = math.radians(k * 45 + ang)
        c.line(ex + math.cos(r) * 9, ey + math.sin(r) * 9, ex + math.cos(r) * 16, ey + math.sin(r) * 16, RED if not glow else YELLOW, 2)
    return ex, ey


def wrench(c, x, y, ang):
    a = math.radians(ang); dx, dy = math.cos(a), math.sin(a)
    c.line(x - dx * 7, y - dy * 7, x + dx * 7, y + dy * 7, LGREY, 3)
    c.ell(x + dx * 8, y + dy * 8, 3, 3, LGREY); c.px(x + dx * 8.5, y + dy * 8.5, BLACK)
    c.ell(x - dx * 8, y - dy * 8, 2, 2, LGREY)


def poop(c, x, y, big=1.0):
    c.ell(x, y + 3, 6 * big, 3 * big, (110, 65, 25)); c.ell(x, y, 4.5 * big, 3 * big, (125, 75, 30)); c.ell(x, y - 3 * big, 2.5 * big, 2 * big, (140, 85, 35))
    c.px(x - 1, y - 1, (180, 120, 60)); c.px(x + 1, y + 2, BLACK)


def mini(c, b=0, tilt=0, legs=(0, 0), mouth=3, pup=((3, 2), (-3, 3)), rage=False, steam=0, mace_ang=-4, mace_glow=False, rarm=(76, 68), spin_eyes=0,
         hair=0, grin=False, wiggle=0, hide_mace=False, poop_hand=False, mace_ln=64):
    X = tilt   # смещение верхней части
    # ноги в ботинках
    for x0, lift in ((18, legs[0]), (50, legs[1])):
        c.rect(x0, 86 + lift, x0 + 16, 94 + lift, BLACK); c.rect(x0, 92 + lift, x0 + 16, 94 + lift, YELLOW)
    # готический ёж на голове
    for i in range(7):
        x = 14 + i * 9; h = 14 + (i % 3) * 5 + hair + ((i + wiggle) % 2) * (2 if rage else 0)
        c.line(x + X, 20 + b, x + (i - 3) * 2 + X, 20 - h + b, BLACK, 3)
    # комбинезон и тело-капсула
    c.rect(20, 60 + b, 64, 88, BLUE, dither=(80, 80, 255))
    body_c = YEL if not rage else (255, 170, 20); body_d = ORANGE if not rage else RED
    c.rect(18 + X, 22 + b, 66 + X, 62 + b, body_c, dither=body_d)
    c.ell(42 + X, 22 + b, 24, 18, body_c, dither=body_d); c.rect(18 + X, 22 + b, 66 + X, 58 + b, body_c)
    c.rect(18 + X, 34 + b, 66 + X, 38 + b, BLACK)
    # очки-иллюминаторы + глаза
    c.ell(28 + X, 36 + b, 12, 12, LGREY); c.ell(56 + X, 36 + b, 10, 10, LGREY)
    c.ell(28 + X, 36 + b, 9, 9, WHITE); c.ell(56 + X, 36 + b, 8, 8, WHITE)
    if spin_eyes:
        for (cx, r) in ((28 + X, 8), (56 + X, 7)):
            for k in range(14):
                a = math.radians(k * 26 + spin_eyes * 40); rr = r * (0.2 + k / 16)
                c.px(cx + math.cos(a) * rr, 36 + b + math.sin(a) * rr, PINK if k % 2 else CYAN)
    else:
        c.pts([(28 + X + pup[0][0] + i, 36 + b + pup[0][1] + j) for i in (0, 1, 2) for j in (0, 1, 2)], BLACK)
        c.pts([(56 + X + pup[1][0] + i, 36 + b + pup[1][1] + j) for i in (0, 1) for j in (0, 1, 2)], BLACK)
        c.pts([(24 + X, 31 + b), (52 + X, 32 + b), (31 + X, 41 + b)], RED)
    c.line(16 + X, 24 + b, 38 + X, 30 + b, BLACK, 3); c.line(68 + X, 24 + b, 48 + X, 31 + b, BLACK, 3)
    # пасть
    m = mouth
    c.rect(26 + X, 50 + b, 58 + X, 50 + b + m, BLACK)
    for x in range(27, 58, 4): c.rect(x + X, 50 + b, x + 1 + X, 52 + b, WHITE); c.rect(x + 2 + X, 50 + b + m - 2, x + 3 + X, 50 + b + m, WHITE)
    c.rect(34 + X, 52 + b + m, 52 + X, 54 + b + m, PINK)
    if grin: c.pts([(24 + X, 49 + b), (25 + X, 50 + b), (59 + X, 50 + b), (60 + X, 49 + b)], BLACK)
    # карман комбеза
    c.rect(28, 66, 56, 78, BLUE); c.rect(30, 68, 36, 74, CYAN); c.pts([(32, 70), (34, 72)], BLACK)
    c.rect(14, 60, 18, 78, BLUE); c.rect(66, 60, 70, 78, BLUE)
    # левая рука + булава
    c.ell(8, 66 + b, 6, 7, YEL)
    if not hide_mace: mace(c, (8, 66 + b), mace_ang, glow=mace_glow, ln=mace_ln)
    # правая рука
    c.line(66, 62 + b, rarm[0], rarm[1] + b, YEL, 6); c.ell(rarm[0], rarm[1] + b, 6, 7, YEL)
    if rage or steam:
        for k, xx in enumerate((24, 60)):
            for j in range(3): c.ell(xx + (j - 1) * 2 + ((steam + j) % 3) - 1, 8 - j * 6 - steam * 2 + b, 3 + j, 2 + j, (255, 200, 200), dither=(230, 120, 120))
    c.pts([(60, 4), (74, 10), (80, 40), (4, 90)], PINK); c.pts([(30, 2), (50, 4)], CYAN)


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    if st == "walk":
        b = [0, 2, 0, 2][t]; tilt = [0, 2, 0, -2][t]
        pup = [((3, 2), (-3, 3)), ((-2, 2), (2, 3)), ((4, 1), (-4, 2)), ((0, 3), (0, 3))][t]
        mini(c, b=b, tilt=tilt, legs=[(0, 0), (-4, 0), (0, 0), (0, -4)][t], mouth=[3, 4, 3, 5][t], pup=pup, mace_ang=[-4, 10, -4, -14][t], wiggle=t, rarm=(76, [68, 66, 68, 70][t]))
    elif st == "wrench":
        if t == 0: mini(c, rarm=(74, 80), mouth=3, pup=((3, 2), (-3, 3)))
        elif t == 1: mini(c, b=-1, rarm=(80, 52), mouth=5, mace_ang=-10); wrench(c, 82, 44, 60)
        elif t == 2:
            mini(c, b=-2, rarm=(78, 30), mouth=6, mace_ang=-14, tilt=-2); wrench(c, 80, 18, 20); wrench(c, 92, 26, 100)
            c.pts([(70, 4), (84, 2), (96, 12)], YELLOW)
        else:
            mini(c, b=0, rarm=(84, 48), mouth=8, mace_ang=0, tilt=3, grin=True)
            for k, (x, y, a) in enumerate(((98, 26, 30), (104, 42, 80), (98, 58, 140))): wrench(c, x, y, a + t * 20); c.line(x - 12, y, x - 20, y, WHITE)
    elif st == "poop":
        if t == 0: mini(c, rarm=(62, 84), mouth=3, pup=((2, 3), (-3, 3)))     # лезет в зад
        elif t == 1:
            mini(c, b=1, rarm=(70, 78), mouth=6, grin=True); poop(c, 74, 70)
            for k in range(3): c.pts([(66 + k * 6, 56 - k % 2 * 2), (67 + k * 6, 52), (66 + k * 6, 48)], STINK2)
        elif t == 2:
            mini(c, b=-2, rarm=(80, 38), mouth=7, grin=True, tilt=-2); poop(c, 82, 24, 1.2)
            for k in range(3): c.pts([(74 + k * 6, 6 - k % 2 * 2), (75 + k * 6, 2)], STINK2)
        else:
            mini(c, rarm=(86, 54), mouth=9, grin=True, tilt=4)
            poop(c, 102, 40, 1.0); c.line(88, 52, 98, 44, STINK); c.line(90, 46, 100, 40, STINK2)
            c.ell(104, 72, 8, 3, (110, 65, 25), dither=STINK)    # лужа-метка
    elif st == "rage":
        b = [0, 2, 0, 2][t]; tilt = [0, 3, 0, -3][t]
        mini(c, b=b, tilt=tilt, legs=[(0, 0), (-5, 0), (0, 0), (0, -5)][t], mouth=[8, 10, 8, 11][t], rage=True, spin_eyes=t + 1, steam=t, mace_ang=[-4, 14, -4, -22][t], mace_glow=True, hair=4, wiggle=t, grin=True)
        for k, x in enumerate(range(10, 80, 6)):
            h = 4 + ((k + t) % 3) * 3; c.line(x, 96, x + ((k + t) % 2) - 1, 96 - h, ORANGE if k % 2 else RED)
    elif st == "whirl":
        # корпус крутится: наклоны, булава описывает круг
        tilt = [-3, 0, 3, 0][t]; ang = [-60, 30, 120, 210][t]
        mini(c, b=[0, 1, 0, 1][t], tilt=tilt, legs=(0, 0), mouth=9, rage=True, spin_eyes=t + 2, mace_ang=ang, mace_glow=True, hide_mace=False, hair=5, grin=True, rarm=(76, 66), mace_ln=44)
        # дуга-размах
        for k in range(14):
            a = math.radians(ang - 20 - k * 8 - 90); c.px(8 + math.cos(a) * 44, 66 + math.sin(a) * 44, WHITE if k % 2 else YELLOW)
        if t == 3:
            for k in range(8):
                a = math.radians(k * 45); wrench(c, 42 + math.cos(a) * 54, 52 + math.sin(a) * 50, k * 45 + 90)
    return cv.finish(PURPLE, WHITE, lim=0.1)


def build(): return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_minion.png"); print(im.size)
