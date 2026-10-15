#!/usr/bin/env python3
"""Иконки предметов (ларёк), статов и перков 16×16. python3 tools/redraw_icons.py [--apply] [id ...]"""
import sys, math
import numpy as np
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
TIN = (190, 200, 210); LG = (205, 205, 215); MG = (150, 150, 160); WOOD = (170, 100, 50); CREAM = (255, 240, 170)
I = {}
def icon(sh=PURPLE, hi=WHITE, w=14, h=14, lim=0.15):
    def d(f): I[f.__name__] = (f, sh, hi, w, h, lim); return f
    return d

@icon()
def bandage(c):
    c.rect(1, 5, 12, 9, WHITE, dither=(235, 215, 190)); c.rect(5, 4, 8, 10, WHITE); c.rect(6, 6, 7, 8, (200, 40, 40)); c.pts([(3, 6), (3, 8), (10, 6), (10, 8)], BROWN); c.pts([(0, 8), (13, 5)], WHITE)
@icon(GREY, WHITE)
def barbed_wire(c):
    for x in range(14): c.px(x, 6 + round(math.sin(x / 2.2) * 1.5), MG); c.px(x, 7 - round(math.sin(x / 2.2) * 1.5), LG)
    for bx in (3, 10):
        for dx, dy in ((-2, -3), (2, -3), (-2, 3), (2, 3)): c.line(bx, 7, bx + dx, 7 + dy, LG)
        c.px(bx, 7, WHITE)
@icon(GREEN)
def battery(c):
    c.rect(2, 3, 11, 12, DGREY); c.rect(2, 3, 11, 5, (20, 160, 20)); c.rect(5, 1, 8, 2, GREY); c.rect(3, 6, 10, 11, GREEN); c.line(7, 7, 5, 10, BLACK); c.line(5, 10, 8, 10, BLACK); c.px(7, 7, YELLOW); c.px(4, 6, WHITE)
@icon()
def binoculars(c):
    c.rect(1, 3, 5, 11, DGREY); c.rect(8, 3, 12, 11, DGREY); c.rect(5, 5, 8, 8, GREY); c.ell(3, 10, 3, 2, BLACK); c.ell(10, 10, 3, 2, BLACK); c.px(2, 10, CYAN); c.px(9, 10, CYAN); c.pts([(2, 3), (10, 3)], WHITE)
@icon(RED)
def bloody_rag(c):
    c.rect(1, 2, 11, 11, (200, 190, 175), dither=(170, 160, 150)); c.pts([(0, 5), (12, 12), (2, 12), (11, 1)], (200, 190, 175)); c.ell(5, 6, 2.5, 3, RED); c.pts([(5, 10), (5, 12), (9, 5), (8, 6)], RED); c.px(4, 5, PINK)
@icon()
def bomber_pigeon(c):
    c.ell(7, 8, 5, 3.5, GREY, dither=LG); c.ell(11, 5, 2.5, 2.5, LG); c.pts([(13, 5), (13, 6)], ORANGE); c.px(11, 4, BLACK); c.px(12, 4, RED); c.line(2, 8, 0, 4, DGREY); c.line(4, 7, 3, 3, DGREY); c.rect(5, 11, 8, 13, BLACK); c.px(6, 11, RED); c.px(5, 13, ORANGE)
    c.pts([(6, 12)], YELLOW)
@icon()
def bone_club(c):
    c.line(2, 12, 11, 3, WHITE, 2); c.ell(12, 2, 2, 2, WHITE); c.ell(10, 1, 1.5, 1.5, WHITE); c.ell(1, 12, 2, 2, WHITE); c.ell(3, 13, 1.5, 1.5, WHITE); c.pts([(8, 5), (4, 9)], (200, 195, 170)); c.pts([(2, 12), (12, 1)], RED)
