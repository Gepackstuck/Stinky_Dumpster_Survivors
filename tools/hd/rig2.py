"""Скелет с мягкой кожей для ПИКСЕЛЬНЫХ спрайтов (новый стиль).

Исходник - крупный рисунок (вырезанный, RGBA, float 0..1). Цепочки костей (щупальце, лапа, рука) двигают свои пиксели по-настоящему:
каждый пиксель знает ближайшую цепочку и место на ней, его матрица плавно смешивается между костями (изгиб без швов), у корня -
с телом. Мягкие «пластилиновые» зоны (челюсть, язык, веки, брови) дополняют лицо. Кадр считается на большом холсте точечным
разбрасыванием пикселей вперёд, потом сводится к сетке игровых пикселей: общая палитра, чёткий контур.

    rig = Rig2(cutout_rgba)
    rig.chain("tl", [(x, y), ...], radius)          # точки в долях картинки, от корня к кончику
    rig.warp("jaw", (x, y), radius); rig.lid("eye_l", (x, y), rx, ry)
    frame = rig.render(pose, root, F)               # pose: {"tl0": угол_градусов, "~jaw": (dx, dy, масштаб, угол, масштаб_y), "^eye_l": 0..1}
Запуск только из ml-окружения (numpy, scipy, PIL).
"""
import math
import os

import numpy as np
from PIL import Image
from scipy import ndimage

import rig as rig1

OUTLINE = (20, 10, 16)


def _T(x, y):
    return np.array([[1, 0, x], [0, 1, y], [0, 0, 1]], np.float64)


def rot_about(angle_deg, cx, cy, sx=1.0, sy=1.0):
    c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
    return _T(cx, cy) @ np.array([[c * sx, -s * sy, 0], [s * sx, c * sy, 0], [0, 0, 1]], np.float64) @ _T(-cx, -cy)


