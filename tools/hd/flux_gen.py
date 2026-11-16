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


def main():
    jobs = [j for j in json.load(open(sys.argv[1])) if not os.path.exists(j["out"])]
    if not jobs:
        print("nothing to do"); return
    flux = Flux1(model_config=ModelConfig.from_name(model_name=MODEL, base_model="schnell"), quantize=None)
    for i, j in enumerate(jobs):
        t0 = time.time()
        img = flux.generate_image(seed=int(j.get("seed", 1)), prompt=j["prompt"], width=int(j.get("w", 768)), height=int(j.get("h", 768)),
                                  num_inference_steps=int(j.get("steps", 4)))
        os.makedirs(os.path.dirname(j["out"]) or ".", exist_ok=True)
        img.save(path=j["out"], overwrite=True)
        print("[%d/%d] %s %.0fs" % (i + 1, len(jobs), j["out"], time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