@icon(PURPLE, YELLOW)
def bottle_cap(c):
    c.ell(6.5, 6.5, 6, 6, YELLOW, dither=ORANGE)
    for a in range(0, 360, 30): c.px(round(6.5 + math.cos(math.radians(a)) * 6), round(6.5 + math.sin(math.radians(a)) * 6), ORANGE)
    c.ell(6.5, 6.5, 3.5, 3.5, RED); c.px(5, 5, WHITE); c.pts([(6, 7), (7, 7)], YELLOW)
@icon(GREEN)
def bottle_mine(c):
    c.ell(6.5, 9, 6, 3, DGREY); c.rect(1, 9, 12, 12, DGREY); c.ell(6.5, 7, 5, 2, TIN); c.rect(5, 4, 8, 6, GREEN); c.rect(6, 2, 7, 3, GREEN); c.px(6, 2, WHITE); c.px(6, 8, RED); c.px(3, 7, WHITE); c.pts([(4, 11), (9, 11)], YELLOW)
@icon(PURPLE, YELLOW, 14, 18)
def bucket_turret(c):
    c.rect(2, 7, 11, 16, MG, dither=LG); c.rect(1, 6, 12, 7, GREY); c.rect(3, 9, 4, 15, WHITE); c.rect(9, 16, 10, 17, DGREY); c.rect(3, 16, 4, 17, DGREY)
    c.rect(5, 2, 8, 5, DGREY); c.rect(8, 3, 13, 4, BLACK); c.px(13, 3, RED); c.pts([(5, 11), (7, 12), (9, 11)], RUST if False else (160, 70, 30)); c.line(1, 6, 0, 3, GREY)
@icon(PURPLE, YELLOW, 14, 18)
def cart_mortar(c):
    c.rect(1, 9, 12, 14, (170, 175, 185), dither=DGREY); c.line(1, 15, 12, 15, DGREY); c.line(3, 9, 3, 15, DGREY); c.line(7, 9, 7, 15, DGREY); c.line(10, 9, 10, 15, DGREY)
    c.ell(3, 16, 1.5, 1.5, BLACK); c.ell(10, 16, 1.5, 1.5, BLACK); c.line(12, 9, 13, 5, GREY, 2)
    c.rect(4, 2, 7, 8, DGREY); c.rect(3, 1, 8, 2, GREY); c.px(5, 0, ORANGE); c.px(6, 1, YELLOW)
@icon(PURPLE, YELLOW)
def cigarette(c):
    c.rect(0, 7, 8, 9, WHITE); c.rect(8, 7, 11, 9, ORANGE); c.rect(11, 7, 12, 9, RED); c.px(12, 8, YELLOW); c.pts([(13, 5), (12, 3), (13, 1)], GREY); c.pts([(4, 8), (6, 8)], (200, 190, 170)); c.px(2, 7, WHITE)
@icon(RED)
def coupon(c):
    c.rect(1, 2, 12, 11, YELLOW, dither=(230, 230, 0)); c.rect(2, 4, 11, 4, RED); c.rect(3, 6, 10, 6, BLACK); c.rect(3, 8, 8, 8, BLACK); c.px(10, 9, RED); c.pts([(0, 5), (0, 8), (13, 5), (13, 8)], BLACK)
@icon(RED, WHITE)
def crowbar(c):
    c.line(2, 12, 11, 3, RED, 2); c.pts([(11, 1), (12, 1), (13, 2)], RED); c.line(11, 2, 13, 4, RED, 2); c.px(1, 13, RED); c.px(0, 12, RED); c.pts([(3, 11), (6, 8)], WHITE)
@icon(ORANGE, YELLOW)
def crown(c):
    c.rect(1, 6, 12, 11, YELLOW, dither=ORANGE); c.pts([(1, 3), (2, 4), (3, 5), (6, 2), (5, 3), (7, 3), (10, 5), (11, 4), (12, 3), (6, 4), (6, 5), (7, 5)], YELLOW)
    c.px(1, 3, RED); c.px(6, 1, RED); c.px(12, 3, RED); c.pts([(3, 8), (6, 8), (9, 8)], RED); c.pts([(4, 8), (7, 8), (10, 8)], CYAN)
