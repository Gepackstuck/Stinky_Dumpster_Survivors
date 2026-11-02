"""Н24 Тёща (финал): халат в цветочек, бигуди, скалка, рот нараспашку. Ряды: ходьба, ор (буквы), рывок со скалкой,
пилёж кольцом, ярость. Ещё буквы-снаряды из нашего пиксельного шрифта. --apply -> enemy_boss_mother_in_law.png, proj_letter_*.png"""
import re
from boss_kit import *
W, H, OX, OY = 104, 96, 6, 6
ROWS = ["walk", "shout", "charge", "nag", "enrage"]
ROBE = (230, 90, 150); ROBE2 = (180, 50, 110); FLOWER = (250, 230, 90); HAIR = (150, 80, 40); CURL = (90, 200, 255)
WORDS = ["ЛЕНТЯЙ", "НЕУДАЧНИК", "ЛОХ", "БЕЗДАРЬ", "ПОЗОР", "ТУНЕЯДЕЦ"]


def mil(c, b=0, lean=0, m=2, pin=0, rage=False, arms=0):
    cy = 50 - b
    c.ell(46 + lean, cy + 16, 24, 26, ROBE, dither=ROBE2)                     # халат-туша
    for (fx, fy) in ((36, cy + 6), (54, cy + 12), (42, cy + 26), (58, cy + 30), (32, cy + 22)):
        c.ell(fx + lean, fy, 2, 2, FLOWER); c.px(fx + lean, fy, RED)            # цветочки
    c.rect(32 + lean, cy + 40, 40 + lean, cy + 46, (240, 200, 170)); c.rect(52 + lean, cy + 40, 60 + lean, cy + 46, (240, 200, 170))   # ноги
    c.rect(30 + lean, cy + 46, 41 + lean, cy + 48, PINK); c.rect(51 + lean, cy + 46, 62 + lean, cy + 48, PINK)   # тапки с помпоном
    c.ell(46 + lean, cy - 14, 14, 13, SKIN)                                    # голова
    c.ell(46 + lean, cy - 26, 15, 6, HAIR)                                     # причёска
    for k in range(5): c.ell(34 + k * 6 + lean, cy - 28 + (k % 2) * 2, 2, 3, CURL)   # бигуди
    if rage:
        c.ell(41 + lean, cy - 16, 3, 3, RED); c.ell(52 + lean, cy - 17, 4, 4, RED); c.px(52 + lean, cy - 17, YELLOW)
        c.line(37 + lean, cy - 22, 44 + lean, cy - 19, BLACK, 2); c.line(56 + lean, cy - 22, 49 + lean, cy - 19, BLACK, 2)
    else:
        c.eye(41 + lean, cy - 16, 2, (1, 0)); c.eye(52 + lean, cy - 17, 3, (-1, 0))
        c.line(37 + lean, cy - 21, 44 + lean, cy - 20, BLACK); c.line(56 + lean, cy - 21, 49 + lean, cy - 20, BLACK)
    c.ell(46 + lean, cy - 6, 6, m, BLACK); c.rect(43 + lean, cy - 6 - m, 49 + lean, cy - 6 - m, WHITE) if m > 1 else None   # рот
    c.pts([(36 + lean, cy - 10), (56 + lean, cy - 9)], (240, 140, 140))      # румяна
    # руки и скалка
    ax = 20 + lean; ay = cy + 6 - arms
    c.line(26 + lean, cy + 4, ax, ay, ROBE2, 4)
    c.line(66 + lean, cy + 4, 72 + lean + pin, cy - 6 - pin, ROBE2, 4)
    c.line(66 + lean + pin, cy - 14 - pin, 84 + lean + pin, cy - 2 - pin, (210, 170, 110), 4)   # скалка
    c.ell(64 + lean + pin, cy - 16 - pin, 2, 2, (170, 120, 70)); c.ell(86 + lean + pin, cy, 2, 2, (170, 120, 70))


def draw(st, t):
    cv = Canvas(W, H); c = O(cv, OX, OY)
    if st == "walk":
        mil(c, b=[0, 2, 0, 2][t], lean=[0, 1, 0, -1][t], m=[2, 1, 2, 1][t])
    elif st == "shout":
        mil(c, b=[0, 2, 4, 2][t], m=[3, 6, 8, 6][t], arms=[0, 6, 10, 6][t])
        if t >= 1:
            for k in range(3): c.ring(46, 44 - 6, 14 + k * 6 + t * 2, WHITE if k % 2 else YELLOW)
    elif st == "charge":
        mil(c, b=[2, 4, 4, 2][t], lean=[0, 6, 10, 12][t], pin=[0, 6, 10, 4][t], m=6, rage=t >= 2)
        for k in range(3): c.line(0, 40 + k * 10, 10, 40 + k * 10, WHITE) if t >= 2 else None
    elif st == "nag":
        mil(c, b=[0, 1, 0, 1][t], m=[4, 6, 4, 6][t], arms=[4, 12, 4, 12][t])
        for k in range(6):
            a = math.radians(k * 60 + t * 15); c.pts([(46 + 36 * math.cos(a), 46 + 30 * math.sin(a))], RED)
    else:
        mil(c, b=[0, 3, 0, 3][t], lean=[0, 2, 0, -2][t], m=[6, 8, 6, 8][t], rage=True, pin=[0, 4, 0, 4][t])
        c.pts([(30, 10 + t), (62, 8 - t), (24, 20)], RED)
    return cv.finish(RED if st == "enrage" else ROBE2, YELLOW if st == "enrage" else WHITE)


def letters():
    """Буквы для слов-снарядов: вырезаем из assets/fonts/pixel_font.png, красим в красный, x2, чёрная обводка."""
    fnt = open("assets/fonts/pixel_font.fnt", encoding="utf-8").read()
    page = np.array(Image.open("assets/fonts/pixel_font.png").convert("RGBA"))
    need = sorted({ch for w in WORDS for ch in w})
    for ch in need:
        m = re.search(r"char id=%d x=(\d+) y=(\d+) width=(\d+) height=(\d+)" % ord(ch), fnt)
        if not m: print("нет буквы", ch); continue
        x, y, w, h = map(int, m.groups())
        glyph = page[y:y + h, x:x + w, 3] > 0
        big = np.kron(glyph, np.ones((2, 2), dtype=bool))
        out = np.zeros((big.shape[0] + 2, big.shape[1] + 2, 4), np.uint8)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                out[1 + dy:1 + dy + big.shape[0], 1 + dx:1 + dx + big.shape[1]][big] = (10, 10, 10, 255)
        out[1:1 + big.shape[0], 1:1 + big.shape[1]][big] = (255, 40, 60, 255)
        Image.fromarray(out).save("assets/sprites/proj_letter_%d.png" % ord(ch))
    return need


def build():
    return sheet_grid([[draw(r, t) for t in range(4)] for r in ROWS])


if __name__ == "__main__":
    im = build(); im.save("tools/_preview/boss_mil.png")
    if "--apply" in sys.argv:
        im.save("assets/sprites/enemy_boss_mother_in_law.png")
        print("буквы:", "".join(letters()))
    print(im.size)
