"""Проба: пиксельная жаба-плевун, ходьба/удар на новом скелете. Просмотр: tools/_preview/hd/05_пиксели/."""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np

import rig as rig1
import rig2

SRC = "tools/_hd_raw/px1/frog_13.png"
F = 64
cut = rig1.cutout(SRC, 768, 0.04)
h = cut.shape[0]
rgb = cut[..., :3]
sat = rgb.max(-1) - rgb.min(-1)
low = np.zeros(cut.shape[:2], bool); low[int(0.66 * h):] = True
cut[..., 3] = np.where(low & (sat < 0.12), 0.0, cut[..., 3])            # серая тень под жабой - не часть тела
r = rig2.Rig2(cut)
r.chain("al", [(0.26, 0.55), (0.23, 0.66), (0.27, 0.77)], 0.07)          # левая рука: плечо - локоть - пальцы
r.chain("ar", [(0.74, 0.55), (0.77, 0.66), (0.73, 0.77)], 0.07)
r.warp("jaw", (0.50, 0.47), 0.09).warp("throat", (0.50, 0.60), 0.12).warp("head", (0.50, 0.32), 0.18)
r.lid("eye_l", (0.352, 0.305), 0.05, 0.05).lid("eye_r", (0.668, 0.305), 0.05, 0.05)
neutral = r.render({}, {}, F)
pal = rig2.make_palette(neutral, F, 22)
frames = []
n = 10
for i in range(n):
    p = i / n * math.tau
    s = math.sin(p)
    lift_l, lift_r = max(s, 0.0), max(-s, 0.0)
    pose = {"al0": 18 * s, "al1": -26 * lift_l + 6 * lift_r, "ar0": -18 * s, "ar1": -26 * lift_r + 6 * lift_l,
            "~jaw": (0.0, 0.012 * math.sin(2 * p), 1.0, 0.0, 1.0 + 0.22 * math.sin(2 * p)),
            "~throat": (0.0, 0.0, 1.0 + 0.05 * math.sin(2 * p + 1.0)),
            "^eye_l": rig1.blink(i, n, 0.55), "^eye_r": rig1.blink(i, n, 0.62)}
    root = {"dy": -0.018 * abs(math.sin(p)), "rot": 2.0 * s, "sy": 1.0 - 0.025 * math.cos(2 * p), "sx": 1.0 + 0.02 * math.cos(2 * p)}
    frames.append(rig2.pixelize(r.render(pose, root, F), F, pal))
os.makedirs("tools/_preview/hd/05_пиксели", exist_ok=True)
rig2.preview(frames, "tools/_preview/hd/05_пиксели/жаба_ходьба_новый_скелет.gif", 10, 8)
rig1.save_sheet([frames], "tools/_hd_raw/_frog_px_sheet.png")
print("ok", len(frames))
