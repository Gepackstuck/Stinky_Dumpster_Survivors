"""Крупные кадры запечённого листа для проверки глазами: tools/hd/check.py sprites/enemy_x.png -> tools/_hd_raw/_chk_<ряд>.png"""
import json
import sys

from PIL import Image

rel = sys.argv[1]
man = json.load(open("assets/hd/manifest.json"))[rel]
sheet = Image.open("assets/hd/" + rel)
fs = sheet.width // man["h"]
for name, (row, count) in man["rows"].items():
    cols = sorted(set(int(round(i * (count - 1) / 4)) for i in range(5)))
    out = Image.new("RGB", (320 * len(cols), 320), (70, 62, 60))
    for i, c in enumerate(cols):
        f = sheet.crop((c * fs, row * fs, c * fs + fs, row * fs + fs)).resize((320, 320), Image.LANCZOS)
        out.paste(f, (i * 320, 0), f)
    out.save("tools/_hd_raw/_chk_%s.png" % name)
