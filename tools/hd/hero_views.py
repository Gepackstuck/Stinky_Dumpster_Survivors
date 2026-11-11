"""Согласованные виды героя: фас выбирается один (полный рост), а спина и бок получаются из него же (img2img SDXL + пиксель-LoRA),
поэтому одежда, цвета и предметы совпадают. Запуск: python tools/hd/hero_views.py <id> [<id> ...] | all.
Результат: tools/_hd_raw/pf/hv/<id>_front.png, <id>_back_<n>.png, <id>_side_<n>.png"""
import json
import os
import sys

import torch
from diffusers import AutoencoderKL, DPMSolverMultistepScheduler, StableDiffusionXLImg2ImgPipeline, StableDiffusionXLPipeline
from PIL import Image

P = "tools/_hd_raw/pf/"
OUT = P + "hv/"
STYLE = ", pixel art, dark grotesque body horror, absurd, neon green vomit, bright red blood, brown shit, thick dark outline, plain grey background"
NEG = ("cartoon, cute, kawaii, funny, googly eyes, plants vs zombies, bright cheerful, flat colors, clean, smooth, realistic photo, blurry, text, watermark, floor, "
       "background scene, multiple creatures, frame, border, cropped, close-up, portrait, half body")
# фас, который берём за эталон (номер заготовки в tools/_hd_raw/pf; 0 - генерируем новый полноростовой)
FRONT = {}


def desc(hero):
    j = json.load(open(P + "jobs2.json"))
    for x in j:
        if os.path.basename(x["out"]).startswith("hero_%s_front_" % hero):
            return x["prompt"].split(", front view")[0]
    raise KeyError(hero)


def load_pipe(img2img):
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    cls = StableDiffusionXLImg2ImgPipeline if img2img else StableDiffusionXLPipeline
    pipe = cls.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", vae=vae, torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
    pipe.load_lora_weights("nerijs/pixel-art-xl", weight_name="pixel-art-xl.safetensors", adapter_name="px")
    pipe.set_adapters(["px"], adapter_weights=[0.8])
    pipe.to("mps")
    pipe.set_progress_bar_config(disable=True)
    return pipe


def main():
    os.makedirs(OUT, exist_ok=True)
    heroes = sys.argv[1:]
    cfg = json.load(open(OUT + "front.json")) if os.path.exists(OUT + "front.json") else {}
    gen = load_pipe(False)
    for h in heroes:                                    # 1) фас, если эталона ещё нет
        if os.path.exists(OUT + h + "_front.png"):
            continue
        src = cfg.get(h)
        if src:
            Image.open(P + src).convert("RGB").save(OUT + h + "_front.png")
            continue
        for s in range(4):
            g = torch.Generator("cpu").manual_seed(5000 + s + 17 * len(h))
            img = gen(prompt=desc(h) + ", front view facing the viewer, full body from head to toe, feet and shoes visible, wide shot, standing" + STYLE, negative_prompt=NEG,
                      width=1024, height=1024, num_inference_steps=26, guidance_scale=6.5, generator=g).images[0]
            img.save(OUT + "%s_front_new%d.png" % (h, s))
        print("new fronts for", h, "- выбрать и записать в front.json", flush=True)
    del gen
    pipe = load_pipe(True)
    for h in heroes:
        f = OUT + h + "_front.png"
        if not os.path.exists(f):
            continue
        init = Image.open(f).convert("RGB").resize((1024, 1024))
        for view, ptxt, strength in (("back", ", back view seen from behind, rear of the head, no face visible, same outfit, full body, standing", 0.78),
                                     ("side", ", side view profile facing left, walking, same outfit, full body", 0.72)):
            for s in range(2):
                o = OUT + "%s_%s_%d.png" % (h, view, s)
                if os.path.exists(o):
                    continue
                g = torch.Generator("cpu").manual_seed(7000 + s)
                pipe(prompt=desc(h) + ptxt + STYLE, negative_prompt=NEG, image=init, strength=strength, num_inference_steps=30, guidance_scale=6.5,
                     generator=g).images[0].save(o)
                print("ok", o, flush=True)


if __name__ == "__main__":
    main()