class Rig2:
    def __init__(self, img: np.ndarray):
        self.img = img.astype(np.float32)
        self.h, self.w = img.shape[:2]
        self.chains = []
        self.warps = {}
        self.lids = {}
        self._ready = False

    # ---- описание ----
    def chain(self, name, pts, radius, radius_tip=None):
        s = float(self.w)
        self.chains.append({"name": name, "pts": np.array(pts, np.float64) * s, "r0": radius * s, "r1": (radius_tip if radius_tip else radius) * s})
        self._ready = False
        return self

    def warp(self, name, center, radius):
        s = float(self.w)
        self.warps[name] = (center[0] * s, center[1] * s, radius * s)
        return self

    def lid(self, name, center, rx, ry):
        s = float(self.w)
        self.lids[name] = (center[0] * s, center[1] * s, rx * s, ry * s)
        return self

    # ---- подготовка ----
    def _build(self):
        iy, ix = np.nonzero(self.img[..., 3] > 0.3)
        self.iy, self.ix = iy, ix
        X, Y = ix.astype(np.float64), iy.astype(np.float64)
        self.X, self.Y = X, Y
        n = len(X)
        self.dom = np.full(n, -1, np.int32)
        self.wdom = np.zeros(n, np.float64)
        self.s = np.zeros(n, np.float64)
        for ci, c in enumerate(self.chains):
            pts = c["pts"]
            best_d = np.full(n, 1e18)
            best_s = np.zeros(n)
            for j in range(len(pts) - 1):
                a, b = pts[j], pts[j + 1]
                ab = b - a
                t = np.clip(((X - a[0]) * ab[0] + (Y - a[1]) * ab[1]) / max(ab @ ab, 1e-9), 0.0, 1.0)
                d = np.hypot(X - (a[0] + t * ab[0]), Y - (a[1] + t * ab[1]))
                better = d < best_d
                best_d = np.where(better, d, best_d)
                best_s = np.where(better, j + t, best_s)
            r = c["r0"] + (c["r1"] - c["r0"]) * best_s / (len(pts) - 1)
            w = np.clip(1.0 - (best_d - 0.6 * r) / (0.8 * r), 0.0, 1.0)
            w = w * w * (3 - 2 * w)
            take = w > self.wdom
            self.dom = np.where(take, ci, self.dom)
            self.s = np.where(take, best_s, self.s)
            self.wdom = np.where(take, w, self.wdom)
        self._ready = True

    def _lidded(self, pose):
        img = self.img
        for name, (cx, cy, rx, ry) in self.lids.items():
            v = float(pose.get("^" + name, 0.0))
            if v <= 0.01:
                continue
            if img is self.img:
                img = self.img.copy()
            yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
            nx, ny = (xx - cx) / rx, (yy - cy) / ry
            d = np.sqrt(nx * nx + ny * ny)
            ring = (d > 1.25) & (d < 1.9) & (self.img[..., 3] > 0.8)
            skin = np.median(self.img[..., :3][ring], axis=0) if ring.any() else np.array([0.4, 0.3, 0.3], np.float32)
            top = -1.0 + 1.75 * v
            bot = 1.0 - 0.45 * v
            cover = np.clip((top - ny) / 0.1, 0.0, 1.0) + np.clip((ny - bot) / 0.1, 0.0, 1.0)
            cover = np.clip(cover, 0.0, 1.0) * np.clip((1.05 - d) / 0.12, 0.0, 1.0)
            crease = np.clip(np.exp(-((ny - top) / 0.16) ** 2) + np.exp(-((ny - bot) / 0.16) ** 2), 0.0, 1.0)
            col = skin[None, None, :] * (0.95 - 0.45 * crease)[..., None]
            img[..., :3] = img[..., :3] * (1.0 - cover[..., None]) + col * cover[..., None]
        return img

    # ---- кадр ----
    def render(self, pose=None, root=None, out=64, pad=0.12):
        """Возвращает RGBA float (hi x hi) на большом холсте; дальше pixelize(). pad - поля вокруг (доля)."""
        if not self._ready:
            self._build()
        pose = pose or {}
        root = root or {}
        s = float(self.w)
        rp = root.get("pivot", (0.5, 0.9))
        R = _T(root.get("dx", 0.0) * s, root.get("dy", 0.0) * s) @ rot_about(root.get("rot", 0.0), rp[0] * s, rp[1] * s, root.get("sx", 1.0), root.get("sy", 1.0))
        img = self._lidded(pose)
        n = len(self.X)
        mats = np.empty((n, 3, 3))
        mats[:] = R
        for ci, c in enumerate(self.chains):
            sel = self.dom == ci
            if not sel.any():
                continue
            pts = c["pts"]
            nb = len(pts) - 1
            Ms = [R]
            for i in range(nb):
                Ms.append(Ms[-1] @ rot_about(float(pose.get("%s%d" % (c["name"], i), 0.0)), pts[i][0], pts[i][1]))
            Ms = np.stack(Ms)                                  # Ms[0] - тело, Ms[i+1] - кость i
            u = self.s[sel] - 0.5
            k = np.floor(u).astype(int) + 1
            f = (u - np.floor(u))[:, None, None]
            k0 = np.clip(k, 0, nb)
            k1 = np.clip(k + 1, 0, nb)
            Mc = Ms[k0] * (1.0 - f) + Ms[k1] * f
            w = self.wdom[sel][:, None, None]
            mats[sel] = (1.0 - w) * R + w * Mc
        X, Y = self.X, self.Y
        Xp = mats[:, 0, 0] * X + mats[:, 0, 1] * Y + mats[:, 0, 2]
        Yp = mats[:, 1, 0] * X + mats[:, 1, 1] * Y + mats[:, 1, 2]
        for name, (cx, cy, rad) in self.warps.items():
            v = pose.get("~" + name)
            if v is None:
                continue
            v = tuple(v) + (0.0, 0.0, 1.0, 0.0)[len(v):]
            dx, dy, sc, ang = v[0] * s, v[1] * s, v[2], math.radians(v[3])
            scy = v[4] if len(v) > 4 else sc
            g = np.exp(-((X - cx) ** 2 + (Y - cy) ** 2) / (2.0 * rad * rad))
            lx, ly = X - cx, Y - cy
            ca, sa = math.cos(ang), math.sin(ang)
            Xp += g * ((ca * lx - sa * ly) * sc - lx + dx)
            Yp += g * ((sa * lx + ca * ly) * scy - ly + dy)
        hi = int(self.w * (1.0 + 2.0 * pad))
        Xd = np.floor(Xp + pad * s).astype(int)
        Yd = np.floor(Yp + pad * s).astype(int)
        col = img[self.iy, self.ix]
        order = np.argsort(self.wdom, kind="stable")           # части цепочек рисуются поверх тела
        canvas = np.zeros((hi, hi, 4), np.float32)
        for ox in (0, 1):
            for oy in (0, 1):
                xx, yy = Xd[order] + ox, Yd[order] + oy
                ok = (xx >= 0) & (yy >= 0) & (xx < hi) & (yy < hi)
                canvas[yy[ok], xx[ok]] = col[order][ok]
        mask = canvas[..., 3] > 0.3
        closed = ndimage.binary_closing(mask, iterations=2)
        holes = closed & ~mask
        if holes.any():
            idx = ndimage.distance_transform_edt(~mask, return_distances=False, return_indices=True)
            canvas[holes] = canvas[idx[0][holes], idx[1][holes]]
        return canvas