@icon(PURPLE, WHITE)
def dead_rat(c):
    c.ell(6, 8, 5, 3, GREY, dither=DGREY); c.ell(11, 7, 2.5, 2, GREY); c.px(13, 7, PINK); c.px(11, 6, RED); c.pts([(10, 5), (11, 5)], PINK); c.line(1, 8, 0, 12, PINK); c.pts([(4, 11), (7, 11), (9, 10)], PINK); c.px(12, 6, BLACK)
@icon(GREEN)
def diarrhea(c):
    c.ell(6, 9, 5, 3, BROWN); c.ell(6, 6, 3.5, 2.5, BROWN); c.ell(6, 3.5, 2, 1.5, BROWN); c.px(6, 1, BROWN); c.px(4, 5, (150, 90, 40)); c.px(3, 8, (150, 90, 40)); c.pts([(0, 5), (12, 4), (13, 8), (1, 12), (11, 12)], GREEN); c.pts([(6, 12), (6, 13)], YELLOW)
@icon(CYAN)
def dirty_glasses(c):
    c.ell(3.5, 7, 3, 3, BLACK); c.ell(10, 7, 3, 3, BLACK); c.rect(6, 6, 7, 6, BLACK); c.pts([(2, 6), (3, 5), (9, 6), (10, 5)], CYAN); c.pts([(4, 8), (11, 8)], GREEN); c.line(0, 5, 1, 5, BLACK); c.px(12, 9, BROWN)
@icon(ORANGE, YELLOW)
def dried_fish(c):
    c.ell(6, 7, 5.5, 3, YELLOW, dither=(200, 180, 0)); c.pts([(11, 4), (12, 3), (13, 3), (12, 7), (13, 10), (11, 9), (12, 5), (12, 6)], ORANGE); c.px(3, 6, BLACK); c.px(2, 7, WHITE); c.pts([(5, 5), (7, 4), (8, 5), (6, 9), (8, 8)], ORANGE); c.pts([(0, 7)], BROWN)
@icon(GREEN)
def energy_can(c):
    c.rect(3, 2, 10, 12, DGREY); c.rect(3, 2, 10, 3, GREY); c.rect(3, 11, 10, 12, GREY); c.rect(4, 4, 9, 10, (30, 30, 40)); c.pts([(7, 4), (6, 6), (7, 6), (6, 9), (8, 7), (7, 7), (7, 5)], YELLOW); c.px(4, 4, GREEN); c.px(9, 9, GREEN); c.pts([(8, 1)], WHITE)
@icon(CYAN, WHITE)
def foil_hat(c):
    c.pts([(7, 0), (7, 1), (6, 2), (8, 2)], LG); c.line(1, 11, 6, 3, LG, 2); c.line(12, 11, 8, 3, LG, 2); c.rect(2, 8, 11, 11, MG, dither=WHITE); c.pts([(5, 5), (8, 6), (4, 9), (9, 9)], WHITE); c.pts([(3, 7), (10, 7)], CYAN)
@icon(CYAN, WHITE)
def ghost_drunk(c):
    c.ell(6.5, 5, 4.5, 4.5, (150, 235, 255), dither=WHITE); c.rect(2, 5, 11, 11, (150, 235, 255), dither=WHITE); c.pts([(2, 12), (4, 12), (6, 12), (8, 12), (11, 12), (3, 13), (7, 13), (10, 13)], (150, 235, 255))
    c.px(4, 5, BLACK); c.px(8, 5, BLACK); c.px(5, 5, RED); c.px(9, 5, RED); c.rect(5, 8, 8, 8, BLACK); c.rect(10, 8, 12, 11, GREEN); c.px(11, 7, WHITE)
