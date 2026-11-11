"""Декорации арены новой пиксельной рисовки: вырезка -> палитра -> контур -> assets/hd/props/<имя>.png + props.json (размер, подошва, источник света).
Берёт лучшие заготовки из tools/_hd_raw/px9 (имя_сид.png), по одной на имя (первая найденная, либо та, что указана в PICK)."""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from PIL import Image
from scipy import ndimage

import bake
import rig as rig1
import rig2

PICK = {}
# (имя, ширина в мировых единицах, свет: None или (цвет rgb, энергия, радиус))
PROPS = [("dumpster", 56, None), ("container", 90, None), ("car", 100, None), ("tires", 46, None), ("lamp", 30, ((1.0, 0.82, 0.45), 1.1, 150.0)),
         ("barrel_fire", 24, ((1.0, 0.5, 0.15), 1.3, 120.0)), ("fence", 80, None), ("trashpile", 70, None), ("wall", 96, None), ("fridge", 52, None),
         ("mattress", 50, None), ("gravestone", 30, None)]


def main():
    out_dir = os.path.join(bake.ROOT, "assets", "hd", "props")
    os.makedirs(out_dir, exist_ok=True)
    meta = {}
    for name, w_world, light in PROPS:
        files = sorted(glob.glob("tools/_hd_raw/px9/%s_[0-9]*.png" % name))
        if not files:
            continue
        src = PICK.get(name, files[0])
        cut = rig1.cutout(src, 512, 0.02)
        ys, xs = np.where(cut[..., 3] > 0.5)
        cut = cut[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        S = max(cut.shape[:2])
        sq = np.zeros((S, S, 4), np.float32)
        oy, ox = S - cut.shape[0], (S - cut.shape[1]) // 2
        sq[oy:oy + cut.shape[0], ox:ox + cut.shape[1]] = cut
        sq = np.asarray(Image.fromarray((sq * 255).astype(np.uint8)).resize((512, 512), Image.NEAREST)).astype(np.float32) / 255.0
        ys, xs = np.where(sq[..., 3] > 0.5)
        fig_w = xs.max() - xs.min() + 1
        F = int(round(w_world / 0.5 * 512.0 / fig_w))              # размер кадра так, чтобы ширина фигуры = w_world при 0.5 ед/пиксель
        F = max(24, min(F, 240))
        pal = rig2.grade_palette(rig2.make_palette(sq, F, 26), 1.1, 0.7)
        px = rig2.pixelize(sq, F, pal, rim=0.5, lift_dark=0.4)
        a = px[..., 3] > 0
        yy, xx = np.where(a)
        px = px[yy.min():yy.max() + 1, xx.min():xx.max() + 1]
        Image.fromarray(px).save(os.path.join(out_dir, name + ".png"))
        meta[name] = {"w": int(px.shape[1]), "h": int(px.shape[0]), "world_w": w_world}
        if light:
            meta[name]["light"] = {"color": list(light[0]), "energy": light[1], "radius": light[2]}
    json.dump(meta, open(os.path.join(bake.ROOT, "assets", "hd", "props.json"), "w"), indent=1)
    names = sorted(meta)
    sheet = Image.new("RGBA", (1400, 520), (50, 44, 44, 255)); x = 6
    for n in names:
        im = Image.open(os.path.join(out_dir, n + ".png")).convert("RGBA"); im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
        if x + im.width > 1400:
            break
        sheet.alpha_composite(im, (x, 500 - im.height)); x += im.width + 8
    sheet.convert("RGB").save("tools/_preview/hd/05_пиксели/декорации_арены.png")
    print("props", len(meta))


if __name__ == "__main__":
    main()
