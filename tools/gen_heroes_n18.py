#!/usr/bin/env python3
"""Н18: новые герои - ГОПНИК-КАЧОК (жора) и КОТ-ПОМОЕЧНИК (кот в сапогах). Лист 128x96 как у остальных (redraw_heroes_v3).
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_heroes_n18.py --apply -> assets/sprites/player_gopnik_jock.png, player_cat.png"""
import sys
from PIL import Image
sys.path.insert(0, "tools")
from redraw_heroes_v3 import *   # human, mk, sheet_for, Canvas, poly, цвета

TRACK = (30, 40, 150); TRACK2 = (20, 28, 110)


# ================= ГОПНИК-КАЧОК =================
def jock_hat(c, v, t, b):
    # кепка-восьмиклинка и бритый затылок
    c.ell(14, 2.5 + b, 6.5, 2.5, (60, 60, 65)); c.rect(8, 2 + b, 20, 3 + b, (60, 60, 65))
    if v == "side": c.rect(3, 3 + b, 9, 4 + b, (40, 40, 45))
    elif v == "front": c.rect(8, 3 + b, 20, 4 + b, (40, 40, 45))


def jock_face(c, v, t, b):
    if v == "front":
        c.line(10, 5 + b, 13, 6 + b, BLACK); c.line(18, 5 + b, 15, 6 + b, BLACK)   # хмурые брови
        c.rect(12, 11 + b, 16, 11 + b, BLACK); c.px(15, 11 + b, YELLOW)            # фикса
        c.pts([(10, 10 + b), (18, 10 + b)], (220, 150, 120))
    elif v == "side":
        c.px(11, 4 + b, BLACK); c.px(12, 4 + b, BLACK)


def jock_torso(c, v, t, b):
    if v != "back":
        c.line(10, 13 + b, 18, 13 + b, YELLOW); c.pts([(13, 14 + b), (14, 15 + b), (15, 14 + b)], YELLOW)   # цепь
    stripe_x = (9, 19) if v != "side" else (14, 14)
    for x in stripe_x: c.line(x, 13 + b, x, 22, WHITE)                        # лампасы на олимпийке


def jock_arms(c, v, t, b):
    # перекачанные руки: бицепсы шире
    if v == "front":
        c.ell(6, 16 + b, 2.5, 3, TRACK); c.ell(22, 16 + b, 2.5, 3, TRACK)
    elif v == "side":
        c.ell(14, 16 + b, 3, 3, TRACK)


JOCK = mk(skin=(240, 190, 150), skin_dark=(205, 145, 110), coat=TRACK, coat2=TRACK2, pants=TRACK, pants2=TRACK2, boots=WHITE, shade=BLUE, hi=WHITE, w=15, hem=22,
          hat=jock_hat, face_x=jock_face, torso=jock_torso, arms_x=jock_arms, sleeve=TRACK, brow=False, mouth=False, hair=(60, 60, 65))


# ================= КОТ-ПОМОЕЧНИК =================
FURC = (150, 150, 160); FURD = (100, 100, 110); BOOT = (120, 60, 25)


def cat(view, t):
    c = Canvas(CV, CV); b = 1 if t in (1, 3) else 0
    st = [-2, 0, 2, 0][t]
    if view == "side":
        c.line(21, 18 + b, 26, 10 + b - st // 2, FURD, 2); c.px(26, 9 + b - st // 2, FURC)               # хвост трубой
        for dx in (st, -st):                                                                               # лапы в сапогах
            c.rect(11 + dx // 2, 21, 13 + dx // 2, 25, FURC); c.rect(10 + dx // 2, 24, 14 + dx // 2, 27, BOOT)
        c.ell(15, 18 + b, 7, 5, FURC, dither=FURD); c.line(10, 16 + b, 20, 16 + b, FURD)                   # тело, полоска
        c.ell(10, 10 + b, 5.5, 5, FURC, dither=FURD)                                                        # голова
        poly(c, [(8, 6 + b), (9, 2 + b), (11, 6 + b)], FURC); poly(c, [(11, 5 + b), (13, 1 + b), (14, 6 + b)], FURC)   # уши (одно надорвано)
        c.px(13, 2 + b, PINK)
        c.ell(7, 10 + b, 1.5, 2, YELLOW); c.px(7, 10 + b, BLACK)                                           # глаз
        c.px(5, 12 + b, PINK); c.pts([(3, 12 + b), (2, 11 + b), (3, 13 + b)], WHITE)                        # нос, усы
    elif view == "back":
        c.line(14, 20 + b, 14 + st, 10 + b, FURD, 2)
        for x in (10, 16):
            c.rect(x, 21, x + 2, 25, FURC); c.rect(x - 1, 24, x + 3, 27, BOOT)
        c.ell(14, 17 + b, 7, 6, FURC, dither=FURD)
        c.ell(14, 9 + b, 5.5, 5, FURC, dither=FURD)
        poly(c, [(9, 6 + b), (10, 1 + b), (12, 5 + b)], FURC); poly(c, [(16, 5 + b), (18, 1 + b), (19, 6 + b)], FURC)
    else:
        for x, s in ((10, st), (16, -st)):
            c.rect(x, 21, x + 2, 25 - (1 if s > 0 else 0), FURC); c.rect(x - 1, 24 - (1 if s > 0 else 0), x + 3, 27 - (1 if s > 0 else 0), BOOT)
        c.ell(14, 17 + b, 7, 6, FURC, dither=FURD); c.ell(14, 19 + b, 3.5, 3, WHITE)                       # пузо
        c.ell(14, 9 + b, 6, 5.5, FURC, dither=FURD)
        poly(c, [(8, 6 + b), (9, 1 + b), (12, 5 + b)], FURC); poly(c, [(16, 5 + b), (19, 1 + b), (20, 6 + b)], FURC); c.px(19, 2 + b, PINK)
        c.ell(11, 9 + b, 1.6, 2, YELLOW); c.ell(17, 9 + b, 2.2, 2.4, YELLOW); c.px(11, 9 + b, BLACK); c.rect(17, 8 + b, 17, 10 + b, BLACK)   # глаза разные
        c.px(14, 11 + b, PINK); c.rect(13, 12 + b, 15, 12 + b, BLACK)
        c.pts([(7, 11 + b), (6, 10 + b), (21, 11 + b), (22, 12 + b)], WHITE)                               # усы
        c.line(10, 14 + b, 12, 15 + b, RED)                                                                 # шрам
    return c.finish(DGREY, WHITE, lim=0.35)


CAT = mk(draw=cat)
NEW = {"gopnik_jock": JOCK, "cat": CAT}

if __name__ == "__main__":
    prev = Image.new("RGBA", (128 * 3 + 20, len(NEW) * (96 * 3 + 8) + 8), (45, 30, 20, 255))
    for i, (n, P) in enumerate(NEW.items()):
        im = Image.fromarray(sheet_for(P), "RGBA")
        if "--apply" in sys.argv: im.save(f"assets/sprites/player_{n}.png")
        big = im.resize((im.width * 3, im.height * 3), Image.NEAREST); prev.paste(big, (10, 6 + i * (96 * 3 + 8)), big)
    prev.save("tools/_preview/heroes_n18.png"); print(prev.size)
