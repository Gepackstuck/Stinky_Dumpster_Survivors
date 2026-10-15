#!/usr/bin/env python3
"""Компаньоны: пёс, крыса, голубь, духи, лампа, мина, миномёт, турель. python3 tools/redraw_pets.py [--apply] [имена]"""
import sys, os, math, random
import numpy as np
from PIL import Image
sys.path.insert(0, "tools")
from icon_kit import *
GH = (160, 235, 255)

def sheet(frames): return np.concatenate(frames, axis=1)

# ---------------- ПЁС (28×18, 6 кадров: 0-3 бег, 4-5 стоит/дышит) ----------------
def dog_frame(t):
    c = Canvas(26, 16)
    run = t < 4
    bob = -1 if (run and t % 2 == 1) else 0
    legs = [(3, -3, -3, 3), (1, -1, -1, 1), (-3, 3, 3, -3), (-1, 1, 1, -1)][t] if run else (0, 0, 0, 0)
    for lx, dx in zip((17, 14, 6, 9), legs):      # лапы (дальние тёмные)
        col = DBROWN if lx in (14, 9) else (150, 100, 55)
        c.line(lx, 10 + bob, lx + dx, 14 if abs(dx) < 3 else 13, col, 2)
    wag = [0, -2, -4, -2, -3, 0][t]
    c.line(5, 6 + bob, 0, 3 + wag, (150, 100, 55), 2); c.px(0, 3 + wag, (235, 225, 205))                            # хвост-метёлка
    c.ell(11, 8 + bob, 8.5, 4.3, (170, 120, 70), dither=(140, 95, 55)); c.ell(11, 10 + bob, 6, 2, (205, 170, 120))  # туловище, пузо
    c.pts([(7, 5 + bob), (8, 4 + bob), (9, 5 + bob), (13, 5 + bob), (14, 6 + bob)], DBROWN)                          # пятна/шерсть
    c.ell(20, 6 + bob, 5, 4.2, (170, 120, 70)); c.ell(24, 8 + bob, 3, 2.3, (235, 225, 205))                          # голова, морда
    c.px(26 if False else 25, 7 + bob, BLACK); c.px(26 - 1, 7 + bob, BLACK)
    poly(c, [(17, 1 + bob), (21, 1 + bob), (21, 7 + bob), (17, 8 + bob)], DBROWN)                                    # висячее ухо
    c.rect(21, 4 + bob, 22, 5 + bob, WHITE); c.px(22, 5 + bob, BLACK)                                                # глаз
    c.px(21, 3 + bob, DBROWN); c.px(22, 3 + bob, DBROWN)                                                              # бровь
    tongue = (t % 2 == 0) if not run else True
    if tongue: c.rect(24, 10 + bob, 25, 12 + bob if run or t == 4 else 11 + bob, PINK)
    c.rect(18, 9 + bob, 19, 9 + bob, RED)                                                                            # ошейник-тряпка
    return fin16(c)

def fin16(c, sh=PURPLE, hi=WHITE, lim=0.5): return c.finish(sh, hi, lim=lim)

