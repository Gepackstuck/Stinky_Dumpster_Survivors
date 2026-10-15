#!/usr/bin/env python3
"""Герои v3: крупнее (кадр 32×32), реалистичные пропорции, детали одежды и лица.
Лист 128×96 (4 кадра × [бок влево, спина, фас]). python3 tools/redraw_heroes_v3.py [--apply] [id ...]"""
import sys, os, math
import numpy as np
from PIL import Image
sys.path.insert(0, "tools")
from icon_kit import *   # Canvas, poly, ringc, цвета
FR = 32; CV = 28
GOLD = (255, 200, 40)
LGREY = (190, 190, 200); FUR = (150, 150, 155); TAN = (205, 150, 100); SKINSH = (215, 150, 110)


def mk(**kw): return kw


def human(view, t, P):
    c = Canvas(CV, CV); b = 1 if t in (1, 3) else 0     # покачивание вверх-вниз
    sw = [-3, 0, 3, 0][t]                                  # шаг
    W = P.get("w", 12); x0 = 14 - W // 2; x1 = x0 + W - 1
    skin, sd = P["skin"], P.get("skin_dark", SKINSH)
    coat = P["coat"]; coat2 = P.get("coat2")
    hem = P.get("hem", 22)                                 # докуда доходит одежда сверху
    # ---- ноги ----
    if view == "side":
        for dx, shade in ((sw, 0), (-sw, 1)):
            col = P["pants"] if not shade else P.get("pants2", P["pants"])
            c.rect(11 + dx // 2, 21, 15 + dx // 2, 26, col, dither=P.get("pants_d"))
            c.rect(9 + dx, 26, 16 + dx // 2, 27, P["boots"]) if dx <= 0 else c.rect(11 + dx // 2, 26, 18 + dx, 27, P["boots"])
    else:
        l, r = (1 if t == 1 else 0), (1 if t == 3 else 0)
        c.rect(x0 + 1, 21, x0 + 5, 26 - l, P["pants"], dither=P.get("pants_d")); c.rect(x1 - 5, 21, x1 - 1, 26 - r, P["pants"], dither=P.get("pants_d"))
        c.rect(x0, 26 - l, x0 + 5, 27 - l, P["boots"]); c.rect(x1 - 5, 26 - r, x1, 27 - r, P["boots"])
    P.get("legs_x", lambda *a: None)(c, view, t, b)
    # ---- туловище ----
    if view == "side":
        c.rect(10, 12 + b, 18, hem, coat, dither=coat2)
        c.ell(14, 13 + b, 4, 2, coat)
    else:
        c.rect(x0, 12 + b, x1, hem, coat, dither=coat2)
        c.ell(x0 + 1, 13 + b, 2.5, 2.5, coat); c.ell(x1 - 1, 13 + b, 2.5, 2.5, coat)
    P.get("torso", lambda *a: None)(c, view, t, b)
    # ---- руки ----
    sl = P.get("sleeve", coat)
    if view == "side":
        a = sw // 2
        c.rect(12 + a, 13 + b, 15 + a, 19, sl); c.ell(13.5 + a, 20, 2, 2, skin)
    else:
        a = sw // 2
        c.rect(x0 - 3, 13 + b, x0 - 1, 19 + a // 2, sl); c.rect(x1 + 1, 13 + b, x1 + 3, 19 - a // 2, sl)
        c.ell(x0 - 2, 20 + a // 2, 1.8, 1.8, skin); c.ell(x1 + 2, 20 - a // 2, 1.8, 1.8, skin)
    P.get("arms_x", lambda *a: None)(c, view, t, b)
    # ---- шея и голова ----
    cx = 14
    c.rect(12, 11 + b, 16, 13 + b, sd)
    c.ell(cx, 7 + b, 5.5, 6, skin, dither=sd)
    if view == "side":
        c.pts([(8, 8 + b), (8, 9 + b), (7, 9 + b)], skin)               # нос профиль
        c.px(7, 9 + b, sd)
        c.ell(12, 6 + b, 1.3, 1.5, WHITE); c.px(11, 6 + b, BLACK); c.px(11, 5 + b, BLACK) if P.get("brow", True) else None
        c.rect(8, 11 + b, 11, 11 + b, BLACK) if P.get("mouth", True) else None
        c.ell(17, 8 + b, 1.2, 1.6, sd)                                    # ухо
    elif view == "front":
        c.ell(11, 7 + b, 1.5, 1.7, WHITE); c.ell(17, 7 + b, 1.5, 1.7, WHITE); c.px(11, 8 + b, BLACK); c.px(17, 8 + b, BLACK); c.px(11, 7 + b, BLACK); c.px(17, 7 + b, BLACK)
        if P.get("brow", True): c.line(9, 5 + b, 12, 5 + b, BLACK); c.line(16, 5 + b, 19, 5 + b, BLACK)
        c.px(14, 9 + b, sd); c.px(14, 10 + b, sd)
        if P.get("mouth", True): c.rect(12, 12 + b, 16, 12 + b, BLACK); c.pts([(12, 12 + b), (16, 12 + b)], PINK) if False else None
        c.ell(8.5, 8 + b, 1, 1.5, sd); c.ell(19.5, 8 + b, 1, 1.5, sd)
    else:
        c.rect(9, 3 + b, 19, 8 + b, P.get("hair", sd))
    P.get("face_x", lambda *a: None)(c, view, t, b)
    P["hat"](c, view, t, b)
    P.get("extra", lambda *a: None)(c, view, t, b)
    return c.finish(P["shade"], P.get("hi", WHITE), lim=P.get("lim", 0.35))   # 30×30


def pad32(a):
    out = np.zeros((FR, FR, 4), np.uint8); h, w = a.shape[:2]; out[FR - h - 1:FR - 1, (FR - w) // 2:(FR - w) // 2 + w] = a; return out


def sheet_for(P):
    rows = []
    for view in ("side", "back", "front"):
        rows.append(np.concatenate([pad32(P["draw"](view, t) if "draw" in P else human(view, t, P)) for t in range(4)], axis=1))
    return np.concatenate(rows, axis=0)


# ================= БОМЖ ВАСЯ =================
FURC = (165, 160, 150); DFUR = (110, 105, 100); BEARD = (70, 45, 28)
def hobo_hat(c, v, t, b):
    # ушанка: меховой купол над бровями, опущенные уши по бокам, красная звезда
    c.ell(14, 2.5 + b, 7, 3.5, FURC, dither=DFUR); c.rect(7, 2 + b, 21, 4 + b, FURC, dither=DFUR)
    if v == "side":
        c.rect(14, 3 + b, 20, 11 + b, FURC, dither=DFUR); c.rect(13, 3 + b, 14, 4 + b, DFUR); c.pts([(9, 3 + b), (8, 4 + b)], FURC)
        c.pts([(9, 2 + b), (10, 1 + b)], WHITE); c.pts([(10, 3 + b), (11, 3 + b)], RED)
    elif v == "front":
        c.rect(7, 4 + b, 9, 12 + b, FURC, dither=DFUR); c.rect(19, 4 + b, 21, 12 + b, FURC, dither=DFUR)
        c.rect(13, 2 + b, 15, 3 + b, RED); c.px(14, 1 + b, RED); c.px(14, 4 + b, RED); c.px(12, 3 + b, RED); c.px(16, 3 + b, RED); c.px(14, 3 + b, YELLOW)
        c.pts([(8, 12 + b), (20, 12 + b)], WHITE); c.pts([(8, 13 + b), (20, 13 + b)], DFUR)
    else:
        c.rect(7, 3 + b, 21, 11 + b, FURC, dither=DFUR); c.rect(9, 11 + b, 19, 12 + b, DFUR)
    c.pts([(10, 0 + b), (17, 0 + b), (12, 1 + b)], WHITE)

def hobo_face(c, v, t, b):
    # борода с крошками, красный нос, мешки под глазами
    if v == "front":
        poly(c, [(9, 9 + b), (19, 9 + b), (19, 14 + b), (16, 18 + b), (12, 18 + b), (9, 14 + b)], BEARD, dither=(95, 62, 38))
        c.rect(12, 12 + b, 16, 12 + b, BLACK); c.ell(14, 9 + b, 2, 1.5, (235, 90, 80)); c.px(13, 9 + b, PINK)
        c.pts([(10, 15 + b), (17, 16 + b), (13, 17 + b), (15, 14 + b)], YELLOW); c.pts([(10, 8 + b), (18, 8 + b)], (200, 120, 120))
    elif v == "side":
        poly(c, [(8, 10 + b), (16, 9 + b), (16, 13 + b), (13, 18 + b), (9, 16 + b)], BEARD, dither=(95, 62, 38)); c.ell(7.5, 9 + b, 1.8, 1.5, (235, 90, 80)); c.pts([(10, 14 + b), (12, 16 + b)], YELLOW)
    else: pass
def hobo_torso(c, v, t, b):
    # заплатки, пуговицы, верёвка-пояс, рваный подол
    if v == "front":
        c.rect(9, 15 + b, 12, 18 + b, PINK); c.rect(10, 16 + b, 11, 17 + b, (220, 60, 200)); c.rect(16, 18 + b, 19, 21, YELLOW); c.line(16, 19, 19, 19, ORANGE)
        for y in (14, 17, 20): c.px(14, y + b, (30, 90, 30)); c.px(14, y + b, BLACK)
        c.line(8, 19, 20, 19, BROWN); c.pts([(18, 19), (19, 21)], BROWN); c.line(14, 12 + b, 14, 22, (20, 130, 20))
    elif v == "side":
        c.rect(11, 15 + b, 14, 18 + b, PINK); c.rect(10, 19, 18, 19, BROWN); c.pts([(12, 22), (15, 23), (17, 22)], GREEN)
    else:
        c.rect(10, 15 + b, 14, 19 + b, PINK); c.rect(15, 17, 18, 20, YELLOW); c.rect(9, 19, 19, 19, BROWN); c.line(14, 12, 14, 22, (20, 130, 20))
    for x in (9, 12, 15, 18): c.px(x, 22, BLACK)   # рваная кромка
def hobo_arms(c, v, t, b):
    # бутылка в руке (качается)
    a = [-2, 0, 2, 0][t] // 2
    if v == "front": poly(c, [(21, 17 - a), (24, 17 - a), (24, 24 - a), (21, 24 - a)], GREEN); c.rect(22, 15 - a, 23, 17 - a, GREEN); c.rect(22, 14 - a, 23, 14 - a, WHITE); c.rect(21, 20 - a, 24, 22 - a, WHITE); c.rect(21, 19 - a, 21, 19 - a, WHITE)
    elif v == "side": poly(c, [(8 + a, 19), (11 + a, 19), (11 + a, 25), (8 + a, 25)], GREEN); c.rect(9 + a, 17, 10 + a, 19, GREEN); c.rect(8 + a, 22, 11 + a, 23, WHITE)
    else: poly(c, [(4, 17), (7, 17), (7, 23), (4, 23)], GREEN); c.rect(5, 15, 6, 17, GREEN)
HOBO = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=(45, 220, 30), coat2=(30, 150, 25), pants=(45, 40, 55), pants2=(30, 28, 38), boots=(120, 70, 30), shade=PURPLE, hi=YELLOW,
          w=14, hem=23, hat=hobo_hat, face_x=hobo_face, torso=hobo_torso, arms_x=hobo_arms, brow=True, mouth=False, sleeve=(35, 185, 28))

# ================= БАБКА С ПОДЪЕЗДА =================
FLORAL = (190, 140, 230); FLORAL2 = (150, 100, 200)
def gran_hat(c, v, t, b):
    # платок в горошек: над бровями и по бокам лица, седая чёлка
    PK = (235, 90, 130); PK2 = (205, 60, 105)
    c.ell(14, 2.5 + b, 7, 3.5, PK, dither=PK2); c.rect(7, 2 + b, 21, 4 + b, PK)
    for p in [(9, 1), (12, 0), (16, 1), (19, 2), (10, 3), (14, 2), (18, 4)]: c.px(p[0], p[1] + b, WHITE)
    if v == "front":
        c.rect(7, 4 + b, 9, 13 + b, PK); c.rect(19, 4 + b, 21, 13 + b, PK); c.pts([(8, 7 + b), (20, 9 + b), (8, 11 + b)], WHITE)
        c.pts([(11, 4 + b), (13, 4 + b), (16, 4 + b)], (210, 210, 215)); poly(c, [(12, 13 + b), (16, 13 + b), (14, 16 + b)], PK)
    elif v == "side":
        c.rect(14, 3 + b, 20, 12 + b, PK); c.pts([(16, 6 + b), (18, 9 + b), (15, 11 + b)], WHITE); c.pts([(10, 4 + b), (11, 4 + b)], (210, 210, 215))
    else:
        c.rect(7, 3 + b, 21, 13 + b, PK, dither=PK2); c.pts([(10, 6 + b), (14, 8 + b), (18, 6 + b), (12, 10 + b), (17, 11 + b)], WHITE); poly(c, [(12, 13 + b), (16, 13 + b), (14, 16 + b)], PK)

def gran_face(c, v, t, b):
    # очки-блюдца, морщины, оскал
    if v == "front":
        ringc(c, 11, 7.5 + b, 3, BLACK, 1); ringc(c, 17, 7.5 + b, 3, BLACK, 1); c.rect(13, 7 + b, 15, 7 + b, BLACK); c.pts([(9, 6 + b), (19, 6 + b)], BLACK)
        c.ell(11, 7.5 + b, 2, 2, (200, 235, 245)); c.ell(17, 7.5 + b, 2, 2, (200, 235, 245)); c.px(11, 8 + b, BLACK); c.px(17, 8 + b, BLACK); c.pts([(10, 6 + b), (16, 6 + b)], WHITE)
        c.rect(11, 12 + b, 17, 13 + b, WHITE); c.rect(11, 12 + b, 17, 12 + b, BLACK); c.pts([(13, 13 + b), (15, 13 + b)], BLACK); c.pts([(8, 10 + b), (20, 10 + b), (9, 11 + b)], (210, 150, 120))
    elif v == "side":
        ringc(c, 11.5, 7.5 + b, 3, BLACK, 1); c.ell(11.5, 7.5 + b, 2, 2, (200, 235, 245)); c.line(14, 7 + b, 18, 6 + b, BLACK); c.rect(8, 12 + b, 11, 12 + b, BLACK); c.pts([(9, 11 + b), (10, 11 + b)], WHITE); c.pts([(14, 10 + b), (15, 11 + b)], (210, 150, 120))
def gran_torso(c, v, t, b):
    # халат в цветочек, пояс, пуговицы
    pts = [(10, 15), (13, 17), (17, 14), (20, 19), (11, 21), (16, 22), (9, 19), (19, 22), (13, 14)]
    for i, (x, y) in enumerate(pts):
        if (v == "side" and 10 <= x <= 17) or v != "side":
            c.px(x, y + (b if y < 20 else 0), YELLOW if i % 2 else WHITE); c.px(x + 1, y + (b if y < 20 else 0), PINK) if i % 3 == 0 else None
    if v != "back": c.line(8 if v != "side" else 10, 18, 20 if v != "side" else 18, 18, (120, 70, 160))
    if v == "front": c.line(14, 13 + b, 14, 23, (120, 70, 160)); c.pts([(13, 15 + b), (13, 19), (13, 21)], WHITE)
    c.rect(10, 22, 18, 23, FLORAL2) if v != "front" else c.rect(8, 22, 20, 23, FLORAL2)
def gran_arms(c, v, t, b):
    # клюка и авоська
    a = [-2, 0, 2, 0][t] // 2
    if v == "front":
        c.line(4, 20 - a, 4, 27, BROWN, 2); c.rect(3, 19 - a, 6, 19 - a, BROWN); c.px(3, 20 - a, BROWN)
        poly(c, [(21, 20 + a), (26, 20 + a), (27, 26 + a), (21, 26 + a)], (200, 190, 150), dither=BROWN)
        c.pts([(22, 22 + a), (24, 23 + a), (23, 25 + a), (26, 24 + a)], BLACK); c.line(23, 18 + a, 22, 20 + a, BROWN)
    elif v == "side":
        c.line(8 + a, 20, 7 + a, 27, BROWN, 2); c.rect(6 + a, 19, 9 + a, 19, BROWN); poly(c, [(15 - a, 21), (21 - a, 21), (21 - a, 27), (15 - a, 27)], (200, 190, 150), dither=BROWN); c.pts([(16 - a, 23), (18 - a, 25), (20 - a, 24)], BLACK)
    else:
        c.line(24, 20 - a, 24, 27, BROWN, 2); poly(c, [(2, 20 + a), (7, 20 + a), (7, 26 + a), (2, 26 + a)], (200, 190, 150), dither=BROWN); c.pts([(3, 22 + a), (5, 24 + a)], BLACK)
GRAN = mk(skin=(240, 195, 165), skin_dark=(210, 150, 120), coat=FLORAL, coat2=(210, 170, 245), pants=(240, 195, 165), pants2=(220, 170, 140), boots=(150, 70, 90), shade=PURPLE, hi=WHITE,
          w=13, hem=23, hat=gran_hat, face_x=gran_face, torso=gran_torso, arms_x=gran_arms, brow=False, mouth=False, sleeve=FLORAL)

# ================= ГОЛУБЬ (особый: птица) =================
def pigeon(view, t):
    c = Canvas(CV, CV); b = 1 if t in (1, 3) else 0
    BL = (150, 160, 190); BD = (105, 115, 150); BW = (225, 230, 240)
    st = [-2, 0, 2, 0][t]
    if view == "side":
        c.rect(12 + st, 21, 12 + st, 26, PINK); c.rect(17 - st, 21, 17 - st, 26, PINK); c.line(9 + st, 27, 12 + st, 27, PINK); c.line(14 - st, 27, 17 - st, 27, PINK)
        c.line(20, 17 + b, 27, 22 + b, BD, 3); poly(c, [(22, 16 + b), (27, 20 + b), (24, 24 + b), (21, 20 + b)], BD)                   # хвост
        c.ell(14, 17 + b, 8.5, 6, BL, dither=BD); c.ell(12, 19 + b, 5, 3, BW)
        poly(c, [(12, 13 + b), (20, 15 + b), (19, 21 + b), (11, 19 + b)], BD); c.rect(13, 16 + b, 19, 16 + b, BW); c.rect(12, 18 + b, 18, 18 + b, BW)  # крыло с полосами
        c.ell(9, 9 + b, 4.5, 4.5, BL); c.ell(8, 12 + b, 4, 3.5, (60, 170, 130)); c.ell(9, 13 + b, 3, 2.5, (150, 70, 190))              # шея: зелёно-фиолетовый перелив
        poly(c, [(4, 8 + b), (1, 10 + b), (4, 11 + b)], ORANGE); c.px(2, 10 + b, (190, 110, 0))                                      # клюв
        c.ell(7, 8 + b, 1.6, 1.6, ORANGE); c.px(7, 8 + b, BLACK); c.px(6, 7 + b, WHITE)                                               # безумный глаз
        c.ell(10, 5 + b, 1.4, 1.4, RED); c.px(10, 5 + b, YELLOW)                                                                      # третий глаз
    elif view == "back":
        c.rect(11 + st, 21, 12 + st, 26, PINK); c.rect(16 - st, 21, 17 - st, 26, PINK); c.line(9 + st, 27, 13 + st, 27, PINK); c.line(15 - st, 27, 19 - st, 27, PINK)
        poly(c, [(11, 20 + b), (17, 20 + b), (19, 27), (9, 27)], BD); c.rect(11, 25, 17, 26, BW)                                    # хвост
        c.ell(14, 16 + b, 8, 7, BL, dither=BD); poly(c, [(6, 12 + b), (22, 12 + b), (20, 22 + b), (8, 22 + b)], BD); c.rect(7, 15 + b, 21, 15 + b, BW); c.rect(8, 18 + b, 20, 18 + b, BW)
        c.ell(14, 8 + b, 4.5, 4.5, BL); c.ell(14, 12 + b, 5, 2.5, (60, 170, 130)); c.ell(14, 11 + b, 3, 1.5, (150, 70, 190))
    else:
        c.rect(11 + st, 21, 12 + st, 26, PINK); c.rect(16 - st, 21, 17 - st, 26, PINK); c.line(9 + st, 27, 13 + st, 27, PINK); c.line(15 - st, 27, 19 - st, 27, PINK)
        c.ell(14, 17 + b, 7, 6.5, BL, dither=BD); c.ell(14, 19 + b, 4.5, 4, BW); poly(c, [(5, 13 + b), (9, 14 + b), (9, 22 + b), (6, 21 + b)], BD); poly(c, [(23, 13 + b), (19, 14 + b), (19, 22 + b), (22, 21 + b)], BD)
        c.rect(5, 16 + b, 8, 16 + b, BW); c.rect(20, 16 + b, 23, 16 + b, BW); c.ell(14, 11 + b, 5, 3, (60, 170, 130)); c.ell(14, 12 + b, 3, 2, (150, 70, 190))
        c.ell(14, 7 + b, 4.6, 4.6, BL); poly(c, [(13, 8 + b), (15, 8 + b), (14, 12 + b)], ORANGE); c.rect(13, 8 + b, 15, 9 + b, ORANGE)
        c.ell(11, 7 + b, 1.6, 1.6, ORANGE); c.ell(17, 7 + b, 1.6, 1.6, ORANGE); c.px(11, 7 + b, BLACK); c.px(17, 7 + b, BLACK); c.ell(14, 3.5 + b, 1.4, 1.4, RED); c.px(14, 3 + b, YELLOW)
    return c.finish(PURPLE, WHITE, lim=0.35)
PIGEON = mk(draw=pigeon)


# ================= КАЛЬМАР-ГОПНИК =================
BLU = (60, 120, 255); BLU2 = (30, 70, 200)
def squid_hat(c, v, t, b):
    # кепка набекрень
    c.ell(14, 2.5 + b, 7, 3.2, (30, 30, 40)); c.rect(7, 2 + b, 21, 4 + b, (30, 30, 40))
    if v == "side": c.rect(4, 4 + b, 11, 5 + b, (30, 30, 40)); c.px(12, 2 + b, WHITE)
    elif v == "front": c.rect(4, 4 + b, 17, 5 + b, (30, 30, 40)); c.px(10, 2 + b, WHITE); c.pts([(12, 1 + b)], LGREY)
    else: c.rect(9, 4 + b, 19, 4 + b, (30, 30, 40)); c.px(14, 5 + b, (60, 60, 70))
    c.pts([(8, 1 + b), (9, 0 + b)], WHITE) if v != "back" else None
def squid_face(c, v, t, b):
    # щупальца вместо бороды, бычок во рту, уверенный прищур
    if v == "front":
        for i, x in enumerate((9, 12, 15, 18)):
            wob = (i + t) % 2; c.line(x, 11 + b, x + (1 if wob else -1), 18 + b, BLU2, 2); c.px(x + (1 if wob else -1), 19 + b, PINK)
        c.rect(14, 12 + b, 19, 12 + b, WHITE); c.rect(19, 12 + b, 20, 12 + b, ORANGE); c.px(21, 11 + b, GREY) if t % 2 else c.px(21, 10 + b, GREY)
        c.line(9, 6 + b, 12, 6 + b, BLU2); c.line(16, 6 + b, 19, 6 + b, BLU2)
    elif v == "side":
        for i, x in enumerate((9, 11, 13)):
            wob = (i + t) % 2; c.line(x, 11 + b, x - wob, 18 + b, BLU2, 2); c.px(x - wob, 19 + b, PINK)
        c.rect(5, 12 + b, 8, 12 + b, WHITE); c.rect(4, 12 + b, 4, 12 + b, ORANGE); c.pts([(3, 11 + b)], GREY)
def squid_torso(c, v, t, b):
    # адидас: чёрная олимпийка с белыми лампасами и молнией
    if v == "front": c.rect(8, 12 + b, 9, 22, WHITE); c.rect(18, 12 + b, 19, 22, WHITE); c.line(14, 12 + b, 14, 22, WHITE); c.pts([(12, 14 + b), (16, 14 + b)], WHITE)
    elif v == "side": c.rect(10, 12 + b, 11, 22, WHITE); c.rect(17, 12 + b, 18, 22, WHITE) if False else None
    else: c.rect(8, 12 + b, 9, 22, WHITE); c.rect(18, 12 + b, 19, 22, WHITE); c.pts([(12, 15 + b), (14, 15 + b), (16, 15 + b)], WHITE)
def squid_legs(c, v, t, b):
    if v == "side": c.rect(11, 21, 12, 25, WHITE)
    else: c.rect(9, 21, 9, 25, WHITE); c.rect(18, 21, 18, 25, WHITE)
SQUID = mk(skin=BLU, skin_dark=BLU2, coat=(25, 25, 35), coat2=(45, 45, 60), pants=(25, 25, 35), pants2=(35, 35, 45), boots=WHITE, shade=PURPLE, hi=CYAN, w=13, hem=22,
           hat=squid_hat, face_x=squid_face, torso=squid_torso, legs_x=squid_legs, sleeve=(25, 25, 35), brow=False, mouth=False, hair=BLU2)

# ================= ОФИСНЫЙ КЛЕРК =================
def clerk_hat(c, v, t, b):
    # жидкая причёска
    c.ell(14, 2.5 + b, 6.5, 3, (90, 60, 40)); c.rect(8, 2 + b, 20, 3 + b, (90, 60, 40))
    if v == "side": c.rect(14, 3 + b, 19, 8 + b, (90, 60, 40))
    if v == "back": c.rect(8, 3 + b, 20, 9 + b, (90, 60, 40))
    if v == "front": c.pts([(10, 4 + b), (13, 4 + b), (17, 4 + b)], (90, 60, 40)); c.pts([(8, 4 + b), (20, 4 + b)], (90, 60, 40))
def clerk_face(c, v, t, b):
    # очки-линзы, мешки под глазами
    if v == "front":
        c.rect(8, 5 + b, 13, 10 + b, BLACK) if False else None
        ringc(c, 11, 7.5 + b, 2.8, BLACK, 1); ringc(c, 17, 7.5 + b, 2.8, BLACK, 1); c.rect(13, 7 + b, 14, 7 + b, BLACK); c.pts([(10, 6 + b), (16, 6 + b)], WHITE)
        c.pts([(9, 10 + b), (10, 10 + b), (11, 10 + b), (16, 10 + b), (17, 10 + b), (18, 10 + b)], (170, 120, 150)); c.pts([(13, 12 + b), (15, 12 + b)], (150, 80, 70))
    elif v == "side": ringc(c, 11.5, 7 + b, 2.8, BLACK, 1); c.line(14, 7 + b, 18, 6 + b, BLACK); c.pts([(10, 10 + b), (11, 10 + b)], (170, 120, 150))
def clerk_torso(c, v, t, b):
    # красный галстук, бейдж на шнурке, воротник
    if v == "front":
        poly(c, [(12, 13 + b), (16, 13 + b), (15, 14 + b), (14, 21), (13, 14 + b)], WHITE) if False else None
        c.rect(12, 12 + b, 16, 13 + b, WHITE); poly(c, [(13, 13 + b), (15, 13 + b), (15, 15 + b), (14, 16 + b), (13, 15 + b)], RED); poly(c, [(13, 16 + b), (15, 16 + b), (16, 21), (14, 22), (12, 21)], RED)
        c.line(11, 13 + b, 12, 20, DGREY) if False else None; c.rect(17, 17 + b, 19, 20, WHITE); c.rect(17, 17 + b, 19, 17 + b, BLUE); c.px(18, 19, BLACK)
        c.pts([(10, 14 + b), (10, 17 + b), (10, 20)], LGREY)
    elif v == "side": c.rect(10, 12 + b, 11, 13 + b, WHITE); poly(c, [(11, 14 + b), (13, 14 + b), (13, 20), (11, 20)], RED); c.rect(14, 16 + b, 16, 19, WHITE)
    else: c.rect(8, 12 + b, 19, 13 + b, WHITE); c.rect(10, 13 + b, 17, 14 + b, LGREY)
CLERK = mk(skin=(240, 200, 170), skin_dark=(205, 155, 125), coat=WHITE, coat2=(225, 225, 235), pants=(70, 75, 90), pants2=(55, 60, 75), boots=BLACK, shade=BLUE, hi=WHITE, w=12, hem=22,
           hat=clerk_hat, face_x=clerk_face, torso=clerk_torso, sleeve=WHITE, brow=True, mouth=False)

# ================= ДВОРНИК =================
ORG = (255, 140, 0)
def jan_hat(c, v, t, b):
    # кепка с козырьком, седые усы вынесены в лицо
    c.ell(14, 2.5 + b, 6.5, 3.2, (60, 70, 100)); c.rect(7, 2 + b, 21, 4 + b, (60, 70, 100))
    if v == "side": c.rect(3, 4 + b, 10, 5 + b, (45, 55, 80))
    elif v == "front": c.rect(8, 4 + b, 20, 5 + b, (45, 55, 80)); c.pts([(14, 2 + b)], YELLOW)
def jan_face(c, v, t, b):
    if v == "front": c.rect(9, 10 + b, 19, 11 + b, LGREY); c.pts([(9, 12 + b), (19, 12 + b)], LGREY); c.pts([(11, 8 + b), (17, 8 + b)], (190, 130, 100))
    elif v == "side": c.rect(5, 10 + b, 10, 11 + b, LGREY); c.pts([(10, 12 + b)], LGREY)
def jan_torso(c, v, t, b):
    # оранжевый жилет с полосами-светоотражателями
    if v == "front":
        c.rect(8, 12 + b, 11, 22, ORG); c.rect(17, 12 + b, 19, 22, ORG); c.rect(12, 12 + b, 16, 22, (90, 100, 80))
        for y in (16, 20): c.rect(8, y, 19, y, (230, 255, 130)); c.rect(8, y + 1, 19, y + 1, WHITE) if False else None
    elif v == "side": c.rect(10, 12 + b, 18, 22, ORG); c.rect(10, 16, 18, 16, (230, 255, 130)); c.rect(10, 20, 18, 20, (230, 255, 130))
    else: c.rect(8, 12 + b, 19, 22, ORG); c.rect(8, 16, 19, 16, (230, 255, 130)); c.rect(8, 20, 19, 20, (230, 255, 130)); c.line(11, 12, 16, 12, ORG) if False else None
def jan_arms(c, v, t, b):
    # метла
    a = [-2, 0, 2, 0][t] // 2
    if v == "front": c.line(24, 8 + a, 24, 26, BROWN, 2); poly(c, [(22, 22 + a), (27, 22 + a), (28, 28), (21, 28)], (210, 180, 60), dither=BROWN); c.pts([(22, 26), (25, 27)], BROWN)
    elif v == "side": c.line(8 + a, 8, 8 + a, 25, BROWN, 2); poly(c, [(6 + a, 21), (11 + a, 21), (12 + a, 27), (5 + a, 27)], (210, 180, 60), dither=BROWN)
    else: c.line(4, 8 + a, 4, 26, BROWN, 2); poly(c, [(2, 22 + a), (7, 22 + a), (8, 28), (1, 28)], (210, 180, 60), dither=BROWN)
JAN = mk(skin=(225, 170, 130), skin_dark=(190, 130, 95), coat=(95, 105, 85), coat2=(75, 85, 65), pants=(60, 65, 80), pants2=(45, 50, 65), boots=(30, 90, 40), shade=PURPLE, hi=YELLOW, w=13, hem=22,
         hat=jan_hat, face_x=jan_face, torso=jan_torso, arms_x=jan_arms, sleeve=(95, 105, 85), brow=True, mouth=False)

# ================= ДЯДЯ ВИТЯ =================
def vit_hat(c, v, t, b):
    # лысина с редкими прядями
    c.ell(14, 2 + b, 6, 2.2, (235, 175, 140)); c.rect(8, 3 + b, 9, 7 + b, (110, 90, 75)) if v != "side" else None; c.rect(19, 3 + b, 20, 7 + b, (110, 90, 75)) if v != "side" else None
    c.pts([(12, 0 + b), (14, 0 + b), (16, 1 + b)], (110, 90, 75))
    if v == "side": c.rect(16, 3 + b, 20, 8 + b, (110, 90, 75))
    if v == "back": c.rect(8, 3 + b, 20, 8 + b, (235, 175, 140)); c.rect(8, 6 + b, 20, 9 + b, (110, 90, 75))
def vit_face(c, v, t, b):
    # щетина, красный нос, мутный взгляд
    if v == "front":
        c.ell(14, 9 + b, 2, 1.6, (245, 90, 90)); c.rect(9, 10 + b, 19, 13 + b, (150, 130, 120), dither=SKIN) if False else None
        for x, y in [(9, 11), (11, 12), (13, 13), (15, 13), (17, 12), (19, 11), (10, 10), (18, 10)]: c.px(x, y + b, (90, 75, 65))
        c.pts([(10, 5 + b), (17, 5 + b)], (200, 140, 120))
    elif v == "side": c.ell(7.5, 9 + b, 1.8, 1.5, (245, 90, 90)); [c.px(x, y + b, (90, 75, 65)) for x, y in [(9, 11), (11, 12), (13, 12), (10, 10)]]
def vit_torso(c, v, t, b):
    # майка-алкоголичка с лямками, бутылка торчит из кармана штанов
    if v == "front":
        c.rect(8, 12 + b, 10, 13 + b, (235, 175, 140)); c.rect(17, 12 + b, 19, 13 + b, (235, 175, 140)); c.ell(14, 12 + b, 3.5, 2, (235, 175, 140)); c.pts([(12, 17 + b), (15, 18 + b), (11, 20), (16, 21)], (205, 205, 205))
        poly(c, [(17, 19), (20, 19), (20, 24), (17, 24)], GREEN); c.rect(18, 17, 19, 19, GREEN); c.px(18, 16, WHITE)
    elif v == "side": c.rect(10, 12 + b, 11, 13 + b, (235, 175, 140)); c.pts([(12, 17 + b), (14, 19)], (205, 205, 205)); poly(c, [(15, 19), (17, 19), (17, 24), (15, 24)], GREEN)
    else: c.rect(8, 12 + b, 10, 13 + b, (235, 175, 140)); c.rect(17, 12 + b, 19, 13 + b, (235, 175, 140)); c.rect(8, 12 + b, 19, 14 + b, (235, 175, 140)); c.pts([(13, 18), (15, 20)], (205, 205, 205))
VITYA = mk(skin=(240, 175, 140), skin_dark=(205, 130, 100), coat=(240, 240, 240), coat2=(205, 205, 205), pants=(60, 80, 130), pants2=(45, 60, 105), boots=(70, 50, 40), shade=PURPLE, hi=WHITE, w=12, hem=22,
             hat=vit_hat, face_x=vit_face, torso=vit_torso, sleeve=(240, 175, 140), brow=True, mouth=True)

# ================= БЛОГЕР-ЗОМБИ =================
ZG = (110, 200, 110); ZG2 = (70, 150, 80)
def blog_hat(c, v, t, b):
    # розовые волосы, зачёс
    c.ell(14, 2.5 + b, 7, 3.5, PINK); c.rect(7, 2 + b, 21, 5 + b, PINK)
    if v == "side": c.rect(14, 3 + b, 20, 11 + b, PINK); c.rect(8, 3 + b, 10, 5 + b, PINK)
    if v == "back": c.rect(7, 3 + b, 21, 11 + b, PINK); c.pts([(9, 11 + b), (18, 12 + b)], PINK)
    if v == "front": c.rect(7, 4 + b, 9, 10 + b, PINK); c.rect(19, 4 + b, 21, 10 + b, PINK); c.pts([(11, 5 + b), (14, 5 + b), (17, 5 + b)], (255, 120, 245))
    c.pts([(10, 1 + b), (13, 0 + b), (17, 1 + b)], WHITE)
def blog_face(c, v, t, b):
    if v == "front":
        c.rect(9, 9 + b, 12, 9 + b, (60, 90, 100)); c.rect(16, 9 + b, 19, 9 + b, (60, 90, 100)); c.pts([(11, 7 + b), (17, 7 + b)], RED)
        c.rect(12, 12 + b, 16, 12 + b, BLACK); c.pts([(13, 12 + b), (15, 12 + b)], WHITE); c.pts([(9, 11 + b)], (60, 90, 100)); c.px(19, 10 + b, ZG2)
    elif v == "side": c.rect(9, 9 + b, 12, 9 + b, (60, 90, 100)); c.px(11, 6 + b, RED); c.pts([(18, 10 + b)], ZG2)
def blog_torso(c, v, t, b):
    # золотая цепь, неоновый воротник худи
    if v == "front": c.line(10, 13 + b, 13, 17 + b, GOLD); c.line(18, 13 + b, 15, 17 + b, GOLD); c.rect(13, 17 + b, 15, 18 + b, GOLD); c.px(14, 19 + b, GOLD); c.pts([(9, 14 + b), (19, 14 + b)], CYAN)
    elif v == "side": c.line(11, 13 + b, 12, 17 + b, GOLD); c.rect(11, 12 + b, 12, 12 + b, CYAN)
    else: c.rect(9, 12 + b, 18, 13 + b, CYAN)
def blog_arms(c, v, t, b):
    # светящийся смартфон
    if v == "front": c.rect(20, 17, 24, 23, BLACK); c.rect(21, 18, 23, 22, (120, 255, 255)); c.pts([(22, 19), (22, 21)], WHITE); c.pts([(24, 16), (25, 17)], CYAN)
    elif v == "side": c.rect(9, 19, 12, 24, BLACK); c.rect(9, 20, 11, 23, (120, 255, 255)); c.px(8, 18, CYAN)
    else: c.rect(4, 17, 8, 23, BLACK); c.pts([(4, 16)], CYAN)
BLOG = mk(skin=ZG, skin_dark=ZG2, coat=(35, 35, 55), coat2=(55, 55, 85), pants=(25, 25, 40), pants2=(35, 35, 55), boots=(240, 240, 240), shade=PURPLE, hi=CYAN, w=12, hem=22,
          hat=blog_hat, face_x=blog_face, torso=blog_torso, arms_x=blog_arms, sleeve=(35, 35, 55), brow=False, mouth=False)

# ================= КУРЬЕР =================
YEL = (255, 220, 0)
def cour_hat(c, v, t, b):
    c.ell(14, 2.5 + b, 6.5, 3.2, (40, 170, 60)); c.rect(7, 2 + b, 21, 4 + b, (40, 170, 60))
    if v == "side": c.rect(3, 4 + b, 10, 5 + b, (25, 120, 40))
    elif v == "front": c.rect(8, 4 + b, 20, 5 + b, (25, 120, 40)); c.rect(12, 2 + b, 16, 3 + b, YELLOW)
    else: c.rect(11, 2 + b, 17, 3 + b, YELLOW)
def cour_torso(c, v, t, b):
    # зелёная куртка со светоотражающей полосой, огромный жёлтый короб на спине
    if v == "front": c.rect(8, 18, 19, 18, (230, 255, 130)); c.line(14, 12 + b, 14, 22, (25, 120, 40)); c.rect(8, 12, 9, 13, YELLOW) if False else None; c.pts([(9, 14 + b), (19, 14 + b)], (25, 120, 40)); c.line(8, 12 + b, 6, 8 + b, YEL) if False else None
def cour_extra(c, v, t, b):
    if v == "back":
        poly(c, [(5, 9 + b), (23, 9 + b), (23, 24), (5, 24)], YEL, dither=ORANGE); c.rect(5, 9 + b, 23, 10 + b, ORANGE); c.rect(13, 9 + b, 15, 24, BROWN); c.rect(5, 15, 23, 16, (200, 150, 0)); c.pts([(8, 12 + b), (19, 13 + b)], WHITE); c.rect(8, 19, 11, 22, WHITE); c.rect(9, 20, 10, 21, RED) if False else None
        c.rect(15, 18, 19, 21, RED); c.rect(16, 19, 18, 20, WHITE)
    elif v == "side":
        poly(c, [(16, 9 + b), (25, 9 + b), (25, 24), (16, 24)], YEL, dither=ORANGE); c.rect(16, 9 + b, 25, 10 + b, ORANGE); c.rect(16, 15, 25, 16, (200, 150, 0)); c.rect(19, 18, 22, 21, RED)
    else:
        c.line(8, 12 + b, 6, 8 + b, YEL); c.line(19, 12 + b, 21, 8 + b, YEL); c.pts([(5, 7 + b), (22, 7 + b)], YEL)   # лямки/уголки короба из-за плеч
COUR = mk(skin=(240, 190, 150), skin_dark=(205, 145, 110), coat=(40, 170, 60), coat2=(30, 135, 50), pants=(40, 45, 60), pants2=(30, 35, 50), boots=(250, 250, 250), shade=PURPLE, hi=YELLOW, w=12, hem=22,
          hat=cour_hat, torso=cour_torso, extra=cour_extra, sleeve=(40, 170, 60), brow=True, mouth=True)

# ================= ПАНК-КРЫСА =================
RAT = (150, 150, 160); RAT2 = (105, 105, 120)
def punk_hat(c, v, t, b):
    # зелёный ирокез + розовые уши
    for x in range(9, 20, 2): c.line(x, 4 + b, x, 0 - (x % 3) + b, GREEN, 2)
    c.rect(9, 3 + b, 19, 4 + b, GREEN)
    if v == "front": c.ell(8.5, 4 + b, 2.2, 2.6, PINK); c.ell(19.5, 4 + b, 2.2, 2.6, PINK); c.px(8, 4 + b, (200, 0, 190)); c.px(20, 4 + b, (200, 0, 190))
    if v == "side": c.ell(15, 4 + b, 2.2, 2.6, PINK)
    if v == "back": c.ell(8.5, 4 + b, 2.2, 2.6, PINK); c.ell(19.5, 4 + b, 2.2, 2.6, PINK)
def punk_face(c, v, t, b):
    # крысиная морда, жёлтые зубы, усы
    if v == "front":
        poly(c, [(11, 9 + b), (17, 9 + b), (16, 13 + b), (12, 13 + b)], (190, 180, 190)); c.ell(14, 9 + b, 1.3, 1, PINK); c.rect(12, 12 + b, 13, 14 + b, YELLOW); c.rect(15, 12 + b, 16, 14 + b, YELLOW); c.rect(14, 12 + b, 14, 13 + b, BLACK)
        c.pts([(7, 10 + b), (8, 11 + b), (20, 11 + b), (21, 10 + b)], WHITE)
    elif v == "side":
        poly(c, [(8, 9 + b), (3, 11 + b), (8, 13 + b)], (190, 180, 190)); c.ell(3, 11 + b, 1.2, 1.2, PINK); c.rect(6, 12 + b, 7, 14 + b, YELLOW); c.pts([(2, 9 + b), (1, 12 + b), (2, 13 + b)], WHITE)
def punk_torso(c, v, t, b):
    # кожанка с заклёпками и косой молнией
    if v == "front": c.line(10, 12 + b, 18, 22, LGREY); [c.px(x, y + b, WHITE) for x, y in [(9, 13), (18, 13), (9, 17), (18, 18), (10, 21), (17, 21)]]; c.pts([(12, 15 + b)], RED)
    elif v == "side": [c.px(x, y + b, WHITE) for x, y in [(11, 14), (11, 18), (16, 16)]]
    else: [c.px(x, y + b, WHITE) for x, y in [(9, 13), (18, 13), (13, 16), (9, 19), (18, 19)]]; c.pts([(12, 14 + b), (13, 14 + b), (14, 14 + b), (15, 14 + b)], PINK)
def punk_extra(c, v, t, b):
    # хвост торчит как протест
    w = [0, 1, 0, -1][t]
    if v == "side": c.line(18, 22, 22, 20 + w, PINK, 2); c.line(22, 20 + w, 24, 15 + w, PINK, 2); c.px(24, 14 + w, PINK)
    elif v == "back": c.line(14, 23, 20, 25 + w, PINK, 2); c.line(20, 25 + w, 23, 21, PINK, 2)
    else: c.line(19, 23, 23, 24 + w, PINK, 2)
PUNK = mk(skin=RAT, skin_dark=RAT2, coat=(30, 30, 35), coat2=(55, 55, 60), pants=(60, 20, 70), pants2=(45, 10, 55), boots=(60, 20, 20), shade=PURPLE, hi=GREEN, w=12, hem=22,
          hat=punk_hat, face_x=punk_face, torso=punk_torso, extra=punk_extra, sleeve=(30, 30, 35), brow=True, mouth=False)

# ================= ШАУРМИСТ =================
def shaw_hat(c, v, t, b):
    # высокий поварской колпак
    c.rect(8, 2 + b, 20, 4 + b, WHITE); poly(c, [(8, 2 + b), (20, 2 + b), (22, -1), (19, -3), (14, -4), (9, -3), (6, -1)], WHITE, dither=LGREY) if False else None
    c.ell(14, 0 + b, 8, 3.5, WHITE, dither=(225, 225, 235)); c.rect(9, 0 + b, 19, 3 + b, WHITE); c.rect(8, 3 + b, 20, 4 + b, LGREY); c.pts([(10, 0 + b), (14, -1 + b)], (230, 230, 240))
def shaw_face(c, v, t, b):
    # густые усищи
    if v == "front": poly(c, [(9, 10 + b), (14, 9 + b), (19, 10 + b), (19, 12 + b), (14, 11 + b), (9, 12 + b)], (30, 25, 25)); c.pts([(9, 11 + b), (19, 11 + b)], (60, 50, 50))
    elif v == "side": poly(c, [(6, 10 + b), (11, 10 + b), (11, 12 + b), (5, 12 + b)], (30, 25, 25))
def shaw_torso(c, v, t, b):
    # фартук в пятнах, золотая цепь
    if v == "front":
        c.rect(9, 15 + b, 18, 22, WHITE); c.rect(9, 15 + b, 18, 15 + b, LGREY); c.pts([(11, 17 + b), (12, 17 + b), (15, 20), (16, 20), (13, 22)], (190, 120, 40)); c.pts([(10, 19), (17, 18)], RED); c.px(14, 21, GREEN)
        c.line(10, 13 + b, 14, 17 + b, GOLD); c.line(18, 13 + b, 14, 17 + b, GOLD); c.px(14, 18 + b, GOLD)
    elif v == "side": c.rect(10, 15 + b, 14, 22, WHITE); c.pts([(11, 17 + b), (12, 20)], (190, 120, 40)); c.line(11, 13 + b, 12, 16 + b, GOLD)
    else: c.rect(9, 12 + b, 18, 13 + b, LGREY); c.line(14, 13, 14, 22, LGREY); c.pts([(10, 17), (17, 19)], (190, 120, 40))
SHAW = mk(skin=(225, 165, 120), skin_dark=(185, 125, 90), coat=(70, 70, 85), coat2=(55, 55, 70), pants=(35, 35, 50), pants2=(25, 25, 40), boots=BLACK, shade=PURPLE, hi=WHITE, w=13, hem=22,
          hat=shaw_hat, face_x=shaw_face, torso=shaw_torso, sleeve=WHITE, brow=True, mouth=False)

# ================= ОХРАННИК =================
NAVY = (25, 35, 100)
def guard_hat(c, v, t, b):
    # фуражка с кокардой
    c.rect(6, 3 + b, 22, 5 + b, NAVY); c.ell(14, 2 + b, 8, 3, NAVY); c.rect(7, 4 + b, 21, 4 + b, (60, 70, 140)); c.ell(14, 2 + b, 4, 1.5, (60, 70, 140)) if False else None
    if v == "front": c.rect(10, 5 + b, 18, 5 + b, BLACK); c.rect(13, 2 + b, 15, 4 + b, GOLD); c.px(14, 3 + b, RED)
    elif v == "side": c.rect(3, 5 + b, 11, 5 + b, BLACK); c.rect(10, 3 + b, 11, 4 + b, GOLD)
    else: c.rect(8, 5 + b, 20, 5 + b, BLACK)
def guard_face(c, v, t, b):
    if v == "front": c.rect(10, 10 + b, 18, 10 + b, (60, 45, 35)); c.pts([(9, 11 + b), (19, 11 + b)], (60, 45, 35)); c.rect(12, 12 + b, 16, 12 + b, BLACK)
    elif v == "side": c.rect(6, 10 + b, 10, 10 + b, (60, 45, 35)); c.rect(6, 11 + b, 8, 11 + b, (60, 45, 35))
def guard_torso(c, v, t, b):
    # ремень, бляха, дубинка на поясе, погоны
    if v == "front": c.rect(8, 18, 19, 19, BLACK); c.rect(13, 18, 15, 19, GOLD); c.rect(8, 12 + b, 10, 12 + b, GOLD); c.rect(17, 12 + b, 19, 12 + b, GOLD); c.rect(19, 19, 20, 24, BLACK); c.px(19, 25, LGREY); c.pts([(12, 14 + b), (16, 14 + b)], (60, 70, 140)); c.rect(10, 15 + b, 12, 16 + b, GOLD) if False else None
    elif v == "side": c.rect(10, 18, 18, 19, BLACK); c.rect(14, 18, 15, 19, GOLD); c.rect(16, 19, 17, 24, BLACK)
    else: c.rect(8, 18, 19, 19, BLACK); c.rect(18, 19, 20, 24, BLACK); c.rect(8, 12 + b, 10, 12 + b, GOLD); c.rect(17, 12 + b, 19, 12 + b, GOLD)
GUARD = mk(skin=(235, 185, 150), skin_dark=(200, 140, 110), coat=NAVY, coat2=(20, 28, 80), pants=(20, 25, 70), pants2=(15, 20, 55), boots=BLACK, shade=BLUE, hi=WHITE, w=13, hem=22,
           hat=guard_hat, face_x=guard_face, torso=guard_torso, sleeve=NAVY, brow=True, mouth=False)

# ================= СТУДЕНТ =================
PUR = (130, 60, 200)
def stud_hat(c, v, t, b):
    # всклокоченная шевелюра
    c.ell(14, 2 + b, 7, 3.5, (60, 45, 35)); c.rect(7, 2 + b, 21, 4 + b, (60, 45, 35))
    for x in (8, 11, 14, 17, 20): c.line(x, 3 + b, x + ((x + t) % 3) - 1, -1 + b, (60, 45, 35), 2)
    if v == "side": c.rect(14, 3 + b, 20, 9 + b, (60, 45, 35))
    if v == "back": c.rect(7, 3 + b, 21, 9 + b, (60, 45, 35))
    if v == "front": c.pts([(9, 5 + b), (12, 5 + b), (16, 5 + b), (19, 5 + b)], (60, 45, 35))
def stud_face(c, v, t, b):
    if v == "front": c.pts([(9, 9 + b), (10, 9 + b), (11, 9 + b), (17, 9 + b), (18, 9 + b), (19, 9 + b)], (120, 90, 150)); c.pts([(13, 12 + b), (15, 12 + b)], (150, 70, 70))
    elif v == "side": c.pts([(10, 9 + b), (11, 9 + b)], (120, 90, 150))
def stud_torso(c, v, t, b):
    # худи: капюшон, карман-кенгуру, шнурки
    if v == "front": c.ell(14, 12 + b, 5, 2, (100, 40, 170)); c.rect(10, 18, 17, 21, (100, 40, 170)); c.pts([(12, 14 + b), (12, 16 + b), (16, 14 + b), (16, 16 + b)], WHITE); c.line(10, 21, 17, 21, (80, 25, 140))
    elif v == "side": c.rect(10, 12 + b, 12, 14 + b, (100, 40, 170)); c.rect(11, 18, 16, 21, (100, 40, 170))
    else: c.ell(14, 14 + b, 6, 3, (100, 40, 170)); c.rect(8, 13 + b, 19, 14 + b, (100, 40, 170))
def stud_arms(c, v, t, b):
    # банка энергетика в кулаке
    if v == "front": c.rect(21, 17, 25, 24, (30, 30, 40)); c.rect(21, 17, 25, 18, MG); c.pts([(23, 20), (22, 21), (23, 22)], YELLOW); c.rect(21, 24, 25, 24, MG); c.rect(22, 16, 24, 16, LGREY)
    elif v == "side": c.rect(8, 18, 11, 24, (30, 30, 40)); c.rect(8, 18, 11, 18, MG); c.pts([(9, 20), (10, 22)], YELLOW)
    else: c.rect(3, 17, 7, 24, (30, 30, 40)); c.rect(3, 17, 7, 18, MG)
STUD = mk(skin=(235, 195, 165), skin_dark=(200, 150, 120), coat=PUR, coat2=(105, 45, 170), pants=(50, 55, 75), pants2=(38, 42, 62), boots=(230, 230, 230), shade=PURPLE, hi=WHITE, w=13, hem=22,
          hat=stud_hat, face_x=stud_face, torso=stud_torso, arms_x=stud_arms, sleeve=PUR, brow=False, mouth=False)

# ================= САНТЕХНИК =================
def plum_hat(c, v, t, b):
    c.ell(14, 2.5 + b, 6.5, 3.2, RED); c.rect(7, 2 + b, 21, 4 + b, RED)
    if v == "side": c.rect(3, 4 + b, 10, 5 + b, (170, 0, 30))
    elif v == "front": c.rect(8, 4 + b, 20, 5 + b, (170, 0, 30)); c.ell(14, 3 + b, 2, 1.4, WHITE); c.px(14, 3 + b, RED)
    else: c.rect(10, 4 + b, 18, 4 + b, (170, 0, 30))
def plum_face(c, v, t, b):
    if v == "front": poly(c, [(8, 10 + b), (14, 9 + b), (20, 10 + b), (21, 13 + b), (14, 11 + b), (7, 13 + b)], (45, 30, 20)); c.ell(14, 8 + b, 1.8, 1.4, (235, 120, 100))
    elif v == "side": poly(c, [(4, 10 + b), (11, 10 + b), (11, 13 + b), (3, 13 + b)], (45, 30, 20))
def plum_torso(c, v, t, b):
    # синий комбинезон на жёлтой футболке, лямки с пуговицами
    if v == "front": c.rect(8, 12 + b, 19, 14 + b, YEL); c.rect(8, 15 + b, 19, 22, BLUE2 if False else (40, 80, 220)); c.rect(9, 12 + b, 10, 15 + b, (40, 80, 220)); c.rect(17, 12 + b, 18, 15 + b, (40, 80, 220)); c.px(10, 15 + b, YELLOW); c.px(17, 15 + b, YELLOW); c.rect(11, 17, 16, 19, (30, 60, 190)); c.rect(11, 17, 16, 17, (20, 40, 150))
    elif v == "side": c.rect(10, 12 + b, 12, 14 + b, YEL); c.rect(11, 15 + b, 18, 22, (40, 80, 220)); c.rect(12, 17, 15, 19, (30, 60, 190))
    else: c.rect(8, 12 + b, 19, 14 + b, YEL); c.rect(9, 15 + b, 18, 22, (40, 80, 220)); c.rect(9, 12 + b, 10, 15 + b, (40, 80, 220)); c.rect(17, 12 + b, 18, 15 + b, (40, 80, 220))
def plum_arms(c, v, t, b):
    # гаечный ключ
    a = [-2, 0, 2, 0][t] // 2
    if v == "front": c.line(23, 26, 25, 15 + a, MG, 2); c.ell(25, 14 + a, 2.5, 2.5, LG); c.rect(25, 13 + a, 26, 14 + a, BLACK) if False else None; c.px(26, 13 + a, BLACK)
    elif v == "side": c.line(7 + a, 26, 6 + a, 17, MG, 2); c.ell(6 + a, 15, 2.5, 2.5, LG); c.px(5 + a, 15, BLACK)
    else: c.line(5, 26, 3, 15 + a, MG, 2); c.ell(3, 14 + a, 2.5, 2.5, LG)
PLUM = mk(skin=(235, 180, 140), skin_dark=(200, 135, 100), coat=(40, 80, 220), coat2=(30, 60, 190), pants=(40, 80, 220), pants2=(30, 60, 190), boots=(70, 45, 25), shade=BLUE, hi=WHITE, w=13, hem=22,
          hat=plum_hat, face_x=plum_face, torso=plum_torso, arms_x=plum_arms, sleeve=YEL, brow=True, mouth=False)

# ================= ДАЧНИЦА =================
def dacha_hat(c, v, t, b):
    # соломенная шляпа с цветами
    STR = (235, 200, 110); STR2 = (200, 160, 70)
    c.ell(14, 3 + b, 11, 2.5, STR, dither=STR2); c.ell(14, 1 + b, 6, 3, STR, dither=STR2); c.rect(8, 1 + b, 20, 3 + b, STR); c.rect(8, 2 + b, 20, 2 + b, PINK)
    for p, col in (((9, 2), RED), ((13, 0), YELLOW), ((18, 2), PINK), ((20, 3), WHITE)): c.px(p[0], p[1] + b, col); c.px(p[0] + 1, p[1] + b, col) if col != WHITE else None
    c.rect(3, 4 + b, 4, 4 + b, STR2); c.rect(24, 4 + b, 25, 4 + b, STR2)
    if v == "back": c.rect(8, 4 + b, 20, 9 + b, (180, 120, 70))
    if v == "side": c.rect(14, 4 + b, 19, 9 + b, (180, 120, 70))
def dacha_face(c, v, t, b):
    # румянец
    if v == "front": c.ell(9.5, 9 + b, 1.5, 1.2, (255, 120, 140)); c.ell(18.5, 9 + b, 1.5, 1.2, (255, 120, 140)); c.rect(13, 12 + b, 15, 12 + b, (190, 40, 80)); c.pts([(10, 6 + b), (18, 6 + b)], BLACK) if False else None
    elif v == "side": c.ell(10, 9 + b, 1.5, 1.2, (255, 120, 140)); c.rect(8, 12 + b, 10, 12 + b, (190, 40, 80))
def dacha_torso(c, v, t, b):
    # розовое платье в горошек, белый фартук, ведро в руке
    if v == "front":
        c.rect(9, 15 + b, 18, 23, WHITE); c.rect(10, 12 + b, 11, 15 + b, WHITE); c.rect(17, 12 + b, 18, 15 + b, WHITE); c.rect(9, 15 + b, 18, 15 + b, LGREY); c.pts([(12, 18), (15, 19), (13, 21)], (255, 150, 170))
        c.pts([(9, 14 + b), (18, 14 + b), (8, 18), (19, 20)], WHITE)
    elif v == "side": c.rect(11, 15 + b, 16, 23, WHITE); c.pts([(12, 18)], (255, 150, 170))
    else: c.rect(8, 12 + b, 19, 22, (255, 120, 170)); c.pts([(10, 14), (14, 17), (17, 14), (11, 20), (16, 21)], WHITE); c.rect(12, 15 + b, 16, 16 + b, WHITE)
def dacha_arms(c, v, t, b):
    a = [-2, 0, 2, 0][t] // 2
    if v == "front": poly(c, [(21, 20 - a), (27, 20 - a), (26, 27 - a), (22, 27 - a)], MG, dither=LG); c.rect(21, 19 - a, 27, 20 - a, GREY); c.line(21, 19 - a, 23, 16 - a, GREY); c.line(27, 19 - a, 25, 16 - a, GREY); c.rect(23, 22 - a, 25, 23 - a, DGREY); c.pts([(23, 18 - a), (24, 17 - a)], RED)
    elif v == "side": poly(c, [(8, 22), (14, 22), (13, 28), (9, 28)], MG, dither=LG); c.rect(8, 21, 14, 22, GREY); c.pts([(10, 20), (11, 19)], RED)
    else: poly(c, [(2, 21 + a), (8, 21 + a), (7, 27 + a), (3, 27 + a)], MG, dither=LG); c.rect(2, 20 + a, 8, 21 + a, GREY)
DACHA = mk(skin=(245, 200, 170), skin_dark=(215, 160, 130), coat=(255, 120, 170), coat2=(225, 85, 140), pants=(245, 200, 170), pants2=(215, 160, 130), boots=(40, 130, 60), shade=PURPLE, hi=WHITE, w=13, hem=23,
          hat=dacha_hat, face_x=dacha_face, torso=dacha_torso, arms_x=dacha_arms, sleeve=(255, 120, 170), brow=False, mouth=False)

# ================= СКЕЙТЕР =================
def skate_hat(c, v, t, b):
    # красный козырёк-кепка задом наперёд и наушники
    c.ell(14, 2.5 + b, 6.5, 3.2, RED); c.rect(7, 2 + b, 21, 4 + b, RED)
    if v == "side": c.rect(18, 4 + b, 24, 5 + b, (170, 0, 30)); c.ell(15, 8 + b, 3, 3.5, DGREY); c.ell(15, 8 + b, 1.6, 2, BLACK)
    elif v == "front": c.rect(7, 4 + b, 21, 4 + b, (170, 0, 30)); c.rect(6, 6 + b, 8, 11 + b, DGREY); c.rect(20, 6 + b, 22, 11 + b, DGREY); c.rect(7, 4 + b, 7, 6 + b, DGREY); c.rect(21, 4 + b, 21, 6 + b, DGREY)
    else: c.rect(8, 4 + b, 20, 5 + b, (170, 0, 30)); c.rect(9, 6 + b, 19, 6 + b, (170, 0, 30)); c.rect(6, 6 + b, 8, 11 + b, DGREY); c.rect(20, 6 + b, 22, 11 + b, DGREY)
def skate_face(c, v, t, b):
    if v == "front": c.pts([(13, 12 + b), (14, 12 + b), (15, 12 + b)], BLACK); c.px(12, 11 + b, BLACK); c.px(16, 11 + b, BLACK); c.pts([(9, 10 + b)], (80, 160, 60))
def skate_torso(c, v, t, b):
    # жёлтая футболка с принтом
    if v == "front": c.rect(11, 15 + b, 16, 19, BLACK); c.pts([(12, 16 + b), (14, 17 + b), (15, 16 + b), (13, 18)], YELLOW) if False else c.pts([(12, 16 + b), (14, 17 + b), (15, 16 + b), (13, 18)], RED)
    elif v == "side": c.rect(11, 15 + b, 16, 18, BLACK)
    else: c.rect(10, 14 + b, 17, 19, BLACK); c.pts([(12, 15 + b), (14, 17), (16, 15 + b)], RED)
def skate_legs(c, v, t, b):
    # колени в зелёнке
    if v == "side": c.pts([(12, 23), (13, 24)], (80, 220, 60))
    else: c.pts([(10, 23), (11, 24), (17, 23), (18, 24)], (80, 220, 60))
def skate_extra(c, v, t, b):
    # доска под мышкой
    if v == "front": poly(c, [(21, 14), (23, 14), (25, 26), (23, 27)], (200, 120, 40)); c.line(23, 15, 24, 25, BLACK); c.pts([(22, 17), (23, 20)], RED); c.ell(24, 19, 1, 1, DGREY); c.ell(24, 24, 1, 1, DGREY)
    elif v == "side": poly(c, [(15, 16), (23, 15), (24, 17), (15, 19)], (200, 120, 40)); c.line(15, 17, 23, 16, BLACK); c.ell(17, 20, 1.5, 1.5, DGREY); c.ell(22, 19, 1.5, 1.5, DGREY)
    else: poly(c, [(3, 14), (5, 14), (7, 26), (5, 27)], (200, 120, 40)); c.line(5, 15, 6, 25, BLACK); c.ell(4, 19, 1, 1, DGREY)
SKATE = mk(skin=(240, 195, 160), skin_dark=(205, 150, 120), coat=YEL, coat2=(220, 190, 0), pants=(60, 90, 140), pants2=(45, 70, 115), boots=(230, 230, 230), shade=PURPLE, hi=WHITE, w=12, hem=22,
           hat=skate_hat, face_x=skate_face, torso=skate_torso, legs_x=skate_legs, extra=skate_extra, sleeve=YEL, brow=False, mouth=False)

HEROES = {"hobo": HOBO, "squid": SQUID, "clerk": CLERK, "janitor": JAN, "uncle_vitya": VITYA, "blogger": BLOG, "granny": GRAN, "courier": COUR, "pigeon": PIGEON, "punk": PUNK, "shawarma": SHAW, "guard": GUARD, "student": STUD, "plumber": PLUM, "dacha": DACHA, "skater": SKATE}

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(HEROES)
    k = 4
    prev = Image.new("RGBA", (len(ids) * (128 * k // 1 + 20), 2 * 96 * k // 1 // 1 + 10), (45, 30, 20, 255))
    prev = Image.new("RGBA", (len(ids) * (128 * k // 2 + 20) * 1, 96 * k // 2 * 2 + 20), (45, 30, 20, 255)) if False else prev
    for i, n in enumerate(ids):
        im = Image.fromarray(sheet_for(HEROES[n]), "RGBA")
        if apply: im.save(f"assets/sprites/player_{n}.png")
        big = im.resize((im.width * 3, im.height * 3), Image.NEAREST); prev.paste(big, (i * (128 * k // 1 + 20) // 1 if False else 0, 0), None) if False else None
        x = (i % 1) * 0
        prev.paste(big, (10, 5 + i * (96 * 3 + 6)), big) if False else None
    # компактный превью: каждый герой отдельной строкой ×3
    prev = Image.new("RGBA", (128 * 3 + 20, len(ids) * (96 * 3 + 8) + 8), (45, 30, 20, 255))
    for i, n in enumerate(ids):
        im = Image.fromarray(sheet_for(HEROES[n]), "RGBA"); big = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
        prev.paste(big, (10, 6 + i * (96 * 3 + 8)), big)
    prev.save("tools/_preview/heroes_v3.png"); print(prev.size)
