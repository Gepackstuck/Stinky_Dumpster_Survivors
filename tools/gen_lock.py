"""Значок замка для замороженных карточек Ларька (12x14). Запуск из корня: python3 tools/gen_lock.py"""
import sys
sys.path.insert(0, "tools")
from gen_art import BLACK, GREY, UI, YELLOW, finish, line, new_img, new_mask, paint, px, rect, union

W, H = 12, 14
shackle = new_mask(W, H); line(shackle, [(3, 6), (3, 3), (4, 1), (7, 1), (8, 3), (8, 6)], 2)
body = new_mask(W, H); rect(body, 1, 6, 10, 12)
img = new_img(W, H); paint(img, shackle, GREY); paint(img, body, YELLOW)
out = finish(img, union(shackle, body))
for x, y in ((5, 8), (6, 8), (5, 9), (6, 9), (5, 10)):
    px(out, x, y, BLACK)
out.save(UI + "lock_icon.png")
