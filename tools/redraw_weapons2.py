#!/usr/bin/env python3
"""Оружие 24×24, смотрит вправо. Крупнее и детальнее, чтобы читалось по названию."""
import sys, os
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
S = 24
LG = (205, 205, 215); MG = (150, 150, 160); TIN = (190, 200, 210)
def fin(c, sh, hi=WHITE): return c.finish(sh, hi, lim=0.14)

def lighter():  # зажигалка Zippo с пламенем
    c = Canvas(S, S)
    c.rect(3, 9, 12, 20, MG, dither=LG); c.rect(4, 10, 5, 19, WHITE)           # корпус
    c.rect(3, 6, 12, 9, LG); c.line(3, 9, 12, 9, DGREY)                          # крышка
    c.rect(6, 3, 10, 6, GREY); c.ell(8, 4, 2, 1, DGREY); c.px(7, 3, WHITE)       # колёсико
    c.rect(7, 12, 10, 16, RED); c.px(8, 13, YELLOW)                              # гравировка
    c.pts([(13, 7), (13, 8), (14, 6)], DGREY)
    c.pts([(9, 2), (9, 1), (8, 0)], DGREY)
    c.ell(9, 0, 3, 0, ORANGE)
    return fin(c, PURPLE, YELLOW)

def lighter2():
    c = Canvas(S, S)
    # зажигалка лежит горизонтально, пламя справа
    c.rect(0, 9, 11, 17, MG, dither=LG); c.rect(1, 10, 10, 11, WHITE)
    c.rect(11, 9, 14, 17, LG); c.line(11, 9, 11, 17, DGREY)
    c.rect(12, 6, 14, 8, GREY); c.px(13, 6, WHITE)                               # колёсико
    c.rect(3, 13, 8, 15, RED); c.px(4, 14, YELLOW); c.px(6, 14, YELLOW)
    c.ell(18, 10, 3, 4, ORANGE); c.ell(18, 11, 2, 3, YELLOW); c.pts([(18, 5), (19, 6), (17, 6)], ORANGE); c.px(18, 12, WHITE)
    c.rect(14, 10, 15, 12, DGREY)
    return fin(c, PURPLE, YELLOW)

def slipper():  # тапок-бомба
    c = Canvas(S, S)
    c.ell(11, 15, 10, 4, BROWN, dither=(150, 90, 40))                             # подошва
    c.ell(11, 12, 9, 4, PINK, dither=(255, 120, 245))                             # верх
    c.rect(2, 9, 8, 12, PINK); c.rect(14, 8, 20, 13, PINK)
    c.ell(16, 10, 4, 3, (255, 90, 245)); c.line(14, 8, 18, 8, WHITE)              # носок-блик
    c.rect(4, 6, 10, 9, BLACK); c.rect(5, 7, 9, 9, (40, 40, 40))                  # пятка/вырез
    c.line(1, 18, 21, 18, BROWN, 2)
    c.rect(8, 4, 12, 8, DGREY); c.rect(9, 5, 11, 7, RED); c.px(10, 6, YELLOW)    # бомба-динамит
    c.line(10, 4, 12, 1, YELLOW); c.pts([(13, 0), (12, 0)], ORANGE); c.px(13, 1, WHITE)  # фитиль
    return fin(c, PURPLE, YELLOW)

def mop():
    c = Canvas(S, S)
    c.line(1, 20, 14, 8, BROWN, 2); c.line(1, 19, 13, 8, (170, 100, 50))        # палка
    c.rect(13, 3, 17, 12, GREY, dither=LG); c.line(13, 3, 17, 3, WHITE)         # зажим
    for i, y in enumerate(range(5, 22)):                                         # мокрые пряди
        c.px(18 + (i % 3), y, WHITE if i % 2 else (190, 190, 170))
        c.px(19 + (i % 2), y, (170, 170, 140))
    c.rect(17, 6, 20, 20, (200, 200, 180), dither=(150, 150, 130))
    c.pts([(21, 22), (22, 20), (19, 23)], CYAN); c.pts([(16, 22), (14, 21)], GREEN)
    return fin(c, CYAN, WHITE)

def bottle():  # бутылка пива «розочка»
    c = Canvas(S, S)
    c.rect(2, 8, 13, 17, GREEN, dither=(20, 170, 20)); c.ell(3, 12, 3, 5, GREEN)
    c.rect(13, 10, 20, 15, GREEN); c.rect(20, 9, 22, 16, GREY); c.line(20, 9, 22, 9, WHITE)  # горло, крышка
    c.rect(5, 10, 11, 15, WHITE); c.rect(6, 11, 10, 13, RED); c.px(8, 12, YELLOW); c.px(7, 14, BLACK) # этикетка
    c.line(3, 8, 12, 8, (180, 255, 180)); c.pts([(2, 11), (2, 12)], WHITE)       # блик
    c.pts([(1, 17), (3, 18), (6, 18)], YELLOW)                                    # пена/капли
    c.pts([(14, 11), (15, 11)], (180, 255, 180))
    return fin(c, PURPLE, YELLOW)

