"""Шесть новых героев: шаурмист, охранник, студент-должник, сантехник, тётя с дачи, скейтер.
Лист 4x3 кадров, клетка 26 px. Запуск из корня: python3 tools/gen_heroes4.py"""
import random
import sys

sys.path.insert(0, "tools")
import gen_heroes2 as h2
from gen_heroes2 import BLACK, BLUE, BROWN, GREY, GREEN, PINK, RED, WHITE, YELLOW, SKIN, DARK, ORANGE, blob, compose, legs, line, m, poly, rect
from PIL import Image


def shawarma(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(31)
    body = m(); rect(body, 7, 10 + bob, 17, 19 + bob)
    apron = m(); rect(apron, 8, 12 + bob, 16, 20 + bob)
    arms = m(); rect(arms, 4, 11 + bob, 6, 16 + bob); rect(arms, 18, 11 + bob, 20, 16 + bob)
    head = m(); blob(head, 12, 7 + bob, 4, 4, rng, 0.2, 10)
    hat = m(); poly(hat, [(8, 4 + bob), (10, -1 + bob), (14, -1 + bob), (16, 4 + bob)])
    skewer = m(); rect(skewer, 21, 3 + bob, 22, 19 + bob); rect(skewer, 20, 6 + bob, 23, 15 + bob)
    parts = [(legs(frame, bob, DARK, 8, 14, 19, 3)), (body, WHITE), (arms, SKIN), (apron, (230, 230, 235)), (head, SKIN), (hat, WHITE)]
    if view != "back":
        parts.append((skewer, (150, 80, 40)))
    dots = [(9, 22, BLACK), (15, 22, BLACK), (12, 4 + bob, RED), (11, 14 + bob, RED), (14, 17 + bob, (190, 60, 30))]
    if view == "front":
        dots += [(10, 7 + bob, BLACK), (14, 7 + bob, BLACK), (10, 9 + bob, BLACK), (11, 9 + bob, BLACK), (13, 9 + bob, BLACK), (14, 9 + bob, BLACK), (12, 10 + bob, SKIN)]
    elif view == "side":
        dots += [(9, 7 + bob, BLACK), (7, 9 + bob, BLACK), (8, 9 + bob, BLACK)]
    return compose(parts, dots)


def guard(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(32)
    uni = (30, 40, 90)
    body = m(); rect(body, 6, 9 + bob, 18, 19 + bob)
    arms = m(); rect(arms, 3, 10 + bob, 5, 17 + bob); rect(arms, 19, 10 + bob, 21, 17 + bob)
    head = m(); blob(head, 12, 6 + bob, 4, 3, rng, 0.2, 10)
    cap = m(); rect(cap, 7, 1 + bob, 17, 3 + bob); rect(cap, 6 if view == "side" else 8, 3 + bob, 16, 4 + bob)
    baton = m(); rect(baton, 21, 12 + bob, 22, 21 + bob)
    parts = [(legs(frame, bob, (20, 25, 55), 8, 14, 19, 3)), (body, uni), (arms, uni), (head, SKIN), (cap, (20, 28, 70))]
    if view != "back":
        parts.append((baton, BLACK))
    dots = [(9, 22, BLACK), (15, 22, BLACK), (12, 2 + bob, YELLOW), (7, 17 + bob, BROWN), (8, 17 + bob, YELLOW), (x := 16, 17 + bob, BROWN)]
    dots += [(x_, 17 + bob, BROWN) for x_ in range(7, 18)]   # ремень
    if view == "front":
        dots += [(15, 12 + bob, YELLOW), (16, 12 + bob, YELLOW), (10, 6 + bob, BLACK), (14, 6 + bob, BLACK), (10, 8 + bob, (90, 70, 50)), (11, 8 + bob, (90, 70, 50)), (12, 8 + bob, (90, 70, 50)), (13, 8 + bob, (90, 70, 50)), (14, 8 + bob, (90, 70, 50))]
    elif view == "side":
        dots += [(9, 6 + bob, BLACK), (8, 8 + bob, (90, 70, 50))]
    return compose(parts, dots)


def student(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(33)
    hood = (110, 70, 170)
    body = m(); rect(body, 9, 10 + bob, 15, 19 + bob)
    arms = m(); rect(arms, 7, 11 + bob, 8, 17 + bob); rect(arms, 16, 11 + bob, 17, 17 + bob)
    head = m(); blob(head, 12, 6 + bob, 4, 4, rng, 0.2, 10)
    hair = m(); rect(hair, 8, 1 + bob, 16, 3 + bob); rect(hair, 7, 3 + bob, 8, 5 + bob)
    pack = m()
    if view == "back":
        rect(pack, 5, 8 + bob, 19, 21 + bob)
    elif view == "side":
        rect(pack, 14, 8 + bob, 21, 21 + bob)
    can = m(); rect(can, 18, 12 + bob, 20, 16 + bob)
    phones = m(); rect(phones, 7, 5 + bob, 8, 8 + bob); rect(phones, 16, 5 + bob, 17, 8 + bob); rect(phones, 8, 3 + bob, 16, 3 + bob)
    parts = [(legs(frame, bob, (50, 60, 90), 9, 13, 19, 2)), (body, hood), (arms, hood), (head, SKIN), (hair, (60, 40, 30)), (phones, BLACK)]
    if view != "front":
        parts.insert(2, (pack, (200, 50, 60)))
    if view != "back":
        parts.append((can, (80, 230, 255)))
    dots = [(10, 22, WHITE), (14, 22, WHITE), (11, 14 + bob, (140, 100, 200))]
    if view == "front":
        dots += [(10, 6 + bob, BLACK), (14, 6 + bob, BLACK), (10, 5 + bob, WHITE), (14, 5 + bob, WHITE), (11, 9 + bob, RED), (12, 9 + bob, RED), (12, 13 + bob, WHITE), (11, 13 + bob, WHITE)]
    elif view == "side":
        dots += [(9, 6 + bob, BLACK), (8, 9 + bob, RED)]
    return compose(parts, dots)


def plumber(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(34)
    ov = (50, 90, 170)
    body = m(); rect(body, 6, 10 + bob, 18, 20 + bob)
    arms = m(); rect(arms, 3, 11 + bob, 5, 17 + bob); rect(arms, 19, 11 + bob, 21, 17 + bob)
    head = m(); blob(head, 12, 6 + bob, 4, 4, rng, 0.2, 10)
    cap = m(); rect(cap, 8, 1 + bob, 16, 3 + bob); rect(cap, 6 if view == "side" else 8, 3 + bob, 16, 3 + bob)
    plunger = m(); rect(plunger, 12, -1 + bob, 12, 1 + bob); rect(plunger, 10, -1 + bob, 14, -1 + bob)
    wrench = m(); line(wrench, [(20, 9 + bob), (20, 21)], 1); rect(wrench, 19, 7 + bob, 21, 9 + bob)
    parts = [(legs(frame, bob, (40, 55, 110), 8, 14, 20, 3)), (body, ov), (arms, (200, 60, 50)), (head, SKIN), (cap, (200, 60, 50)), (plunger, BROWN)]
    if view != "back":
        parts.append((wrench, GREY))
    dots = [(9, 22, BLACK), (15, 22, BLACK), (9, 11 + bob, YELLOW), (15, 11 + bob, YELLOW), (12, 15 + bob, (30, 60, 130)), (11, 15 + bob, (30, 60, 130)), (13, 15 + bob, (30, 60, 130))]
    if view == "front":
        dots += [(10, 6 + bob, BLACK), (14, 6 + bob, BLACK), (10, 8 + bob, (60, 40, 30)), (11, 8 + bob, (60, 40, 30)), (12, 8 + bob, (60, 40, 30)), (13, 8 + bob, (60, 40, 30)), (14, 8 + bob, (60, 40, 30))]
    elif view == "side":
        dots += [(9, 6 + bob, BLACK), (7, 8 + bob, (60, 40, 30)), (8, 8 + bob, (60, 40, 30))]
    return compose(parts, dots)


def dacha(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(35)
    body = m(); blob(body, 12, 15 + bob, 8, 6, rng, 0.3, 14)
    head = m(); blob(head, 12, 8 + bob, 4, 4, rng, 0.2, 10)
    hat = m(); rect(hat, 3, 4 + bob, 21, 5 + bob); rect(hat, 8, 1 + bob, 16, 4 + bob)
    arms = m(); rect(arms, 3, 12 + bob, 5, 17 + bob); rect(arms, 19, 12 + bob, 21, 17 + bob)
    bucket = m(); rect(bucket, 19, 16 + bob, 23, 21 + bob)
    parts = [(legs(frame, bob, SKIN, 9, 14, 20, 2)), (body, (230, 100, 140)), (arms, SKIN), (head, SKIN), (hat, (230, 200, 90))]
    if view != "back":
        parts.append((bucket, (60, 130, 200)))
    dots = [(9, 22, (90, 60, 40)), (15, 22, (90, 60, 40)), (10, 4 + bob, RED), (13, 4 + bob, RED), (9, 13 + bob, WHITE), (14, 16 + bob, WHITE), (11, 19 + bob, WHITE), (16, 12 + bob, YELLOW)]
    if view == "front":
        dots += [(10, 8 + bob, BLACK), (14, 8 + bob, BLACK), (11, 10 + bob, RED), (12, 10 + bob, RED), (13, 10 + bob, RED), (8, 9 + bob, PINK), (16, 9 + bob, PINK)]
    elif view == "side":
        dots += [(9, 8 + bob, BLACK), (8, 10 + bob, RED)]
    return compose(parts, dots)


def skater(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(36)
    hood = (240, 200, 50)
    board = m(); rect(board, 3, 22, 21, 23); rect(board, 4, 23, 5, 23); rect(board, 19, 23, 20, 23)
    body = m(); rect(body, 8, 11 + bob, 16, 18 + bob)
    arms = m(); rect(arms, 5, 12 + bob, 7, 17 + bob); rect(arms, 17, 12 + bob, 19, 17 + bob)
    head = m(); blob(head, 12, 7 + bob, 4, 4, rng, 0.2, 10)
    beanie = m(); rect(beanie, 8, 2 + bob, 16, 5 + bob); rect(beanie, 11, 0 + bob, 13, 1 + bob)
    pants = m(); rect(pants, 7, 18 + bob, 17, 21)
    parts = [(board, (160, 70, 40)), (pants, (60, 70, 100)), (body, hood), (arms, hood), (head, SKIN), (beanie, (220, 60, 60))]
    dots = [(x, 21, BLACK) for x in (8, 9, 15, 16)] + [(5, 23, YELLOW), (19, 23, YELLOW), (9, 17 + bob, (190, 160, 30))]
    if view == "front":
        dots += [(10, 7 + bob, BLACK), (14, 7 + bob, BLACK), (11, 10 + bob, RED), (12, 10 + bob, RED), (12, 14 + bob, BLACK), (11, 14 + bob, BLACK)]
    elif view == "side":
        dots += [(9, 7 + bob, BLACK), (8, 10 + bob, RED)]
    return compose(parts, dots)


HEROES4 = {"shawarma": shawarma, "guard": guard, "student": student, "plumber": plumber, "dacha": dacha, "skater": skater}

if __name__ == "__main__":
    preview = Image.new("RGBA", (len(HEROES4) * 30, 3 * 30), (60, 40, 20, 255))
    for i, (hero_id, fn) in enumerate(HEROES4.items()):
        sheet = h2.build(fn)
        sheet.save("assets/sprites/player_%s.png" % hero_id)
        for r in range(3):
            preview.alpha_composite(sheet.crop((0, r * 26, 26, r * 26 + 26)), (i * 30 + 2, r * 30 + 2))
    preview.resize((preview.width * 8, preview.height * 8), Image.NEAREST).save("tools/_preview/heroes4.png")
    print("ok")
