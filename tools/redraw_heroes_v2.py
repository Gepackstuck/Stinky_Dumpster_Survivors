#!/usr/bin/env python3
"""Узнаваемые герои: единый «риг» (ноги, туловище, руки, голова) + набор шапок/лиц/аксессуаров на героя.
Листы 104×78 (4 кадра × [бок влево, спина, фас]). python3 tools/redraw_heroes_v2.py [--apply]"""
import sys, random, os
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
LGREY = (190, 190, 200); STEEL = (110, 130, 170); FUR = (150, 150, 155); NAVY = (20, 30, 100); TAN = (205, 150, 100)
GOLD = (255, 200, 0); ZOMBIE = (120, 200, 120); GRAYHAIR = (170, 170, 175); DBROWN = (60, 35, 20)


# ---------- вспомогательное ----------
def head_cx(view): return 11 if view == "side" else 12


def hat_cap(col, visor=None, peaked=False):
    def f(c, v, b, t):
        cx = head_cx(v)
        c.rect(cx - 6, 2 + b, cx + 6, 4 + b, col); c.rect(cx - 4, 0 + b, cx + 4, 3 + b, col)
        if v == "front" and visor: c.rect(cx - 5, 4 + b, cx + 5, 5 + b, visor)
        if v == "side" and visor: c.rect(cx - 10, 4 + b, cx - 3, 5 + b, visor)
        if peaked and v != "back": c.pts([(cx, 2 + b)], YELLOW)
    return f


def hat_hair(col, tall=0, spiky=False):
    def f(c, v, b, t):
        cx = head_cx(v)
        c.rect(cx - 5, 2 + b, cx + 5, 5 + b, col)
        c.rect(cx - 5, 5 + b, cx - 4, 8 + b, col); c.rect(cx + 4, 5 + b, cx + 5, 8 + b, col)
        if v == "back": c.rect(cx - 5, 2 + b, cx + 5, 11 + b, col)
        for k in range(tall): c.line(cx - 4 + k * 4, 2 + b, cx - 4 + k * 4 + (k - 1), -1 + b + 1, col, 2)
    return f


def face_basic(c, v, b, t, skin_shade=None, eyes=True):
    pass


def face(c, v, b, t, P):
    cx = head_cx(v)
    if v == "front":
        c.eye(cx - 3, 7 + b, 2, (1, 1)); c.eye(cx + 3, 7 + b, 2, (-1, 1))
        c.line(cx - 5, 5 + b, cx - 2, 6 + b, BLACK); c.line(cx + 5, 5 + b, cx + 2, 6 + b, BLACK)
        c.line(cx - 2, 10 + b, cx + 2, 10 + b, BLACK); c.pts([(cx - 1, 10 + b), (cx + 1, 10 + b)], WHITE)
    elif v == "side":
        c.eye(cx - 3, 7 + b, 2, (-1, 1)); c.line(cx - 5, 5 + b, cx - 2, 6 + b, BLACK)
        c.pts([(cx - 6, 8 + b), (cx - 6, 9 + b)], P["skin_dark"]); c.line(cx - 5, 10 + b, cx - 2, 10 + b, BLACK)


