"""Хелперы для иконок 32×32 (холст 28×28 + контур → 30, центр в 32)."""
import sys, math
import numpy as np
from PIL import Image
sys.path.insert(0, "tools")
from pix import *
LG = (205, 205, 215); MG = (150, 150, 160); TIN = (190, 200, 210); WOOD = (170, 100, 50); CREAM = (255, 240, 170); STEEL = (170, 175, 190)
DRED = (140, 0, 30); DBROWN = (110, 60, 25); SKINC = (240, 190, 150); LGREEN = (150, 255, 100); DGRN = (10, 150, 10)
N = 28

def new(): return Canvas(N, N)

def poly(c, pts, col, dither=None):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    for y in range(max(0, int(min(ys))), min(c.h, int(max(ys)) + 1)):
        for x in range(max(0, int(min(xs))), min(c.w, int(max(xs)) + 1)):
            inside = False; j = len(pts) - 1
            for i in range(len(pts)):
                xi, yi = pts[i]; xj, yj = pts[j]
                if ((yi > y + .5) != (yj > y + .5)) and (x + .5 < (xj - xi) * (y + .5 - yi) / (yj - yi) + xi): inside = not inside
                j = i
            if inside: c.px(x, y, dither if (dither and (x + y) % 2 == 0) else col)

def ringc(c, cx, cy, r, col, th=1.0):
    for y in range(c.h):
        for x in range(c.w):
            d = math.hypot(x + .5 - cx, y + .5 - cy)
            if abs(d - r) <= th / 2 + .25: c.px(x, y, col)

def tri_font(c, x, y, txt, col):
    G = {"x": ["101", "101", "010", "101", "101"], "2": ["111", "001", "111", "100", "111"], "+": ["000", "010", "111", "010", "000"], "1": ["010", "110", "010", "010", "111"]}
    for k, ch in enumerate(txt):
        for ry, row in enumerate(G[ch]):
            for rx, v in enumerate(row):
                if v == "1": c.px(x + k * 4 + rx, y + ry, col)

def fin(c, shade, hi=WHITE, lim=0.3, tall=False):
    a = c.finish(shade, hi, lim=lim)                    # 30×30
    out = np.zeros((32, 32, 4), np.uint8) if not tall else np.zeros((40, 32, 4), np.uint8)
    h, w = a.shape[:2]; out[(out.shape[0] - h) // 2:(out.shape[0] - h) // 2 + h, (32 - w) // 2:(32 - w) // 2 + w] = a
    return out

def small(a):
    """32→16 для мелких мест: усреднение и порог по альфе, чёрный контур сохраняем."""
    im = Image.fromarray(a, "RGBA"); sm = im.resize((im.width // 2, im.height // 2), Image.BOX)
    arr = np.array(sm); arr[:, :, 3] = np.where(arr[:, :, 3] > 120, 255, 0)
    return arr
