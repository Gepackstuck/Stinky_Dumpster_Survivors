#!/usr/bin/env python3
"""Смешные мерзкие звуки новой стилистики: пердёж (мокрый, длинный, писклявый), отрыжка, рвота, понос-хлюп, икота, булькающий стон алкаша,
звон бутылки, скользкий «уиии». Всё синтезом. PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_audio_gross.py -> assets/sfx/*.wav"""
import os
import numpy as np
import gen_audio as G
from gen_audio import SR, N, T, TAU, filt, noise, save, gate, sweep, phase, reverb

R = np.random.default_rng(404)


def fart(seed, long=False, squeak=False):
    r = np.random.default_rng(seed)
    dur = r.uniform(0.9, 1.6) if long else r.uniform(0.25, 0.6)
    n = N(dur); t = T(n)
    f0 = r.uniform(70, 160) * (2.2 if squeak else 1.0)
    f = f0 * (1 + 0.5 * np.exp(-t / 0.08)) * (1 + 0.06 * np.sin(TAU * r.uniform(15, 40) * t) + 0.25 * np.sin(TAU * r.uniform(3, 9) * t) * np.exp(-t / dur))
    ph = np.cumsum(f) / SR
    x = sum(np.sin(TAU * k * ph) / k ** 0.6 for k in range(1, 22))
    flutter = (np.sin(TAU * r.uniform(35, 70) * t) > -0.3) * (0.7 + 0.3 * noise(n))                   # дребезг
    x = filt(x * flutter, lo=60, hi=1800 if not squeak else 3200, order=2) + 0.25 * filt(noise(n), lo=300, hi=1500) * np.exp(-t / (dur * 0.5))
    return np.tanh(2.0 * x) * np.sin(np.pi * np.minimum(t / t[-1], 1.0)) ** 0.5 * (1.0 - 0.3 * t / t[-1])


def burp(seed):
    r = np.random.default_rng(seed)
    n = N(r.uniform(0.7, 1.3)); t = T(n)
    f0 = r.uniform(70, 110)
    f = f0 * (1.0 + 0.4 * np.sin(np.pi * t / t[-1])) * (1 + 0.1 * np.sin(TAU * 22 * t))
    ph = np.cumsum(f) / SR
    x = sum(np.sin(TAU * k * ph) * (1 + 1.6 * np.exp(-((f0 * k - 520) / 190) ** 2)) / k ** 0.8 for k in range(1, 26))
    x = filt(x, lo=50, hi=2600) * (1 + 0.5 * noise(n)) * np.sin(np.pi * t / t[-1]) ** 0.6
    return np.tanh(1.8 * x)


def puke(seed):
    r = np.random.default_rng(seed)
    n = N(r.uniform(1.3, 1.9)); t = T(n); out = np.zeros(n)
    for c, d in ((0.05, 0.3), (0.45, 0.28)):                                  # два позыва: «уээээ»
        i0 = N(c); m = N(d); tt = T(m)
        f = 130 * (1 - 0.25 * tt / d) * (1 + 0.1 * np.sin(TAU * 30 * tt)); ph = np.cumsum(f) / SR
        v = sum(np.sin(TAU * k * ph) / k ** 0.7 for k in range(1, 16))
        out[i0:i0 + m] += filt(v, lo=80, hi=1400) * np.sin(np.pi * tt / d) * 0.8
    i0 = N(0.85)
    m = n - i0; tt = T(m)                                                    # плюх и хлюпанье
    splat = filt(noise(m), lo=150, hi=1800) * np.exp(-tt / 0.18) + 0.8 * np.sin(phase(sweep(210, 60, m, 0.06), m)) * np.exp(-tt / 0.1)
    drip = np.zeros(m)
    for _ in range(9):
        j = int(r.uniform(0.1, 0.9) * m); d = N(0.04); q = T(d)
        drip[j:j + d] += (np.sin(TAU * r.uniform(300, 900) * q * (1 + 2 * np.exp(-q / 0.01))) * np.exp(-q / 0.014))[:m - j] * r.uniform(0.2, 0.6)
    out[i0:] += splat + drip
    return np.tanh(1.6 * out)