def human(view, t, P):
    c = Canvas(24, 24); b = t % 2
    ws = P.get("w", 13)  # ширина туловища
    x0 = 12 - ws // 2; x1 = x0 + ws
    sx = [-2, 0, 2, 0][t]
    # ноги
    if view == "side":
        for k, (dx, col) in enumerate(((sx, P["pants"]), (-sx, P["pants"]))):
            c.rect(10 + dx, 18, 13 + dx, 21, col); c.rect(10 + dx - (1 if k == 0 else 0), 21, 13 + dx, 22, P["boots"])
    else:
        la, lb = (t % 2), (1 - t % 2)
        c.rect(x0 + 2, 18, x0 + 5, 22 - la, P["pants"]); c.rect(x1 - 5, 18, x1 - 2, 22 - lb, P["pants"])
        c.rect(x0 + 1, 22 - la, x0 + 5, 22 - la, P["boots"]); c.rect(x1 - 5, 22 - lb, x1 - 1, 22 - lb, P["boots"])
    P.get("under", lambda *a: None)(c, view, t, b)
    # туловище
    if view == "side":
        c.rect(8, 11 + b, 15, 19, P["coat"], dither=P.get("coat2"))
    else:
        c.rect(x0, 11 + b, x1, 19, P["coat"], dither=P.get("coat2"))
    P.get("torso", lambda *a: None)(c, view, t, b)
    # руки
    ar = [-2, 0, 2, 0][t]
    if view == "side":
        c.rect(10 + ar, 12 + b, 13 + ar, 17, P.get("sleeve", P["coat"])); c.ell(11.5 + ar, 18, 2, 2, P["skin"])
    else:
        c.rect(x0 - 2, 12 + b, x0 + 0, 17, P.get("sleeve", P["coat"])); c.rect(x1, 12 + b, x1 + 2, 17, P.get("sleeve", P["coat"]))
        c.ell(x0 - 1, 18 + (t % 2), 2, 2, P["skin"]); c.ell(x1 + 1, 18 + (1 - t % 2), 2, 2, P["skin"])
    # голова
    cx = head_cx(view); hx = P.get("sway", lambda t: 0)(t)
    c.ell(cx + hx, 7 + b, 5, 5, P["skin"], dither=P["skin_dark"])
    if view != "back":
        c.rect(cx - 5 + hx, 6 + b, cx + 5 + hx, 6 + b, P["skin"]) if False else None
        face(c, view, b, t, P)
    P.get("face_extra", lambda *a: None)(c, view, b, t)
    P["hat"](c, view, b, t)
    P.get("extra", lambda *a: None)(c, view, t, b)
    return c.finish(P["shade"], P.get("hi", WHITE), lim=P.get("lim", 0.1))


def sheet_for(P):
    frames = []
    for view in ("side", "back", "front"):
        for t in range(4):
            a = P["draw"](view, t) if "draw" in P else human(view, t, P)
            frames.append(a)
    out = Image.new("RGBA", (104, 78), (0, 0, 0, 0))
    for i, a in enumerate(frames):
        im = Image.fromarray(a, "RGBA"); r, k = i // 4, i % 4
        out.paste(im, (k * 26 + (26 - im.width) // 2, r * 26 + (26 - im.height)), im)
    return out


# ---------- наборы героев ----------
def beard(col):
    def f(c, v, b, t):
        if v == "front": c.rect(7, 9 + b, 17, 13 + b, col); c.pts([(8, 13 + b), (15, 13 + b), (12, 14 + b)], YELLOW)
        if v == "side": c.rect(6, 9 + b, 12, 13 + b, col)
    return f


def mustache(col, w=5):
    def f(c, v, b, t):
        if v == "front": c.rect(12 - w, 9 + b, 12 + w, 10 + b, col)
        if v == "side": c.rect(5, 9 + b, 9, 10 + b, col)
    return f


def glasses(col=BLACK):
    def f(c, v, b, t):
        if v == "front": c.rect(6, 6 + b, 18, 6 + b, col); c.rect(6, 6 + b, 10, 8 + b, col) if False else None
        if v == "side": c.rect(4, 6 + b, 9, 6 + b, col)
    return f


def mk(**kw): return kw


def e_hobo(c, v, t, b):
    if v == "front": c.rect(20, 15 + t % 2, 22, 21, GREEN); c.rect(20, 14 + t % 2, 21, 15 + t % 2, GREEN); c.px(21, 18, WHITE)
    if v == "side": c.rect(6, 15 + b, 8, 20, GREEN); c.px(7, 17, WHITE)
    c.pts([(3, 3), (21, 6), (2, 10)], YELLOW)


HOBO = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=GREEN, coat2=DGREEN, pants=BLACK, boots=BROWN, shade=PURPLE, hi=YELLOW,
          hat=lambda c, v, b, t: (c.rect(7, 2 + b, 17, 6 + b, FUR, dither=WHITE), c.rect(5, 5 + b, 7, 11 + b, FUR), c.rect(17, 5 + b, 19, 11 + b, FUR)) if v != "side" else (c.rect(6, 2 + b, 16, 6 + b, FUR, dither=WHITE), c.rect(10, 5 + b, 14, 11 + b, FUR)),
          face_extra=beard((45, 30, 20)), extra=e_hobo, torso=lambda c, v, b, t: c.pts([(7, 14 + b), (8, 15 + b), (15, 17), (6, 18)], YELLOW) if v == "front" else None)


def squid_extra(c, v, t, b):
    cx = head_cx(v)
    if v == "front":
        for k, x in enumerate((8, 10, 12, 14, 16)): c.line(x, 11 + b, x + [-1, 0, 1, 0, -1][(k + t) % 5], 15 + b, PINK, 2)   # щупальца-борода
    if v == "side":
        for k in range(3): c.line(5 + k, 11 + b, 4 + k + (t + k) % 2, 15 + b, PINK, 2)
    if v == "back":
        c.ell(12, 3 + b, 3, 3, PINK); c.line(12, 0 + b, 12, -1 + b, PINK)
    c.pts([(2, 3), (22, 2)], YELLOW)


SQUID = mk(skin=(110, 170, 255), skin_dark=(70, 120, 230), coat=BLUE, coat2=(70, 70, 255), pants=BLUE, boots=WHITE, sleeve=BLUE, shade=PINK, hi=WHITE,
           hat=hat_cap(RED, (200, 0, 40)), extra=squid_extra,
           torso=lambda c, v, b, t: (c.rect(5, 12 + b, 5, 19, WHITE), c.rect(18, 12 + b, 18, 19, WHITE), c.rect(9, 11 + b, 9, 13 + b, WHITE)) if v != "side" else c.rect(8, 12 + b, 8, 19, WHITE),
           face_extra=lambda c, v, b, t: c.pts([(13, 11 + b), (14, 11 + b), (15, 11 + b), (16, 12 + b)], WHITE) if v == "front" else None)


CLERK = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=WHITE, coat2=LGREY, pants=(50, 50, 70), boots=BLACK, sleeve=WHITE, shade=PINK, hi=YELLOW,
           hat=hat_hair((70, 50, 30)), face_extra=glasses(),
           torso=lambda c, v, b, t: (c.rect(11, 11 + b, 13, 18, RED), c.pts([(12, 11 + b)], BLACK), c.rect(7, 14 + b, 9, 16 + b, YELLOW)) if v == "front" else (c.rect(5, 11 + b, 18, 12 + b, GREY) if v == "back" else c.rect(8, 11 + b, 9, 17, RED)),
           extra=lambda c, v, t, b: (c.pts([(2, 17), (21, 14 + t % 2)], YELLOW), c.rect(0, 15 + b, 2, 19, WHITE)))


