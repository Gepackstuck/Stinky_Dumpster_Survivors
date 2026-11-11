"""Оружие в руках в тоне «В с абсурдом»: заготовки tools/_hd_raw/wp/<id>_<n>.png -> вырезка, поворот длинной осью вправо, 48x48 -> assets/hd/sprites/held_<id>.png.
Какую из двух заготовок брать и нужно ли отразить/перевернуть - в PICK."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from PIL import Image

import rig as rig1

S = 48
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
IDS = ["blowtorch", "bottle", "condensed_milk", "crossbow", "extension_cord", "frying_pan", "laser_pointer", "lighter", "mop", "mosin", "pipe_gun", "plunger",
       "rolling_pin", "rotten_cheese", "shiv", "shovel", "slingshot", "slipper", "sock", "spray_can", "syringe", "tin_bomb"]
PICK = {"mop": (0, False, -90.0), "slingshot": (1, False, 0.0), "blowtorch": (1, False, 0.0)}   # id: (номер заготовки, отразить по горизонтали, доп. поворот в градусах)


def make(wid):
    n, flip, extra = PICK.get(wid, (0, False, 0.0))
    cut = rig1.cutout(os.path.join(ROOT, "tools/_hd_raw/wp/%s_%d.png" % (wid, n)), 768, 0.02)
    ys, xs = np.where(cut[..., 3] > 0.5)
    pts = np.stack([xs, ys], 1).astype(np.float32)
    c = pts.mean(0)
    w, v = np.linalg.eigh(np.cov((pts - c).T))
    ax = v[:, 1]
    ang = np.degrees(np.arctan2(ax[1], ax[0]))
    if abs(ang) > 90:
        ang -= 180 * np.sign(ang)
    if w[1] / max(w[0], 1e-6) < 1.5:      # почти круглое (банка, носок) - не крутим
        ang = 0.0
    im = Image.fromarray((cut * 255).astype(np.uint8), "RGBA").rotate(ang + extra, resample=Image.BICUBIC, expand=True)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    a = np.asarray(im)
    ys, xs = np.where(a[..., 3] > 30)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    k = (S - 2) / max(im.size)
    im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.BOX)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.alpha_composite(im, ((S - im.width) // 2, (S - im.height) // 2))
    arr = np.asarray(out).copy()
    arr[..., 3] = np.where(arr[..., 3] > 110, 255, 0)
    arr[..., :3] = (arr[..., :3] // 24) * 24 + 12      # жёсткая палитра: пиксельный вид
    dst = os.path.join(ROOT, "assets/hd/sprites/held_%s.png" % wid)
    Image.fromarray(arr, "RGBA").save(dst)
    man_p = os.path.join(ROOT, "assets/hd/manifest.json")
    man = json.load(open(man_p))
    man["sprites/held_%s.png" % wid] = {"h": 1, "v": 1, "scale": 1.0, "pixel": True}
    json.dump(man, open(man_p, "w"), indent=1, sort_keys=True)
    print("held", wid, "angle %.0f" % ang)


if __name__ == "__main__":
    for wid in (sys.argv[1:] or IDS):
        make(wid)
