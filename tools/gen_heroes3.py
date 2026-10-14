"""Старые герои, перерисованные под своё описание: кальмар-гопник, офисный планктон, дворник Палыч, дядя Витя, зомби-блогер.
Лист 4x3 кадров, клетка 26 px. Запуск из корня: python3 tools/gen_heroes3.py"""
import random
import sys

sys.path.insert(0, "tools")
import gen_art as ga
import gen_heroes2 as h2
from gen_heroes2 import BLACK, BLUE, BROWN, GREY, GREEN, PINK, RED, WHITE, YELLOW, SKIN, DARK, ORANGE, blob, compose, legs, line, m, poly, rect
from PIL import Image


def squid(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(21)
    teal = (70, 170, 190)
    suit = (30, 60, 170)
    body = m(); rect(body, 6, 11 + bob, 18, 19 + bob)
    arms = m(); rect(arms, 3, 12 + bob, 5, 18 + bob); rect(arms, 19, 12 + bob, 21, 18 + bob)
    head = m(); blob(head, 12, 8 + bob, 5, 4, rng, 0.2, 10)
    mantle = m(); poly(mantle, [(8, 5 + bob), (12, -1 + bob), (16, 5 + bob)]) if view != "side" else poly(mantle, [(9, 5 + bob), (14, 0 + bob), (17, 6 + bob)])
    beard = m()
    if view == "front":
        for x in (9, 12, 15):
            line(beard, [(x, 11 + bob), (x - 1 + (frame and 1 or 0), 14 + bob)], 1)
    elif view == "side":
        line(beard, [(8, 11 + bob), (6 + frame, 14 + bob)], 1); line(beard, [(10, 11 + bob), (9, 14 + bob)], 1)
    parts = [(legs(frame, bob, WHITE, 8, 14, 19, 3)), (body, suit), (arms, suit), (beard, teal), (head, teal), (mantle, teal)]
    dots = [(9, 22, BLACK), (15, 22, BLACK)]
    dots += [(7, y + bob, WHITE) for y in range(12, 19)] + [(17, y + bob, WHITE) for y in range(12, 19)]   # полосы адидас
    if view == "front":
        dots += [(10, 8 + bob, YELLOW), (14, 8 + bob, YELLOW), (10, 9 + bob, BLACK), (14, 9 + bob, BLACK), (12, 6 + bob, WHITE), (3, 17 + bob, BROWN), (4, 18 + bob, BROWN)]
    elif view == "side":
        dots += [(9, 8 + bob, YELLOW), (9, 9 + bob, BLACK)]
    else:
        dots += [(12, 14 + bob, WHITE), (11, 14 + bob, WHITE), (13, 14 + bob, WHITE)]
    return compose(parts, dots)


def clerk(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(22)
    suit = (95, 100, 120)
    body = m(); rect(body, 9, 9 + bob, 15, 19 + bob)
    arms = m(); rect(arms, 7, 10 + bob, 8, 17 + bob); rect(arms, 16, 10 + bob, 17, 17 + bob)
    head = m(); blob(head, 12, 5 + bob, 4, 4, rng, 0.2, 10)
    hair = m(); rect(hair, 9, 1 + bob, 15, 2 + bob)
    papers = m(); rect(papers, 17, 12 + bob, 21, 17 + bob)
    parts = [(legs(frame, bob, DARK, 9, 13, 19, 2)), (body, suit), (arms, suit), (head, SKIN), (hair, (90, 70, 50))]
    if view != "back":
        parts.append((papers, WHITE))
    dots = [(10, 22, BLACK), (14, 22, BLACK)]
    if view == "front":
        dots += [(12, 10 + bob, WHITE), (11, 10 + bob, WHITE), (13, 10 + bob, WHITE), (12, 11 + bob, RED), (12, 12 + bob, RED), (12, 13 + bob, RED), (12, 14 + bob, RED)]  # рубашка и галстук
        dots += [(10, 5 + bob, WHITE), (11, 5 + bob, WHITE), (13, 5 + bob, WHITE), (14, 5 + bob, WHITE), (10, 4 + bob, BLACK), (13, 4 + bob, BLACK), (12, 8 + bob, GREY)]   # очки, усталый рот
        dots += [(8, 13 + bob, YELLOW), (8, 14 + bob, YELLOW)]   # бейдж
    elif view == "side":
        dots += [(9, 5 + bob, WHITE), (8, 5 + bob, WHITE), (9, 4 + bob, BLACK), (9, 11 + bob, RED), (9, 12 + bob, RED), (18, 14 + bob, GREY), (19, 15 + bob, GREY)]
    else:
        dots += [(12, 12 + bob, GREY), (11, 15 + bob, GREY)]
    return compose(parts, dots)


def janitor(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(23)
    vest = (255, 140, 20)
    body = m(); rect(body, 5, 9 + bob, 19, 19 + bob)
    arms = m(); rect(arms, 2, 10 + bob, 4, 17 + bob); rect(arms, 20, 10 + bob, 22, 17 + bob)
    head = m(); blob(head, 12, 6 + bob, 4, 3, rng, 0.2, 10)
    helm = m(); blob(helm, 12, 3 + bob, 6, 3, rng, 0.1, 10); rect(helm, 5, 4 + bob, 19, 5 + bob)
    parts = [(legs(frame, bob, (50, 70, 130), 7, 14, 19, 3)), (body, vest), (arms, vest), (head, SKIN), (helm, YELLOW)]
    dots = [(8, 22, BLACK), (15, 22, BLACK), (2, 17 + bob, (60, 60, 60)), (3, 17 + bob, (60, 60, 60)), (21, 17 + bob, (60, 60, 60)), (22, 17 + bob, (60, 60, 60))]
    dots += [(x, 13 + bob, YELLOW) for x in range(6, 19)] + [(x, 16 + bob, YELLOW) for x in range(6, 19)]   # светоотражающие полосы
    if view == "front":
        dots += [(10, 6 + bob, BLACK), (14, 6 + bob, BLACK), (10, 8 + bob, GREY), (11, 8 + bob, GREY), (12, 8 + bob, GREY), (13, 8 + bob, GREY), (14, 8 + bob, GREY), (12, 4 + bob, WHITE)]
    elif view == "side":
        dots += [(9, 6 + bob, BLACK), (7, 8 + bob, GREY), (8, 8 + bob, GREY), (9, 8 + bob, GREY)]
    return compose(parts, dots)


def vitya(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(24)
    sway = 1 if frame else -1
    body = m(); blob(body, 12 + sway, 14 + bob, 8, 7, rng, 0.3, 14)
    head = m(); blob(head, 12 + sway * 2, 6 + bob, 4, 4, rng, 0.2, 10)
    hair = m(); rect(hair, 9 + sway * 2, 1 + bob, 15 + sway * 2, 2 + bob); rect(hair, 8 + sway * 2, 3 + bob, 8 + sway * 2, 5 + bob)
    arms = m(); rect(arms, 3 + sway, 11 + bob, 5 + sway, 17 + bob); rect(arms, 19 + sway, 11 + bob, 21 + sway, 17 + bob)
    bottle = m(); rect(bottle, 20 + sway, 8 + bob, 21 + sway, 15 + bob); rect(bottle, 20 + sway, 5 + bob, 20 + sway, 7 + bob)
    parts = [(legs(frame, bob, (40, 50, 130), 8, 14, 19, 3)), (body, WHITE), (arms, SKIN), (head, SKIN), (hair, (110, 90, 60))]
    if view != "back":
        parts.append((bottle, GREEN))
    dots = [(9, 22, BLACK), (15, 22, BLACK)]
    dots += [(x + sway, 17 + bob, (200, 200, 205)) for x in (9, 12, 15)]   # складки майки
    if view == "front":
        dots += [(10 + sway * 2, 6 + bob, RED), (14 + sway * 2, 6 + bob, RED), (12 + sway * 2, 8 + bob, (230, 60, 70)), (11 + sway * 2, 8 + bob, (230, 60, 70)), (11 + sway * 2, 10 + bob, BLACK), (12 + sway * 2, 10 + bob, BLACK), (13 + sway * 2, 10 + bob, BLACK), (12 + sway, 14 + bob, SKIN)]
    elif view == "side":
        dots += [(9 + sway * 2, 6 + bob, RED), (7 + sway * 2, 8 + bob, (230, 60, 70)), (8 + sway * 2, 10 + bob, BLACK)]
    return compose(parts, dots)


def blogger(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(25)
    skin = (140, 190, 140)
    hood = (60, 60, 75)
    ring = m()
    cy = 7 + bob
    line(ring, [(6, cy - 3), (9, cy - 6), (15, cy - 6), (18, cy - 3), (18, cy + 2), (15, cy + 5), (9, cy + 5), (6, cy + 2), (6, cy - 3)], 1)
    body = m(); rect(body, 8, 11 + bob, 16, 19 + bob)
    head = m(); blob(head, 12, 7 + bob, 4, 4, rng, 0.2, 10)
    hair = m(); rect(hair, 8, 2 + bob, 16, 4 + bob); rect(hair, 7, 4 + bob, 8, 12 + bob); rect(hair, 16, 4 + bob, 17, 12 + bob)
    if view == "back":
        hair = m(); blob(hair, 12, 8 + bob, 5, 6, rng, 0.2, 10)
    arms = m(); rect(arms, 5, 12 + bob, 7, 16 + bob); rect(arms, 17, 12 + bob, 19, 16 + bob)
    phone = m(); rect(phone, 17, 8 + bob, 19, 12 + bob)
    parts = [(ring, WHITE), (legs(frame, bob, (45, 45, 60), 9, 13, 19, 2)), (body, hood), (arms, skin), (head, skin), (hair, (240, 60, 170))]
    if view != "back":
        parts.append((phone, BLACK))
    dots = [(10, 22, BLACK), (14, 22, BLACK), (9, 17 + bob, skin), (15, 14 + bob, skin), (12, 19 + bob, skin)]   # дыры на толстовке
    if view != "back":
        dots += [(18, 9 + bob, (80, 220, 255)), (18, 10 + bob, (80, 220, 255))]
    if view == "front":
        dots += [(10, 7 + bob, RED), (14, 7 + bob, RED), (12, 10 + bob, BLACK), (13, 10 + bob, YELLOW), (11, 10 + bob, BLACK), (12, 14 + bob, PINK), (12, 15 + bob, PINK)]
    elif view == "side":
        dots += [(9, 7 + bob, RED), (8, 10 + bob, YELLOW)]
    return compose(parts, dots)


HEROES3 = {"squid": squid, "clerk": clerk, "janitor": janitor, "uncle_vitya": vitya, "blogger": blogger}

if __name__ == "__main__":
    preview = Image.new("RGBA", (len(HEROES3) * 30, 3 * 30), (60, 40, 20, 255))
    for i, (hero_id, fn) in enumerate(HEROES3.items()):
        sheet = h2.build(fn)
        sheet.save("assets/sprites/player_%s.png" % hero_id)
        for r in range(3):
            preview.alpha_composite(sheet.crop((0, r * 26, 26, r * 26 + 26)), (i * 30 + 2, r * 30 + 2))
    preview.resize((preview.width * 8, preview.height * 8), Image.NEAREST).save("tools/_preview/heroes3.png")
    print("ok")