def mosin():
    c = Canvas(S, S)
    c.rect(0, 13, 7, 19, BROWN, dither=(150, 90, 40)); c.rect(0, 12, 2, 13, BROWN)       # приклад
    c.rect(7, 12, 12, 15, BROWN); c.rect(7, 12, 11, 12, (150, 90, 40))                    # ложе
    c.rect(8, 10, 12, 12, DGREY); c.rect(8, 9, 10, 10, LG); c.px(11, 8, LG)                # затвор и рукоять
    c.rect(12, 11, 21, 13, DGREY, dither=GREY); c.line(12, 11, 21, 11, WHITE)              # ствол
    c.rect(17, 13, 20, 14, BROWN)                                                          # цевьё
    c.pts([(20, 9), (20, 10)], BLACK)                                                      # мушка
    c.line(21, 12, 23, 12, LG); c.px(23, 12, WHITE)                                        # штык
    c.rect(8, 15, 10, 16, GREY); c.px(9, 15, BLACK)                                        # спуск
    c.pts([(4, 15), (5, 17)], (190, 120, 60))
    return fin(c, GREEN, WHITE)

def frying_pan():
    c = Canvas(S, S)
    c.line(0, 21, 9, 13, BROWN, 3); c.line(0, 20, 8, 13, (170, 100, 50))                  # ручка
    c.ell(16, 9, 7, 7, DGREY, dither=GREY); c.ell(16, 9, 5, 5, BLACK)                     # сковорода
    c.ell(15, 8, 3, 3, YELLOW); c.ell(15, 8, 1, 1, ORANGE)                                 # яичница
    c.pts([(11, 4), (12, 3), (13, 2)], WHITE); c.pts([(20, 14), (21, 13)], GREY)
    c.px(7, 15, GREY); c.px(8, 14, LG)
    return fin(c, GREEN, WHITE)

def syringe():
    c = Canvas(S, S)
    c.rect(2, 10, 5, 13, PINK); c.rect(0, 9, 1, 14, GREY)                                  # поршень
    c.rect(5, 9, 16, 14, (220, 240, 255), dither=WHITE); c.rect(7, 11, 15, 13, GREEN)      # цилиндр с ядом
    for x in (8, 10, 12, 14): c.px(x, 9, BLACK)                                            # деления
    c.rect(16, 10, 18, 13, GREY); c.line(18, 11, 23, 11, LG); c.px(23, 11, WHITE)          # игла
    c.pts([(3, 8), (3, 15)], BLACK); c.pts([(23, 13), (22, 15)], GREEN)
    return fin(c, PURPLE, YELLOW)

def condensed_milk():
    c = Canvas(S, S)
    c.rect(4, 6, 17, 20, TIN, dither=WHITE); c.rect(4, 6, 17, 8, GREY); c.rect(4, 18, 17, 20, GREY)  # банка
    c.rect(4, 9, 17, 17, BLUE); c.rect(5, 10, 8, 16, (80, 80, 255))                        # этикетка
    c.ell(12, 13, 3, 3, WHITE); c.px(11, 12, BLACK); c.px(13, 12, BLACK); c.px(12, 14, PINK)  # корова
    c.pts([(10, 10), (14, 10)], WHITE)
    c.rect(18, 8, 21, 10, WHITE); c.pts([(21, 11), (21, 12), (20, 13)], WHITE)             # капает
    c.rect(18, 7, 18, 11, GREY)                                                            # дыра
    return fin(c, CYAN, WHITE)

WEAP = {"lighter": lighter2, "slipper": slipper, "mop": mop, "bottle": bottle,
        "mosin": mosin, "frying_pan": frying_pan, "syringe": syringe, "condensed_milk": condensed_milk}
if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(WEAP)
    k = 8; W = S * k
    prev = Image.new("RGBA", (len(names) * (W + 20) + 20, W + 20), (45, 30, 20, 255))
    for i, n in enumerate(names):
        im = Image.fromarray(WEAP[n](), "RGBA")
        os.makedirs("tools/_preview/weapons_new", exist_ok=True); im.save(f"tools/_preview/weapons_new/held_{n}.png")
        prev.paste(im.resize((W, W), Image.NEAREST), (20 + i * (W + 20), 10), im.resize((W, W), Image.NEAREST))
    prev.save("tools/_preview/weapons_sample2.png"); print(prev.size)