JAN = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=ORANGE, coat2=(200, 90, 0), pants=BLUE, boots=BLUE, sleeve=GREY, shade=RED, hi=YELLOW,
         hat=hat_cap(BLUE, BLUE), face_extra=mustache(GRAYHAIR, 5),
         torso=lambda c, v, b, t: (c.rect(5, 14 + b, 18, 15 + b, YELLOW), c.rect(5, 17, 18, 17, YELLOW)) if v != "side" else (c.rect(8, 14 + b, 15, 15 + b, YELLOW), c.rect(8, 17, 15, 17, YELLOW)),
         extra=lambda c, v, t, b: (c.line(21 + [0, 1, 0, -1][t], 3, 19 + [0, 1, 0, -1][t], 20, BROWN, 2), c.rect(16 + [0, 1, 0, -1][t], 19, 23 + [0, 1, 0, -1][t], 23, YELLOW, dither=ORANGE)))


VITYA = mk(skin=(240, 170, 150), skin_dark=(215, 130, 120), coat=WHITE, coat2=LGREY, pants=(30, 60, 140), boots=BROWN, sleeve=(240, 170, 150), shade=CYAN, hi=YELLOW,
           hat=hat_cap(GREY, DGREY), sway=lambda t: [0, 1, 0, -1][t], face_extra=lambda c, v, b, t: (c.rect(6, 9 + b, 18, 11 + b, (110, 90, 80), dither=SKIN), c.pts([(12, 8 + b), (13, 8 + b)], RED)) if v == "front" else None,
           torso=lambda c, v, b, t: (c.rect(5, 11 + b, 7, 14 + b, (240, 170, 150)), c.rect(16, 11 + b, 18, 14 + b, (240, 170, 150)), c.pts([(9, 15), (14, 17)], BROWN)) if v == "front" else None,
           extra=lambda c, v, t, b: (c.rect(19, 14 + b, 21, 17, GREEN), c.rect(20, 12 + b, 20, 14 + b, GREEN), c.pts([(20, 15 + b)], WHITE)) if v != "side" else c.rect(6, 14 + b, 8, 17, GREEN))


