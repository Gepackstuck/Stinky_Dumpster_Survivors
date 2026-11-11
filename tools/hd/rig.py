"""Скелетная анимация одной нарисованной картинки (реалистичный стиль).

Картинка существа -> вырезаем фон -> кости (точка вращения, кончик, радиус влияния) -> позы по кадрам ->
плавная деформация (linear blend skinning с обратным отображением) -> лист кадров PNG + GIF для просмотра.

Запуск только из ml-окружения: tools/_venv/ml/bin/python (numpy, scipy, PIL, rembg).
"""
import math
import os

import numpy as np
from PIL import Image
from scipy import ndimage

_SESSION = None


def cutout(path: str, work: int = 640, pad: float = 0.12) -> np.ndarray:
    """Вырезать существо с ровного фона. Возвращает RGBA float32 0..1, обрезано по фигуре, с полями; длинная сторона = work."""
    global _SESSION
    from rembg import new_session, remove
    if _SESSION is None:
        _SESSION = new_session("isnet-general-use")
    im = remove(Image.open(path).convert("RGB"), session=_SESSION, post_process_mask=True)
    a = np.asarray(im).astype(np.float32) / 255.0
    alpha = a[..., 3]
    alpha = np.clip((alpha - 0.35) / 0.5, 0.0, 1.0)   # срезать полупрозрачную тень под ногами
    lab, n = ndimage.label(alpha > 0.5)              # оставить только самый большой кусок (без клякс и вторых фигур)
    if n > 1:
        sizes = ndimage.sum(alpha > 0.5, lab, range(1, n + 1))
        keep = ndimage.binary_dilation(lab == (1 + int(np.argmax(sizes))), iterations=6)
        alpha = alpha * keep
    a[..., 3] = alpha
    ys, xs = np.where(alpha > 0.05)
    a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = a.shape[:2]
    side = int(max(h, w) * (1.0 + pad * 2))
    canvas = np.zeros((side, side, 4), np.float32)
    oy, ox = (side - h) // 2, (side - w) // 2
    canvas[oy:oy + h, ox:ox + w] = a
    out = Image.fromarray((canvas * 255).astype(np.uint8)).resize((work, work), Image.LANCZOS)
    return np.asarray(out).astype(np.float32) / 255.0


def _rot(angle_deg: float, cx: float, cy: float, sx: float = 1.0, sy: float = 1.0, axis_deg: float = 0.0) -> np.ndarray:
    """Поворот вокруг точки + растяжение вдоль оси кости (sx) и поперёк (sy)."""
    def r(a):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], np.float64)
    t1 = np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]], np.float64)
    t2 = np.array([[1, 0, cx], [0, 1, cy], [0, 0, 1]], np.float64)
    sc = r(axis_deg) @ np.diag([sx, sy, 1.0]) @ r(-axis_deg)
    return t2 @ r(angle_deg) @ sc @ t1


