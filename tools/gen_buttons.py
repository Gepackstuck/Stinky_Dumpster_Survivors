"""Разные рамки кнопок (200x28, обычная и под курсором) -> assets/ui/button_v<i>.png / button_v<i>_hover.png. Запуск: python3 tools/gen_buttons.py"""
import sys

sys.path.insert(0, "tools")
import gen_art as ga
from PIL import Image

VARIANTS = [
    (ga.GREEN, ga.PINK, 311, 6, 5), (ga.PINK, ga.GREEN, 322, 9, 4), (ga.YELLOW, ga.PINK, 333, 4, 6),
    (ga.CYAN, ga.YELLOW, 344, 8, 5), (ga.RED, ga.YELLOW, 355, 5, 7), (ga.PINK, ga.CYAN, 366, 7, 4),
]

if __name__ == "__main__":
    sheet = Image.new("RGBA", (2 * 204, len(VARIANTS) * 32), (60, 40, 20, 255))
    for i, (a, b, seed, drips, chamfer) in enumerate(VARIANTS):
        normal = ga.draw_frame(200, 28, a, b, seed, chamfer=chamfer, drips=drips, eyes=False, clean=True)
        hover = ga.draw_frame(200, 28, b, ga.YELLOW if a != ga.YELLOW else ga.GREEN, seed, chamfer=chamfer, drips=drips + 2, eyes=False, clean=True)
        normal.save(ga.UI + "button_v%d.png" % i)
        hover.save(ga.UI + "button_v%d_hover.png" % i)
        sheet.alpha_composite(normal, (2, i * 32 + 2))
        sheet.alpha_composite(hover, (206, i * 32 + 2))
    sheet.resize((sheet.width * 3, sheet.height * 3), Image.NEAREST).save("tools/_preview/buttons.png")
    print("ok")