@icon(PINK)
def ghost_granny(c):
    c.ell(6.5, 6, 4.5, 5, (150, 235, 255), dither=WHITE); c.rect(2, 6, 11, 11, (150, 235, 255), dither=WHITE); c.pts([(2, 12), (5, 12), (8, 12), (11, 12)], (150, 235, 255))
    c.rect(1, 1, 12, 3, PINK); c.ell(6.5, 2, 4, 2, PINK); c.px(4, 6, BLACK); c.px(8, 6, BLACK); c.pts([(3, 6), (9, 6)], WHITE); c.rect(5, 9, 8, 9, BLACK); c.px(2, 7, GREY)
@icon(ORANGE, YELLOW)
def gold_tooth(c):
    c.ell(4, 4, 3.5, 3, YELLOW); c.ell(9, 4, 3.5, 3, YELLOW); c.rect(1, 4, 12, 8, YELLOW, dither=ORANGE); c.rect(2, 9, 5, 12, YELLOW); c.rect(8, 9, 11, 12, YELLOW); c.px(3, 3, WHITE); c.px(2, 4, WHITE); c.pts([(6, 7), (6, 8)], ORANGE); c.pts([(11, 1), (12, 0)], WHITE)
@icon(ORANGE, YELLOW)
def golden_toilet(c):
    c.rect(2, 1, 10, 5, YELLOW, dither=ORANGE); c.rect(1, 6, 12, 8, YELLOW, dither=ORANGE); c.ell(6.5, 8, 5, 2, YELLOW); c.rect(3, 9, 9, 12, YELLOW, dither=ORANGE); c.rect(2, 12, 10, 13, ORANGE); c.pts([(3, 2), (4, 3)], WHITE); c.pts([(2, 6), (5, 7)], WHITE); c.px(11, 3, RED); c.rect(4, 6, 9, 6, BROWN)
@icon(PINK)
def gum(c):
    c.ell(6, 7, 5, 4, PINK, dither=(255, 120, 245)); c.ell(11, 3, 2, 2, PINK); c.px(11, 3, WHITE); c.pts([(3, 5), (4, 4)], WHITE); c.pts([(4, 10), (8, 11), (9, 9)], (200, 0, 190)); c.pts([(2, 8), (3, 13)], DGREY); c.px(6, 12, DGREY)
@icon(ORANGE, YELLOW)
def helmet(c):
    c.ell(6.5, 8, 6, 5, YELLOW, dither=(230, 230, 0)); c.rect(0, 9, 13, 11, YELLOW); c.rect(0, 12, 13, 12, ORANGE); c.rect(5, 3, 8, 8, ORANGE); c.rect(6, 2, 7, 2, ORANGE); c.pts([(3, 5), (2, 6)], WHITE); c.px(6, 5, WHITE)
@icon(GREEN)
def holey_sock(c):
    c.rect(3, 1, 8, 9, WHITE, dither=LG); c.rect(3, 9, 12, 12, WHITE, dither=LG); c.rect(3, 2, 8, 3, RED); c.rect(3, 5, 8, 5, RED); c.ell(10, 10, 3, 3, WHITE); c.rect(8, 8, 12, 12, WHITE); c.ell(5, 11, 1.5, 1.2, BLACK); c.pts([(4, 8), (6, 8), (5, 9)], BROWN); c.pts([(9, 0), (10, 1)], GREEN)
@icon(PURPLE, YELLOW)
def hot_dog(c):
    c.ell(6.5, 7, 6.5, 3.5, (225, 160, 80), dither=(190, 120, 50)); c.rect(1, 6, 12, 8, (230, 70, 50)); c.pts([(2, 5), (4, 6), (6, 5), (8, 6), (10, 5)], YELLOW); c.pts([(3, 8), (6, 9), (9, 8)], YELLOW); c.pts([(2, 7), (11, 7)], (160, 40, 30)); c.pts([(10, 3), (11, 2)], GREEN)
