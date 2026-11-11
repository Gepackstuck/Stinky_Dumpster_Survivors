"""Шаблон существа: по описанию костей (spec) собирает ходьбу, удар, урон и смерть и запекает лист в assets/hd/.
spec = {
  "id": "enemy_chaser",                # имя файла в assets/sprites/
  "src": "tools/_hd_raw/px6/chaser_501.png",
  "title": "муха_жуть",                # префикс гифок
  "world_w": 36.0,                     # ширина фигуры в мировых единицах
  "F": 96,
  "chains": [("name", [(x, y), ...], radius, role)],   # role: wave (щупальце/хвост), leg (нога/лапа), arm (рука), wing (крыло)
  "warps": {"jaw": (x, y, r), "head": ..., "body": ..., "eye_l": ..., "eye_r": ...},   # доли картинки
  "lids": {"lid_l": (x, y, rx, ry), ...},
  "death": "collapse" | "fall" | "deflate",
  "fly": True/False,                   # летун: качается вверх-вниз, тень ниже
  "clean": callable(cut) -> cut        # убрать лишнее (тень под ногами и т.п.)
}
Движения: wave - волна по костям; leg - попарная ходьба (чётные и нечётные в противофазе); arm - взмах навстречу ногам; wing - взмахи;
jaw - чавканье; body - дыхание; веки - моргание вразнобой."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np

import bake
import rig as rig1
import rig2

GRADE = (1.18, 1.0)   # смешной блевотный стиль: яркие тошнотворные цвета, без обесцвечивания


def build(spec):
    cut = rig1.cutout(spec["src"], 768, 0.04)
    if spec.get("clean"):
        cut = spec["clean"](cut)
    if spec.get("auto"):
        spec["warps"] = dict(spec.get("warps", {}), **detect_warps(cut))
        spec.setdefault("chains", [])
    r = rig2.Rig2(cut)
    for name, pts, rad, role in spec["chains"]:
        r.chain(name, pts, rad)
    for name, (x, y, rad) in spec.get("warps", {}).items():
        r.warp(name, (x, y), rad)
    for name, (x, y, rx, ry) in spec.get("lids", {}).items():
        r.lid(name, (x, y), rx, ry)
    return r


def detect_warps(cut):
    """Скелет без ручной разметки: по силуэту находим ступни, руки, голову и торс и вешаем на них мягкие зоны. Работает для любого существа."""
    import numpy as np
    m = cut[..., 3] > 0.5
    ys, xs = np.where(m)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    W, H = float(cut.shape[1]), float(cut.shape[0])
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) / 2.0
    out = {}

    def cen(sel):
        yy, xx = np.where(sel)
        return (float(xx.mean()) / W, float(yy.mean()) / H) if len(xx) else None

    low = np.zeros_like(m); low[int(y1 - 0.2 * h):y1] = True
    left = np.zeros_like(m); left[:, :int(cx)] = True
    right = ~left
    for name, side in (("footL", left), ("footR", right)):
        c = cen(m & low & side)
        if c:
            out[name] = (c[0], c[1], 0.09 * w / W + 0.03)
    mid = np.zeros_like(m); mid[int(y0 + 0.3 * h):int(y0 + 0.7 * h)] = True
    for name, side, edge in (("armL", left, x0), ("armR", right, x1 - 1)):
        band = m & mid & side
        yy, xx = np.where(band)
        if len(xx):
            k = np.argsort(np.abs(xx - edge))[:max(30, len(xx) // 10)]
            out[name] = (float(xx[k].mean()) / W, float(yy[k].mean()) / H, 0.1 * w / W + 0.03)
    top = np.zeros_like(m); top[y0:int(y0 + 0.28 * h)] = True
    c = cen(m & top)
    if c:
        out["head"] = (c[0], c[1], 0.17 * w / W + 0.04)
    c = cen(m & mid)
    if c:
        out["torso"] = (c[0], c[1], 0.28 * w / W + 0.05)
    for k, fx in enumerate((0.2, 0.5, 0.8)):                       # волна по низу: щупальца, подол, лохмотья колышутся
        out["wave%d" % k] = ((x0 + fx * w) / W, (y0 + 0.78 * h) / H, 0.12 * w / W + 0.02)
    return out


def _chains_pose(spec, p, mode, k=1.0, hit=0.0, wind=0.0):
    """Позы цепочек по ролям. mode: walk/attack/hurt/death. k - сила (0..1+)."""
    pose = {}
    legs = [c for c in spec["chains"] if c[3] == "leg"]
    for idx, (name, pts, rad, role) in enumerate(spec["chains"]):
        n = len(pts) - 1
        sg = 1.0 if np.mean([q[0] for q in pts]) < 0.5 else -1.0
        for i in range(n):
            key = "%s%d" % (name, i)
            if role == "wave":
                pose[key] = 6.5 * k * math.sin(p - i * 0.9 + idx * 0.85) * (0.6 + 0.4 * i) * sg
            elif role == "leg":
                li = legs.index((name, pts, rad, role))
                lift = max(math.sin(p + (math.pi if li % 2 else 0.0)), 0.0)
                pose[key] = sg * ((20.0 * math.sin(p + (math.pi if li % 2 else 0.0)) if i == 0 else -30.0 * lift) * k)
            elif role == "arm":
                pose[key] = sg * (10.0 * math.sin(p + math.pi * (idx % 2)) * k) * (0.6 + 0.4 * i)
            elif role == "wing":
                pose[key] = sg * 28.0 * math.sin(p * 2.0) * k * (0.4 + 0.6 * i)
            if mode == "attack":
                pose[key] = pose.get(key, 0.0) + sg * (-26.0 * hit + 16.0 * wind) * (0.5 + 0.5 * i)
            if mode == "hurt":
                pose[key] = pose.get(key, 0.0) + sg * 18.0 * k * (0.5 + 0.5 * i)
            if mode == "death":
                pose[key] = pose.get(key, 0.0) * (1.0 - k) + sg * 30.0 * k * (0.5 + 0.5 * i)
    return pose


def frames(spec, r, pal):
    F = spec.get("F", 96)
    pad = (0.92 * F / (2.0 * spec["world_w"]) - 1.0) / 2.0
    fly = spec.get("fly", False)
    warps = spec.get("warps", {})
    lids = spec.get("lids", {})
    rows = {"walk": [], "attack": [], "hurt": [], "death": []}

    def shot(pose, root):
        return rig2.pixelize(r.render(pose, root, F, pad), F, pal)

    def face(pose, s, i, n, jaw=0.0, jaw_amp=0.2, lid=None):
        if "jaw" in warps:
            pose["~jaw"] = (0.0, 0.01 * jaw, 1.0, 0.0, 1.0 + jaw_amp * jaw)
        if "head" in warps:
            pose["~head"] = (0.006 * math.sin(s * 2), 0.004 * math.cos(s * 3), 1.0, 2.0 * math.sin(s))
        if "body" in warps:
            pose["~body"] = (0.0, 0.0, 1.0 + 0.04 * math.sin(s * 2 + 1.0))
        for nm in ("eye_l", "eye_r"):
            if nm in warps:
                ph = 0.0 if nm == "eye_l" else 1.1
                pose["~" + nm] = (0.010 * math.sin(s * 2 + ph), 0.006 * math.cos(s * 3 + ph))
        for j, nm in enumerate(lids):
            pose["^" + nm] = (rig1.blink(i, n, 0.5 + 0.14 * j) if lid is None else lid)

    n = 12
    for i in range(n):
        p = i / n * math.tau
        pose = _chains_pose(spec, p, "walk")
        face(pose, p, i, n, jaw=math.sin(2 * p), jaw_amp=0.3)
        if spec.get("auto"):
            sn = math.sin(p)
            ll, lr = max(sn, 0.0) ** 0.7, max(-sn, 0.0) ** 0.7
            pose["~footL"] = (0.018 * ll, -0.07 * ll, 1.0 + 0.10 * ll)
            pose["~footR"] = (-0.018 * lr, -0.07 * lr, 1.0 + 0.10 * lr)
            pose["~armL"] = (0.0, -0.03 * lr, 1.0, 16 * sn)
            pose["~armR"] = (0.0, -0.03 * ll, 1.0, 16 * sn)
            for kk in range(3):
                pose["~wave%d" % kk] = (0.018 * math.sin(p + kk * 1.4), 0.006 * math.cos(p * 2 + kk), 1.0, 7 * math.sin(p + kk * 1.4 + 0.8))
            pose["~torso"] = (0.008 * sn, 0.0, 1.0 + 0.03 * math.sin(2 * p))
            pose["~head"] = (0.006 * sn, 0.004 * math.cos(2 * p), 1.0, 3 * sn)
        root = {"dy": (-0.03 * math.sin(p) if fly else -0.016 * abs(math.cos(p))), "rot": 2.0 * math.sin(p), "pivot": (0.5, 0.82)}
        rows["walk"].append(shot(pose, root))
    for wind, hit in [(0.0, 0.0), (0.6, 0.0), (1.0, 0.0), (0.4, 0.5), (0.0, 1.0), (0.0, 0.8), (0.0, 0.4), (0.0, 0.1)]:
        pose = _chains_pose(spec, 1.7, "attack", 0.4, hit, wind)
        face(pose, 1.7, 0, 8, jaw=hit - 0.3 * wind, jaw_amp=0.7, lid=0.6 * wind)
        if spec.get("auto"):
            pose["~armL"] = (-0.03 * hit + 0.02 * wind, -0.05 * hit, 1.0 + 0.12 * hit, -22 * hit + 15 * wind)
            pose["~armR"] = (0.03 * hit - 0.02 * wind, -0.05 * hit, 1.0 + 0.12 * hit, 22 * hit - 15 * wind)
            pose["~head"] = (0.0, 0.015 * wind - 0.02 * hit, 1.0 + 0.06 * hit - 0.03 * wind)
        rows["attack"].append(shot(pose, {"sy": 1.0 - 0.10 * wind + 0.10 * hit, "sx": 1.0 + 0.06 * wind + 0.05 * hit, "dy": 0.02 * wind - 0.025 * hit, "pivot": (0.5, 0.82)}))
    for k in (1.0, 0.75, 0.4, 0.1):
        pose = _chains_pose(spec, 2.4, "hurt", k)
        face(pose, 2.4, 0, 4, jaw=k, jaw_amp=0.3, lid=k)
        if spec.get("auto"):
            pose["~armL"] = (-0.02 * k, -0.02 * k, 1.0, 14 * k); pose["~armR"] = (0.02 * k, -0.02 * k, 1.0, -14 * k)
            pose["~head"] = (-0.015 * k, -0.01 * k, 1.0 - 0.04 * k)
        rows["hurt"].append(shot(pose, {"rot": -7 * k, "sy": 1.0 - 0.07 * k, "sx": 1.0 + 0.05 * k, "dx": -0.012 * k, "pivot": (0.5, 0.82)}))
    m = 14
    kind = spec.get("death", "collapse")
    goo = spec.get("goo", (0.55, 0.04, 0.06))
    if kind in ("burst", "headpop", "melt", "dissolve"):
        for i in range(m):                                  # настоящая смерть: куски, кровь, лужа (rig2.death_frame)
            t = (i + 1) / m
            big = rig2.death_frame(r, kind, t, goo, F, pad, seed=spec.get("seed", 3), head_y=spec.get("head_y", 0.28))
            rows["death"].append(rig2.pixelize(big, F, pal))
        return rows
    for i in range(m):
        t = i / (m - 1)
        k = rig1.ease(t)
        pose = _chains_pose(spec, t * 4.0, "death", k)
        face(pose, t * 4, i, m, jaw=k, jaw_amp=0.5, lid=rig1.ease(min(t / 0.4, 1.0)))
        if kind == "fall":
            root = {"rot": 72 * k, "sy": 1.0 - 0.1 * rig1.ease(min(t / 0.3, 1.0)), "dy": 0.16 * k, "dx": -0.03 * k, "pivot": (0.5, 0.58)}
        elif kind == "deflate":
            root = {"sy": 1.0 - 0.55 * k, "sx": 1.0 + 0.25 * k, "dy": 0.01 * k, "rot": 5 * math.sin(k * 5.0) * (1 - k), "pivot": (0.5, 0.88)}
        else:
            root = {"rot": 180 * k if fly else 0.0, "sy": 1.0 - 0.45 * k, "sx": 1.0 + 0.22 * k, "dy": 0.05 * k, "pivot": (0.5, 0.6 if fly else 0.88)}
        rows["death"].append(shot(pose, root))
    return rows


def run(spec):
    F = spec.get("F", 96)
    pad = (0.92 * F / (2.0 * spec["world_w"]) - 1.0) / 2.0
    r = build(spec)
    pal = rig2.grade_palette(rig2.make_palette(r.render({}, {}, F, pad), F, 28), *spec.get("grade", GRADE))
    pal = np.concatenate([pal, np.array([spec.get("goo", (0.55, 0.04, 0.06)), (0.32, 0.02, 0.04)])], 0)   # кровь и слизь для смерти
    bake.emit("sprites/%s.png" % spec["id"], frames(spec, r, pal), spec["world_w"], 10, spec.get("title", spec["id"]), lift=spec.get("lift", 0.0), texel=0.5)