# ---- перевод в игровые пиксели ----
def _box(frame_hi, F):
    a = frame_hi[..., 3:4]
    pm = np.concatenate([frame_hi[..., :3] * a, a], -1)
    im = [Image.fromarray(pm[..., c].astype(np.float32), "F").resize((F, F), Image.BOX) for c in range(4)]
    arr = np.stack([np.asarray(i) for i in im], -1)
    al = arr[..., 3:4]
    rgb = np.where(al > 1e-4, arr[..., :3] / np.maximum(al, 1e-4), 0.0)
    return np.concatenate([np.clip(rgb, 0, 1), al], -1)


def make_palette(frame_hi, F, n=24, seed=1):
    arr = _box(frame_hi, F)
    px = arr[arr[..., 3] > 0.5][:, :3]
    rng = np.random.default_rng(seed)
    cent = px[rng.choice(len(px), n, replace=len(px) < n)]
    for _ in range(14):
        d = ((px[:, None, :] - cent[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        for k in range(n):
            if (lab == k).any():
                cent[k] = px[lab == k].mean(0)
    return np.clip(cent, 0, 1)


def pixelize(frame_hi, F, palette, outline=True, island=3):
    arr = _box(frame_hi, F)
    mask = arr[..., 3] > 0.5
    lab, cnt = ndimage.label(mask)
    if cnt:
        sizes = ndimage.sum(mask, lab, range(1, cnt + 1))
        for i, sz in enumerate(sizes):
            if sz < island:
                mask[lab == i + 1] = False
    rgb = arr[..., :3]
    d = ((rgb[..., None, :] - palette[None, None]) ** 2).sum(-1)
    q = palette[d.argmin(-1)]
    out = np.zeros((F, F, 4), np.uint8)
    out[..., :3] = (q * 255).astype(np.uint8)
    out[..., 3] = np.where(mask, 255, 0)
    if outline:
        edge = ndimage.binary_dilation(mask, structure=ndimage.generate_binary_structure(2, 1)) & ~mask
        out[edge] = (*OUTLINE, 255)
    return out


def preview(frames, path, fps=10, scale=6, bg=(52, 44, 44)):
    rig1.save_gif(frames, path, fps, bg=bg, scale=scale)


def grade_palette(pal, sat=0.82, gamma=1.18, tint=(0.96, 1.0, 1.05)):
    """Мрачная цветокоррекция палитры: приглушить цвета, затемнить, холодный оттенок. Применяется один раз к палитре спрайта."""
    p = np.clip(np.asarray(pal, np.float64), 0.0, 1.0)
    g = p.mean(-1, keepdims=True)
    p = np.clip(g + (p - g) * sat, 0.0, 1.0)
    p = np.power(p, gamma)
    return np.clip(p * np.array(tint), 0.0, 1.0)
