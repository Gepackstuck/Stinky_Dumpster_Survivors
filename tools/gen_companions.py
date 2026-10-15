"""Питомцы и структуры пачки 3 (спрайты 2 кадра + иконки предметов 16x16).
Запуск из корня: python3 tools/gen_companions.py"""
import random
import sys

sys.path.insert(0, "tools")
from gen_art import BLACK, BLUE, BROWN, CYAN, GREEN, GREY, PINK, RED, UI, WHITE, YELLOW, blob, finish, line, new_img, new_mask, paint, poly, px, rect, union
from PIL import Image

ORANGE = (255, 120, 0)
SP = "assets/sprites/"


def build(w, h, layers, dots=()):
    sil = union(*[m for m, _ in layers])
    img = new_img(w, h)
    for m, c in layers:
        paint(img, m, c)
    out = finish(img, sil)
    for x, y, c in dots:
        px(out, x, y, c)
    return out


def sheet(frames):
    w, h = frames[0].size
    out = new_img(w * len(frames), h)
    for i, f in enumerate(frames):
        out.alpha_composite(f, (i * w, 0))
    return out


# ---------------------------------------------------------------- пёс (смотрит вправо), 20x12
def dog(frame):
    W, H = 20, 12
    m = lambda: new_mask(W, H)
    body = m(); blob(body, 9, 6, 6, 3, random.Random(61), 0.5, 12)
    head = m(); blob(head, 15, 5, 3, 3, random.Random(62), 0.3, 10)
    ear = m(); poly(ear, [(14, 1), (16, 1), (16, 4), (14, 4)])
    tail = m(); line(tail, [(3, 4), (1, 2 if frame == 0 else 3)], 0)
    l = 0 if frame == 0 else 1
    legs = m(); rect(legs, 5, 9, 6, 10 + l); rect(legs, 11, 9, 12, 11 - l)
    return build(W, H, [(body, BROWN), (head, BROWN), (ear, BLACK), (tail, BROWN), (legs, BROWN)],
                 [(17, 5, BLACK), (16, 4, WHITE), (11, 5, YELLOW), (7, 5, YELLOW), (8, 7, PINK), (18, 7, RED)])


# ---------------------------------------------------------------- голубь-бомбардир, 16x12
def pigeon(frame):
    W, H = 16, 12
    m = lambda: new_mask(W, H)
    body = m(); blob(body, 8, 7, 5, 3, random.Random(63), 0.4, 12)
    head = m(); blob(head, 13, 4, 2, 2, random.Random(64), 0.2, 8)
    beak = m(); rect(beak, 15, 4, 15, 5)
    tail = m(); poly(tail, [(0, 6), (3, 5), (3, 8)])
    wing = m()
    if frame == 0:
        poly(wing, [(6, 3), (9, 3), (8, 0), (5, 1)])
    else:
        poly(wing, [(5, 7), (10, 7), (9, 10), (4, 10)])
    return build(W, H, [(body, GREY), (head, GREY), (beak, YELLOW), (tail, GREY), (wing, WHITE)],
                 [(13, 3, RED), (12, 8, WHITE), (7, 8, PINK), (1, 7, BLACK)])


# ---------------------------------------------------------------- мина из крышек, 14x8
def mine(frame):
    W, H = 14, 8
    m = lambda: new_mask(W, H)
    disc = m(); blob(disc, 7, 5, 6, 2, random.Random(65), 0.3, 10)
    dome = m(); rect(dome, 4, 1, 9, 3)
    return build(W, H, [(disc, GREY), (dome, RED if frame == 0 else YELLOW)],
                 [(3, 5, WHITE), (6, 5, BLACK), (9, 5, WHITE), (10, 5, BLACK), (6, 0, YELLOW if frame else RED), (7, 0, ORANGE)])


# ---------------------------------------------------------------- лампа-вонялка, 16x24
def lamp(frame):
    W, H = 16, 24
    m = lambda: new_mask(W, H)
    base = m(); rect(base, 3, 20, 12, 22)
    pole = m(); rect(pole, 7, 8, 8, 20)
    shade = m(); poly(shade, [(2, 9), (13, 9), (11, 3), (4, 3)])
    glow = m(); poly(glow, [(3, 9), (12, 9), (13, 12 + frame), (2, 12 + frame)])
    return build(W, H, [(base, BROWN), (pole, GREY), (shade, GREEN), (glow, YELLOW)],
                 [(6, 5, WHITE), (5, 6, WHITE), (9, 6, BLACK), (4, 10 + frame, WHITE), (11, 11, GREEN), (3, 1 + frame, GREEN), (12, 0, GREEN), (7, 14, BLACK)])


