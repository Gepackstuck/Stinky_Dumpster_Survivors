#!/usr/bin/env python3
"""Звук ужаса для новой стилистики: гудящий фон-лупа, шёпот, скрипы, далёкие стоны, сердцебиение, мокрые удары и ломающиеся кости.
Всё синтезом. PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_audio_horror.py -> assets/music/amb_horror.wav (стерео луп),
assets/sfx/{whisper,creak,moan,heartbeat,wet_hit,gore_burst,bone_crack}[_N].wav"""
import os
import numpy as np
import gen_audio as G
from gen_audio import SR, N, T, TAU, filt, noise, save, reverb, phase, sweep, gate, plus

R = np.random.default_rng(66)


def amb():
    """24 с, бесшовно: тёмный органный гул (ре и ля), малая секунда кластера, сабовая пульсация, ледяной ветер, редкие металлические удары."""
    sec = 24.0
    n = N(sec); t = T(n)
    L = np.zeros(n); Rr = np.zeros(n)
    for f, g in ((36.7, 0.9), (73.4, 0.7), (110.0, 0.4), (116.5, 0.28), (146.8, 0.22), (55.0, 0.5)):   # D1, D2, A2, Bb2 (малая секунда), D3, A1
        k = round(f * sec)                                      # целое число периодов за луп
        ff = k / sec
        for det, side in ((-0.18, 0), (0.0, 2), (0.21, 1)):
            ph = np.sin(TAU * (ff + det) * t * 1.0 + R.random() * TAU)
            am = 0.6 + 0.4 * np.sin(TAU * (0.5 + 0.1 * R.random()) * round(sec * 0.25) / sec * t)
            sig = np.tanh(1.8 * ph) * am * g * 0.2
            if side == 0: L += sig
            elif side == 1: Rr += sig
            else: L += sig * 0.6; Rr += sig * 0.6
    pulse = 0.55 + 0.45 * np.sin(TAU * 3 * t / 1.0 * 0.0 + TAU * (sec / 8.0) * t / sec * 8 * 0.5)   # медленное дыхание
    L *= pulse; Rr *= pulse[::-1] * 0 + pulse * 0.9
    for _ in range(2):                                           # ледяной ветер
        w = filt(noise(n), lo=180, hi=900) * (0.5 + 0.5 * np.sin(TAU * 2 * t / sec + R.random() * TAU)) ** 2
        L += w * 0.05; Rr += np.roll(w, N(0.07)) * 0.05
    for at in (4.0, 11.5, 17.0):                                 # далёкий удар по железу, затухает в реверберации
        i0 = N(at); d = N(3.0); tt = T(d)
        hit = sum(a * np.sin(TAU * f * tt) * np.exp(-tt / dec) for f, a, dec in ((113, 1, 1.2), (213, 0.5, 0.8), (331, 0.3, 0.5), (547, 0.2, 0.3)))
        m = min(d, n - i0)
        L[i0:i0 + m] += hit[:m] * 0.05; Rr[i0:i0 + m] += hit[:m] * 0.045
    x = np.stack([L, Rr])
    x = x + 0.55 * reverb(x, 3.5)
    x = np.stack([filt(x[0], lo=28, hi=3500), filt(x[1], lo=28, hi=3500)])
    x /= np.max(np.abs(x)) + 1e-9
    fade = N(0.5)                                                # петля: стык через перекрытие
    w = np.linspace(0, 1, fade)
    x[:, :fade] = x[:, :fade] * w + x[:, -fade:] * (1 - w)
    x = x[:, :-fade]
    save(f"{G.OUT_MUS}/amb_horror.wav", x * 0.8, stereo=True)


def whisper(seed):
    r = np.random.default_rng(seed)
    n = N(r.uniform(1.4, 2.4)); t = T(n)
    out = np.zeros(n)
    syl = int(r.integers(4, 8))
    for i in range(syl):                                         # слоги: шипение + гласный с формантой
        c = int(n * (0.1 + 0.8 * i / syl)); d = int(n * 0.08)
        env = np.sin(np.pi * np.arange(d) / d) ** 1.5
        hiss = filt(noise(d), lo=1800, hi=4800) * env * 0.6
        v = filt(noise(d), lo=500 + 400 * r.random(), hi=1300 + 900 * r.random(), order=3) * env * 1.3
        out[c:c + d] += hiss * 0.9 + v
    out = filt(out, lo=200, hi=4500)
    out = out + 0.7 * reverb(np.stack([out, out]), 1.8)[0] * 1.6
    return out * np.sin(np.pi * t / t[-1]) ** 0.7


