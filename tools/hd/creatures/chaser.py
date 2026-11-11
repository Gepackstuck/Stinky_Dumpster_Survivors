"""Муха-кусака (enemy_chaser): жирная трупная муха, красные фасеточные глаза. Быстрый летающий ближник.
Ряды: walk (8) - висит и молотит крыльями, лапы болтаются; attack (6) - бросок мордой; hurt (4); death (10) - складывает крылья и падает на спину."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bake
import rig

SRC = "tools/_hd_raw/t3/fly_41.png"
FS = 192
PAD = 0.12


def build() -> rig.Rig:
    r = rig.Rig(rig.cutout(SRC))
    r.body((0.5, 0.33), (0.5, 0.70), 0.115)
    r.body((0.33, 0.62), (0.30, 0.80), 0.05).body((0.67, 0.62), (0.70, 0.80), 0.05)   # лапы - с телом, их качают деформации
    r.bone("wl", (0.42, 0.42), (0.15, 0.30), 0.055, radius_tip=0.15, z=-1)
    r.bone("wr", (0.58, 0.42), (0.85, 0.28), 0.055, radius_tip=0.15, z=-1)
    r.warp("legs_l", (0.32, 0.72), 0.10).warp("legs_r", (0.68, 0.72), 0.10).warp("head", (0.5, 0.35), 0.13).warp("belly", (0.5, 0.63), 0.12)
    return r


def wings(f: float, fold: float = 0.0) -> dict:
    """f -1..1 - фаза взмаха (вверх/вниз), fold 0..1 - сложены к спине."""
    squash = 1.0 - 0.45 * abs(f) - 0.5 * fold
    return {"wl": (-24 * f + 38 * fold, 1.0 - 0.25 * fold, squash), "wr": (24 * f - 38 * fold, 1.0 - 0.25 * fold, squash)}


def frames(r: rig.Rig) -> dict:
    rows = {"walk": [], "attack": [], "hurt": [], "death": []}
    n = 8
    for i in range(n):
        p = i / n * math.tau
        pose = wings(math.sin(p * 2))
        pose.update({"~legs_l": (0.012 * math.sin(p), 0.010 * math.cos(p)), "~legs_r": (0.012 * math.sin(p + 0.8), 0.010 * math.cos(p + 0.8)),
                     "~belly": (0.0, 0.006 * math.sin(p), 1.0 + 0.06 * math.sin(p)),
                     "~head": (0.008 * math.sin(2 * p), 0.0, 1.0 + 0.05 * math.sin(2 * p + 1.0), 6 * math.sin(p))})   # вертит башкой, трёт морду
        rows["walk"].append(rig.polish(r.render(pose, FS, {"dy": 0.025 * math.sin(p), "rot": 2.5 * math.sin(p)}, PAD)))
    for j, k in enumerate([-0.6, -1.0, 0.6, 1.0, 0.6, 0.15]):   # отлёт назад -> бросок мордой на зрителя
        wind, hit = max(-k, 0.0), max(k, 0.0)
        pose = wings(1.0 if j % 2 else -1.0)
        pose.update({"~head": (0.0, 0.02 * hit, 1.0 + 0.22 * hit - 0.05 * wind), "~legs_l": (-0.03 * hit, -0.02 * hit), "~legs_r": (0.03 * hit, -0.02 * hit)})
        rows["attack"].append(rig.polish(r.render(pose, FS, {"sy": 1.0 - 0.06 * wind + 0.10 * hit, "sx": 1.0 - 0.06 * wind + 0.10 * hit, "dy": -0.03 * wind + 0.03 * hit}, PAD)))
    for k in [1.0, 0.7, 0.35, 0.1]:
        pose = wings(-0.6 * k, 0.3 * k)
        pose.update({"~head": (0.0, -0.015 * k, 1.0 - 0.06 * k)})
        rows["hurt"].append(rig.polish(r.render(pose, FS, {"rot": 14 * k, "dy": -0.03 * k, "sx": 1.0 + 0.06 * k, "sy": 1.0 - 0.06 * k}, PAD)))
    m = 10
    for i in range(m):
        t = i / (m - 1)
        fold = rig.ease(min(t / 0.35, 1.0))
        fall = rig.ease(max(0.0, min((t - 0.15) / 0.6, 1.0)))
        pose = wings(0.0, fold)
        pose.update({"~legs_l": (0.03 * fall, -0.05 * fall, 1.0 - 0.2 * fall), "~legs_r": (-0.03 * fall, -0.05 * fall, 1.0 - 0.2 * fall)})
        bounce = math.sin(max(0.0, (t - 0.75) / 0.25) * math.pi) * 0.025
        rows["death"].append(rig.polish(r.render(pose, FS, {"rot": 170 * fall, "dy": 0.10 * fall - bounce, "pivot": (0.5, 0.5)}, PAD)))
    return rows


if __name__ == "__main__":
    r = build()
    r.debug("tools/_hd_raw/rig_chaser.png")
    bake.emit("sprites/enemy_chaser.png", frames(r), 30.0, 14, "муха", lift=7.0)