# ---------------------------------------------------------------- тележка-миномёт, 24x18
def mortar(frame):
    W, H = 24, 18
    m = lambda: new_mask(W, H)
    cart = m(); rect(cart, 3, 8, 18, 14)
    wheel1 = m(); blob(wheel1, 6, 15, 2, 2, random.Random(66), 0.2, 8)
    wheel2 = m(); blob(wheel2, 15, 15, 2, 2, random.Random(67), 0.2, 8)
    tube = m(); poly(tube, [(10, 8), (13, 8), (18, 1), (15, 0)])
    mesh = m(); rect(mesh, 3, 8, 18, 9)
    return build(W, H, [(cart, GREY), (mesh, WHITE), (tube, BLACK), (wheel1, BLACK), (wheel2, BLACK)],
                 [(5, 11, RED), (9, 11, RED), (13, 11, RED), (6, 15, WHITE), (15, 15, WHITE), (16, 1 if frame == 0 else 0, YELLOW if frame else GREY)] +
                 ([(17, 0, YELLOW), (18, 0, ORANGE), (16, 0, RED)] if frame else []))


# ---------------------------------------------------------------- иконки предметов 16x16
def _icon(layers, dots=()):
    return build(16, 16, layers, dots)


def im():
    return new_mask(16, 16)


def icon_dog():
    head = im(); blob(head, 8, 8, 6, 5, random.Random(71), 0.5, 12)
    ear1 = im(); poly(ear1, [(2, 2), (6, 4), (3, 8)])
    ear2 = im(); poly(ear2, [(13, 2), (9, 4), (12, 8)])
    snout = im(); rect(snout, 6, 9, 10, 12)
    return _icon([(head, BROWN), (ear1, BLACK), (ear2, BLACK), (snout, WHITE)], [(5, 7, WHITE), (11, 7, WHITE), (5, 8, BLACK), (11, 8, BLACK), (8, 10, BLACK), (9, 12, RED), (8, 12, PINK)])


def icon_pigeon():
    body = im(); blob(body, 8, 9, 6, 4, random.Random(72), 0.5, 12)
    head = im(); blob(head, 12, 5, 3, 3, random.Random(73), 0.2, 8)
    wing = im(); poly(wing, [(3, 8), (8, 3), (10, 9), (5, 12)])
    return _icon([(body, GREY), (head, GREY), (wing, WHITE)], [(13, 4, RED), (15, 5, YELLOW), (14, 5, YELLOW), (6, 13, PINK), (7, 14, PINK), (8, 13, PINK), (1, 10, BLACK)])


def icon_mine():
    disc = im(); blob(disc, 8, 10, 7, 3, random.Random(74), 0.3, 12)
    dome = im(); rect(dome, 5, 5, 10, 8)
    return _icon([(disc, GREY), (dome, RED)], [(8, 3, YELLOW), (8, 4, BROWN), (4, 10, WHITE), (7, 10, BLACK), (10, 10, WHITE), (12, 10, BLACK), (7, 6, WHITE), (9, 2, ORANGE)])


def icon_lamp():
    base = im(); rect(base, 4, 13, 11, 15)
    pole = im(); rect(pole, 7, 7, 8, 13)
    shade = im(); poly(shade, [(2, 8), (13, 8), (11, 2), (4, 2)])
    return _icon([(base, BROWN), (pole, GREY), (shade, GREEN)], [(6, 4, WHITE), (5, 5, WHITE), (9, 5, BLACK), (4, 10, YELLOW), (7, 10, YELLOW), (11, 10, YELLOW), (2, 12, GREEN), (13, 12, GREEN)])


def icon_mortar():
    cart = im(); rect(cart, 2, 8, 13, 12)
    w1 = im(); blob(w1, 4, 13, 2, 2, random.Random(75), 0.2, 8)
    w2 = im(); blob(w2, 11, 13, 2, 2, random.Random(76), 0.2, 8)
    tube = im(); poly(tube, [(7, 8), (10, 8), (14, 2), (11, 1)])
    return _icon([(cart, GREY), (tube, BLACK), (w1, BLACK), (w2, BLACK)], [(4, 10, RED), (7, 10, RED), (10, 10, RED), (13, 0, YELLOW), (14, 0, ORANGE), (4, 13, WHITE), (11, 13, WHITE)])


SPRITES = {"pet_dog": dog, "pet_pigeon": pigeon, "structure_mine": mine, "structure_lamp": lamp, "structure_mortar": mortar}
ICONS = {"stray_dog": icon_dog, "bomber_pigeon": icon_pigeon, "bottle_mine": icon_mine, "stink_lamp": icon_lamp, "cart_mortar": icon_mortar}

if __name__ == "__main__":
    prev = Image.new("RGBA", (330, 60), (60, 40, 20, 255))
    x = 4
    for name, fn in SPRITES.items():
        s = sheet([fn(0), fn(1)])
        s.save(SP + name + ".png")
        prev.alpha_composite(s, (x, 4))
        x += s.width + 6
    x = 4
    for name, fn in ICONS.items():
        img = fn()
        img.save(UI + "item_" + name + ".png")
        prev.alpha_composite(img, (x, 38))
        x += 20
    prev.resize((prev.width * 5, prev.height * 5), Image.NEAREST).save("tools/_preview/companions.png")
    print("ok")
