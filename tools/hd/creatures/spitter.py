"""Плевун (enemy_spitter): жирная зубастая жаба, плюётся кислотой издалека.
Ряды: walk (10) - жабий прыжок: присела, оттолкнулась, приземлилась и расплющилась; attack (8) - надула горло, запрокинула
голову и харкнула, пасть настежь; hurt (4); death (10) - заваливается на бок, пасть отвисает."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import bake
import rig

SRC = "tools/_hd_raw/t4/spitter_93.png"
FS = 224
PAD = 0.18


def build() -> rig.Rig:
    r = rig.Rig(rig.cutout(SRC))
    r.warp("head", (0.55, 0.22), 0.22).warp("jaw", (0.56, 0.46), 0.14).warp("throat", (0.42, 0.57), 0.13)
    r.warp("hand_l", (0.30, 0.82), 0.11).warp("hand_r", (0.70, 0.77), 0.11).warp("back", (0.22, 0.35), 0.14)
    r.lid("eye_l", (0.445, 0.17), 0.052, 0.05).lid("eye_r", (0.755, 0.19), 0.032, 0.045)
    return r


def frames(r: rig.Rig) -> dict:
    rows = {"walk": [], "attack": [], "hurt": [], "death": []}
    # прыжок: (присед, высота, плющение при приземлении) по кадрам
    hop = [(0.3, 0.0, 0.0), (0.8, 0.0, 0.0), (1.0, 0.0, 0.0), (0.2, 0.5, 0.0), (0.0, 0.9, 0.0), (0.0, 1.0, 0.0),
           (0.0, 0.6, 0.0), (0.0, 0.1, 0.6), (0.0, 0.0, 1.0), (0.1, 0.0, 0.4)]
    for i, (crouch, air, land) in enumerate(hop):
        pose = {"^eye_l": max(rig.blink(i, len(hop), 0.2), 0.7 * land), "^eye_r": max(rig.blink(i, len(hop), 0.25), 0.7 * land),
                "~jaw": (0.0, 0.02 * land - 0.012 * air, 1.0, 0.0, 1.0 + 0.14 * air - 0.22 * crouch),"~hand_l": (0.0, -0.055 * air, 1.0 - 0.10 * air, 10 * air), "~hand_r": (0.0, -0.055 * air, 1.0 - 0.10 * air, -10 * air),
                "~throat": (0.0, 0.0, 1.0 + 0.08 * crouch - 0.05 * air),
                "~head": (0.0, 0.012 * land, 1.0)}
        root = {"sy": 1.0 - 0.10 * crouch + 0.07 * air - 0.13 * land, "sx": 1.0 + 0.05 * crouch - 0.03 * air + 0.09 * land, "dy": -0.10 * air}
        rows["walk"].append(rig.polish(r.render(pose, FS, root, PAD)))
    for swell, spit in [(0.3, 0.0), (0.7, 0.0), (1.0, 0.0), (1.0, 0.3), (0.3, 1.0), (0.0, 0.9), (0.0, 0.5), (0.0, 0.15)]:
        pose = {"~throat": (0.0, 0.01 * swell, 1.0 + 0.25 * swell - 0.08 * spit), "~head": (-0.015 * swell + 0.02 * spit, -0.02 * swell + 0.015 * spit, 1.0 + 0.05 * spit),
                "~jaw": (0.0, -0.02 * swell + 0.055 * spit, 1.0 + 0.10 * spit, 0.0, 1.0 + 0.30 * spit - 0.35 * swell),
                "^eye_l": 0.8 * swell, "^eye_r": 0.8 * swell}
        root = {"rot": -5 * swell + 6 * spit, "sx": 1.0 + 0.03 * swell + 0.05 * spit, "sy": 1.0 + 0.03 * swell - 0.03 * spit}
        rows["attack"].append(rig.polish(r.render(pose, FS, root, PAD)))
    for k in [1.0, 0.75, 0.4, 0.1]:
        pose = {"^eye_l": k, "^eye_r": k, "~head": (-0.02 * k, -0.01 * k, 1.0 - 0.04 * k), "~jaw": (0.0, 0.03 * k), "~hand_l": (-0.02 * k, -0.03 * k), "~hand_r": (0.02 * k, -0.03 * k)}
        rows["hurt"].append(rig.polish(r.render(pose, FS, {"rot": -7 * k, "sy": 1.0 - 0.08 * k, "sx": 1.0 + 0.06 * k}, PAD)))
    m = 10
    for i in range(m):
        t = i / (m - 1)
        fall = rig.ease(max(0.0, min((t - 0.1) / 0.6, 1.0)))
        bounce = math.sin(max(0.0, (t - 0.7) / 0.3) * math.pi) * 0.02
        pose = {"^eye_l": rig.ease(min(t / 0.5, 1.0)), "^eye_r": rig.ease(min(t / 0.6, 1.0)), "~jaw": (0.0, 0.05 * fall, 1.0 + 0.10 * fall), "~throat": (0.0, 0.0, 1.0 - 0.12 * fall),
                "~hand_l": (0.0, -0.04 * fall, 1.0, 20 * fall), "~hand_r": (0.0, -0.04 * fall, 1.0, 20 * fall)}
        root = {"rot": 80 * fall, "sy": 1.0 - 0.10 * rig.ease(min(t / 0.3, 1.0)), "dy": -bounce - 0.02 * fall, "dx": -0.10 * fall, "pivot": (0.5, 0.82)}
        rows["death"].append(rig.polish(r.render(pose, FS, root, PAD)))
    return rows


if __name__ == "__main__":
    r = build()
    r.debug("tools/_hd_raw/rig_spitter.png")
    bake.emit("sprites/enemy_spitter.png", frames(r), 34.0, 12, "плевун")
