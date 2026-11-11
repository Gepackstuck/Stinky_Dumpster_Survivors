"""10 боссов в тоне «В с абсурдом»: лист = ходьба(12) + ряды действий босса (8) + урон(4) + смерть(14). Ряды действий идут сразу после ходьбы в том же порядке, что ROW_* в мозгах боссов."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np

import auto
import bake
import rig as rig1
import rig2

BLOOD = (0.80, 0.04, 0.08)
VOMIT = (0.55, 0.92, 0.12)
BROWN = (0.42, 0.26, 0.06)
P = "tools/_hd_raw/pf/"
# id, файл, размер (мир. ед.), смерть, цвет, летун, ряды действий (виды), вид ярости
B = [
    ("boss_mega_hamster", "boss_mega_hamster_2039", 80, "burst", BLOOD, False, ["spit", "slam", "spin", "rage"]),
    ("boss_zakhar", "boss_zakhar_2041", 86, "headpop", BLOOD, False, ["throw", "roar", "slam", "rage", "spin"]),
    ("boss_rat_queen", "boss_rat_queen_2045", 80, "burst", BLOOD, False, ["roar", "lunge", "spin", "rage"]),
    ("boss_roach_king", "boss_roach_king_2049", 84, "burst", BROWN, False, ["lunge", "roar", "slam", "rage"]),
    ("boss_trash_golem", "boss_trash_golem_2057", 92, "melt", VOMIT, False, ["throw", "slam", "roar", "rage"]),
    ("boss_pigeon_papa", "boss_pigeon_papa_2051", 84, "burst", BLOOD, True, ["lunge", "spit", "spin", "rage"]),
    ("boss_mother_in_law", "boss_mother_in_law_2053", 86, "headpop", BLOOD, False, ["roar", "lunge", "roar", "rage"]),
    ("boss_uk", "boss_uk_2055", 86, "headpop", BLOOD, False, ["slam", "throw", "throw", "spit"]),
    ("boss_blue_whale", "boss_blue_whale_2047", 94, "burst", VOMIT, False, ["spit", "slam", "roar", "rage"]),
    ("boss_minion", "boss_minion_2043", 80, "headpop", BLOOD, False, ["slam", "spit", "rage", "spin"]),
]


def action(kind, i, n):
    """Поза действия на кадре i из n: (рука, голова, масштаб, корень)."""
    t = i / (n - 1)
    wind = math.sin(min(t / 0.45, 1.0) * math.pi / 2)        # замах 0..1
    hit = max(0.0, (t - 0.45) / 0.55)                          # удар
    hit = math.sin(hit * math.pi) if hit > 0 else 0.0
    arm = {"slam": (-30 * wind + 60 * hit), "throw": (-40 * wind + 50 * hit), "spit": 0.0, "lunge": (-15 * wind + 30 * hit),
           "roar": (-25 * math.sin(t * math.pi)), "rage": 12 * math.sin(t * 22), "spin": 25 * math.sin(t * 12)}[kind]
    root = {"pivot": (0.5, 0.82)}
    jaw = 0.0
    if kind == "slam":
        root.update(dy=-0.07 * wind + 0.05 * hit, sy=1.0 + 0.08 * wind - 0.13 * hit, sx=1.0 - 0.04 * wind + 0.08 * hit)
    elif kind == "throw":
        root.update(rot=-5 * wind + 6 * hit, dy=-0.02 * wind, sy=1.0 + 0.05 * wind - 0.05 * hit)
    elif kind == "spit":
        root.update(rot=-6 * wind + 4 * hit, sy=1.0 + 0.06 * wind - 0.08 * hit, sx=1.0 - 0.04 * wind + 0.05 * hit)
        jaw = 0.2 * wind + 1.0 * hit
    elif kind == "lunge":
        root.update(dx=-0.04 * wind + 0.07 * hit, rot=-5 * wind + 7 * hit, sx=1.0 - 0.06 * wind + 0.1 * hit, sy=1.0 + 0.05 * wind - 0.05 * hit)
        jaw = hit
    elif kind == "roar":
        s = math.sin(t * math.pi)
        root.update(sy=1.0 + 0.1 * s, sx=1.0 - 0.03 * s, dy=-0.03 * s, rot=2 * math.sin(t * 30) * s)
        jaw = 1.0 * s
    elif kind == "rage":
        s = math.sin(t * math.pi)
        root.update(sx=1.0 + 0.12 * s, sy=1.0 + 0.12 * s, dx=0.012 * math.sin(t * 40) * s, dy=0.012 * math.cos(t * 37) * s)
        jaw = 0.9 * s
    elif kind == "spin":
        root.update(rot=360 * rig1.ease(t) if False else 14 * math.sin(t * math.tau * 2), sx=1.0 + 0.05 * math.sin(t * math.tau * 2), dx=0.03 * math.sin(t * math.tau * 2))
        jaw = 0.5
    return arm, jaw, root


def fit_pad(r, F, pad, fill=0.56):
    """Подобрать поле так, чтобы фигура (любой формы: высокая, широкая) занимала долю fill кадра - с запасом на замахи, прыжки и разлёт кусков."""
    a = r.render({}, {}, F, pad)[..., 3] > 0.15
    ys, xs = np.where(a)
    f = max(ys.max() - ys.min(), xs.max() - xs.min()) / float(a.shape[0])
    return ((1 + 2 * pad) * f / fill - 1.0) / 2.0


def frames(spec, r, pal):
    F = spec["F"]
    pad = spec["pad"]
    fly = spec.get("fly", False)
    rows = {}
    base = auto.frames(dict(spec, death="none_" ), r, pal) if False else None

    def shot(pose, root):
        return rig2.pixelize(r.render(pose, root, F, pad), F, pal)

    def common(pose, p, jaw=0.0, arm=0.0, lid=None, k=1.0):
        sn = math.sin(p)
        ll, lr = max(sn, 0.0) ** 0.7, max(-sn, 0.0) ** 0.7
        w = r_warps
        if "footL" in w:
            pose["~footL"] = (0.018 * ll * k, -0.07 * ll * k, 1.0 + 0.10 * ll * k)
            pose["~footR"] = (-0.018 * lr * k, -0.07 * lr * k, 1.0 + 0.10 * lr * k)
        if "armL" in w:
            pose["~armL"] = (0.0, -0.03 * lr * k, 1.0, 16 * sn * k - arm)
            pose["~armR"] = (0.0, -0.03 * ll * k, 1.0, 16 * sn * k + arm)
        for kk in range(3):
            if "wave%d" % kk in w:
                pose["~wave%d" % kk] = (0.018 * math.sin(p + kk * 1.4), 0.006 * math.cos(p * 2 + kk), 1.0, 7 * math.sin(p + kk * 1.4 + 0.8))
        if "torso" in w:
            pose["~torso"] = (0.008 * sn, 0.0, 1.0 + 0.03 * math.sin(2 * p))
        if "head" in w:
            pose["~head"] = (0.006 * sn, 0.004 * math.cos(2 * p) - 0.01 * jaw, 1.0 + 0.04 * jaw, 3 * sn)

    r_warps = spec["warps"]
    rows["walk"] = []
    for i in range(12):
        p = i / 12 * math.tau
        pose = {}
        common(pose, p)
        rows["walk"].append(shot(pose, {"dy": (-0.03 * math.sin(p) if fly else -0.014 * abs(math.cos(p))), "rot": 1.5 * math.sin(p), "pivot": (0.5, 0.82)}))
    for j, kind in enumerate(spec["actions"]):
        nm = "attack" if j == 0 else "act%d" % (j + 1)
        rows[nm] = []
        for i in range(8):
            arm, jaw, root = action(kind, i, 8)
            pose = {}
            common(pose, i * 0.7, jaw, arm, k=0.4)
            rows[nm].append(shot(pose, root))
    rows["hurt"] = []
    for k in (1.0, 0.75, 0.4, 0.1):
        pose = {}
        common(pose, 2.4, k, 14 * k, k=0.3)
        rows["hurt"].append(shot(pose, {"rot": -6 * k, "sy": 1.0 - 0.06 * k, "sx": 1.0 + 0.04 * k, "dx": -0.012 * k, "pivot": (0.5, 0.82)}))
    rows["death"] = []
    for i in range(14):
        t = (i + 1) / 14
        big = rig2.death_frame(r, spec["death"], t, spec["goo"], F, pad, seed=spec.get("seed", 3), head_y=spec.get("head_y", 0.3))
        rows["death"].append(rig2.pixelize(big, F, pal))
    return rows


def run(e):
    id_, f, w, death, goo, fly, acts = e
    spec = {"id": "enemy_" + id_, "src": P + f + ".png", "title": id_ + "_финал", "world_w": float(w) * 1.15, "F": 256, "death": death, "goo": goo, "fly": fly,
            "lift": 8.0 if fly else 0.0, "auto": True, "seed": (sum(map(ord, id_)) % 5) + 1, "head_y": 0.3, "actions": acts}
    r = auto.build(spec)
    F = spec["F"]
    pad = fit_pad(r, F, (0.92 * F / (2.0 * spec["world_w"]) - 1.0) / 2.0)
    spec["pad"] = pad
    pal = rig2.grade_palette(rig2.make_palette(r.render({}, {}, F, pad), F, 32), *auto.GRADE)
    pal = np.concatenate([pal, np.array([goo, (0.32, 0.02, 0.04)])], 0)
    bake.emit("sprites/%s.png" % spec["id"], frames(spec, r, pal), spec["world_w"], 10, spec["title"], lift=spec["lift"], texel=0.5)


if __name__ == "__main__":
    only = sys.argv[1:]
    for e in B:
        if only and e[0] not in only:
            continue
        run(e)