class Rig:
    """Кости заданы в долях картинки (0..1): pivot - вокруг чего вращается, tip - куда тянется, radius - толщина влияния."""

    def __init__(self, img: np.ndarray):
        self.img = img
        self.h, self.w = img.shape[:2]
        self.bones = []   # name, pivot, tip, radius, parent
        self.statics = []
        self.warps = {}   # мягкие деформации: имя -> (cx, cy, радиус) в пикселях
        self.lids = {}    # веки: имя -> (cx, cy, rx, ry) в пикселях
        self.blend = 0.012   # ширина размытия границ между частями (доля картинки)
        self._weights = None

    def bone(self, name: str, pivot, tip, radius: float, parent: str = "", radius_tip: float = -1.0, z: float = 1.0) -> "Rig":
        s = float(self.w)
        self.bones.append({"name": name, "pivot": (pivot[0] * s, pivot[1] * s), "tip": (tip[0] * s, tip[1] * s),
                           "radius": radius * s, "radius_tip": (radius_tip if radius_tip > 0 else radius) * s, "parent": parent, "z": z})
        self._weights = None
        return self

    def chain(self, name: str, points, radius: float, parent: str = "", taper: float = 0.6) -> "Rig":
        """Цепочка костей по точкам (щупальце, хвост): name0, name1, ... каждая - ребёнок предыдущей."""
        for i in range(len(points) - 1):
            k = 1.0 - (1.0 - taper) * i / max(len(points) - 2, 1)
            self.bone("%s%d" % (name, i), points[i], points[i + 1], radius * k, parent if i == 0 else "%s%d" % (name, i - 1))
        return self

    def warp(self, name: str, center, radius: float) -> "Rig":
        """Мягкая деформация («пластилин»): область вокруг center плавно сдвигается/растягивается/поворачивается, без швов и дыр.
        В позе: {"~имя": (dx, dy)} или (dx, dy, масштаб) или (dx, dy, масштаб, угол) - сдвиги в долях картинки."""
        s = float(self.w)
        self.warps[name] = (center[0] * s, center[1] * s, radius * s)
        return self

    def lid(self, name: str, center, rx: float, ry: float) -> "Rig":
        """Веко над глазом (эллипс center, rx, ry в долях). В позе: {"^имя": 0..1} - насколько закрыт глаз (моргание, прищур).
        Цвет века берётся с кожи вокруг глаза, по краю века - тёмная складка."""
        s = float(self.w)
        self.lids[name] = (center[0] * s, center[1] * s, rx * s, ry * s)
        return self

    def _with_lids(self, pose: dict) -> np.ndarray:
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
            ring = (d > 1.25) & (d < 1.8) & (self.img[..., 3] > 0.8)
            skin = np.median(self.img[..., :3][ring], axis=0) if ring.any() else np.array([0.4, 0.3, 0.3], np.float32)
            top = -1.0 + 1.75 * v - 0.25 * nx * nx * (1.0 - v)    # край верхнего века (дугой)
            bot = 1.0 - 0.45 * v + 0.15 * nx * nx * (1.0 - v)     # нижнее веко поднимается чуть-чуть
            cover = np.clip((top - ny) / 0.08, 0.0, 1.0) + np.clip((ny - bot) / 0.08, 0.0, 1.0)
            cover = np.clip(cover, 0.0, 1.0) * np.clip((1.05 - d) / 0.12, 0.0, 1.0)
            crease = np.exp(-((ny - top) / 0.14) ** 2) + np.exp(-((ny - bot) / 0.14) ** 2)
            shade = (0.92 - 0.25 * ny * 0.5) * (1.0 - 0.5 * np.clip(crease, 0.0, 1.0))
            col = skin[None, None, :] * shade[..., None]
            img[..., :3] = img[..., :3] * (1.0 - cover[..., None]) + col * cover[..., None]
        return img

    def body(self, pivot, tip, radius: float) -> "Rig":
        """Неподвижная часть тела (туловище): пиксели рядом с ней не достаются конечностям."""
        s = float(self.w)
        self.statics.append(((pivot[0] * s, pivot[1] * s), (tip[0] * s, tip[1] * s), radius * s))
        self._weights = None
        return self

    def _score(self, xx, yy, pivot, tip, r0, r1):
        px, py = pivot
        dx, dy = tip[0] - px, tip[1] - py
        ln2 = max(dx * dx + dy * dy, 1e-6)
        t = np.clip(((xx - px) * dx + (yy - py) * dy) / ln2, 0.0, 1.0)
        d = np.hypot(xx - (px + t * dx), yy - (py + t * dy))
        return d / np.maximum(r0 + (r1 - r0) * t, 1e-6)

    def _build(self) -> None:
        """Каждый пиксель достаётся ближайшей кости (расстояние в её толщинах), границы размываются - суставы гнутся плавно."""
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        # без заданного туловища: дальше одной толщины от любой кости - туловище; с туловищем - просто ближайшая часть
        root = np.full((self.h, self.w), 1.0 if not self.statics else 1e9, np.float32)
        for pv, tp, r in self.statics:
            root = np.minimum(root, self._score(xx, yy, pv, tp, r, r))
        scores = [root] + [self._score(xx, yy, b["pivot"], b["tip"], b["radius"], b["radius_tip"]) for b in self.bones]
        label = np.argmin(np.stack(scores), axis=0)
        sigma = self.blend * self.w
        ws = np.stack([ndimage.gaussian_filter((label == i).astype(np.float32), sigma) for i in range(len(scores))])
        self._weights = (ws / np.maximum(ws.sum(0), 1e-6)).astype(np.float32)

    def render(self, pose: dict, out: int = 192, root: dict = None, pad: float = 0.0) -> np.ndarray:
        """pose: {кость: угол} или {кость: (угол, растяжение_вдоль, поперёк)}. root: dx, dy (доли), rot, sx, sy, pivot (доли).
        Возвращает кадр RGBA uint8 out x out."""
        if self._weights is None:
            self._build()
        root = root or {}
        s = float(self.w)
        rp = root.get("pivot", (0.5, 0.92))
        R = _rot(root.get("rot", 0.0), rp[0] * s, rp[1] * s, root.get("sx", 1.0), root.get("sy", 1.0))
        R[0, 2] += root.get("dx", 0.0) * s
        R[1, 2] += root.get("dy", 0.0) * s
        mats = {"": np.eye(3)}
        order = []
        for b in self.bones:   # родители объявляются раньше детей
            v = pose.get(b["name"], 0.0)
            ang, sx, sy = (v if isinstance(v, tuple) else (v, 1.0, 1.0))
            axis = math.degrees(math.atan2(b["tip"][1] - b["pivot"][1], b["tip"][0] - b["pivot"][0]))
            mats[b["name"]] = mats[b["parent"]] @ _rot(ang, b["pivot"][0], b["pivot"][1], sx, sy, axis)
            order.append(mats[b["name"]])
        allm = [np.eye(3)] + order
        zs = [0.0] + [float(b.get("z", 1.0)) for b in self.bones]
        # Порядок: части тела (слои) -> мягкие деформации -> общий наклон/сжатие. Обратно идём от выходного пикселя.
        k = self.w * (1.0 + 2.0 * pad) / float(out)   # pad - поля вокруг картинки (доля): место для падений и замахов
        yy, xx = np.mgrid[0:out, 0:out].astype(np.float64)
        ox, oy = (xx + 0.5) * k - 0.5 - pad * self.w, (yy + 0.5) * k - 0.5 - pad * self.w
        ri = np.linalg.inv(R)
        dst_x = ri[0, 0] * ox + ri[0, 1] * oy + ri[0, 2]
        dst_y = ri[1, 0] * ox + ri[1, 1] * oy + ri[1, 2]
        for name, (cx, cy, rad) in self.warps.items():
            v = pose.get("~" + name)
            if v is None:
                continue
            v = tuple(v) + (0.0, 0.0, 1.0, 0.0)[len(v):]
            dx, dy, sc, ang = v[0] * s, v[1] * s, v[2], math.radians(v[3])
            scy = v[4] if len(v) > 4 else sc   # пятое число - отдельный масштаб по вертикали (пасть шире/уже, глаз щурится)
            g = np.exp(-((dst_x - cx - dx) ** 2 + (dst_y - cy - dy) ** 2) / (2.0 * rad * rad))
            lx, ly = dst_x - cx - dx, dst_y - cy - dy
            ca, sa = math.cos(-ang), math.sin(-ang)
            fx = cx + (ca * lx - sa * ly) / sc
            fy = cy + (sa * lx + ca * ly) / scy
            dst_x = dst_x + g * (fx - dst_x)
            dst_y = dst_y + g * (fy - dst_y)
        frame = np.zeros((out, out, 4), np.float32)   # premultiplied
        src = self._with_lids(pose)
        pm = src[..., :3] * src[..., 3:4]
        for i in sorted(range(len(allm)), key=lambda n: (zs[n], n)):
            inv = np.linalg.inv(allm[i])
            sx = inv[0, 0] * dst_x + inv[0, 1] * dst_y + inv[0, 2]
            sy = inv[1, 0] * dst_x + inv[1, 1] * dst_y + inv[1, 2]
            w = ndimage.map_coordinates(self._weights[i], [sy, sx], order=1, mode="constant")
            w = np.clip(w * 2.0, 0.0, 1.0)   # часть непрозрачна до середины шва и тает дальше
            al = ndimage.map_coordinates(self.img[..., 3], [sy, sx], order=1, mode="constant") * w
            if al.max() <= 0.0:
                continue
            for c in range(3):
                col = ndimage.map_coordinates(pm[..., c], [sy, sx], order=1, mode="constant") * w
                frame[..., c] = col + frame[..., c] * (1.0 - al)
            frame[..., 3] = al + frame[..., 3] * (1.0 - al)
        a = np.maximum(frame[..., 3:4], 1e-4)
        frame[..., :3] = np.clip(frame[..., :3] / a, 0.0, 1.0)
        frame[..., 3] = np.clip((frame[..., 3] - 0.3) / 0.5, 0.0, 1.0)   # без полупрозрачной грязи вокруг фигуры
        return (np.clip(frame, 0.0, 1.0) * 255).astype(np.uint8)

    def debug(self, path: str) -> None:
        """Картинка с костями поверх - проверить глазами, что скелет лёг на тело."""
        from PIL import ImageDraw
        bg = np.zeros((self.h, self.w, 3), np.float32) + 0.25
        rgb = self.img[..., :3] * self.img[..., 3:4] + bg * (1 - self.img[..., 3:4])
        im = Image.fromarray((rgb * 255).astype(np.uint8))
        d = ImageDraw.Draw(im)
        for cx, cy, rad in self.warps.values():
            d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(0, 200, 255), width=2)
        for b in self.bones:
            d.line([b["pivot"], b["tip"]], fill=(0, 255, 0), width=3)
            px, py = b["pivot"]
            d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(255, 255, 0))
            r = b["radius_tip"]
            tx, ty = b["tip"]
            d.ellipse([tx - r, ty - r, tx + r, ty + r], outline=(255, 0, 255))
        im.save(path)


