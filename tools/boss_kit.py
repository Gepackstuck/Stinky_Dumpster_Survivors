"""Набор для боссов: холст со смещением, поворот точек, лист «состояния × кадры»."""
import math, sys
import numpy as np
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
GOLD = (255, 200, 0); LGREY = (190, 190, 200); RUST = (170, 80, 30); DBROWN = (80, 45, 20)
LGREEN = (150, 255, 100); STINK = (110, 210, 30); STINK2 = (190, 255, 80)


class O:
    """Тот же интерфейс, что у Canvas, но со сдвигом (ox, oy): рисуем героя в его «базовых» координатах."""
    def __init__(self, c, ox=0, oy=0): self.c, self.ox, self.oy = c, ox, oy
    def px(self, x, y, col): self.c.px(round(x + self.ox), round(y + self.oy), col)
    def pts(self, p, col):
        for x, y in p: self.px(x, y, col)
    def ell(self, cx, cy, rx, ry, col, dither=None): self.c.ell(cx + self.ox, cy + self.oy, rx, ry, col, dither)
    def rect(self, x0, y0, x1, y1, col, dither=None): self.c.rect(x0 + self.ox, y0 + self.oy, x1 + self.ox, y1 + self.oy, col, dither)
    def line(self, x0, y0, x1, y1, col, th=1): self.c.line(x0 + self.ox, y0 + self.oy, x1 + self.ox, y1 + self.oy, col, th)
    def eye(self, cx, cy, r, pupil=(0, 0), iris=BLACK, blood=True): self.c.eye(cx + self.ox, cy + self.oy, r, pupil, iris, blood)
    def teeth(self, x0, x1, y, col=WHITE, mouth=BLACK, h=2): self.c.teeth(x0 + self.ox, x1 + self.ox, y + self.oy, col, mouth, h)
    def poly(self, pts, col, dither=None):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            for x in range(int(min(xs)), int(max(xs)) + 1):
                if _inside(x + .5, y + .5, pts):
                    self.px(x, y, dither if dither and (x + y) % 2 == 0 else col)
    def ring(self, cx, cy, r, col, th=1):
        for a in range(0, 360, 3):
            for k in range(th):
                self.px(cx + (r - k) * math.cos(math.radians(a)), cy + (r - k) * math.sin(math.radians(a)), col)


def _inside(x, y, pts):
    n = len(pts); ins = False; j = n - 1
    for i in range(n):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi: ins = not ins
        j = i
    return ins


def rot(p, c, deg):
    a = math.radians(deg); dx, dy = p[0] - c[0], p[1] - c[1]
    return (c[0] + dx * math.cos(a) - dy * math.sin(a), c[1] + dx * math.sin(a) + dy * math.cos(a))


def sheet_grid(rows, cols=4):
    """rows: список списков кадров (np.array RGBA) -> одна картинка rows×cols, кадры одного размера."""
    h = max(f.shape[0] for r in rows for f in r); w = max(f.shape[1] for r in rows for f in r)
    out = Image.new("RGBA", (w * cols, h * len(rows)), (0, 0, 0, 0))
    for ri, r in enumerate(rows):
        for ci, f in enumerate(r):
            im = Image.fromarray(f, "RGBA")
            out.paste(im, (ci * w + (w - f.shape[1]) // 2, ri * h + (h - f.shape[0])))
    return out