def creak(seed):
    r = np.random.default_rng(seed)
    n = N(r.uniform(0.9, 1.8)); t = T(n)
    f0 = r.uniform(80, 220)
    glide = f0 * (1 + 0.5 * np.sin(TAU * r.uniform(0.6, 1.4) * t) * 0.4 + 0.3 * t / t[-1] * (1 if r.random() < 0.5 else -1))
    saw = np.zeros(n); ph = np.cumsum(glide) / SR
    for k in range(1, 12):
        saw += np.sin(TAU * k * ph) / k
    stut = (np.sin(TAU * r.uniform(23, 41) * t) > -0.2) * (0.6 + 0.4 * noise(n))
    x = filt(saw * stut, lo=140, hi=2600, order=3) * np.sin(np.pi * t / t[-1]) ** 0.8
    return x * 0.9


def moan(seed):
    r = np.random.default_rng(seed)
    n = N(r.uniform(2.2, 3.6)); t = T(n)
    f0 = r.uniform(70, 130)
    f = f0 * (1.0 + 0.35 * (t / t[-1]) - 0.15 * np.sin(TAU * 0.7 * t)) * (1 + 0.012 * np.sin(TAU * 5.3 * t))
    ph = np.cumsum(f) / SR
    v = sum(np.sin(TAU * k * ph) / k ** 0.8 for k in range(1, 18))
    form = filt(v, lo=300, hi=900, order=2) * 1.2 + filt(v, lo=900, hi=2400, order=2) * 0.45                  # «о-а»: две форманты
    x = form * (1 + 0.3 * noise(n)) * np.sin(np.pi * t / t[-1]) ** 1.2
    return filt(x * 0.8 + 0.35 * reverb(np.stack([x, x]), 3.0)[0], lo=60, hi=1700, order=3)


def heartbeat():
    n = N(1.0); x = np.zeros(n)
    for at, a in ((0.0, 1.0), (0.2, 0.7)):
        i0 = N(at); d = N(0.25); tt = T(d)
        thump = np.sin(TAU * 52 * tt * (1 + 0.5 * np.exp(-tt / 0.05))) * np.exp(-tt / 0.08) * a
        x[i0:i0 + d] += thump[:max(0, n - i0)] if i0 + d > n else thump
    return np.tanh(2.2 * x)


def wet_hit(seed):
    r = np.random.default_rng(seed)
    n = N(0.28); t = T(n)
    slap = filt(noise(n), lo=300, hi=2500) * np.exp(-t / 0.03)
    body = np.sin(phase(sweep(r.uniform(140, 210), 55, n, 0.03), n)) * np.exp(-t / 0.07)
    squelch = filt(noise(n), lo=400, hi=1700) * np.exp(-t / 0.12) * (0.5 + 0.5 * np.sin(TAU * r.uniform(30, 60) * t))
    return np.tanh(1.8 * (slap * 0.8 + body * 1.0 + squelch * 0.7))


def gore_burst():
    n = N(0.7); t = T(n)
    a = filt(noise(n), lo=120, hi=2200) * np.exp(-t / 0.18)
    drops = np.zeros(n)
    for _ in range(14):
        i0 = int(R.uniform(0.04, 0.6) * n); d = N(0.03); tt = T(d)
        drops[i0:i0 + d] += (np.sin(TAU * R.uniform(500, 1400) * tt * (1 + 3 * np.exp(-tt / 0.006))) * np.exp(-tt / 0.01))[:n - i0] * R.uniform(0.2, 0.7)
    return np.tanh(1.6 * (a + 0.9 * np.sin(phase(sweep(120, 40, n, 0.08), n)) * np.exp(-t / 0.1) + drops))


def bone_crack():
    n = N(0.25); t = T(n)
    x = np.zeros(n)
    for at in (0.0, 0.035, 0.09):
        i0 = N(at); d = n - i0; tt = T(d)
        x[i0:] += (filt(noise(d), lo=900, hi=5500) * np.exp(-tt / 0.012) + np.sin(TAU * R.uniform(300, 900) * tt) * np.exp(-tt / 0.02) * 0.4) * R.uniform(0.6, 1.0)
    return np.tanh(1.5 * x)


if __name__ == "__main__":
    os.makedirs(G.OUT_SFX, exist_ok=True); os.makedirs(G.OUT_MUS, exist_ok=True)
    amb()
    sets = {}
    for i in range(4): sets["whisper" + ("" if i == 0 else "_%d" % (i + 1))] = whisper(70 + i)
    for i in range(3): sets["creak" + ("" if i == 0 else "_%d" % (i + 1))] = creak(80 + i)
    for i in range(3): sets["moan" + ("" if i == 0 else "_%d" % (i + 1))] = moan(90 + i)
    sets["heartbeat"] = heartbeat()
    for i in range(3): sets["wet_hit" + ("" if i == 0 else "_%d" % (i + 1))] = wet_hit(100 + i)
    sets["gore_burst"] = gore_burst()
    sets["gore_burst_2"] = gore_burst()
    sets["bone_crack"] = bone_crack()
    for k, v in sets.items():
        x = v * gate(len(v), len(v) / SR - 0.01, 0.01, 0.0005)
        save(f"{G.OUT_SFX}/{k}.wav", x, 0.85)
    print("horror audio:", len(sets) + 1)
