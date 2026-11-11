"""«Надутый рисунок»: картинка существа -> закрытое 3D-тело с текстурой этой же картинки. Запуск (ml-окружение):
tools/_venv/ml/bin/python tools/hd/inflate.py <картинка.png> <имя> [толщина_доля_ширины]
Тело: высота по расстоянию до края силуэта (купол с плато), перед и зад одинаковые, на краю смыкаются. Текстура - вырезанный рисунок,
освещён и подчищен (polish без обводки), по краям цвет растянут наружу, чтобы не было светящейся каймы. Результат: tools/_hd_raw/mesh/<имя>.glb"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import trimesh
from PIL import Image
from scipy import ndimage

import rig

src, name = sys.argv[1], sys.argv[2]
depth_frac = float(sys.argv[3]) if len(sys.argv) > 3 else 0.45
S = 512
cut = rig.cutout(src, S, 0.04)
mask = cut[..., 3] > 0.5
dist = ndimage.distance_transform_edt(mask).astype(np.float32)
r = dist.max() * 0.75
d = np.clip(dist / r, 0.0, 1.0)
T = np.sqrt(1.0 - (1.0 - d) ** 2)                      # круглый край, плоская середина
T = ndimage.gaussian_filter(T, 2.0)
ys, xs = np.where(mask)
width = float(xs.max() - xs.min() + 1)
T = T * depth_frac * width * 0.5                       # половина толщины в пикселях изображения
# текстура: цвет вытянут за край силуэта
rgb = cut[..., :3].copy()
idx = ndimage.distance_transform_edt(~mask, return_distances=False, return_indices=True)
rgb = rgb[idx[0], idx[1]]
tex = Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))
# сетка вершин: шаг 2 px
step = 2
gy, gx = np.mgrid[0:S:step, 0:S:step]
inside = ndimage.binary_erosion(mask, iterations=1)[gy, gx]
vid = -np.ones(gy.shape, int)
vid[inside] = np.arange(inside.sum())
px = gx[inside].astype(np.float32)
py = gy[inside].astype(np.float32)
tz = T[gy, gx][inside]
scale = 1.0 / width
cx = (xs.max() + xs.min()) / 2.0
foot = ys.max()
def pos(zsign):
    return np.stack([(px - cx) * scale, (foot - py) * scale, zsign * tz * scale], -1)
n = len(px)
verts = np.concatenate([pos(1.0), pos(-1.0)])
uv = np.concatenate([np.stack([px / S, 1.0 - py / S], -1)] * 2)
faces = []
H, W = vid.shape
a, b, c, e = vid[:-1, :-1], vid[:-1, 1:], vid[1:, :-1], vid[1:, 1:]
ok = (a >= 0) & (b >= 0) & (c >= 0) & (e >= 0)
a, b, c, e = a[ok], b[ok], c[ok], e[ok]
faces.append(np.stack([a, c, b], 1)); faces.append(np.stack([b, c, e], 1))          # перед (нормаль к +z)
faces.append(np.stack([a + n, b + n, c + n], 1)); faces.append(np.stack([b + n, e + n, c + n], 1))   # зад
faces = np.concatenate(faces)
mat = trimesh.visual.material.PBRMaterial(baseColorTexture=tex, metallicFactor=0.0, roughnessFactor=0.75)
mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False, visual=trimesh.visual.TextureVisuals(uv=uv, material=mat))
# шов по краю: вершины с одинаковым положением и uv у перед/зад склеиваем (тело закрытое)
mesh.merge_vertices(merge_tex=True, digits_vertex=3)
mesh.update_faces(mesh.nondegenerate_faces())
os.makedirs("tools/_hd_raw/mesh", exist_ok=True)
mesh.export("tools/_hd_raw/mesh/%s.glb" % name)
print("inflate", name, len(mesh.vertices), "verts", len(mesh.faces), "faces")
