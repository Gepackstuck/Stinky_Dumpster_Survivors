"""Вырезать картинку и сохранить её с координатной сеткой (доли 0..1) - по ней расставляются кости скелета.
Запуск: tools/_venv/ml/bin/python tools/hd/grid.py <картинка.png> [ещё...] -> рядом <имя>_grid.png"""
import sys

import numpy as np
from PIL import Image, ImageDraw

import rig

for path in sys.argv[1:]:
    a = rig.cutout(path)
    im = Image.fromarray((a * 255).astype(np.uint8))
    bg = Image.new("RGBA", im.size, (60, 90, 60, 255))
    bg.alpha_composite(im)
    d = ImageDraw.Draw(bg)
    for i in range(1, 10):
        v = i * im.width // 10
        d.line([(v, 0), (v, im.height)], fill=(255, 255, 255, 90))
        d.line([(0, v), (im.width, v)], fill=(255, 255, 255, 90))
        d.text((v + 2, 2), "%.1f" % (i / 10), fill=(255, 255, 0))
        d.text((2, v + 2), "%.1f" % (i / 10), fill=(255, 255, 0))
    bg.convert("RGB").save(path.replace(".png", "_grid.png"))
