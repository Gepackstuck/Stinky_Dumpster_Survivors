"""Быстрый просмотр модели без движка: точки с цветом вершин, 6 сторон. tools/hd/mesh_views.py <имя> -> tools/_hd_raw/_mesh_<имя>.png"""
import sys
import numpy as np
import trimesh
from PIL import Image

name = sys.argv[1]
m = trimesh.load("tools/_hd_raw/mesh/%s.glb" % name, force="mesh")
v = np.asarray(m.vertices)
c = np.asarray(m.visual.vertex_colors)[:, :3] if hasattr(m.visual, "vertex_colors") else np.full((len(v), 3), 200)
print("bounds", m.bounds.round(2).tolist())
dirs = {"+z": (0, 1, 2, 1), "-z": (0, 1, 2, -1), "+x": (2, 1, 0, -1), "-x": (2, 1, 0, 1), "верх": (0, 2, 1, -1), "низ": (0, 2, 1, 1)}
S = 360
sheet = Image.new("RGB", (S * 6, S), (30, 30, 36))
for i, (k, (ax, ay, az, sg)) in enumerate(dirs.items()):
    img = np.full((S, S, 3), 30, np.uint8)
    depth = np.full((S, S), -1e9)
    x, y, z = v[:, ax], v[:, ay], v[:, az] * sg
    px = ((x - v[:, ax].min()) / 1.3 * (S - 20) + 10).astype(int)
    py = (S - 10 - (y - v[:, ay].min()) / 1.3 * (S - 20)).astype(int) if ay == 1 else ((y - v[:, ay].min()) / 1.3 * (S - 20) + 10).astype(int)
    for dx in (0, 1):
        for dy in (0, 1):
            qx, qy = np.clip(px + dx, 0, S - 1), np.clip(py + dy, 0, S - 1)
            ok = z > depth[qy, qx]
            idx = np.where(ok)[0]
            # последняя запись побеждает: сортируем по z, чтобы ближние писались позже
            o = np.argsort(z[idx])
            idx = idx[o]
            img[qy[idx], qx[idx]] = c[idx]
            depth[qy[idx], qx[idx]] = z[idx]
    sheet.paste(Image.fromarray(img), (i * S, 0))
sheet.save("tools/_hd_raw/_mesh_%s.png" % name)
