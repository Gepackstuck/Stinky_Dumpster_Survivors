"""Вид сзади для «надутого рисунка»: по вырезанному виду спереди (зеркальному) SDXL img2img рисует спину.
tools/_venv/ml/bin/python tools/hd/back_gen.py <спереди.png> <имя> "<описание спины>" [сила 0..1]
Результат: tools/_hd_raw/back/<имя>_<seed>.png (1024x1024, выровнено по зеркальному силуэту спереди)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import torch
from diffusers import AutoencoderKL, DPMSolverMultistepScheduler, StableDiffusionXLImg2ImgPipeline
from PIL import Image

import rig

src, name, prompt = sys.argv[1], sys.argv[2], sys.argv[3]
strength = float(sys.argv[4]) if len(sys.argv) > 4 else 0.78
cut = rig.cutout(src, 512, 0.04)
flip = cut[:, ::-1].copy()                                      # вид сзади: слева направо наоборот
a = flip[..., 3:4]
base = flip[..., :3] * a + 0.5 * (1 - a)
init = Image.fromarray((base * 255).astype(np.uint8)).resize((1024, 1024), Image.LANCZOS)
vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", vae=vae, torch_dtype=torch.float16, variant="fp16", use_safetensors=True)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
pipe.to("mps")
pipe.set_progress_bar_config(disable=True)
os.makedirs("tools/_hd_raw/back", exist_ok=True)
full = "dark horror creature concept art, realistic digital painting, wet rotting flesh, grimy, dramatic lighting, %s, seen from behind, rear view, full body, plain grey background" % prompt
for seed in (1, 2, 3):
    g = torch.Generator("cpu").manual_seed(seed)
    img = pipe(prompt=full, negative_prompt="face, eyes, mouth, teeth, front view, looking at camera, text, watermark, cartoon, blurry", image=init, strength=strength,
               num_inference_steps=30, guidance_scale=7.0, generator=g).images[0]
    img.save("tools/_hd_raw/back/%s_%d.png" % (name, seed))
    print("back", name, seed, flush=True)