def outline(frame: np.ndarray, color=(8, 4, 6), px: int = 2) -> np.ndarray:
    """Тёмная обводка вокруг фигуры: существо не сливается с полом."""
    a = frame[..., 3].astype(np.float32) / 255.0
    lab, n = ndimage.label(a > 0.3)   # выкинуть оторвавшиеся крошки и бледную грязь: остаются только крупные куски
    if n > 0:
        sizes = ndimage.sum(a > 0.3, lab, range(1, n + 1))
        big = np.isin(lab, [i + 1 for i in range(n) if sizes[i] >= sizes.max() * 0.02])
        a = a * ndimage.binary_dilation(big, iterations=2)
    grown = ndimage.maximum_filter(a, size=px * 2 + 1)
    grown = ndimage.gaussian_filter(grown, 0.6)
    out = frame.astype(np.float32)
    edge = np.clip(grown - a, 0.0, 1.0)
    for c in range(3):
        out[..., c] = out[..., c] * a + color[c] * (1 - a)
    out[..., 3] = np.clip(a + edge, 0.0, 1.0) * 255
    return out.astype(np.uint8)


def save_sheet(rows: list, path: str) -> None:
    """rows: список рядов, ряд - список кадров одинакового размера. Короткие ряды добиваются последним кадром."""
    cols = max(len(r) for r in rows)
    fs = rows[0][0].shape[0]
    sheet = np.zeros((fs * len(rows), fs * cols, 4), np.uint8)
    for y, r in enumerate(rows):
        for x in range(cols):
            sheet[y * fs:(y + 1) * fs, x * fs:(x + 1) * fs] = r[min(x, len(r) - 1)]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(sheet).save(path)