BLOG = mk(skin=ZOMBIE, skin_dark=(70, 150, 90), coat=BLACK, coat2=(40, 40, 50), pants=(40, 40, 70), boots=WHITE, sleeve=BLACK, shade=PINK, hi=CYAN,
          hat=hat_hair(PINK, 0), 
          face_extra=lambda c, v, b, t: (c.pts([(8, 9 + b), (16, 9 + b)], PURPLE), c.rect(8, 10 + b, 9, 12 + b, PURPLE) if False else None) if v == "front" else None,
          torso=lambda c, v, b, t: (c.rect(10, 13 + b, 14, 17, WHITE), c.pts([(12, 14 + b)], RED), c.pts([(9, 11 + b), (15, 11 + b)], GOLD)) if v == "front" else None,
          extra=lambda c, v, t, b: (c.rect(19, 9 + b, 22, 15 + b, CYAN, dither=WHITE), c.line(20, 15 + b, 20, 19, BLACK)) if v != "side" else c.rect(4, 12 + b, 7, 17, CYAN))


GRAN = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=BLUE, coat2=(80, 80, 255), pants=BROWN, boots=PINK, shade=CYAN, hi=WHITE, w=15,
          hat=lambda c, v, b, t: (c.rect(5, 2 + b, 19, 5 + b, PINK, dither=RED), c.rect(5, 5 + b, 7, 12 + b, PINK), c.rect(17, 5 + b, 19, 12 + b, PINK), c.pts([(8, 3 + b), (12, 4 + b), (16, 3 + b)], WHITE)) if v == "front" else (c.rect(5, 2 + b, 19, 12 + b, PINK, dither=RED) if v == "back" else c.rect(5, 2 + b, 17, 12 + b, PINK, dither=RED)),
          face_extra=lambda c, v, b, t: (c.ell(9, 7 + b, 2, 2, WHITE), c.ell(15, 7 + b, 2, 2, WHITE), c.eye(9, 7 + b, 1, (0, 0)), c.eye(15, 7 + b, 1, (0, 0))) if v == "front" else None,
          torso=lambda c, v, b, t: [c.px(x, y + b, YELLOW if x % 2 else PINK) for x, y in ((8, 14), (13, 12), (15, 17), (9, 18), (12, 16))],
          extra=lambda c, v, t, b: (c.line(21, 11, 21 + [0, 1, 0, -1][t], 21, BROWN, 2), c.rect(1, 15 + b, 4, 19 + b, (200, 150, 60))) if v != "side" else c.line(5, 12, 5 + [0, 1, 0, -1][t], 21, BROWN, 2))


def courier_extra(c, v, t, b):
    if v == "back": c.rect(4, 8 + b, 19, 19, YELLOW, dither=ORANGE); c.rect(4, 8 + b, 19, 9 + b, BLACK); c.rect(9, 12 + b, 14, 15 + b, RED); c.pts([(11, 13 + b)], WHITE)
    elif v == "side": c.rect(13, 9 + b, 19, 18, YELLOW, dither=ORANGE); c.rect(13, 9 + b, 19, 10 + b, BLACK)
    else: c.rect(6, 11 + b, 7, 17, BLACK); c.rect(16, 11 + b, 17, 17, BLACK); c.pts([(2, 3), (22, 5)], YELLOW)


COUR = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=GREEN, coat2=DGREEN, pants=BLACK, boots=WHITE, sleeve=GREEN, shade=PINK, hi=YELLOW,
          hat=hat_cap(BLACK, GREEN), extra=courier_extra)


def punk_face(c, v, b, t):
    if v == "front":
        c.ell(6, 3 + b, 3, 3, PINK); c.ell(18, 3 + b, 3, 3, PINK); c.pts([(12, 9 + b)], PINK)
        c.pts([(10, 11 + b), (14, 11 + b)], WHITE); c.pts([(4, 9 + b), (3, 10 + b), (20, 9 + b), (21, 10 + b)], WHITE)
    if v == "side": c.ell(10, 3 + b, 3, 3, PINK); c.pts([(5, 8 + b), (4, 8 + b)], PINK); c.pts([(4, 10 + b), (3, 11 + b)], WHITE)
    if v == "back": c.ell(6, 3 + b, 3, 3, PINK); c.ell(18, 3 + b, 3, 3, PINK)


