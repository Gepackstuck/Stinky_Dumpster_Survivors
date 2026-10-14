"""Герои пачки 2 с НАСТОЯЩИМИ своими силуэтами (не вариации болванки): бабка, курьер, голубь, крыс-панк.
Лист 4x3 кадров (ряды: бок влево / спиной / лицом), клетка 26 px, как у player.png. Запуск из корня: python3 tools/gen_heroes2.py"""
import random
import sys

sys.path.insert(0, "tools")
import gen_art as ga
from gen_art import BLACK, BLUE, BROWN, CYAN, GREEN, GREY, PINK, RED, WHITE, YELLOW, blob, finish, line, new_img, new_mask, paint, poly, px, rect, union
from PIL import Image

N = 24
SKIN = (240, 190, 150)
DARK = (40, 40, 48)
ORANGE = (255, 140, 20)


def m():
    return new_mask(N, N)


def compose(parts, dots=()):
    """parts: [(маска, цвет)] снизу вверх; dots: [(x, y, цвет)] поверх контура."""
    sil = union(*[mask for mask, _ in parts])
    img = new_img(N, N)
    for mask, color in parts:
        paint(img, mask, color)
    out = finish(img, sil)
    for x, y, c in dots:
        if 0 <= x < N and 0 <= y < N:
            px(out, x, y, c)
    return out


def legs(frame, bob, color, lx=8, rx=14, y0=19, thick=2):
    mask = m()
    a = (lx, rx) if not frame else (lx - 1, rx + 1)
    rect(mask, a[0], y0 + bob, a[0] + thick - 1, 22)
    rect(mask, a[1], y0 + bob, a[1] + thick - 1, 22 - (1 if frame else 0))
    return mask, color


