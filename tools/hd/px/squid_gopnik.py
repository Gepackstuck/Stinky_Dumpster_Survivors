"""Кальмар-гопник (enemy_squid_gopnik), НОВАЯ ПИКСЕЛЬНАЯ: розовый кальмар-осьминог в красной бейсболке, зубастая пасть, жёлтые глаза, 8 щупалец.
Описание: розовый кальмар в красной кепке, пасть до ушей. Кепку нейросеть не нарисовала - дорисована здесь по описанию.
Ряды: walk (12) - семенит нижними щупальцами, верхние извиваются волной, моргает, пасть чавкает; attack (8) - присел, подобрал щупальца и бросился,
пасть раскрыта; hurt (4) - отшатнулся, щупальца веером, зажмурился; death (10) - щупальца обмякают, оседает, кепка слетает."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import bake
import rig as rig1
import rig2

SRC = "tools/_hd_raw/px2/squid_33.png"
F = 88
WORLD_W = 34.0                              # желаемая ширина в мировых единицах (пиксель = 0.5 единицы)
PAD = (0.92 * F / (2.0 * WORLD_W) - 1.0) / 2.0
CH = [  # (имя, точки, радиус, знак наклона: +1 слева, -1 справа)
    ("L1", [(0.30, 0.46), (0.20, 0.46), (0.12, 0.41), (0.15, 0.36)], 0.045, 1),
    ("L2", [(0.32, 0.53), (0.22, 0.58), (0.18, 0.66), (0.22, 0.73)], 0.05, 1),
    ("L3", [(0.36, 0.67), (0.28, 0.72), (0.19, 0.73), (0.15, 0.69)], 0.045, 1),
    ("R1", [(0.68, 0.46), (0.77, 0.44), (0.84, 0.38), (0.79, 0.36)], 0.045, -1),
    ("R2", [(0.66, 0.53), (0.78, 0.57), (0.87, 0.62), (0.85, 0.70)], 0.05, -1),
    ("R3", [(0.62, 0.67), (0.72, 0.72), (0.82, 0.73), (0.86, 0.69)], 0.045, -1),
    ("C1", [(0.43, 0.70), (0.40, 0.78), (0.45, 0.85), (0.52, 0.85)], 0.045, 1),
    ("C2", [(0.58, 0.70), (0.60, 0.78), (0.55, 0.85), (0.50, 0.86)], 0.045, -1),
]


def paint_cap(cut):
    """Красная бейсболка: купол, козырёк, швы, кнопка, значок. Рисуется крупно (потом всё равно переводится в пиксели)."""
    H, W = cut.shape[:2]
    K = 3
    im = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def box(x0, y0, x1, y1):
        return [x0 * W * K, (y0 - 0.035) * H * K, x1 * W * K, (y1 - 0.035) * H * K]

    edge, red, mid, light = (36, 4, 14, 255), (206, 26, 42, 255), (236, 56, 58, 255), (255, 118, 104, 255)
    d.ellipse(box(0.235, 0.205, 0.765, 0.345), fill=edge)                          # козырёк: контур
    d.ellipse(box(0.248, 0.215, 0.752, 0.333), fill=(172, 16, 36, 255))            # верх козырька
    d.ellipse(box(0.262, 0.265, 0.738, 0.336), fill=(92, 8, 26, 255))              # тёмная кромка козырька
    d.ellipse(box(0.315, 0.090, 0.685, 0.290), fill=edge)                          # купол: контур
    d.ellipse(box(0.327, 0.100, 0.673, 0.280), fill=red)
    d.ellipse(box(0.35, 0.108, 0.55, 0.20), fill=mid)                              # блик
    d.ellipse(box(0.37, 0.116, 0.48, 0.16), fill=light)
    d.arc(box(0.30, 0.09, 0.50, 0.29), 100, 260, fill=edge, width=int(0.005 * W * K))   # швы
    d.arc(box(0.50, 0.09, 0.70, 0.29), -80, 80, fill=edge, width=int(0.005 * W * K))
    d.ellipse(box(0.488, 0.088, 0.512, 0.110), fill=edge)                           # кнопка
    d.ellipse(box(0.492, 0.092, 0.508, 0.106), fill=mid)
    d.polygon([(0.5 * W * K, 0.123 * H * K), (0.537 * W * K, 0.187 * H * K), (0.463 * W * K, 0.187 * H * K)], fill=(255, 226, 80, 255))   # значок
    d.polygon([(0.5 * W * K, 0.140 * H * K), (0.522 * W * K, 0.179 * H * K), (0.478 * W * K, 0.179 * H * K)], fill=(60, 8, 20, 255))
    cap = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0
    a = cap[..., 3:4]
    out = cut.copy()
    out[..., :3] = cut[..., :3] * (1 - a) + cap[..., :3] * a
    out[..., 3] = np.maximum(cut[..., 3], cap[..., 3])
    return out


def build():
    cut = rig1.cutout(SRC, 768, 0.04)
    cut = paint_cap(cut)
    r = rig2.Rig2(cut)
    for name, pts, rad, _ in CH:
        r.chain(name, pts, rad)
    r.warp("jaw", (0.50, 0.62), 0.10).warp("cap", (0.50, 0.16), 0.15).warp("head", (0.50, 0.32), 0.2)
    r.lid("eye_l", (0.397, 0.355), 0.05, 0.05).lid("eye_r", (0.627, 0.357), 0.05, 0.05)
    return r


def tent(p, amp=1.0, walk=0.0, up=0.0):
    """Волна по щупальцам: каждая кость качается с запаздыванием - щупальце извивается. walk - шагающие нижние, up - подтянуть."""
    pose = {}
    for k, (name, _, _, sg) in enumerate(CH):
        ph = p * 1.0 + k * 0.8
        base = 5.5 * amp * (0.45 if name in ("L2", "R2") else 1.0)   # большие боковые щупальца качаются слабее: иначе тянут за собой клин
        for i in range(3):
            a = base * math.sin(ph - i * 0.9) * (0.6 + 0.4 * i) * sg
            pose["%s%d" % (name, i)] = a + sg * up * (8 + 5 * i)
    if walk:
        for name, ph in (("L3", 0.0), ("R3", math.pi), ("C1", math.pi * 0.5), ("C2", math.pi * 1.5), ("L2", math.pi), ("R2", 0.0)):
            sg = 1 if name[0] in "LC" and name != "C2" else -1
            lift = max(math.sin(p + ph), 0.0)
            pose[name + "0"] = pose.get(name + "0", 0.0) + sg * (-10.0 * lift) * walk
            pose[name + "1"] = pose.get(name + "1", 0.0) + sg * (-15.0 * lift) * walk
    return pose


def frames(r, pal):
    rows = {"walk": [], "attack": [], "hurt": [], "death": []}

    def shot(pose, root):
        return rig2.pixelize(r.render(pose, root, F, PAD), F, pal)

    n = 12
    for i in range(n):
        p = i / n * math.tau
        s, c = math.sin(p), math.cos(p)
        pose = tent(p, 1.0, 1.0)
        pose.update({"~jaw": (0.0, 0.012 * math.sin(2 * p), 1.0, 0.0, 1.0 + 0.16 * math.sin(2 * p)), "~cap": (0.0, -0.008 * abs(s)),
                     "^eye_l": rig1.blink(i, n, 0.5), "^eye_r": rig1.blink(i, n, 0.64)})
        rows["walk"].append(shot(pose, {"dx": -0.012 * s, "dy": -0.016 * abs(c), "rot": -2.0 * s, "pivot": (0.5, 0.8)}))
    for wind, hit in [(0.0, 0.0), (0.6, 0.0), (1.0, 0.0), (0.4, 0.5), (0.0, 1.0), (0.0, 0.8), (0.0, 0.4), (0.0, 0.1)]:
        pose = tent(1.7, 0.5, 0.0, up=0.9 * wind - 1.1 * hit)
        pose.update({"~jaw": (0.0, 0.04 * hit - 0.03 * wind, 1.0 + 0.1 * hit, 0.0, 1.0 + 0.38 * hit - 0.18 * wind), "^eye_l": 0.7 * wind, "^eye_r": 0.7 * wind,
                     "~cap": (0.0, 0.012 * wind - 0.015 * hit), "~head": (0.0, 0.0, 1.0 - 0.04 * wind + 0.05 * hit)})
        rows["attack"].append(shot(pose, {"sy": 1.0 - 0.10 * wind + 0.10 * hit, "sx": 1.0 + 0.06 * wind + 0.05 * hit, "dy": 0.02 * wind - 0.025 * hit, "pivot": (0.5, 0.8)}))
    for k in (1.0, 0.75, 0.4, 0.1):
        pose = tent(2.4, 1.0 + 1.6 * k, 0.0, up=-0.7 * k)
        pose.update({"^eye_l": k, "^eye_r": k, "~jaw": (0.0, 0.02 * k, 1.0, 0.0, 1.0 + 0.2 * k), "~cap": (0.012 * k, -0.01 * k, 1.0, 8 * k), "~head": (-0.015 * k, 0.0, 1.0 - 0.04 * k)})
        rows["hurt"].append(shot(pose, {"rot": -7 * k, "sy": 1.0 - 0.07 * k, "sx": 1.0 + 0.05 * k, "pivot": (0.5, 0.8)}))
    m = 10
    for i in range(m):
        t = i / (m - 1)
        k = rig1.ease(t)
        pose = tent(t * 4.0, 1.0 - k, 0.0, up=0.8 * k)          # щупальца подбираются, обмякают
        pose.update({"^eye_l": rig1.ease(min(t / 0.4, 1.0)), "^eye_r": rig1.ease(min(t / 0.55, 1.0)), "~jaw": (0.0, 0.04 * k, 1.0, 0.0, 1.0 + 0.3 * k),
                     "~cap": (0.07 * k, 0.04 * k, 1.0, 38 * k), "~head": (0.0, 0.03 * k, 1.0 + 0.05 * k, 0.0, 1.0 - 0.22 * k)})
        rows["death"].append(shot(pose, {"sy": 1.0 - 0.45 * k, "sx": 1.0 + 0.22 * k, "dy": 0.01 * k, "rot": 5 * math.sin(k * 5.0) * (1 - k), "pivot": (0.5, 0.88)}))
    return rows


if __name__ == "__main__":
    r = build()
    pal = rig2.make_palette(r.render({}, {}, F, PAD), F, 28)
    bake.emit("sprites/enemy_squid_gopnik.png", frames(r, pal), WORLD_W, 10, "кальмар_гопник_новый", texel=0.5)
