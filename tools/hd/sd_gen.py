"""Локальная генерация картинок для «реалистичного» стиля (SDXL на Apple Silicon, MPS).

Запуск: tools/_venv/ml/bin/python tools/hd/sd_gen.py jobs.json
jobs.json: [{"out": "path.png", "prompt": "...", "neg": "...", "w": 1024, "h": 1024, "seed": 1, "steps": 28, "cfg": 6.5}, ...]
Готовые файлы пропускаются (перегенерация - удалить файл). Сырьё кладём в tools/_hd_raw/ (не в репозиторий).
"""
import json
import os
import sys
import time

import torch
from diffusers import AutoencoderKL, DPMSolverMultistepScheduler, StableDiffusionXLPipeline

MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
VAE = "madebyollin/sdxl-vae-fp16-fix"
STYLE = "dark horror creature concept art, realistic digital painting, wet rotting flesh, grimy, dramatic lighting"
SUFFIX = "full body, isolated on plain grey background"
NEG = ("text, watermark, signature, logo, frame, border, blurry, lowres, cartoon, comic, vector art, sticker, flat colors, cute, anime, pixel art, "
       "photo of people, extra objects, cropped, out of frame")


def main() -> None:
    jobs = json.load(open(sys.argv[1]))
    jobs = [j for j in jobs if not os.path.exists(j["out"])]
    if not jobs:
        print("nothing to do")
        return
    vae = AutoencoderKL.from_pretrained(VAE, torch_dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained(MODEL, vae=vae, torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
    pipe.to("mps")
    pipe.set_progress_bar_config(disable=True)
    for i, j in enumerate(jobs):
        t0 = time.time()
        gen = torch.Generator("cpu").manual_seed(int(j.get("seed", 1)))
        # оба текстовых кодировщика SDXL видят только 77 токенов: стиль впереди, описание короткое
        prompt = j["prompt"] if j.get("raw") else "%s, %s, %s" % (j.get("style", STYLE), j["prompt"], j.get("suffix", SUFFIX))
        n_tok = len(pipe.tokenizer(prompt).input_ids)
        if n_tok > 77:
            print("!! prompt too long (%d tokens): %s" % (n_tok, j["out"]), flush=True)
        img = pipe(prompt=prompt, negative_prompt=j.get("neg", "") + ", " + NEG, width=int(j.get("w", 1024)), height=int(j.get("h", 1024)),
                   num_inference_steps=int(j.get("steps", 22)), guidance_scale=float(j.get("cfg", 6.5)), generator=gen).images[0]
        os.makedirs(os.path.dirname(j["out"]) or ".", exist_ok=True)
        img.save(j["out"])
        print("[%d/%d] %s %.0fs" % (i + 1, len(jobs), j["out"], time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