PUNK = mk(skin=(150, 140, 150), skin_dark=(100, 95, 105), coat=BLACK, coat2=(50, 50, 60), pants=(40, 40, 80), boots=RED, sleeve=BLACK, shade=GREEN, hi=WHITE,
          hat=lambda c, v, b, t: [c.line(12, 3 + b, 12 + (k - 1) * 2, -2 + b, GREEN, 2) for k in range(3)] if v != "side" else [c.line(9 + k, 3 + b, 10 + k, -1 + b, GREEN, 2) for k in range(3)],
          face_extra=punk_face, torso=lambda c, v, b, t: (c.pts([(6, 12 + b), (8, 14 + b), (16, 12 + b), (18, 15 + b)], WHITE), c.line(6, 19, 12, 19, WHITE)) if v == "front" else None,
          extra=lambda c, v, t, b: (c.line(18, 19, 22, 20 - [0, 1, 0, -1][t], PINK, 1) if v != "side" else c.line(15, 19, 21, 20 + [0, 1, 0, -1][t], PINK, 1)))


SHAW = mk(skin=TAN, skin_dark=(170, 110, 70), coat=WHITE, coat2=(200, 200, 160), pants=DGREY, boots=BLACK, sleeve=WHITE, shade=RED, hi=YELLOW, w=17,
          hat=lambda c, v, b, t: (c.rect(5, 3 + b, 19, 5 + b, WHITE), c.ell(12, 0 + b, 6, 3, WHITE, dither=LGREY)) if v != "side" else (c.rect(5, 3 + b, 17, 5 + b, WHITE), c.ell(11, 0 + b, 6, 3, WHITE, dither=LGREY)),
          face_extra=mustache(BLACK, 6), torso=lambda c, v, b, t: (c.pts([(8, 14 + b), (14, 16), (10, 18), (16, 13 + b)], RED), c.pts([(10, 11 + b), (14, 11 + b)], GOLD)) if v == "front" else None,
          extra=lambda c, v, t, b: (c.line(22, 13, 22, 20, BROWN, 2)) if v != "side" else c.line(9, 12, 9, 20, BROWN, 2))


GUARD = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=NAVY, coat2=BLUE, pants=NAVY, boots=BLACK, sleeve=NAVY, shade=PINK, hi=YELLOW, w=15,
           hat=hat_cap(NAVY, BLACK, True), face_extra=mustache(DBROWN, 4),
           torso=lambda c, v, b, t: (c.rect(5, 16, 19, 17, BLACK), c.pts([(12, 16)], GOLD), c.pts([(9, 13 + b), (15, 13 + b)], YELLOW)) if v != "side" else c.rect(8, 16, 15, 17, BLACK),
           extra=lambda c, v, t, b: c.rect(19, 15, 21, 17, BLACK) if v == "front" else None)


STUD = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=PURPLE, coat2=(160, 40, 200), pants=(60, 60, 80), boots=WHITE, sleeve=PURPLE, shade=CYAN, hi=YELLOW,
          hat=hat_hair((90, 55, 25), 0),
          face_extra=lambda c, v, b, t: (c.pts([(8, 9 + b), (9, 9 + b), (15, 9 + b), (16, 9 + b)], (110, 70, 140)), c.rect(6, 6 + b, 10, 6 + b, BLACK), c.rect(14, 6 + b, 18, 6 + b, BLACK)) if v == "front" else None,
          torso=lambda c, v, b, t: (c.line(7, 11 + b, 12, 15, BLACK), c.line(17, 11 + b, 12, 15, BLACK)) if v == "front" else (c.rect(5, 11 + b, 18, 19, BLACK, dither=PURPLE) if v == "back" else None),
          extra=lambda c, v, t, b: (c.rect(19, 14 + b, 21, 17, CYAN), c.pts([(20, 15 + b)], WHITE)) if v != "side" else c.rect(7, 14 + b, 9, 17, CYAN))


