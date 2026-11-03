#!/usr/bin/env python3
"""Н12: лотерейный билет «ГОВНОЛОТО» (иконка 32 и 16).
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_ticket.py -> assets/ui/item_lottery_ticket(_s).png"""
from PIL import Image
from pix import *

PAPER = (240, 230, 190); SCRATCH = (180, 180, 190); GOLD = (255, 200, 40)


def big():
    c = Canvas(32, 32)
    c.rect(2, 7, 29, 24, PAPER, dither=(225, 215, 170))
    for x in range(2, 30, 3): c.px(x, 7, (200, 190, 150)); c.px(x, 24, (200, 190, 150))   # рваный край
    c.rect(4, 9, 27, 11, RED); c.pts([(6, 10), (9, 10), (12, 10), (15, 10), (18, 10)], YELLOW)   # «ГОВНОЛОТО»
    for i, x in enumerate((5, 13, 21)):                                   # три поля стирания
        c.rect(x, 14, x + 5, 20, SCRATCH, dither=GREY)
    c.rect(13, 14, 18, 20, PAPER); c.ell(15, 17, 2, 2, BROWN); c.px(15, 15, BROWN)   # одно стёрто: там какашка
    c.pts([(23, 22), (24, 21), (25, 22)], GOLD)                           # монетка-звёздочка
    return c.finish(BROWN, WHITE)


def small():
    c = Canvas(16, 16)
    c.rect(1, 4, 14, 12, PAPER); c.rect(2, 5, 13, 6, RED)
    c.rect(2, 8, 5, 11, SCRATCH); c.rect(7, 8, 9, 11, PAPER); c.px(8, 9, BROWN); c.rect(11, 8, 13, 11, SCRATCH)
    return c.finish(BROWN, WHITE)


def ticket_big():
    """Большой билет для стирания в Ларьке 128x64: бумага, красная шапка (надпись кладёт игра), окно под слоем, корешок."""
    c = Canvas(128, 64)
    c.rect(2, 2, 125, 61, PAPER, dither=(225, 215, 170))
    for x in range(2, 126, 4): c.px(x, 2, (200, 190, 150)); c.px(x + 2, 61, (200, 190, 150))   # рваный край
    c.rect(4, 4, 123, 15, RED, dither=(200, 0, 40))                       # шапка «ГОВНОЛОТО»
    for x in range(8, 120, 12): c.pts([(x, 5), (x + 1, 6)], YELLOW)
    c.rect(18, 22, 109, 53, (255, 250, 225))                              # окно с призом (под слоем)
    c.line(18, 21, 109, 21, BROWN); c.line(18, 54, 109, 54, BROWN); c.line(17, 22, 17, 53, BROWN); c.line(110, 22, 110, 53, BROWN)
    for y in range(20, 58, 4): c.px(116, y, BROWN); c.px(10, y, BROWN)    # перфорация корешков
    c.ell(122, 56, 2, 2, BROWN); c.px(121, 54, (90, 50, 20))              # пятно от говна
    return c.finish(BROWN, WHITE, lim=0.3)


def ticket_foil():
    """Защитный слой 92x32: серебро с дизерингом и блёстками - стирается в игре."""
    c = Canvas(92, 32)
    c.rect(0, 0, 91, 31, (175, 178, 190), dither=(140, 142, 155))
    import random
    rnd = random.Random(3)
    for _ in range(40): c.px(rnd.randrange(92), rnd.randrange(32), WHITE)
    for x in range(6, 90, 14): c.pts([(x, 15), (x + 1, 14), (x + 2, 15), (x + 1, 16)], (110, 110, 125))   # «?» узор
    return c.a


Image.fromarray(ticket_big()).save("assets/ui/ticket_big.png")
Image.fromarray(ticket_foil()).save("assets/ui/ticket_foil.png")
Image.fromarray(big()).save("assets/ui/item_lottery_ticket.png")
Image.fromarray(small()).save("assets/ui/item_lottery_ticket_s.png")
p = Image.new("RGBA", (56, 34), (40, 30, 30, 255))
for im, x in ((Image.open("assets/ui/item_lottery_ticket.png"), 1), (Image.open("assets/ui/item_lottery_ticket_s.png"), 38)):
    p.paste(im, (x, 1), im)
p.resize((448, 272), Image.NEAREST).save("tools/_preview/ticket.png")
