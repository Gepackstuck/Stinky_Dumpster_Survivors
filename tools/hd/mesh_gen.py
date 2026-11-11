"""Картинка существа -> 3D-модель (TripoSR, локально). Запуск: tools/_venv/ml/bin/python tools/hd/mesh_gen.py <картинка.png> <имя> [разрешение]
Результат: tools/_hd_raw/mesh/<имя>.glb (цвета вершин)."""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "_venv", "src", "TripoSR"))
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import torch
from PIL import Image

import rig
from tsr.system import TSR

src, name = sys.argv[1], sys.argv[2]
res = int(sys.argv[3]) if len(sys.argv) > 3 else 256
dev = "mps" if torch.backends.mps.is_available() and os.environ.get("MESH_CPU") != "1" else "cpu"
t0 = time.time()
cut = rig.cutout(src, 512, 0.10)
a = cut[..., 3:4]
flat = cut[..., :3] * a + 0.5 * (1 - a)               # TripoSR ждёт серый фон
img = Image.fromarray((flat * 255).astype(np.uint8))
model = TSR.from_pretrained("stabilityai/TripoSR", config_name="config.yaml", weight_name="model.ckpt")
model.renderer.set_chunk_size(4096)
model.to(dev)
with torch.no_grad():
    codes = model([img], device=dev)
    mesh = model.extract_mesh(codes, True, resolution=res)[0]
import trimesh
mesh.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))   # оси TripoSR -> y вверх, лицо к +z
mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
b = mesh.bounds
mesh.apply_translation([-(b[0][0] + b[1][0]) / 2, -b[0][1], -(b[0][2] + b[1][2]) / 2])   # ноги на y=0, по центру
mesh.apply_scale(1.0 / max(b[1][0] - b[0][0], b[1][2] - b[0][2]))                           # ширина (по земле) = 1
mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0]))            # лицом к +z (к камере в нашей сцене)


def recolor(mesh, cut):
    """Тыл и брюхо нейросеть красит серой кашей (их нет на картинке): красим проекцией картинки спереди, чуть темнее.
    Существа примерно симметричны, поэтому одинаковый цвет с обеих сторон выглядит правдоподобно."""
    al = cut[..., 3]
    ys, xs = np.where(al > 0.5)
    ix0, ix1, iy0, iy1 = xs.min(), xs.max(), ys.min(), ys.max()
    v = mesh.vertices
    u = (v[:, 0] - v[:, 0].min()) / max(np.ptp(v[:, 0]), 1e-6)
    t = (v[:, 1] - v[:, 1].min()) / max(np.ptp(v[:, 1]), 1e-6)
    px = np.clip((ix1 - u * (ix1 - ix0)).astype(int), 0, cut.shape[1] - 1)   # лицом к +z: x зеркален картинке
    py = np.clip((iy1 - t * (iy1 - iy0)).astype(int), 0, cut.shape[0] - 1)
    proj = cut[py, px, :3]
    n = mesh.vertex_normals
    front = np.clip((n[:, 2] + 0.15) / 0.6, 0.0, 1.0)[:, None]                  # 1 - смотрит на камеру
    old = np.asarray(mesh.visual.vertex_colors)[:, :3].astype(np.float32) / 255.0
    side = np.clip(proj * 0.85, 0.0, 1.0)
    new = old * front + side * (1.0 - front)
    rgba = np.concatenate([(new * 255).astype(np.uint8), np.full((len(v), 1), 255, np.uint8)], 1)
    mesh.visual = trimesh.visual.ColorVisuals(mesh, vertex_colors=rgba)


recolor(mesh, cut)
os.makedirs("tools/_hd_raw/mesh", exist_ok=True)
mesh.export("tools/_hd_raw/mesh/%s.glb" % name)
print("mesh", name, dev, len(mesh.vertices), "verts", len(mesh.faces), "faces", "%.0fs" % (time.time() - t0))