def save_gif(frames: list, path: str, fps: int = 12, bg=(38, 30, 30), scale: int = 2) -> None:
    """GIF для просмотра глазами: кадры на тёмном фоне, увеличенные."""
    ims = []
    for f in frames:
        a = f[..., 3:4].astype(np.float32) / 255.0
        rgb = f[..., :3] * a + np.array(bg, np.float32) * (1 - a)
        im = Image.fromarray(rgb.astype(np.uint8))
        ims.append(im.resize((im.width * scale, im.height * scale), Image.LANCZOS))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0)


def polish(frame: np.ndarray, gamma: float = 0.68, sat: float = 1.25, rim: float = 0.55, rim_color=(255, 232, 200), px: int = 2) -> np.ndarray:
    """Читаемость в игре: существо светлее и сочнее, по верхней кромке - тёплый блик (свет сверху), вокруг - тёмная обводка."""
    f = frame.astype(np.float32) / 255.0
    a = f[..., 3]
    rgb = np.power(np.clip(f[..., :3], 0.0, 1.0), gamma)
    grey = rgb.mean(-1, keepdims=True)
    rgb = np.clip(grey + (rgb - grey) * sat, 0.0, 1.0)
    shifted = np.zeros_like(a)
    d = max(2, frame.shape[0] // 64)
    shifted[d:, :] = a[:-d, :]
    edge = ndimage.gaussian_filter(np.clip(a - shifted, 0.0, 1.0), 0.8) * rim
    rc = np.array(rim_color, np.float32) / 255.0
    rgb = rgb + (rc - rgb) * edge[..., None]
    out = np.concatenate([rgb, a[..., None]], -1)
    return outline((np.clip(out, 0.0, 1.0) * 255).astype(np.uint8), px=px)


def ease(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def normal_map(frame: np.ndarray, dome: float = 1.0, detail: float = 0.5) -> np.ndarray:
    """Карта нормалей кадра для рельефного света: фигура «надута» от края к середине (объём) + мелкий рельеф по яркости.
    Возвращает RGBA uint8 (альфа как у кадра)."""
    a = frame[..., 3].astype(np.float32) / 255.0
    inside = a > 0.5
    dist = ndimage.distance_transform_edt(inside).astype(np.float32)
    r = max(float(dist.max()), 1.0)
    edge = np.clip(dist / (r * 0.55), 0.0, 1.0)
    height = np.sqrt(1.0 - (1.0 - edge) ** 2) * r * 0.55 * dome          # купол: круглый край, плоская середина
    lum = frame[..., :3].astype(np.float32).mean(-1) / 255.0
    height = ndimage.gaussian_filter(height, 1.5) + ndimage.gaussian_filter(lum, 1.0) * detail * r * 0.25
    gy, gx = np.gradient(height)
    n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    out = np.zeros(frame.shape, np.uint8)
    out[..., 0] = ((n[..., 0] * 0.5 + 0.5) * 255).astype(np.uint8)
    out[..., 1] = ((-n[..., 1] * 0.5 + 0.5) * 255).astype(np.uint8)   # в Godot зелёный канал нормали смотрит вверх
    out[..., 2] = ((n[..., 2] * 0.5 + 0.5) * 255).astype(np.uint8)
    out[..., 3] = frame[..., 3]
    return out


def blink(i: int, n: int, at: float = 0.6) -> float:
    """Моргание раз за цикл: 0 - открыт, 1 - закрыт. at - доля цикла, где глаз закрыт полностью."""
    d = abs(i / float(n) - at) * n
    return max(0.0, 1.0 - d / 1.6)
