"""Генерация картинок новой рисовки на FLUX.1-schnell (MLX, локально). Понимает длинные подробные описания - в отличие от SDXL.
Запуск: tools/_venv/flux/bin/python tools/hd/flux_gen.py jobs.json
jobs.json: [{"out": "path.png", "prompt": "...", "seed": 1, "w": 768, "h": 768, "steps": 4}, ...]. Готовые файлы пропускаются."""
import json
import os
import sys
import time

from mflux.models.common.config import ModelConfig
from mflux.models.flux.variants.txt2img.flux import Flux1

MODEL = "dhairyashil/FLUX.1-schnell-mflux-8bit"
TRIES = 4


def flat_bg(path):
    """Фон ровный? (спрайт потом вырезается; если модель дорисовала сцену - перегенерируем с другим зерном)."""
    import numpy as np
    from PIL import Image
    a = np.asarray(Image.open(path).convert("RGB").resize((256, 256))).astype(float)
    edge = np.concatenate([a[:10].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :10].reshape(-1, 3), a[:, -10:].reshape(-1, 3)])
    med = np.median(edge, 0)
    off = (np.abs(edge - med).sum(1) > 45).mean()          # доля пикселей рамки, не похожих на фон
    return off < 0.12 and med.mean() > 60                  # и фон не чёрный (на чёрном теряется обводка)


def main():
    jobs = [j for j in json.load(open(sys.argv[1])) if not os.path.exists(j["out"]) or not (j.get("any_bg") or flat_bg(j["out"]))]
    if not jobs:
        print("nothing to do"); return
    flux = Flux1(model_config=ModelConfig.from_name(model_name=MODEL, base_model="schnell"), quantize=None)
    for i, j in enumerate(jobs):
        t0 = time.time()
        os.makedirs(os.path.dirname(j["out"]) or ".", exist_ok=True)
        for k in range(TRIES):
            prompt = j["prompt"] if k == 0 else "Isolated on a plain flat mid-grey studio background, nothing else in the picture. " + j["prompt"]
            img = flux.generate_image(seed=int(j.get("seed", 1)) + 1000 * k + (7 if os.path.exists(j["out"]) and k == 0 else 0), prompt=prompt,
                                      width=int(j.get("w", 768)), height=int(j.get("h", 768)), num_inference_steps=int(j.get("steps", 4)))
            img.save(path=j["out"], overwrite=True)
            if j.get("any_bg") or flat_bg(j["out"]):
                break
        print("[%d/%d] %s %.0fs tries %d%s" % (i + 1, len(jobs), j["out"], time.time() - t0, k + 1, "" if j.get("any_bg") or flat_bg(j["out"]) else " BG!"), flush=True)


if __name__ == "__main__":
    main()