@icon(PURPLE, WHITE)
def junk_backpack(c):
    c.rect(2, 4, 11, 12, (130, 100, 60), dither=BROWN); c.ell(6.5, 4, 4.5, 3, (130, 100, 60)); c.rect(3, 8, 10, 11, BROWN); c.rect(5, 9, 8, 10, YELLOW); c.line(2, 5, 1, 11, DGREY); c.line(11, 5, 12, 11, DGREY); c.pts([(5, 1), (8, 0)], GREEN); c.pts([(4, 2), (9, 2)], WHITE); c.rect(5, 6, 8, 6, DGREY)
@icon(RED)
def junk_magnet(c):
    c.rect(1, 1, 4, 8, RED); c.rect(9, 1, 12, 8, RED); c.rect(1, 9, 12, 12, RED); c.ell(6.5, 9, 6, 4, RED); c.rect(4, 2, 9, 8, BLACK); c.rect(1, 1, 4, 3, WHITE); c.rect(9, 1, 12, 3, WHITE); c.pts([(2, 5), (10, 6)], PINK); c.pts([(5, 0), (8, 0)], GREEN)
@icon(RED)
def lighter(c):
    c.rect(3, 5, 9, 12, RED); c.rect(3, 3, 9, 5, GREY); c.rect(5, 1, 8, 2, DGREY); c.px(5, 5, WHITE); c.rect(4, 6, 4, 11, PINK); c.pts([(7, 0), (7, 1)], YELLOW); c.pts([(8, 0)], ORANGE); c.pts([(6, 8), (7, 8)], YELLOW)
@icon(PURPLE, WHITE)
def nail_knuckles(c):
    c.rect(1, 5, 12, 9, DGREY, dither=GREY)
    for x in (2, 5, 8, 11): c.line(x, 5, x, 2, LG); c.px(x, 1, WHITE)
    for x in (3, 7, 10): c.rect(x - 1, 6, x, 8, BLACK)
    c.px(2, 6, WHITE); c.pts([(3, 10), (9, 10)], BROWN)
@icon(PURPLE, WHITE)
def old_milk(c):
    c.rect(3, 3, 10, 12, WHITE, dither=LG); c.rect(3, 1, 10, 3, BLUE); c.line(3, 3, 6, 0, BLUE); c.line(6, 0, 10, 3, BLUE); c.rect(4, 6, 9, 9, CREAM); c.px(6, 7, BLACK); c.px(8, 7, BLACK); c.rect(6, 9, 7, 9, GREEN); c.pts([(4, 11), (9, 12), (11, 5)], GREEN)
@icon(PURPLE, WHITE)
def plastic_bag(c):
    c.rect(2, 4, 11, 12, WHITE, dither=(215, 235, 250)); c.line(2, 4, 3, 1, WHITE); c.line(11, 4, 10, 1, WHITE); c.pts([(3, 0), (4, 0), (9, 0), (10, 0)], WHITE); c.rect(3, 7, 10, 10, RED); c.rect(4, 8, 9, 8, WHITE); c.px(5, 5, CYAN); c.pts([(2, 11), (11, 10)], (170, 200, 220))
@icon(PURPLE, YELLOW)
def poop_wallet(c):
    c.rect(1, 3, 12, 11, BROWN, dither=(130, 75, 30)); c.rect(1, 3, 12, 4, (130, 75, 30)); c.rect(9, 6, 12, 8, YELLOW); c.px(11, 7, BLACK); c.pts([(5, 0), (6, 1), (7, 1), (6, 2)], BROWN); c.pts([(2, 12), (7, 12), (10, 13)], GREEN); c.px(3, 5, WHITE)
@icon(PURPLE, WHITE)
def pot(c):
    c.ell(6.5, 8, 5.5, 4, (150, 70, 40), dither=DGREY); c.rect(1, 5, 12, 10, (150, 70, 40), dither=DGREY); c.rect(0, 4, 13, 5, DGREY); c.line(0, 6, 0, 7, DGREY); c.line(13, 6, 13, 7, DGREY); c.pts([(4, 3), (9, 3), (6, 2)], GREY); c.pts([(3, 7), (4, 8), (9, 9)], (200, 110, 40)); c.px(2, 6, WHITE)
