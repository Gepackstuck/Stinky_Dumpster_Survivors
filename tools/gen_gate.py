"""Ворота 48x32: просто железо и колючая проволока (столбы, решётчатые створки). Запуск: python3 tools/gen_gate.py"""
import sys

sys.path.insert(0, "tools")
from gen_art import BLACK, GREY, RED, finish, new_img, new_mask, paint, px, rect, union
from PIL import Image

W, H = 48, 32
IRON = (120, 120, 126)
DARK_IRON = (70, 70, 78)
WIRE = (200, 200, 215)


def gate():
    posts = new_mask(W, H); rect(posts, 1, 5, 4, 31); rect(posts, 43, 5, 46, 31)
    leaf_l = new_mask(W, H); rect(leaf_l, 5, 14, 13, 31)
    leaf_r = new_mask(W, H); rect(leaf_r, 34, 14, 42, 31)
    bars = new_mask(W, H)
    for x in (6, 9, 12, 35, 38, 41):
        rect(bars, x, 15, x, 30)
    rails = new_mask(W, H)
    for y in (16, 22, 29):
        rect(rails, 5, y, 13, y); rect(rails, 34, y, 42, y)
    sil = union(posts, leaf_l, leaf_r)
    img = new_img(W, H)
    paint(img, union(leaf_l, leaf_r), (20, 20, 26))   # просвет между прутьями
    paint(img, posts, IRON)
    paint(img, bars, DARK_IRON)
    paint(img, rails, IRON)
    out = finish(img, sil)
    # блики и ржавчина на столбах
    for y in range(7, 31, 4):
        px(out, 2, y, (170, 170, 178)); px(out, 44, y, (170, 170, 178))
    for x, y in ((3, 12), (3, 25), (45, 18), (45, 28)):
        px(out, x, y, (120, 60, 30))
    # колючая проволока поверх: две волны через весь проём и катушка сверху
    for y0 in (3, 10):
        for x in range(1, 47):
            px(out, x, y0 + (1 if (x // 3) % 2 else 0), WIRE)
        for x in range(4, 45, 7):
            for dx, dy in ((0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)):
                px(out, x + dx, y0 + dy, BLACK if (dx or dy) else RED)
    for x in (2, 44):   # остриё на столбах
        for dy in range(3):
            px(out, x + 1 - (1 if dy == 2 else 0), 4 - dy, IRON if dy < 2 else BLACK)
    return out


if __name__ == "__main__":
    img = gate()
    img.save("assets/sprites/gate.png")
    bg = Image.new("RGBA", (W + 8, H + 8), (60, 40, 20, 255))
    bg.alpha_composite(img, (4, 4))
    bg.resize((bg.width * 8, bg.height * 8), Image.NEAREST).save("tools/_preview/gate.png")
    print("ok")
