"""ЕДИНЫЙ ПРОМПТ ОФОРМЛЕНИЯ «ВОНЮЧАЯ ПОМОЙКА» для локальной SDXL (+ пиксель-LoRA). Всё, что рисуется для новой рисовки, собирается отсюда.

Идея: страшно и одновременно абсурдно-мерзко. Не «серый серьёзный хоррор» и не мультик: гниющая свалка, бомжи, алкаши, трупы, мухи, опарыши.
Правило цвета: база ТЁМНАЯ и грязная (ржавчина, плесень, гниль), а ЯРКИМ светится только мерзость - кислотно-зелёная блевотина,
алая кровь, блестящий коричневый понос, жёлтый гной. Так экран читается: тёмное - мир, яркое - то, что течёт и брызжет.

Правила промпта (SDXL видит только 77 токенов): предмет ПЕРВЫМ и коротко (до ~28 токенов), потом вид, потом STYLE.
"""
STYLE = ("pixel art, stinking garbage dump horror, rotting flesh, maggots and flies, puke green slime, bright red blood, brown diarrhea, "
         "rust and mold, grotesque absurd, thick dark outline, plain grey background")
STYLE_GROUND = ("pixel art, top-down view, stinking garbage dump ground texture, dark wet mud, rotting trash, bones, maggots, dried blood stains, "
                "puke puddles, rusty cans, very dark, flat, seamless, no objects standing")
NEG = ("cartoon, cute, kawaii, funny face, googly eyes, plants vs zombies, bright cheerful, clean, new, shiny, smooth gradient, realistic photo, blurry, text, "
       "watermark, logo, frame, border, multiple objects, hands, person holding")
NEG_GROUND = "cartoon, cute, bright, clean, character, creature, perspective, horizon, sky, wall, text, watermark, frame, border, blurry, realistic photo"


def job(out, subject, seed, view="", lora=0.8, steps=24, ground=False):
    """Задание для tools/hd/sd_gen.py."""
    if ground:
        prompt, neg = STYLE_GROUND, NEG_GROUND
    else:
        prompt, neg = ", ".join([x for x in (subject, view, STYLE) if x]), NEG
    return {"out": out, "seed": seed, "raw": True, "lora": lora, "neg": neg, "steps": steps, "prompt": prompt}