@icon(GREEN)
def rubber_boot(c):
    c.rect(3, 0, 8, 9, GREEN, dither=(20, 180, 20)); c.rect(3, 9, 12, 12, GREEN, dither=(20, 180, 20)); c.ell(11, 10, 2, 2, GREEN); c.rect(2, 12, 12, 13, BLACK); c.rect(3, 0, 8, 1, (190, 255, 150)); c.pts([(4, 3), (4, 5)], WHITE); c.pts([(0, 12), (1, 13)], BROWN)
@icon(PURPLE, WHITE)
def sandwich(c):
    c.rect(1, 2, 12, 4, (225, 170, 90)); c.rect(1, 9, 12, 11, (225, 170, 90)); c.rect(1, 5, 12, 5, GREEN); c.rect(2, 6, 11, 6, RED); c.rect(1, 7, 12, 8, YELLOW); c.pts([(3, 3), (7, 2), (10, 3)], WHITE); c.pts([(5, 10), (9, 10)], BROWN); c.pts([(2, 6), (8, 7)], GREEN)
@icon(RED)
def scarf(c):
    c.rect(1, 2, 12, 6, PINK, dither=(200, 0, 190)); c.rect(7, 5, 10, 12, PINK); c.rect(7, 12, 10, 13, WHITE); c.pts([(3, 3), (5, 5), (8, 8)], WHITE); c.pts([(7, 14 if False else 13), (9, 13)], WHITE); c.pts([(2, 4), (4, 3), (9, 9), (9, 11)], YELLOW)
@icon(CYAN)
def shawarma(c):
    c.line(3, 11, 9, 2, (225, 170, 90), 4); c.line(4, 11, 8, 4, WHITE); c.ell(9, 2.5, 3, 2, GREEN); c.pts([(8, 1), (10, 3)], RED); c.pts([(5, 9), (6, 6)], (110, 60, 20)); c.pts([(4, 12), (3, 12), (2, 13)], BROWN); c.px(10, 1, WHITE)
@icon(ORANGE, YELLOW)
def skateboard(c):
    c.rect(0, 5, 13, 8, YELLOW, dither=ORANGE); c.pts([(0, 4), (13, 4)], YELLOW); c.rect(3, 6, 5, 6, RED); c.pts([(8, 6), (10, 6)], BLACK); c.ell(3, 11, 1.8, 1.8, DGREY); c.ell(10, 11, 1.8, 1.8, DGREY); c.rect(2, 9, 3, 9, GREY); c.rect(9, 9, 10, 9, GREY); c.px(3, 11, WHITE)
@icon(PURPLE, YELLOW)
def stink_lamp(c):
    c.rect(4, 11, 9, 13, DGREY); c.rect(5, 9, 8, 10, GREY); c.ell(6.5, 5, 4, 4.5, GREEN, dither=(150, 255, 90)); c.px(5, 4, WHITE); c.pts([(6, 6), (7, 6)], YELLOW); c.pts([(3, 0), (4, 1), (9, 0), (10, 1)], GREEN)
@icon(PURPLE, WHITE)
def stinky_pants(c):
    c.rect(2, 1, 11, 4, (50, 90, 160)); c.rect(2, 5, 6, 12, (50, 90, 160), dither=(40, 70, 130)); c.rect(7, 5, 11, 12, (50, 90, 160), dither=(40, 70, 130)); c.rect(2, 1, 11, 1, DGREY); c.ell(4, 9, 2, 2, BROWN); c.ell(9, 8, 1.5, 2, BROWN); c.pts([(5, 11), (8, 11), (6, 13)], GREEN); c.px(4, 8, (130, 75, 30))