PLUMB = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=YELLOW, coat2=ORANGE, pants=BLUE, boots=BROWN, sleeve=YELLOW, shade=RED, hi=WHITE, w=14,
           hat=hat_cap(RED, RED), face_extra=mustache(BLACK, 6),
           torso=lambda c, v, b, t: (c.rect(7, 12 + b, 9, 19, BLUE), c.rect(15, 12 + b, 17, 19, BLUE), c.rect(7, 16, 17, 19, BLUE), c.pts([(8, 14 + b), (16, 14 + b)], YELLOW), c.rect(10, 15, 14, 17, BLUE, dither=CYAN)) if v == "front" else (c.rect(5, 16, 19, 19, BLUE) if v == "back" else c.rect(8, 15, 15, 19, BLUE)),
           extra=lambda c, v, t, b: (c.line(21, 12, 21, 21, GREY, 2), c.rect(20, 10, 23, 12, GREY)) if v != "side" else (c.line(6, 12, 6, 21, GREY, 2), c.rect(5, 10, 8, 12, GREY)))


DACHA = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=PINK, coat2=(255, 120, 245), pants=PINK, boots=GREEN, sleeve=PINK, shade=CYAN, hi=YELLOW, w=15,
           hat=lambda c, v, b, t: (c.ell(12, 3 + b, 10, 3, (230, 190, 90), dither=YELLOW), c.rect(7, 1 + b, 17, 3 + b, (230, 190, 90)), c.pts([(5, 3 + b), (9, 2 + b), (17, 2 + b), (20, 3 + b)], PINK)) if v != "side" else (c.ell(11, 3 + b, 9, 3, (230, 190, 90), dither=YELLOW), c.rect(7, 1 + b, 15, 3 + b, (230, 190, 90)), c.pts([(5, 3 + b), (9, 2 + b), (16, 3 + b)], RED)),
           face_extra=lambda c, v, b, t: c.pts([(7, 9 + b), (17, 9 + b)], PINK) if v == "front" else None,
           torso=lambda c, v, b, t: (c.rect(7, 12 + b, 17, 19, WHITE), c.pts([(9, 14 + b), (14, 16)], RED)) if v == "front" else None,
           extra=lambda c, v, t, b: (c.rect(0, 16 + b, 4, 21, DGREY), c.line(1, 16 + b, 2, 12 + b, DGREY), c.pts([(2, 17 + b)], GREEN)) if v != "side" else c.rect(5, 16 + b, 9, 21, DGREY))


SKATE = mk(skin=SKIN, skin_dark=(220, 160, 120), coat=YELLOW, coat2=ORANGE, pants=BLACK, boots=RED, sleeve=YELLOW, shade=PINK, hi=WHITE,
           hat=lambda c, v, b, t: (c.rect(5, 2 + b, 19, 5 + b, RED), c.rect(5, 5 + b, 7, 8 + b, RED), c.rect(17, 5 + b, 19, 8 + b, RED), c.pts([(12, 3 + b)], WHITE)) if v != "side" else (c.rect(6, 2 + b, 16, 5 + b, RED), c.rect(14, 5 + b, 17, 8 + b, RED)),
           face_extra=lambda c, v, b, t: (c.rect(5, 12 + b, 6, 13 + b, WHITE), c.rect(18, 12 + b, 19, 13 + b, WHITE)) if v == "front" else None,
           torso=lambda c, v, b, t: c.pts([(9, 13 + b), (14, 15), (11, 17)], BLACK),
           extra=lambda c, v, t, b: (c.rect(18, 15 + b, 22, 16 + b, BLACK), c.ell(18, 17 + b, 1, 1, YELLOW), c.ell(22, 17 + b, 1, 1, YELLOW)) if v != "side" else (c.rect(5, 15 + b, 9, 16 + b, BLACK), c.ell(5, 17 + b, 1, 1, YELLOW), c.ell(9, 17 + b, 1, 1, YELLOW)))


