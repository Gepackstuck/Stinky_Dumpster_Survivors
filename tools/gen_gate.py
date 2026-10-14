"""Ворота 48x32 в стиле арены: столбы, доски, колючая проволока, череп на перемычке. Запуск: python3 tools/gen_gate.py"""
import random
import sys

sys.path.insert(0, "tools")
from gen_art import BLACK, BROWN, GREY, PINK, RED, WHITE, YELLOW, finish, line, new_img, new_mask, paint, px, rect, union
from PIL import Image

W, H = 48, 32
POST = (120, 120, 126)


def gate():
    rng = random.Random(7)
    posts = new_mask(W, H); rect(posts, 1, 4, 4, 31); rect(posts, 43, 4, 46, 31)
    beam = new_mask(W, H); rect(beam, 1, 4, 46, 9)
    planks = new_mask(W, H); rect(planks, 5, 16, 14, 31); rect(planks, 33, 16, 42, 31)
    wire = new_mask(W, H)
    for y0 in (1, 12):   # два ряда колючки: поверх перемычки и под ней
        pts = [(1, y0 + 1)]
        for x in range(5, 47, 4):
            pts.append((x, y0 + (2 if (x // 4) % 2 else 0)))
        line(wire, pts, 0)
    sil = union(posts, beam, planks, wire)
    img = new_img(W, H)
    paint(img, planks, BROWN)
    paint(img, posts, POST)
    paint(img, beam, BROWN)
    paint(img, wire, GREY)
    out = finish(img, sil)
    # доски: щели и гвозди
    for x in (8, 11, 36, 39):
        for y in range(17, 31):
            px(out, x, y, (60, 34, 16))
    for x, y in ((6, 18), (13, 19), (34, 18), (41, 19), (6, 28), (41, 28)):
        px(out, x, y, YELLOW)
    # проволока: рваный зигзаг между столбами
    for y0 in (1, 12):
        for x in range(1, 47):
            px(out, x, y0 + 1 + (1 if (x // 2) % 2 else 0), (200, 200, 215))
    # колючки на проволоке
    for y0 in (1, 12):
        for x in range(5, 45, 8):
            for dx, dy in ((0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)):
                px(out, x + dx, y0 + 1 + dy, BLACK if (dx or dy) else RED)
    # череп на перемычке и мухи
    for x in range(21, 27):
        for y in range(4, 8):
            px(out, x, y, WHITE)
    for x, y in ((22, 5), (25, 5)):
        px(out, x, y, BLACK)
    px(out, 23, 7, BLACK); px(out, 24, 7, BLACK)
    for x, y in ((8, 6), (38, 7), (14, 8)):
        px(out, x, y, BLACK)
    # столбы: розовые «шляпки» и грязь
    for x in (2, 44):
        px(out, x, 4, PINK); px(out, x + 1, 4, PINK)
    for _ in range(10):
        px(out, rng.choice((2, 3, 44, 45)), rng.randint(10, 30), (60, 40, 30))
    return out


if __name__ == "__main__":
    img = gate()
    img.save("assets/sprites/gate.png")
    bg = Image.new("RGBA", (W + 8, H + 8), (60, 40, 20, 255))
    bg.alpha_composite(img, (4, 4))
    bg.resize((bg.width * 8, bg.height * 8), Image.NEAREST).save("tools/_preview/gate.png")
    print("ok")