# ---------------------------------------------------------------- бабка
def granny(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(3)
    body = m(); blob(body, 12, 14 + bob, 7, 7, rng, 0.5, 14)
    head = m(); blob(head, 12, 7 + bob, 4, 4, rng, 0.3, 10)
    scarf = m(); poly(scarf, [(7, 6 + bob), (12, 1 + bob), (17, 6 + bob), (16, 6 + bob), (8, 6 + bob)])
    if view == "back":
        scarf = m(); blob(scarf, 12, 6 + bob, 5, 5, rng, 0.2, 12)
    cane = m()
    line(cane, [(20, 12 + bob), (20, 22)], 1)
    line(cane, [(20, 12 + bob), (18, 11 + bob)], 1)
    parts = [(legs(frame, bob, GREY, 9, 14, 20)), (cane, BROWN), (body, BLUE), (head, SKIN), (scarf, RED)]
    dots = [(10, 21, BROWN), (15, 21, BROWN)]
    dots += [(9, 12 + bob, WHITE), (15, 16 + bob, WHITE), (11, 18 + bob, WHITE), (13, 13 + bob, WHITE)]  # горох на халате
    if view == "front":
        for ex in (10, 14):   # очки
            dots += [(ex, 7 + bob, WHITE), (ex + 1, 7 + bob, WHITE), (ex, 8 + bob, WHITE), (ex + 1, 8 + bob, WHITE)]
        dots += [(10, 7 + bob, BLACK), (14, 7 + bob, BLACK), (12, 7 + bob, BLACK), (12, 10 + bob, RED), (11, 10 + bob, RED)]
        dots += [(6, 13 + bob, SKIN), (18, 13 + bob, SKIN)]
    elif view == "side":
        dots += [(9, 7 + bob, WHITE), (8, 7 + bob, WHITE), (9, 8 + bob, WHITE), (8, 8 + bob, WHITE), (9, 7 + bob, BLACK), (7, 9 + bob, SKIN), (13, 3 + bob, YELLOW)]
    else:
        dots += [(12, 3 + bob, PINK), (12, 2 + bob, PINK), (9, 5 + bob, WHITE), (15, 5 + bob, WHITE)]  # пучок
    return compose(parts, dots)


# ---------------------------------------------------------------- курьер
def courier(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(5)
    jacket = (40, 105, 70)
    pants = (60, 62, 95)
    cap_c = (35, 35, 48)
    box = (235, 130, 25)
    body = m(); rect(body, 8, 10 + bob, 16, 19 + bob)
    head = m(); blob(head, 12, 6 + bob, 4, 4, rng, 0.2, 10)
    cap = m(); rect(cap, 8, 2 + bob, 16, 5 + bob); rect(cap, 6 if view == "side" else 8, 5 + bob, 14 if view == "side" else 16, 6 + bob)
    pack = m()
    if view == "back":
        rect(pack, 4, 8 + bob, 19, 21 + bob)
    elif view == "side":
        rect(pack, 13, 8 + bob, 21, 20 + bob)
    else:
        rect(pack, 7, 10 + bob, 8, 18 + bob); rect(pack, 16, 10 + bob, 17, 18 + bob)   # лямки
    arms = m(); rect(arms, 5, 11 + bob, 7, 17 + bob); rect(arms, 17, 11 + bob, 19, 17 + bob)
    parts = [(legs(frame, bob, pants, 8, 14, 19, 3)), (body, jacket), (arms, jacket), (head, SKIN), (cap, cap_c)]
    parts.insert(2 if view != "back" else 4, (pack, box if view != "front" else (200, 105, 20)))
    dots = [(9, 22, BLACK), (15, 22, BLACK)]
    if view == "back":
        dots += [(11, 14 + bob, WHITE), (12, 14 + bob, WHITE), (12, 15 + bob, WHITE), (11, 15 + bob, WHITE), (6, 10 + bob, WHITE), (17, 10 + bob, WHITE)]  # логотип
    if view == "front":
        dots += [(10, 6 + bob, BLACK), (14, 6 + bob, BLACK), (11, 8 + bob, RED), (12, 8 + bob, RED), (13, 8 + bob, RED), (12, 13 + bob, WHITE), (12, 14 + bob, WHITE)]
    if view == "side":
        dots += [(9, 6 + bob, BLACK), (8, 8 + bob, RED), (16, 12 + bob, WHITE), (17, 13 + bob, WHITE)]
    dots += [(9, 3 + bob, PINK), (10, 3 + bob, PINK)]   # значок на кепке
    return compose(parts, dots)


# ---------------------------------------------------------------- голубь
def pigeon(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(9)
    body = m(); blob(body, 12, 14 + bob, 8, 6, rng, 0.4, 14)
    head = m(); blob(head, 12 if view != "side" else 8, 6 + bob, 4, 4, rng, 0.2, 10)
    wing_up = frame == 1
    wings = m()
    if view == "side":
        poly(wings, [(10, 12 + bob), (18, 10 + (-3 if wing_up else 0) + bob), (20, 16 + bob), (12, 17 + bob)])
    else:
        poly(wings, [(3, 12 + bob), (6, 9 + bob + (-3 if wing_up else 0)), (8, 16 + bob)]); poly(wings, [(21, 12 + bob), (18, 9 + bob + (-3 if wing_up else 0)), (16, 16 + bob)])
    tail = m(); poly(tail, [(9, 18 + bob), (15, 18 + bob), (17, 23), (7, 23)]) if view == "back" else poly(tail, [(18, 15 + bob), (23, 17), (21, 20), (16, 19 + bob)]) if view == "side" else m()
    beak = m()
    if view == "front":
        poly(beak, [(11, 8 + bob), (13, 8 + bob), (12, 11 + bob)])
    elif view == "side":
        poly(beak, [(5, 6 + bob), (2, 8 + bob), (5, 9 + bob)])
    feet = m(); rect(feet, 9 if not frame else 8, 20 + bob, 10 if not frame else 9, 22); rect(feet, 14 if not frame else 15, 20 + bob, 15 if not frame else 16, 22)
    parts = [(feet, ORANGE), (tail, GREY), (body, (150, 150, 165)), (wings, (110, 110, 130)), (head, (150, 150, 165)), (beak, YELLOW)]
    dots = [(12, 10 + bob, GREEN), (11, 11 + bob, PINK), (13, 11 + bob, GREEN)] if view != "back" else [(12, 10 + bob, GREEN), (11, 11 + bob, PINK)]
    if view == "front":
        dots += [(10, 5 + bob, RED), (14, 5 + bob, RED), (10, 4 + bob, BLACK), (14, 4 + bob, BLACK), (12, 15 + bob, WHITE), (11, 16 + bob, WHITE)]
    elif view == "side":
        dots += [(7, 5 + bob, RED), (7, 4 + bob, BLACK)]
    else:
        dots += [(12, 20 + bob, WHITE), (13, 21, WHITE)]
    return compose(parts, dots)


# ---------------------------------------------------------------- крыс-панк
def rat(view, frame):
    bob = 1 if frame else 0
    rng = random.Random(11)
    body = m(); blob(body, 12, 14 + bob, 6, 7, rng, 0.4, 14)
    head = m(); blob(head, 12, 7 + bob, 5, 4, rng, 0.2, 10)
    ears = m(); blob(ears, 6, 5 + bob, 2, 2, rng, 0.2, 8); blob(ears, 18, 5 + bob, 2, 2, rng, 0.2, 8)
    if view == "side":
        ears = m(); blob(ears, 10, 2 + bob, 3, 3, rng, 0.2, 8)
    mohawk = m()
    for x in (10, 12, 14):
        poly(mohawk, [(x - 1, 4 + bob), (x, -0 + bob), (x + 1, 4 + bob)])
    tail = m(); line(tail, [(17, 18 + bob), (21, 19), (22, 15 + bob), (20, 13 + bob)], 1) if view != "front" else line(tail, [(16, 19 + bob), (20, 21), (21, 18)], 1)
    jacket = m(); rect(jacket, 7, 11 + bob, 17, 18 + bob)
    parts = [(tail, PINK), (legs(frame, bob, GREY, 8, 14, 19, 2)), (body, GREY), (jacket, DARK), (head, GREY), (ears, PINK), (mohawk, GREEN)]
    dots = [(9, 22, BLACK), (15, 22, BLACK), (9, 13 + bob, WHITE), (15, 13 + bob, WHITE), (12, 17 + bob, YELLOW), (8, 17 + bob, YELLOW), (16, 17 + bob, YELLOW)]  # заклёпки
    if view == "front":
        dots += [(10, 7 + bob, RED), (14, 7 + bob, RED), (12, 9 + bob, PINK), (8, 9 + bob, WHITE), (7, 10 + bob, WHITE), (16, 9 + bob, WHITE), (17, 10 + bob, WHITE)]
    elif view == "side":
        dots += [(8, 7 + bob, RED), (6, 9 + bob, PINK), (5, 10 + bob, WHITE)]
    return compose(parts, dots)


HEROES2 = {"granny": granny, "courier": courier, "pigeon": pigeon, "punk": rat}


def build(fn):
    rows = []
    for view in ("side", "back", "front"):
        cells = [fn(view, f) for f in (0, 1, 0, 1)]
        rows.append(ga.sheet(cells))
    out = ga.new_img(rows[0].size[0], rows[0].size[1] * 3)
    for i, r in enumerate(rows):
        out.paste(r, (0, i * rows[0].size[1]))
    return out


if __name__ == "__main__":
    preview = Image.new("RGBA", (len(HEROES2) * 30, 3 * 30), (60, 40, 20, 255))
    for i, (hero_id, fn) in enumerate(HEROES2.items()):
        sheet = build(fn)
        sheet.save("assets/sprites/player_%s.png" % hero_id)
        for r in range(3):
            preview.alpha_composite(sheet.crop((0, r * 26, 26, r * 26 + 26)), (i * 30 + 2, r * 30 + 2))
    preview.resize((preview.width * 8, preview.height * 8), Image.NEAREST).save("tools/_preview/heroes2.png")
    print("ok")
