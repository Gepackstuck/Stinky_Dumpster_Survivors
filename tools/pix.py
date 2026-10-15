"""Мини-набор для рисования пиксель-арта кодом: слои-фигуры, контур, кислотная контр-тень, блики, дизеринг."""
import numpy as np, random
from PIL import Image
BLACK = (10, 10, 10); WHITE = (240, 240, 240); GREEN = (57, 255, 20); PINK = (255, 16, 240); YELLOW = (247, 255, 0)
RED = (255, 0, 51); BLUE = (30, 30, 255); CYAN = (0, 240, 255); BROWN = (107, 62, 31); PURPLE = (120, 0, 160)
GREY = (140, 140, 150); DGREY = (70, 70, 80); ORANGE = (255, 130, 0); SKIN = (240, 190, 150); DGREEN = (20, 130, 20)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.a = np.zeros((h, w, 4), np.uint8)
        self.yy, self.xx = np.mgrid[0:h, 0:w]

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h: self.a[int(y), int(x)] = (*c, 255)

    def pts(self, pts, c):
        for x, y in pts: self.px(x, y, c)

    def ell(self, cx, cy, rx, ry, c, dither=None):
        m = ((self.xx - cx) / max(rx, .5)) ** 2 + ((self.yy - cy) / max(ry, .5)) ** 2 <= 1.0
        self.a[m] = (*c, 255)
        if dither is not None:
            d = m & ((self.xx + self.yy) % 2 == 0)
            self.a[d] = (*dither, 255)

    def rect(self, x0, y0, x1, y1, c, dither=None):
        m = (self.xx >= x0) & (self.xx <= x1) & (self.yy >= y0) & (self.yy <= y1)
        self.a[m] = (*c, 255)
        if dither is not None:
            self.a[m & ((self.xx + self.yy) % 2 == 0)] = (*dither, 255)

    def line(self, x0, y0, x1, y1, c, th=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) * 2 + 1
        for i in range(n + 1):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for dx in range(th):
                for dy in range(th): self.px(round(x) + dx, round(y) + dy, c)

    def eye(self, cx, cy, r, pupil=(0, 0), iris=BLACK, blood=True):
        self.ell(cx, cy, r, r, WHITE)
        if blood:
            for k, (dx, dy) in enumerate([(-1, 0), (1, 0), (0, -1), (-1, 1)]):
                if k % 2 == 0 or r >= 3: self.px(cx + dx * (r - 1), cy + dy * (r - 1), RED)
        self.px(cx + pupil[0], cy + pupil[1], iris)
        if r >= 3: self.px(cx + pupil[0] + 1, cy + pupil[1], iris)

    def teeth(self, x0, x1, y, c=WHITE, mouth=BLACK, h=2):
        self.rect(x0, y, x1, y + h, mouth)
        for x in range(x0, x1 + 1, 2): self.px(x, y, c); self.px(x, y + h, c)

    def finish(self, shade, hi=WHITE, outline=True, glitch=0, rng=None, lim=0.0):
        a = self.a
        op = a[:, :, 3] > 0
        ys, xs = np.nonzero(op)
        x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
        span = max((x1 - x0) + (y1 - y0), 1)
        base = a.copy(); out = a.copy()
        for y, x in zip(ys, xs):
            col = tuple(base[y, x, :3])
            if col in (BLACK, WHITE): continue
            u = ((x - x0) + (y - y0)) / span
            if u > 0.8 + lim or (u > 0.68 + lim and (x + y) % 2 == 0): out[y, x] = (*shade, 255)
            upv = base[y - 1, x] if y > 0 else np.zeros(4)
            lfv = base[y, x - 1] if x > 0 else np.zeros(4)
            if (upv[3] == 0 or tuple(upv[:3]) == BLACK) and (lfv[3] == 0 or tuple(lfv[:3]) == BLACK) and u < 0.42: out[y, x] = (*hi, 255)
        a = out
        if outline:
            pad = np.zeros((self.h + 2, self.w + 2, 4), np.uint8); pad[1:-1, 1:-1] = a
            o = pad[:, :, 3] > 0
            n = np.zeros_like(o)
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]: n |= np.roll(np.roll(o, dx, 1), dy, 0)
            ring = n & ~o
            pad[ring] = (*BLACK, 255)
            a = pad
        if glitch and rng:
            op = a[:, :, 3] > 0
            hh, ww = op.shape
            for c, dx in ((PINK, -1), (CYAN, 1)):
                m = np.roll(op, dx * 2, 1) & ~op
                for y in range(hh):
                    if rng.random() < 0.6: m[y] = False
                a[m] = (*c, 255)
            ys, xs = np.nonzero(a[:, :, 3] > 0)
            for _ in range(glitch):
                i = rng.randrange(len(ys))
                if tuple(a[ys[i], xs[i], :3]) != BLACK: a[ys[i], xs[i]] = (*rng.choice([PINK, CYAN, YELLOW, GREEN]), 255)
        return a


def sheet(frames):
    h = max(f.shape[0] for f in frames); w = max(f.shape[1] for f in frames)
    out = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        im = Image.fromarray(f, "RGBA")
        out.paste(im, (i * w + (w - f.shape[1]) // 2, h - f.shape[0]))
    return out