@icon(PURPLE, WHITE)
def ushanka(c):
    c.ell(6.5, 6, 5.5, 4.5, BROWN, dither=(130, 75, 30)); c.rect(0, 7, 3, 12, BROWN, dither=(130, 75, 30)); c.rect(10, 7, 13, 12, BROWN, dither=(130, 75, 30)); c.rect(3, 7, 10, 9, (130, 75, 30)); c.rect(5, 2, 8, 3, YELLOW); c.px(6, 2, RED); c.pts([(1, 12), (12, 12)], WHITE); c.pts([(3, 4), (9, 4)], (190, 120, 60))
@icon(GREEN, WHITE)
def vodka(c):
    c.rect(4, 5, 9, 13, (225, 245, 255), dither=WHITE); c.rect(5, 2, 8, 5, (225, 245, 255)); c.rect(5, 0, 8, 1, RED); c.rect(5, 7, 8, 11, WHITE); c.rect(6, 8, 7, 9, RED); c.pts([(4, 6), (4, 9)], CYAN); c.rect(5, 12, 8, 12, CYAN); c.px(7, 3, GREEN)
@icon(GREEN)
def stray_dog(c):
    c.ell(7, 7, 5, 5, (160, 110, 60), dither=BROWN); c.pts([(2, 2), (3, 2), (2, 3), (3, 3), (4, 3), (11, 2), (10, 3), (11, 3), (12, 3), (12, 4)], BROWN); c.ell(7, 9, 2.5, 2, WHITE); c.rect(6, 8, 8, 9, BLACK); c.px(4, 6, BLACK); c.px(10, 6, BLACK); c.px(3, 6, WHITE); c.rect(6, 11, 7, 12, PINK); c.px(5, 4, GREEN)

# --- статы (внутри 14×14)
@icon(RED)
def stat_max_hp(c):
    c.ell(4, 4, 3.5, 3, RED); c.ell(9, 4, 3.5, 3, RED)
    for y in range(5, 13): c.rect(round(6.5 - (6.5 - (y - 5) * 0.8)), y, round(6.5 + (6.5 - (y - 5) * 0.8)), y, RED)
    c.rect(6, 4, 7, 9, WHITE); c.rect(4, 6, 9, 7, WHITE); c.px(3, 2, WHITE)
@icon(GREEN)
def stat_regen(c):
    c.ell(6.5, 7, 5, 5, GREEN, dither=(20, 180, 20)); c.ell(6.5, 7, 3, 3, BLACK); c.rect(6, 5, 7, 9, GREEN); c.rect(4, 7, 9, 8, GREEN); c.pts([(11, 1), (12, 2), (1, 12)], YELLOW)
@icon(RED)
def stat_damage(c):
    c.line(1, 12, 10, 3, LG, 2); c.pts([(10, 2), (11, 1), (12, 0), (11, 3), (12, 4)], WHITE); c.rect(0, 10, 3, 13, BROWN); c.line(2, 9, 5, 12, RED, 2); c.pts([(10, 6), (12, 7), (11, 10)], YELLOW)
@icon(ORANGE, YELLOW)
def stat_attack_speed(c):
    c.pts([(8, 0), (7, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 6)], YELLOW); c.rect(2, 6, 9, 7, YELLOW); c.pts([(8, 7), (7, 8), (6, 9), (5, 10), (5, 11), (4, 12), (4, 13)], YELLOW); c.rect(5, 5, 7, 6, ORANGE)
    c.pts([(0, 4), (1, 4), (0, 9), (1, 9), (0, 11)], CYAN)
@icon(YELLOW if False else RED, WHITE)
def stat_crit(c):
    pts = []
    for i in range(10):
        r = 6 if i % 2 == 0 else 2.5; a = -math.pi / 2 + i * math.pi / 5
        pts.append((6.5 + math.cos(a) * r, 6.5 + math.sin(a) * r))
    for y in range(14):
        for x in range(14):
            # point in polygon
            inside = False; j = len(pts) - 1
            for i in range(len(pts)):
                xi, yi = pts[i]; xj, yj = pts[j]
                if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi): inside = not inside
                j = i
            if inside: c.px(x, y, YELLOW)
    c.ell(6.5, 6.5, 1.5, 1.5, RED); c.px(5, 3, WHITE)