def diarrhea(seed):
    r = np.random.default_rng(seed)
    n = N(r.uniform(0.9, 1.4)); t = T(n); out = np.zeros(n)
    for k in range(int(r.integers(4, 8))):
        i0 = int(r.uniform(0, 0.8) * n); d = N(r.uniform(0.08, 0.18)); q = T(d)
        out[i0:i0 + d] += (filt(noise(d), lo=120, hi=1500) * np.exp(-q / 0.05) + np.sin(phase(sweep(r.uniform(120, 200), 50, d, 0.04), d)) * np.exp(-q / 0.06) * 0.8)[:n - i0]
    return np.tanh(1.7 * out * (1 - 0.3 * t / t[-1]))


def hiccup(seed):
    r = np.random.default_rng(seed)
    n = N(0.3); t = T(n)
    f = sweep(520, 230, n, 0.04) * (1 + 0.05 * np.sin(TAU * 40 * t))
    return np.tanh(1.5 * (np.sin(phase(f, n)) * np.exp(-t / 0.08) + 0.4 * filt(noise(n), lo=500, hi=2500) * np.exp(-t / 0.02)))


def drunk_moan(seed):
    r = np.random.default_rng(seed)
    n = N(r.uniform(1.4, 2.2)); t = T(n)
    f0 = r.uniform(90, 150)
    f = f0 * (1 + 0.45 * np.sin(TAU * r.uniform(0.7, 1.3) * t)) * (1 + 0.03 * np.sin(TAU * 6 * t))
    ph = np.cumsum(f) / SR
    v = sum(np.sin(TAU * k * ph) / k ** 0.8 for k in range(1, 20))
    x = filt(v, lo=300, hi=800, order=2) * 1.3 + filt(v, lo=800, hi=2200, order=2) * 0.4
    gurgle = (np.sin(TAU * 17 * t) > 0) * 0.5 + 0.5
    return np.tanh(x * gurgle * np.sin(np.pi * t / t[-1]) ** 0.8)


def slip():
    n = N(0.55); t = T(n)
    f = 1300 * np.exp(-t / 0.18) + 260
    sq = np.sin(phase(f, n)) * np.exp(-t / 0.3) * (0.6 + 0.4 * np.sin(TAU * 18 * t))
    thud = np.zeros(n); i0 = N(0.32); d = n - i0; q = T(d)
    thud[i0:] = np.sin(phase(sweep(150, 45, d, 0.04), d)) * np.exp(-q / 0.07) + filt(noise(d), hi=900) * np.exp(-q / 0.03)
    return np.tanh(sq * 0.7 + thud * 1.2)


def bottle_clink(seed):
    r = np.random.default_rng(seed)
    n = N(0.5); t = T(n)
    return sum(a * np.sin(TAU * r.uniform(0.97, 1.03) * f * t) * np.exp(-t / d) for f, a, d in ((2100, 1, 0.12), (3400, 0.6, 0.07), (5200, 0.35, 0.04), (900, 0.5, 0.18)))


if __name__ == "__main__":
    os.makedirs(G.OUT_SFX, exist_ok=True)
    S = {}
    for i in range(5): S["fart" + ("" if i == 0 else "_%d" % (i + 1))] = fart(10 + i, long=i in (1, 3), squeak=i == 4)
    for i in range(3): S["burp" + ("" if i == 0 else "_%d" % (i + 1))] = burp(20 + i)
    for i in range(3): S["puke" + ("" if i == 0 else "_%d" % (i + 1))] = puke(30 + i)
    for i in range(3): S["poop_splat" + ("" if i == 0 else "_%d" % (i + 1))] = diarrhea(40 + i)
    for i in range(3): S["hiccup" + ("" if i == 0 else "_%d" % (i + 1))] = hiccup(50 + i)
    for i in range(3): S["drunk_moan" + ("" if i == 0 else "_%d" % (i + 1))] = drunk_moan(60 + i)
    S["slip"] = slip()
    for i in range(2): S["bottle_clink" + ("" if i == 0 else "_%d" % (i + 1))] = bottle_clink(70 + i)
    for k, v in S.items():
        x = v * gate(len(v), len(v) / SR - 0.01, 0.01, 0.0005)
        save(f"{G.OUT_SFX}/{k}.wav", x, 0.85)
    print("gross audio:", len(S))
