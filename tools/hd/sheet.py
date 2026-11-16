"""Лист «один персонаж с трёх сторон» (FLUX) -> три отдельные картинки. Фигуры ищутся по просветам фона между ними.
split(path) -> [PIL.Image слева направо]. Порядок видов (фас/бок/спина) на листе модель выбирает сама - его задают вручную после просмотра."""
import numpy as np
from PIL import Image


def split(path, n=3):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(float)
    edge = np.concatenate([a[:8].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    bg = np.median(edge, 0)
    fg = np.abs(a - bg).sum(2) > 60
    col = fg[: int(a.shape[0] * 0.93)].sum(0)                       # без нижней полосы: там тени под ногами сливают фигуры
    thr = max(2, int(0.01 * a.shape[0]))
    busy = col > thr
    runs, start = [], None                                           # отрезки с фигурами
    for x, b in enumerate(busy):
        if b and start is None:
            start = x
        if not b and start is not None:
            runs.append([start, x]); start = None
    if start is not None:
        runs.append([start, len(busy)])
    runs = [r for r in runs if r[1] - r[0] > 0.04 * a.shape[1]]      # мухи и брызги - не фигуры
    while len(runs) > n:                                             # лишние просветы внутри фигуры: склеиваем самый узкий
        gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
        i = int(np.argmin(gaps)); runs[i][1] = runs[i + 1][1]; del runs[i + 1]
    if len(runs) < n:                                                # фигуры слиплись: режем поровну
        w = a.shape[1] // n
        runs = [[i * w, (i + 1) * w] for i in range(n)]
    out = []
    for i, (x0, x1) in enumerate(runs):
        l = (runs[i - 1][1] + x0) // 2 if i > 0 else 0
        r = (x1 + runs[i + 1][0]) // 2 if i < len(runs) - 1 else a.shape[1]
        side = max(r - l, a.shape[0])
        cell = Image.new("RGB", (side, side), tuple(int(v) for v in bg))
        cell.paste(im.crop((l, 0, r, a.shape[0])), ((side - (r - l)) // 2, (side - a.shape[0]) // 2))
        out.append(cell)
    return out


if __name__ == "__main__":
    import sys
    for i, c in enumerate(split(sys.argv[1])):
        c.save(sys.argv[1].replace(".png", "_v%d.png" % i))
        print(c.size)