@icon(CYAN, WHITE)
def stat_speed(c):
    c.rect(4, 3, 10, 11, WHITE); c.rect(1, 9, 11, 12, WHITE); c.rect(8, 8, 12, 12, WHITE); c.rect(1, 12, 12, 13, BLACK); c.rect(5, 4, 8, 4, RED); c.pts([(0, 3), (1, 3), (0, 6), (2, 6), (1, 8)], CYAN); c.pts([(0, 10)], CYAN)
@icon(CYAN, WHITE)
def stat_armor(c):
    c.rect(1, 1, 12, 7, BLUE); c.ell(6.5, 7, 5.5, 5.5, BLUE); c.rect(2, 2, 11, 2, WHITE); c.rect(6, 2, 7, 11, CYAN); c.rect(2, 5, 11, 6, CYAN); c.px(3, 3, WHITE)
@icon(CYAN, WHITE)
def stat_dodge(c):
    c.ell(7, 6, 4, 5, (150, 235, 255), dither=WHITE); c.rect(3, 6, 10, 12, (150, 235, 255), dither=WHITE); c.pts([(0, 3), (1, 5), (0, 8), (1, 10), (11, 4)], CYAN); c.pts([(5, 4), (8, 4)], BLACK); c.px(7, 8, BLACK)
@icon(RED)
def stat_pickup(c):
    c.rect(1, 1, 4, 8, RED); c.rect(9, 1, 12, 8, RED); c.ell(6.5, 9, 6, 4, RED); c.rect(4, 2, 9, 8, BLACK); c.rect(1, 1, 4, 3, WHITE); c.rect(9, 1, 12, 3, WHITE); c.pts([(6, 11), (7, 12)], GREEN)

# --- перки
@icon(ORANGE, YELLOW)
def perk_double_shot(c):
    for y in (3, 8):
        c.rect(0, y, 3, y + 2, DGREY); c.rect(3, y, 9, y + 2, ORANGE); c.pts([(10, y + 1), (11, y + 1), (12, y + 1)], YELLOW); c.px(13, y + 1, WHITE)
@icon(GREEN)
def perk_loot_goblin(c):
    c.ell(6.5, 7, 5.5, 5, GREEN, dither=(20, 180, 20)); c.pts([(0, 3), (1, 4), (13, 3), (12, 4), (0, 2), (13, 2)], GREEN); c.px(4, 5, YELLOW); c.px(9, 5, YELLOW); c.px(4, 6, BLACK); c.px(9, 6, BLACK); c.rect(4, 9, 9, 10, BLACK); c.pts([(5, 9), (8, 9)], WHITE)
@icon(GREEN)
def perk_regen(c):
    stat_regen(c)
@icon(CYAN, WHITE)
def perk_speed(c):
    stat_speed(c)

def render(name):
    f, sh, hi, w, h, lim = I[name]
    c = Canvas(w, h); f(c)
    return c.finish(sh, hi, lim=lim)

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith("--")] or list(I)
    k = 6; cols = 12; cell = 22 * k
    prev = Image.new("RGBA", (cols * cell, ((len(names) + cols - 1) // cols) * cell), (45, 30, 20, 255))
    for i, n in enumerate(names):
        a = render(n); im = Image.fromarray(a, "RGBA")
        if apply:
            im.save(f"assets/ui/{n if n.startswith(('stat_', 'perk_')) else 'item_' + n}.png")
        b = im.resize((im.width * k, im.height * k), Image.NEAREST); prev.paste(b, ((i % cols) * cell + 6, (i // cols) * cell + 6), b)
    prev.save("tools/_preview/icons_new.png"); print(len(names), prev.size, {n: render(n).shape[:2] for n in names if render(n).shape[:2] != (16, 16)})