# --- голубь: отдельный рисунок для трёх видов
def pigeon_draw(view, t):
    c = Canvas(24, 24); b = t % 2; wf = [0, 1, 2, 1][t]
    f1, f2 = (7, 15) if t % 2 == 0 else (8, 14)
    if view == "side":
        for x in (9 + [-1, 1][t % 2], 13 - [-1, 1][t % 2]): c.line(x + 1, 18, x + 1, 22, ORANGE); c.pts([(x - 1, 23), (x, 23), (x + 1, 23)], ORANGE)
        c.ell(13, 13 + b, 9, 6, STEEL, dither=(90, 110, 150)); c.ell(11, 16 + b, 5, 3, LGREY, dither=WHITE)
        c.ell(14, 12 + b - wf // 2, 5, 3, LGREY, dither=STEEL); c.rect(11, 11 + b, 17, 11 + b, WHITE)
        c.line(21, 12 + b, 24, 9 + b, STEEL, 3); c.line(21, 13 + b, 24, 13 + b, LGREY, 2)   # хвост
        c.ell(8, 8 + b, 4, 3, GREEN, dither=PINK); c.ell(6, 5 + b, 4, 4, STEEL, dither=(90, 110, 150))
        c.eye(5, 4 + b, 2, (-1, 1)); c.ell(6, 2 + b, 1, 1, RED); c.pts([(2, 5 + b), (1, 6 + b), (2, 6 + b), (3, 6 + b)], ORANGE)
    elif view == "back":
        for x in (f1, f2): c.line(x + 1, 19, x + 1, 22, ORANGE); c.pts([(x - 1, 23), (x, 23), (x + 1, 23), (x + 2, 23)], ORANGE)
        c.ell(12, 14 + b, 9, 8, STEEL, dither=(90, 110, 150)); c.ell(12, 18 + b, 4, 4, WHITE, dither=LGREY)       # белый круп
        c.ell(3, 13 + b - wf, 3, 6, LGREY, dither=STEEL); c.ell(21, 13 + b - wf, 3, 6, LGREY, dither=STEEL)
        c.rect(1, 12 + b - wf, 5, 13 + b - wf, WHITE); c.rect(18, 12 + b - wf, 22, 13 + b - wf, WHITE)
        c.ell(12, 6 + b, 5, 4, STEEL, dither=(90, 110, 150)); c.ell(12, 9 + b, 4, 2, GREEN, dither=PINK)
        c.line(10, 22, 8, 23, STEEL, 2); c.line(14, 22, 16, 23, STEEL, 2)
    else:
        for x in (f1, f2): c.line(x + 1, 19, x + 1, 22, ORANGE); c.pts([(x - 1, 23), (x, 23), (x + 1, 23), (x + 2, 23)], ORANGE)
        c.ell(12, 14 + b, 9, 8, STEEL, dither=(90, 110, 150)); c.ell(12, 17 + b, 5, 4, LGREY, dither=WHITE)
        c.ell(3, 13 + b - wf, 3, 6, LGREY, dither=STEEL); c.ell(21, 13 + b - wf, 3, 6, LGREY, dither=STEEL)
        c.rect(1, 12 + b - wf, 5, 13 + b - wf, WHITE); c.rect(18, 12 + b - wf, 22, 13 + b - wf, WHITE)
        c.ell(12, 8 + b, 4, 3, GREEN, dither=PINK); c.ell(12, 5 + b, 5, 4, STEEL, dither=(90, 110, 150))
        c.eye(9, 4 + b, 2, (1, 1)); c.eye(15, 4 + b, 2, (-1, 1)); c.ell(12, 2 + b, 1, 1, RED)
        c.pts([(11, 6 + b), (12, 6 + b), (13, 6 + b), (12, 7 + b)], ORANGE)
    c.pts([(6, 19), (18, 20), (2, 3), (21, 5)], GREEN)
    return c.finish(PINK, WHITE)


PIGEON = mk(draw=pigeon_draw)

HEROES = {"hobo": HOBO, "squid": SQUID, "clerk": CLERK, "janitor": JAN, "uncle_vitya": VITYA, "blogger": BLOG, "granny": GRAN,
          "courier": COUR, "pigeon": PIGEON, "punk": PUNK, "shawarma": SHAW, "guard": GUARD, "student": STUD, "plumber": PLUMB,
          "dacha": DACHA, "skater": SKATE}

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    os.makedirs("tools/_preview/heroes_v2", exist_ok=True)
    k = 3
    prev = Image.new("RGBA", (8 * 28 * k + 8, 6 * 28 * k + 8), (45, 30, 20, 255))
    for i, (name, P) in enumerate(HEROES.items()):
        sh = sheet_for(P); sh.save(f"tools/_preview/heroes_v2/player_{name}.png")
        if apply: sh.save(f"assets/sprites/player_{name}.png")
        for r, row in enumerate((2, 1, 0)):   # фас, спина, бок
            fr = sh.crop((0, row * 26, 26, row * 26 + 26)).resize((26 * k, 26 * k), Image.NEAREST)
            prev.paste(fr, ((i % 8) * 28 * k + 4, ((i // 8) * 3 + r) * 28 * k + 4), fr)
    prev.save("tools/_preview/heroes_v2_all.png")