# ---------------- КРЫСА (20×12, 6 кадров) ----------------
def rat_frame(t):
    c = Canvas(18, 10)
    run = t < 4
    bob = -1 if (run and t % 2 == 1) else 0
    legs = [(2, -2, -2, 2), (1, -1, -1, 1), (-2, 2, 2, -2), (-1, 1, 1, -1)][t] if run else (0, 0, 0, 0)
    for lx, dx in zip((12, 10, 5, 7), legs): c.line(lx, 6 + bob, lx + dx, 9, PINK)
    w = [0, 2, 0, -2, 1, -1][t]
    for i in range(6): c.px(3 - i, 6 + bob + round(math.sin(i * .9 + t) * 1.5) + (i // 4), PINK)                      # хвост-верёвка
    c.ell(8, 5 + bob, 6, 3.3, (140, 140, 155), dither=(110, 110, 125)); c.ell(8, 6 + bob, 4, 1.5, (190, 190, 200))
    c.ell(14, 5 + bob, 3, 2.4, (150, 150, 165)); poly(c, [(15, 3 + bob), (18, 5 + bob), (15, 7 + bob)], (200, 170, 180)); c.px(17, 5 + bob, PINK)
    c.ell(12, 2 + bob, 1.6, 1.6, PINK); c.ell(15, 2 + bob, 1.4, 1.4, PINK); c.px(14, 4 + bob, RED); c.px(15, 4 + bob, BLACK)
    c.pts([(17, 7 + bob), (18, 8 + bob)], WHITE) if t % 3 == 0 else None
    return fin16(c, PURPLE, WHITE)

# ---------------- ГОЛУБЬ (22×16, 4 кадра: взмахи) ----------------
def pigeon_frame(t):
    c = Canvas(20, 14)
    wing_up = [(-6, -7), (-4, -3), (-1, 3), (-4, -3)][t]   # (dy кончика назад, dy вверх)
    c.line(3, 7, 0, 7 + [0, 1, 2, 1][t], DGREY, 2); poly(c, [(2, 6), (0, 5), (0, 9), (3, 8)], MG)                      # хвост
    c.ell(10, 8, 7, 4.2, (165, 170, 190), dither=(135, 140, 165)); c.ell(11, 9, 4.5, 2, (205, 210, 225))              # тело
    c.ell(15, 7, 3, 2.7, (110, 130, 175)); c.ell(15, 5, 3, 3, (170, 175, 195))                                          # шея, голова
    poly(c, [(17, 5), (20, 6), (17, 7)], ORANGE); c.px(16, 4, RED); c.px(17, 4, BLACK); c.pts([(14, 7), (15, 8)], (50, 170, 130)); c.pts([(13, 6), (14, 6)], PINK)
    ty = 8 + wing_up[1]
    poly(c, [(9, 7), (14, 7), (11 + (1 if t % 2 else 0), ty - (3 if wing_up[1] < 0 else 0)), (4, ty + (1 if wing_up[1] < 0 else 3))], (130, 135, 160)); c.line(5, ty + 1, 11, 7, DGREY)
    c.pts([(9, 12), (11, 12)], ORANGE); c.px(8, 12 + (t % 2), ORANGE)
    return fin16(c, PURPLE, WHITE)

# ---------------- ДУХИ (22×28, 4 кадра) ----------------
def ghost_frame(kind, t):
    c = Canvas(22, 26)
    sway = [0, 1, 0, -1][t]
    c.ell(11, 10, 8, 8, GH, dither=WHITE); c.rect(3, 10, 19, 20, GH, dither=WHITE)
    for i, x in enumerate((3, 7, 11, 15)):
        off = [(0, 2, 0, 2), (2, 0, 2, 0), (0, 2, 0, 2), (2, 0, 2, 0)][t][i]
        poly(c, [(x, 19), (x + 4, 19), (x + 2, 23 + off)], GH)
    if kind == "drunk":
        eyes = 5 if t % 2 == 0 else 4
        c.rect(6, 8, 8, 11, BLACK); c.rect(13, 8, 15, 11, BLACK); c.px(7, 9 + t % 2, RED); c.px(14, 9 + t % 2, RED)
        c.rect(8, 14 + (t == 2), 13, 15 + (t == 2), BLACK); c.px(10, 15, PINK)
        c.pts([(5, 6), (6, 5), (15, 6), (16, 5)], DGREY)                                                                 # брови набекрень
        bx = 17 + sway; by = [14, 11, 8, 11][t]                                                                           # рука с бутылкой качается к рту
        poly(c, [(bx, by), (bx + 3, by), (bx + 3, by + 9), (bx, by + 9)], GREEN); c.rect(bx + 1, by - 2, bx + 2, by, GREEN); c.rect(bx + 1, by - 3, bx + 2, by - 3, WHITE); c.rect(bx, by + 4, bx + 3, by + 6, WHITE)
        c.px(2, 4, CYAN) if t % 2 else c.px(19, 3, CYAN)
        if t == 2: c.pts([(19, 2), (20, 1)], YELLOW)
    else:
        poly(c, [(2, 6), (11, 0), (20, 6), (19, 10), (3, 10)], PINK, dither=(255, 120, 245)); c.rect(3, 10, 19, 11, (200, 0, 190)); c.pts([(7, 3), (12, 2), (16, 4)], WHITE)   # платок
        c.rect(6, 12, 8, 13, BLACK); c.rect(13, 12, 15, 13, BLACK); c.pts([(5, 11), (9, 11), (12, 11), (16, 11)], WHITE); c.rect(9, 17, 12, 17, BLACK)
        n = [0, 1, 2, 1][t]                                                                                                 # спицы стучат
        c.line(3, 17, 8, 14 + n, MG); c.line(18, 17, 13, 14 + (2 - n), MG); c.ell(11, 18, 3, 2, (255, 120, 245)); c.px(10 + n, 18, WHITE)
        if t == 1: c.pts([(19, 3), (20, 2)], PINK)
    return fin16(c, CYAN, WHITE, 0.5)

# ---------------- ЛАМПА (20×28, 4 кадра) ----------------
def lamp_frame(t):
    c = Canvas(18, 26)
    c.rect(6, 20, 11, 22, DGREY); c.rect(4, 22, 13, 24, DGREY); c.rect(4, 22, 13, 22, STEEL); c.rect(8, 15, 9, 20, MG)
    c.ell(9, 9, 7.5, 7.5, (215, 245, 215), dither=WHITE); c.ell(9, 10, 5, 5, GREEN); c.ell(9, 10, 2.5 + (t % 2) * .5, 2.5 + (t % 2) * .5, LGREEN); c.px(5, 5, WHITE); c.pts([(4, 7), (4, 8)], WHITE)
    poly(c, [(6, 15), (12, 15), (11, 18), (7, 18)], MG)
    for i in range(3):                                                                                                   # вонь поднимается
        y = (3 - ((t * 2 + i * 3) % 7)); x = 2 + i * 6 + (1 if (t + i) % 2 else 0)
        c.pts([(x, y + 3), (x + 1, y + 2), (x, y + 1)], GREEN) if y > -2 else None
    return fin16(c, GREEN, WHITE, 0.5)

# ---------------- МИНА (16×10, 4 кадра: мигает) ----------------
def mine_frame(t):
    c = Canvas(14, 8)
    c.ell(7, 5, 7, 3, DGREY); c.rect(0, 5, 13, 7, DGREY); c.ell(7, 4, 5, 2, MG, dither=LG)
    for x in (1, 4, 7, 10, 12): c.px(x, 7, YELLOW)
    c.rect(6, 0, 7, 3, BLACK); c.px(6, 0, [RED, WHITE, RED, PINK][t]); c.px(7, 0, [RED, RED, PINK, RED][t]); c.pts([(3, 4), (10, 4)], WHITE)
    return fin16(c, ORANGE, YELLOW, 0.5)

# ---------------- МИНОМЁТ-ТЕЛЕЖКА (28×24, 4 кадра: 0-1 ждёт, 2 залп, 3 дым) ----------------
def mortar_frame(t):
    c = Canvas(26, 22)
    c.rect(1, 12, 20, 18, STEEL, dither=DGREY); c.rect(1, 12, 20, 12, WHITE); c.rect(0, 11, 21, 12, MG)
    for x in (4, 8, 12, 16): c.rect(x, 13, x, 18, DGREY)
    c.ell(5, 20, 2.8, 2.8, BLACK); c.ell(16, 20, 2.8, 2.8, BLACK); c.px(4, 19, GREY); c.px(15, 19, GREY); c.line(20, 12, 25, 16, MG, 2)
    k = 2 if t == 2 else 0
    poly(c, [(8, 12), (14, 12), (13 + k, 3), (9 + k, 3)], DGREY); c.rect(8 + k, 2, 14 + k, 4, GREY); c.rect(9 + k, 6, 10 + k, 11, MG)
    if t == 2: c.ell(11, 0, 3, 2, YELLOW); c.ell(11, 0, 1.5, 1, WHITE); c.pts([(6, 1), (17, 1), (14, -1)], ORANGE)
    elif t == 3: c.ell(11, 0, 3, 1.5, GREY); c.pts([(8, 1), (15, 0)], (110, 110, 110))
    else: c.px(11, 1, ORANGE if t == 0 else RED)
    return fin16(c, PURPLE, YELLOW, 0.4)

# ---------------- ТУРЕЛЬ ИЗ ВЕДРА (34×34, 8 направлений × 2 состояния) ----------------
def turret_frame(aim, charging):
    c = Canvas(32, 32)
    ang = aim * math.pi / 4 - math.pi / 2
    poly(c, [(8, 14), (24, 14), (22, 29), (10, 29)], MG, dither=LG); c.rect(7, 12, 25, 15, GREY); c.rect(7, 12, 25, 12, WHITE)
    for y in (18, 22, 26): c.rect(9, y, 22, y, DGREY)
    c.rect(11, 15, 12, 28, WHITE); c.ell(18, 22, 2.5, 2.5, (160, 70, 30)); c.pts([(16, 21), (20, 23)], (210, 110, 40)); c.line(7, 12, 5, 8, MG); c.line(25, 12, 27, 8, MG)
    c.ell(16, 11, 5, 4, DGREY); c.ell(16, 10, 3, 2.5, MG)                                                              # вращающаяся башенка
    ex, ey = 16 + math.cos(ang) * 11, 10 + math.sin(ang) * 9
    c.line(16, 10, round(ex), round(ey), BLACK, 3); c.line(16, 10, round(ex), round(ey), DGREY, 2)
    c.px(round(ex), round(ey), RED if charging else ORANGE)
    if charging: c.ell(round(ex + math.cos(ang) * 2), round(ey + math.sin(ang) * 2), 2, 2, YELLOW)
    a = fin16(c, PURPLE, YELLOW, 0.4)                                                                                   # 34×34
    return a

SPECS = {
    "pet_dog": lambda: sheet([dog_frame(t) for t in range(6)]),
    "pet_rat": lambda: sheet([rat_frame(t) for t in range(6)]),
    "pet_pigeon": lambda: sheet([pigeon_frame(t) for t in range(4)]),
    "pet_ghost_drunk": lambda: sheet([ghost_frame("drunk", t) for t in range(4)]),
    "pet_ghost_granny": lambda: sheet([ghost_frame("granny", t) for t in range(4)]),
    "structure_lamp": lambda: sheet([lamp_frame(t) for t in range(4)]),
    "structure_mine": lambda: sheet([mine_frame(t) for t in range(4)]),
    "structure_mortar": lambda: sheet([mortar_frame(t) for t in range(4)]),
    "structure_turret": lambda: np.concatenate([sheet([turret_frame(a, ch) for a in range(8)]) for ch in (False, True)], axis=0),
}

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(SPECS)
    k = 5; rows = []
    for n in names:
        a = SPECS[n](); im = Image.fromarray(a, "RGBA"); print(n, im.size)
        if apply: im.save(f"assets/sprites/{n}.png")
        rows.append(im)
    W = max(r.width for r in rows) * k + 20; H = sum(r.height * k + 12 for r in rows) + 10
    prev = Image.new("RGBA", (W, H), (45, 30, 20, 255)); y = 6
    for r in rows:
        b = r.resize((r.width * k, r.height * k), Image.NEAREST); prev.paste(b, (10, y), b); y += b.height + 12
    prev.save("tools/_preview/pets_new.png")
