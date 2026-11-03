#!/usr/bin/env python3
"""Звук v2 «Помойки»: всё синтезом, без чужих сэмплов. Тёплый грув под Brotato: электропиано, мягкий бас,
пэды, живые барабаны, реверб, эхо, сайдчейн. Звуки мягкие, с вариантами (имя.wav, имя_2.wav, имя_3.wav).
PYTHONPATH=tools tools/_venv/py/bin/python tools/gen_audio.py  -> assets/sfx/*.wav (моно), assets/music/*.wav (стерео лупы).
Треки: бой в духе кладбищенского хорала меню + ритм - battle_a (хорал на помойке), battle_b (похоронный бит),
battle_c (ночная служба, 6/8), boss (хозяин свалки: орган, хор, колокол); shop (злобный ярмарочный вальс), menu (кладбищенский хорал).
Оружие и враги: tools/gen_audio_fx.py (свои звуки у каждого)."""
import os, wave
import numpy as np

SR = 32000
OUT_SFX = "assets/sfx"; OUT_MUS = "assets/music"
R = np.random.default_rng(11)
TAU = 2 * np.pi
# баланс микса (подобран по спектру: низ не должен глушить клавиши и хэты)
BASS_G = 0.5; KICK_G = 0.65; KEYS_G = 1.7; LEAD_G = 1.5; HAT_G = 2.3


def N(sec):
    return max(int(round(sec * SR)), 1)


def T(n):
    return np.arange(n) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pow2(n):
    return 1 << int(np.ceil(np.log2(max(n, 2))))


def filt(x, lo=None, hi=None, order=2):
    """Фильтр через FFT (с запасом нулей, без заворота хвоста). lo - срез снизу, hi - сверху."""
    n = x.shape[-1]; m = pow2(2 * n)
    f = np.fft.rfftfreq(m, 1 / SR); H = np.ones_like(f)
    if hi: H *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    if lo: H *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(np.fft.rfft(x, m) * H, m)[..., :n]


def noise(n):
    return R.uniform(-1, 1, n)


def gate(n, dur, rel=0.05, att=0.003):
    """1 до dur, потом линейный спад за rel; мягкая атака."""
    e = np.ones(n); a = N(att); e[:a] = np.linspace(0, 1, a)
    s = min(N(dur), n); r = N(rel)
    e[s:] = 0.0
    k = min(r, n - s)
    if k > 0: e[s:s + k] = np.linspace(1, 0, k)
    return e


def sweep(f0, f1, n, tau):
    """Частота от f0 к f1 по экспоненте (tau - сек)."""
    return f1 + (f0 - f1) * np.exp(-T(n) / tau)


def phase(freq, n):
    return TAU * np.cumsum(np.broadcast_to(freq, (n,))) / SR


def plus(*xs):
    """Сумма звуков разной длины."""
    out = np.zeros(max(len(x) for x in xs))
    for x in xs: out[:len(x)] += x
    return out


# ---------------- инструменты ----------------
def rhodes(f, dur, vel=1.0):
    n = N(dur + 1.0); t = T(n)
    idx = (1.1 + vel * 1.6) * np.exp(-t / 0.35)
    car = np.sin(TAU * f * t + idx * np.sin(TAU * f * t))
    tine = 0.22 * vel * np.sin(TAU * f * 7.0 * t) * np.exp(-t / 0.04)
    trem = 1 + 0.05 * np.sin(TAU * 4.5 * t)
    return (car + tine) * np.exp(-t / 1.8) * gate(n, dur, 0.18) * trem * vel


def ebass(f, dur, vel=1.0, bright=1.0):
    n = N(dur + 0.08); t = T(n); ph = TAU * f * t
    x = 0.9 * np.sin(ph)
    for k in range(2, 10):
        if f * k > SR * 0.4: break
        x += (0.5 / k) * bright * np.sin(k * ph) * np.exp(-t * (5 + k * 4))
    return x * gate(n, dur, 0.04, 0.004) * (0.75 + 0.25 * np.exp(-t / 0.15)) * vel


def pluck(f, dur, vel=1.0, bright=1.0):
    n = N(max(dur, 0.25) + 0.5); t = T(n); ph = TAU * f * t
    x = np.zeros(n)
    for k in range(1, 11):
        if f * k > SR * 0.42: break
        x += k ** -1.3 * np.sin(k * ph) * np.exp(-t * (2.5 + k * 3.5 / bright))
    return x * np.exp(-t / 0.6) * gate(n, max(dur, 0.25) + 0.2, 0.2) * vel


def pad(f, dur, vel=1.0):
    n = N(dur + 0.8); t = T(n); x = np.zeros(n)
    for dt in (-0.006, 0.0, 0.0065):
        ph = TAU * f * (1 + dt) * t + R.uniform(0, TAU)
        for k in range(1, 8):
            if f * k > SR * 0.4: break
            x += k ** -1.6 * np.sin(k * ph)
    a = np.minimum(t / 0.35, 1.0) ** 2
    return x / 3 * a * gate(n, dur, 0.7, 0.001) * vel


def lead(f, dur, vel=1.0):
    n = N(dur + 0.12); t = T(n)
    vib = 1 + 0.004 * np.sin(TAU * 5.5 * t) * np.clip((t - 0.12) / 0.2, 0, 1)
    ph = phase(f * vib, n)
    x = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.22 * np.sin(3 * ph) + 0.08 * np.sin(5 * ph)
    return x * gate(n, dur, 0.1, 0.012) * (0.85 + 0.15 * np.exp(-t / 0.1)) * vel


def bell(f, dur=0.6, vel=1.0):
    n = N(dur + 0.4); t = T(n); x = np.zeros(n)
    for r, a, d in ((1, 1, 1.0), (2.0, 0.3, 0.5), (2.76, 0.25, 0.35), (5.4, 0.1, 0.12), (8.93, 0.04, 0.06)):
        if f * r < SR * 0.45: x += a * np.sin(TAU * f * r * t) * np.exp(-t / (d * dur))
    return x * gate(n, dur + 0.3, 0.1, 0.001) * vel


# ---------------- барабаны ----------------
def kick(vel=1.0):
    n = N(0.38); t = T(n)
    x = np.sin(phase(sweep(160, 46, n, 0.03), n)) * np.exp(-t / 0.17)
    x[:N(0.004)] += filt(noise(N(0.004)), lo=2500) * 0.25
    return np.tanh(1.6 * x) * vel


def snare(vel=1.0):
    n = N(0.25); t = T(n)
    tone = 0.55 * np.sin(TAU * 185 * t) * np.exp(-t / 0.05) + 0.25 * np.sin(TAU * 330 * t) * np.exp(-t / 0.03)
    nz = filt(noise(n), lo=1300, hi=8500) * np.exp(-t / 0.1) * 0.9
    return (tone + nz) * vel


def clap(vel=1.0):
    n = N(0.3); t = T(n); e = 0.6 * np.exp(-t / 0.09)
    for d in (0.0, 0.009, 0.019):
        e += np.where(t >= d, np.exp(-(t - d) / 0.005), 0)
    return filt(noise(n), lo=900, hi=4500) * e * 0.7 * vel


def hat(open_=False, vel=1.0):
    n = N(0.25 if open_ else 0.06); t = T(n)
    return filt(noise(n), lo=7000, hi=13000) * np.exp(-t / (0.12 if open_ else 0.02)) * vel * HAT_G


def shaker(vel=1.0):
    n = N(0.08); t = T(n)
    return filt(noise(n), lo=4500, hi=11000) * np.minimum(t / 0.012, 1) * np.exp(-t / 0.035) * vel * HAT_G


def rim(vel=1.0):
    n = N(0.08); t = T(n)
    return (np.sin(TAU * 1750 * t) * np.exp(-t / 0.01) + 0.6 * np.sin(TAU * 820 * t) * np.exp(-t / 0.02)) * vel


def crackle(n, density=7.0):
    x = filt(noise(n), lo=3000, hi=9000) * 0.012
    for p in R.integers(0, n - 200, int(density * n / SR)):
        x[p:p + 60] += filt(noise(60), lo=1500) * R.uniform(0.05, 0.25) * np.exp(-np.arange(60) / 12)
    return x


# ---------------- микшер и песня ----------------
class Song:
    def __init__(self, bpm, bars, swing=0.0, steps=16):
        """steps - шестнадцатых в такте: 16 = 4/4, 12 = 3/4 (вальс), 20 = 5/4."""
        self.sd = 60.0 / bpm / 4; self.bars = bars; self.swing = swing; self.steps = steps
        self.length = bars * steps * self.sd
        self.L = N(self.length); self.n = self.L + N(4.0)
        self.dry = np.zeros((2, self.n)); self.duck = np.zeros((2, self.n))
        self.rev = np.zeros((2, self.n)); self.dly = np.zeros((2, self.n)); self.kicks = []

    def t(self, bar, step):
        s = bar * self.steps + step + (self.swing if int(step) % 2 == 1 else 0.0)
        return s * self.sd + R.normal(0, 0.002)

    def add(self, x, t0, pan=0.0, gain=1.0, rev=0.15, dly=0.0, duck=False):
        s = max(int(t0 * SR), 0); e = min(s + len(x), self.n)
        if e <= s: return
        seg = x[:e - s] * gain
        th = (np.clip(pan, -1, 1) + 1) * np.pi / 4
        lr = (np.cos(th) * np.sqrt(2), np.sin(th) * np.sqrt(2))
        bus = self.duck if duck else self.dry
        for ch in (0, 1):
            bus[ch, s:e] += seg * lr[ch]
            if rev: self.rev[ch, s:e] += seg * lr[ch] * rev
            if dly: self.dly[ch, s:e] += seg * lr[ch] * dly

    def chord(self, t0, notes, dur, vel=1.0, inst=rhodes, gain=0.22, rev=0.25, spread=0.4, duck=False, dly=0.0):
        k = len(notes)
        for i, m in enumerate(notes):
            pan = -spread + 2 * spread * i / max(k - 1, 1)
            self.add(inst(midi(m), dur, vel * (1 + R.normal(0, 0.05))), t0 + i * 0.005, pan, gain * KEYS_G, rev, dly, duck)

    def drum(self, x, t0, gain=1.0, pan=0.0, rev=0.06, is_kick=False):
        self.add(x, t0, pan, gain * (KICK_G if is_kick else 1.0), rev)
        if is_kick: self.kicks.append(t0)

    def render(self, name, sc=0.45, rev_sec=2.2, rev_wet=1.0, dly_steps=3, dly_fb=0.38, rms=0.13, extra=None, wow=0.0):
        if sc > 0 and self.kicks:
            env = np.ones(self.n)
            for tk in self.kicks + [k + self.length for k in self.kicks if k < 1.0]:
                s = max(int(tk * SR), 0); e = min(s + N(0.35), self.n)
                if s >= self.n: continue
                env[s:e] = np.minimum(env[s:e], 1 - sc * np.exp(-T(e - s) / 0.1))
            self.duck *= env
        out = self.dry + self.duck
        if self.dly.any():
            d = N(dly_steps * self.sd); echo = np.zeros_like(self.dly)
            for i in range(1, 6):
                if d * i >= self.n: break
                sh = np.zeros_like(self.dly); sh[:, d * i:] = self.dly[:, :self.n - d * i] * dly_fb ** i
                echo += sh[::-1] if i % 2 else sh   # пинг-понг
            echo = filt(echo, lo=300, hi=4500)
            out += echo; self.rev += echo * 0.3
        out += reverb(self.rev, rev_sec) * rev_wet
        if extra is not None: out[:, :extra.shape[-1]] += extra[:, :self.n]
        tail = self.n - self.L
        out[:, :tail] += out[:, self.L:]   # хвосты из конца - в начало: луп без шва
        out = out[:, :self.L]
        f = np.fft.rfftfreq(self.L, 1 / SR)   # срез низа по кругу: луп остаётся бесшовным
        out = np.fft.irfft(np.fft.rfft(out, self.L) / np.sqrt(1 + (32 / np.maximum(f, 1e-3)) ** 4), self.L)
        if wow > 0:   # «плёнка плывёт»: высота гуляет, целое число качаний за луп - шов не рвётся
            L = self.L; k = max(1, round(self.length * 0.35)); n_ = np.arange(L)
            pos = (n_ + wow * SR * np.sin(TAU * k * n_ / L)) % L
            out = np.vstack([np.interp(pos, np.arange(L + 1), np.append(ch, ch[0])) for ch in out])
        out *= rms / (np.sqrt(np.mean(out ** 2)) + 1e-9)
        out = np.tanh(out * 1.3) / 1.3
        out *= min(1.0, 0.94 / np.max(np.abs(out)))
        save(f"{OUT_MUS}/{name}.wav", out, stereo=True)
        print(f"music {name}: {self.length:.1f}s")


def reverb(x, sec):
    n = x.shape[-1]; ni = N(sec); t = T(ni); out = np.zeros_like(x); m = pow2(n + ni)
    for ch in (0, 1):
        ir = R.standard_normal(ni) * np.exp(-t * 6.9 / sec)
        ir = filt(ir, lo=250, hi=4200); ir[:N(0.015)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        out[ch] = np.fft.irfft(np.fft.rfft(x[ch], m) * np.fft.rfft(ir, m), m)[:n]
    return out * 0.5


def save(path, x, vol=None, stereo=False):
    if vol is not None:
        x = x / (np.max(np.abs(x)) + 1e-9) * vol
    x = np.clip(x, -1, 1)
    data = (x.T if stereo else x)
    data = (data * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2 if stereo else 1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())


# ---------------- гадкие инструменты (помойка, кладбище) ----------------
def organ(f, dur, vel=1.0):
    n = N(dur + 0.15); t = T(n); x = np.zeros(n)
    for k, w in ((1, 1.0), (2, 0.7), (3, 0.45), (4, 0.3), (6, 0.18), (8, 0.12)):
        if f * k < SR * 0.42: x += w * np.sin(TAU * f * k * t + 0.4 * np.sin(TAU * 6.2 * t))   # «лесли»
    return x * gate(n, dur, 0.12, 0.02) * (0.9 + 0.1 * np.sin(TAU * 6.2 * t)) * vel


def musicbox(f, dur=0.8, vel=1.0):
    n = N(dur + 0.5); t = T(n); x = np.zeros(n)
    for r, a, d in ((1.0, 1.0, 1.1), (1.003, 0.6, 0.9), (4.0, 0.22, 0.12), (9.2, 0.07, 0.04)):
        if f * r < SR * 0.45: x += a * np.sin(TAU * f * r * t) * np.exp(-t / d)
    return x * gate(n, dur + 0.4, 0.1, 0.001) * vel


def detuned_lead(f, dur, vel=1.0):
    return plus(lead(f * 1.007, dur, vel * 0.6), lead(f * 0.993, dur, vel * 0.6))


def gritty_bass(f, dur, vel=1.0):
    return np.tanh(2.2 * ebass(f, dur, vel, 1.6)) * 0.7


def drip(vel=1.0):
    n = N(0.12); t = T(n)
    return np.sin(phase(sweep(500, 1500, n, 0.015), n)) * np.exp(-t / 0.03) * np.minimum(t / 0.002, 1) * vel


def squelch(vel=1.0):
    n = N(0.18); t = T(n)
    return (filt(noise(n), lo=200, hi=1500) * np.exp(-t / 0.05) + 0.6 * np.sin(phase(sweep(150, 60, n, 0.03), n)) * np.exp(-t / 0.06)) * vel


def clink(vel=1.0):
    n = N(0.15); t = T(n)
    return sum(a * np.sin(TAU * 2600 * r * t) * np.exp(-t / d) for r, a, d in ((1, 1, 0.05), (1.52, 0.6, 0.03), (2.75, 0.4, 0.02))) * vel


def wind(n, k_cycles=3):
    """Ветер над кладбищем: шум с медленными порывами (целое число порывов за луп - без шва)."""
    t = np.arange(n) / n
    gust = 0.55 + 0.45 * np.sin(TAU * k_cycles * t) * np.sin(TAU * (k_cycles + 2) * t + 1)
    return filt(noise(n), lo=150, hi=900) * gust * 0.05


def crow(vel=1.0):
    out = np.zeros(N(0.9))
    for d in (0.0, 0.38):
        n = N(0.26); t = T(n); f = sweep(620, 430, n, 0.15); ph = phase(f, n)
        x = sum(k ** -0.7 * np.sin(k * ph) * (2.0 if 1000 < 520 * k < 2200 else 1) for k in range(1, 12))
        x = filt(x + 0.4 * noise(n), lo=400, hi=3500) * np.sin(np.pi * t / t[-1]) ** 0.6
        s0 = N(d); out[s0:s0 + n] += x
    return out * vel


def flybuzz(n, f=115.0):
    t = T(n); ph = TAU * f * t + 3 * np.sin(TAU * 0.7 * t)
    x = sum(k ** -1.0 * np.sin(k * ph) for k in range(1, 16))
    return filt(x, lo=300, hi=2500) * (0.6 + 0.4 * np.sin(TAU * 0.25 * t)) * 0.03


# ---------------- треки ----------------
def bass_line(s, bar, root, pattern, gain=0.5, bright=1.0, duck=True, inst=None):
    for st, semi, ln, *v in pattern:
        x = (inst or (lambda f, d, vv: ebass(f, d, vv, bright)))(midi(root + semi), ln * s.sd * 0.92, v[0] if v else 1.0)
        s.add(x, s.t(bar, st), 0.0, gain * BASS_G, 0.02, 0, duck)


def melody(s, bar0, notes, inst=lead, gain=0.18, pan=0.15, rev=0.3, dly=0.35, oct_=0):
    for st, m, ln in notes:
        s.add(inst(midi(m + oct_), ln * s.sd * 0.95, 1.0), s.t(bar0, st), pan, gain * LEAD_G, rev, dly)


def four_floor(s, bar, kick_g=0.9, clap_g=0.5, hats="off", ghost=0.0, open_on=None, slimy=True):
    for st in (0, 4, 8, 12): s.drum(kick(), s.t(bar, st), kick_g, is_kick=True)
    for st in (4, 12):
        s.drum(clap(), s.t(bar, st), clap_g, 0.05, 0.12); s.drum(snare(0.6), s.t(bar, st), clap_g * 0.6)
        if slimy: s.drum(squelch(0.8), s.t(bar, st), clap_g * 0.5, -0.1, 0.1)   # хлюп в малом барабане
    for st in range(16):
        if hats == "off" and st % 4 == 2: s.drum(hat(vel=0.9), s.t(bar, st), 0.35, 0.25)
        elif hats == "16" and st % 2 == 0: s.drum(hat(vel=0.9 if st % 4 == 2 else 0.5), s.t(bar, st), 0.3, 0.25)
        if ghost and st % 2 == 1: s.drum(hat(vel=ghost), s.t(bar, st), 0.3, -0.25)
    if open_on is not None: s.drum(hat(True), s.t(bar, open_on), 0.25, 0.3, 0.1)


# ---------------- страшилка: хэллоуин на помойке ----------------
def theremin(f, dur, vel=1.0):
    n = N(dur + 0.25); t = T(n)
    glide = 1 - 0.06 * np.exp(-t / 0.07)
    vib = 1 + 0.018 * np.sin(TAU * 6.3 * t) * np.clip(t / 0.25, 0, 1)
    ph = phase(f * glide * vib, n)
    return (np.sin(ph) + 0.12 * np.sin(2 * ph)) * np.minimum(t / 0.06, 1) * gate(n, dur, 0.2, 0.001) * vel


def choir(f, dur, vel=1.0, vowel="o"):
    """Хор «у-у-у» / «а-а-а»: пилы через форманты, несколько голосов вразнобой."""
    n = N(dur + 0.9); t = T(n); x = np.zeros(n)
    fm = ((320, 1.0), (800, 0.5)) if vowel == "o" else ((700, 1.0), (1150, 0.6))
    for dt in (-0.008, 0.0, 0.007):
        ph = TAU * f * (1 + dt) * t + 0.02 * np.sin(TAU * 5.1 * t + dt * 900) * TAU + R.uniform(0, TAU)
        for k in range(1, 24):
            fk = f * k
            if fk > SR * 0.4: break
            amp = sum(a * np.exp(-((fk - c) / (c * 0.25)) ** 2) for c, a in fm) + 0.04 / k
            x += amp * np.sin(k * ph)
    return x / 3 * np.minimum(t / 0.5, 1) ** 2 * gate(n, dur, 0.8, 0.001) * vel


def harpsi(f, dur, vel=1.0):
    n = N(max(dur, 0.2) + 0.6); t = T(n); ph = TAU * f * t; x = np.zeros(n)
    for k in range(1, 16):
        if f * k > SR * 0.42: break
        x += (k ** -0.8) * np.sin(k * ph + 0.3 * k) * np.exp(-t * (3 + k * 1.2))
    return x * gate(n, max(dur, 0.2) + 0.3, 0.1, 0.001) * vel * 0.6


def tuba(f, dur, vel=1.0):
    n = N(dur + 0.1); t = T(n); ph = TAU * f * t; br = np.minimum(t / 0.06, 1)
    x = sum(k ** -1.0 * np.sin(k * ph) * np.exp(-k * (1.2 - 0.6 * br)) for k in range(1, 12))
    return np.tanh(1.5 * x) * gate(n, dur, 0.06, 0.015) * vel


def tbell(f, dur=2.5, vel=1.0):
    """Колокол (церковный/трубчатый): гудящая нижняя, малая терция - звучит тревожно."""
    n = N(dur); t = T(n); x = np.zeros(n)
    for r, a, d in ((0.5, 0.6, 1.0), (1.0, 1.0, 0.7), (1.19, 0.5, 0.5), (1.5, 0.35, 0.35), (2.0, 0.3, 0.25), (2.5, 0.2, 0.15), (3.0, 0.12, 0.1)):
        if f * r < SR * 0.45: x += a * np.sin(TAU * f * r * t + R.uniform(0, TAU)) * np.exp(-t / (d * dur))
    return x * np.minimum(t / 0.002, 1) * vel


def fart_bass(f, dur, vel=1.0):
    """Пердящий бас: жужжащая пила с дрожанием, мокрым низом и хлюпом на конце."""
    n = N(dur + 0.06); t = T(n)
    fl = f * (1 + 0.06 * np.sin(TAU * 17 * t) + 0.03 * np.sin(TAU * 7.3 * t))
    ph = phase(fl, n)
    x = sum(k ** -0.7 * np.sin(k * ph) for k in range(1, 18))
    x = filt(x, hi=900) * (0.75 + 0.25 * np.sin(TAU * 23 * t))
    return np.tanh(1.8 * x) * gate(n, dur, 0.05, 0.01) * vel * 0.8


def tom(f=110, vel=1.0):
    n = N(0.5); t = T(n)
    return (np.sin(phase(sweep(f * 1.6, f, n, 0.04), n)) * np.exp(-t / 0.18) + 0.2 * filt(noise(n), hi=2000) * np.exp(-t / 0.03)) * vel


def calliope(f, dur, vel=1.0):
    """Ярмарочная дудка: свистящая, чуть фальшивая."""
    n = N(dur + 0.08); t = T(n); ph = phase(f * (1.004 + 0.006 * np.sin(TAU * 5.5 * t)), n)
    x = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph) + 0.05 * filt(noise(n), lo=2000, hi=6000)
    return x * gate(n, dur, 0.05, 0.02) * vel


def accordion(f, dur, vel=1.0):
    n = N(dur + 0.08); t = T(n); x = np.zeros(n)
    for dt in (-0.004, 0.005):   # две язычковые - бьются друг об друга
        ph = TAU * f * (1 + dt) * t
        x += sum((0.8 if k % 2 else 0.5) / k * np.sin(k * ph) for k in range(1, 10))
    return x * 0.5 * gate(n, dur, 0.06, 0.02) * vel


def chains(vel=1.0):
    b = np.zeros(N(0.3))
    for p in np.sort(R.uniform(0, 0.2, 5)):
        n = N(0.06); tt = T(n); s0 = N(p)
        b[s0:s0 + n] += sum(np.sin(TAU * R.uniform(2500, 5000) * tt) * np.exp(-tt / 0.012) for _ in range(2)) * R.uniform(0.4, 1)
    return b * vel


def burp(vel=1.0):
    n = N(0.45); t = T(n); f = sweep(110, 75, n, 0.2) * (1 + 0.08 * np.sin(TAU * 26 * t)); ph = phase(f, n)
    x = sum(k ** -0.9 * np.sin(k * ph) * (1 + 1.5 * np.exp(-((110 * k - 500) / 180) ** 2)) for k in range(1, 20))
    return np.tanh(filt(x, hi=2500)) * gate(n, 0.38, 0.06, 0.02) * vel


def hymn_drums(s, bar, steps=16, kick_at=(0, 8), snare_at=(4, 12), hats=2, kick_g=0.8, snare_g=0.42):
    for st in kick_at: s.drum(kick(0.9), s.t(bar, st), kick_g, is_kick=True)
    for st in snare_at:
        s.drum(snare(0.9), s.t(bar, st), snare_g, 0, 0.25)
        s.drum(squelch(0.7), s.t(bar, st), snare_g * 0.5, 0.15, 0.2)
    for st in range(0, steps, hats): s.drum(hat(vel=0.55 if st % 4 == 0 else 0.3), s.t(bar, st), 0.2, 0.25, 0.1)


def battle_a():
    """Хорал на помойке: 96 bpm, D минор (Dm - Bb - Gm - A), как кладбище в меню, но с битом. Колокол, хор, орган, шкатулка."""
    s = Song(96, 16)
    prog = [(38, [57, 62, 65]), (34, [58, 62, 65]), (43, [55, 58, 62]), (45, [57, 61, 64])]
    box = [(0, 74, 2), (2, 77, 2), (4, 76, 4), (8, 74, 2), (10, 73, 2), (12, 69, 4), (16, 70, 4), (20, 69, 2), (22, 67, 2), (24, 69, 8)]
    for bar in range(16):
        root, ch = prog[bar % 4]; sec = bar // 8
        s.add(tbell(midi(50), 2.5, 0.8), s.t(bar, 0), -0.2, 0.11, 0.6)
        hymn_drums(s, bar, kick_at=(0, 6, 8) if sec else (0, 8))
        for st in range(0, 16, 2):   # бас пульсирует восьмыми, как сердце
            s.add(ebass(midi(root - 12 + (12 if st % 8 == 6 else 0)), 1.8 * s.sd, 0.9 if st % 4 == 0 else 0.7, 0.5), s.t(bar, st), 0, 0.42 * BASS_G, 0.03, 0, True)
        s.chord(s.t(bar, 0), [n + 12 for n in ch], 16 * s.sd, 0.6, choir, 0.07, 0.6, 0.6, True)
        for st in (0, 6, 10): s.chord(s.t(bar, st), ch, 3 * s.sd, 0.6, organ, 0.04, 0.4, 0.5, True)
        if sec == 1 and bar % 2 == 0:
            for st, m, ln in box: s.add(musicbox(midi(m) * 0.995, 0.7, 0.7), s.t(bar, st), 0.35, 0.13 * LEAD_G, 0.5, 0.3)
    s.add(crow(0.6), s.t(3, 9), 0.6, 0.12, 0.5)
    w = wind(s.n)
    s.render("battle_a", sc=0.3, rev_sec=3.0, rms=0.125, wow=0.002, extra=np.vstack([crackle(s.n, 4) + w, crackle(s.n, 4) + np.roll(w, 7000)]))


def battle_b():
    """Похоронный бит: 104 bpm, A минор (Am - F - C - E), тяжёлый полутемп, колокола перекликаются, органное арпеджио, хор «а-а»."""
    s = Song(104, 16)
    prog = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (40, [56, 59, 64])]
    for bar in range(16):
        root, ch = prog[bar % 4]; sec = bar // 8
        s.add(tbell(midi(57 if bar % 2 == 0 else 52), 2.2, 0.75), s.t(bar, 0), -0.3 if bar % 2 else 0.3, 0.1, 0.6)
        hymn_drums(s, bar, kick_at=(0, 3, 10), snare_at=(8,), kick_g=0.85, snare_g=0.5)
        if bar % 4 == 3:
            for k, st in enumerate((12, 13, 14, 15)): s.drum(tom(150 - 22 * k), s.t(bar, st), 0.32, -0.4 + 0.27 * k, 0.2)
        s.add(fart_bass(midi(root - 12), 6 * s.sd, 0.7), s.t(bar, 0), 0, 0.35, 0.05, 0, True)
        s.add(ebass(midi(root - 12), 5 * s.sd, 0.8, 0.4), s.t(bar, 10), 0, 0.4 * BASS_G, 0.03, 0, True)
        arp = [ch[0], ch[1], ch[2], ch[1] + 12 if len(ch) > 2 else ch[0] + 12]
        for st in range(0, 16, 2): s.add(organ(midi(arp[(st // 2) % 4] + 12), 1.8 * s.sd, 0.5), s.t(bar, st), 0.3 if st % 4 else -0.3, 0.045, 0.4, 0.15)
        if bar % 2 == 0: s.chord(s.t(bar, 0), ch, 32 * s.sd, 0.7, lambda f, d, v: choir(f, d, v, "a"), 0.07, 0.6, 0.6, True)
        if sec == 1 and bar % 4 in (0, 2):
            for st, m in ((0, 76), (4, 77), (8, 76), (12, 72)): s.add(tbell(midi(m + 12), 1.2, 0.4), s.t(bar, st), 0.4, 0.05, 0.5, 0.2)
    s.render("battle_b", sc=0.35, rev_sec=3.0, rms=0.13, wow=0.0015, extra=np.vstack([wind(s.n) * 0.8] * 2))


def battle_c():
    """Ночная служба: 6/8 (12 шестнадцатых), 100 bpm, G минор (Gm - Eb - Cm - D). Качающийся бит, хор, орган, шкатулка, капли."""
    s = Song(100, 24, steps=12)
    prog = [(43, [55, 58, 62]), (39, [55, 58, 63]), (36, [55, 60, 63]), (38, [54, 57, 62])]
    box = [(0, 74, 3), (3, 75, 3), (6, 74, 2), (8, 70, 4), (12, 72, 3), (15, 70, 3), (18, 69, 6)]
    for bar in range(24):
        root, ch = prog[bar % 4]; sec = bar // 8
        if bar % 2 == 0: s.add(tbell(midi(55), 2.4, 0.7), s.t(bar, 0), 0.2, 0.1, 0.6)
        hymn_drums(s, bar, steps=12, kick_at=(0, 8) if sec else (0,), snare_at=(6,), hats=2)
        s.add(ebass(midi(root - 12), 5 * s.sd, 0.9, 0.4), s.t(bar, 0), 0, 0.45 * BASS_G, 0.03, 0, True)
        s.add(ebass(midi(root - 12 + 7), 3 * s.sd, 0.7, 0.4), s.t(bar, 8), 0, 0.4 * BASS_G, 0.03, 0, True)
        s.chord(s.t(bar, 0), [n + 12 for n in ch], 12 * s.sd, 0.6, choir, 0.07, 0.6, 0.6, True)
        for st in (0, 4, 8): s.chord(s.t(bar, st), ch, 2 * s.sd, 0.5, organ, 0.035, 0.4, 0.5, True)
        if bar % 3 == 1: s.drum(drip(0.7), s.t(bar, 9), 0.11, R.uniform(-0.6, 0.6), 0.5)
        if sec >= 1 and bar % 2 == 0:
            for st, m, ln in box: s.add(musicbox(midi(m) * 0.995, 0.7, 0.7), s.t(bar, st), -0.3 if sec == 1 else 0.3, 0.13 * LEAD_G, 0.5, 0.3)
    s.render("battle_c", sc=0.3, rev_sec=3.2, rms=0.12, wow=0.003, extra=np.vstack([crackle(s.n, 4)] * 2))


def boss():
    """Хозяин свалки: 120 bpm, D минор. Органное остинато восьмыми, хор-удары, большой колокол, двойная бочка, томы."""
    s = Song(120, 16)
    prog = [(38, [57, 62, 65]), (34, [58, 62, 65]), (36, [55, 60, 64]), (45, [57, 61, 64])]
    ost = [62, 65, 69, 65, 62, 65, 70, 69]
    for bar in range(16):
        root, ch = prog[bar % 4]; sec = bar // 8
        s.add(tbell(midi(38), 3.0, 1.0), s.t(bar, 0), 0, 0.13, 0.6)
        hymn_drums(s, bar, kick_at=(0, 2, 8, 10) if sec else (0, 8, 10), snare_at=(4, 12), kick_g=0.9, snare_g=0.48)
        if bar % 2 == 1:
            for k, st in enumerate((12, 13, 14, 15)): s.drum(tom(140 - 20 * k), s.t(bar, st), 0.35, -0.4 + 0.27 * k, 0.2)
        for st in range(0, 16, 2):
            s.add(gritty_bass(midi(root - 12), 1.7 * s.sd, 0.9 if st % 4 == 0 else 0.7), s.t(bar, st), 0, 0.4 * BASS_G, 0.02, 0, True)
            s.add(organ(midi(ost[st // 2] + (root - 38 if root < 44 else root - 45)), 1.8 * s.sd, 0.6), s.t(bar, st), 0.25 if st % 4 else -0.25, 0.05, 0.3)
        for st in (0, 6): s.chord(s.t(bar, st), [n + 12 for n in ch], 4 * s.sd, 1.0, lambda f, d, v: choir(f, d, v, "a"), 0.09, 0.5, 0.6)
    s.render("boss", sc=0.4, rev_sec=2.8, rms=0.14, wow=0.001)


def battle_d():
    """Псалом мусорщика: 110 bpm, F минор (Fm - Db - Bbm - C), шаффл-хэты, высокие колокола, органные удары на слабую долю, хор."""
    s = Song(110, 16, swing=0.25)
    prog = [(41, [56, 60, 65]), (37, [56, 61, 65]), (46, [58, 61, 65]), (48, [55, 60, 64])]
    bells = [(0, 80), (4, 77), (8, 75), (12, 72)]
    for bar in range(16):
        root, ch = prog[bar % 4]; sec = bar // 8
        hymn_drums(s, bar, kick_at=(0, 7, 10), snare_at=(4, 12))
        s.add(ebass(midi(root - 12), 3 * s.sd, 0.9, 0.6), s.t(bar, 0), 0, 0.45 * BASS_G, 0.03, 0, True)
        s.add(ebass(midi(root - 12 + 7), 2 * s.sd, 0.7, 0.6), s.t(bar, 7), 0, 0.4 * BASS_G, 0.03, 0, True)
        s.add(ebass(midi(root - 12 + 12), 2 * s.sd, 0.7, 0.6), s.t(bar, 10), 0, 0.4 * BASS_G, 0.03, 0, True)
        for st in (2, 6, 10, 14): s.chord(s.t(bar, st), ch, 1.5 * s.sd, 0.6, organ, 0.04, 0.35, 0.5, True)
        if bar % 2 == 0: s.chord(s.t(bar, 0), [n + 12 for n in ch], 32 * s.sd, 0.6, choir, 0.065, 0.6, 0.6, True)
        if sec == 1:
            for st, m in bells: s.add(tbell(midi(m + (root - 41) % 12 * 0), 1.0, 0.45), s.t(bar, st), 0.35 if st % 8 else -0.35, 0.06, 0.5, 0.2)
    s.render("battle_d", sc=0.3, rev_sec=2.8, rms=0.125, wow=0.002, extra=np.vstack([crackle(s.n, 3)] * 2))


def battle_e():
    """Чёрная месса: 128 bpm, E фригийский (Em - F - Em - D), гонящий бас восьмыми, хор «а», колокол раз в два такта, томы, шкатулка."""
    s = Song(128, 16)
    prog = [(40, [52, 55, 59]), (41, [53, 57, 60]), (40, [52, 55, 59]), (38, [54, 57, 62])]
    box = [(0, 76, 2), (2, 77, 2), (4, 79, 2), (6, 77, 2), (8, 76, 4), (12, 74, 4), (16, 76, 2), (18, 77, 2), (20, 81, 4), (24, 79, 8)]
    for bar in range(16):
        root, ch = prog[bar % 4]; sec = bar // 8
        if bar % 2 == 0: s.add(tbell(midi(40), 3.0, 1.0), s.t(bar, 0), 0, 0.12, 0.6)
        hymn_drums(s, bar, kick_at=(0, 4, 8, 12), snare_at=(4, 12), kick_g=0.85)
        if bar % 4 == 3:
            for k, st in enumerate((10, 12, 14)): s.drum(tom(150 - 25 * k), s.t(bar, st), 0.33, -0.3 + 0.3 * k, 0.2)
        for st in range(0, 16, 2):
            s.add(gritty_bass(midi(root - 12 + (12 if st % 4 == 2 else 0)), 1.7 * s.sd, 0.8), s.t(bar, st), 0, 0.38 * BASS_G, 0.02, 0, True)
        s.chord(s.t(bar, 0), [n + 12 for n in ch], 16 * s.sd, 0.8, lambda f, d, v: choir(f, d, v, "a"), 0.08, 0.55, 0.6, True)
        if sec == 1 and bar % 2 == 0:
            for st, m, ln in box: s.add(musicbox(midi(m) * 0.995, 0.6, 0.7), s.t(bar, st), 0.3, 0.12 * LEAD_G, 0.5, 0.3)
    s.render("battle_e", sc=0.4, rev_sec=2.6, rms=0.135, wow=0.0015)


def shop_b():
    """Ларёк-шкатулка: 3/4, 132 bpm, D минор. Заводная шкатулка, орган «умпа-па», колокольчик, скрип."""
    s = Song(132, 16, steps=12)
    prog = [(38, [57, 62, 65]), (45, [57, 61, 64]), (38, [57, 62, 65]), (43, [55, 58, 62])]
    mel = [(0, 74, 4), (4, 77, 2), (6, 76, 2), (8, 74, 4), (12, 73, 6), (18, 69, 6), (24, 70, 4), (28, 74, 2), (30, 73, 2), (32, 74, 4), (36, 69, 6), (42, 62, 6)]
    for bar in range(16):
        root, ch = prog[bar % 4]
        s.add(tuba(midi(root - 12), 3 * s.sd, 0.8), s.t(bar, 0), 0, 0.28, 0.1)
        s.drum(kick(0.6), s.t(bar, 0), 0.5, is_kick=True)
        for st in (4, 8): s.chord(s.t(bar, st), ch, 2.5 * s.sd, 0.55, organ, 0.04, 0.35, 0.5)
        if bar % 4 == 0:
            for st, m, ln in mel: s.add(musicbox(midi(m + 12) * 0.993, 0.6, 0.75), s.t(bar, st), -0.2, 0.13 * LEAD_G, 0.45, 0.25)
        if bar % 4 == 2: s.add(tbell(midi(74), 1.2, 0.4), s.t(bar, 6), 0.4, 0.05, 0.5)
    s.render("shop_b", sc=0.0, rev_sec=2.6, rms=0.11, wow=0.004, extra=np.vstack([crackle(s.n, 5)] * 2))


def shop_c():
    """Ларёк в склепе: 80 bpm, C минор. Тихий хор, редкий колокол, щелчки рима, капли, шкатулка вразвалку."""
    s = Song(80, 12, swing=0.3)
    prog = [(36, [55, 60, 63]), (32, [56, 60, 63]), (34, [55, 58, 62]), (31, [55, 59, 62])]
    for bar in range(12):
        root, ch = prog[bar % 4]
        s.drum(kick(0.6), s.t(bar, 0), 0.5, is_kick=True); s.drum(kick(0.4), s.t(bar, 10), 0.45, is_kick=True)
        for st in (4, 12): s.drum(rim(0.6), s.t(bar, st), 0.14, 0.3, 0.2)
        for st in range(0, 16, 4): s.drum(hat(vel=0.4), s.t(bar, st + 2), 0.15, 0.25)
        s.add(ebass(midi(root - 12), 12 * s.sd, 0.8, 0.3), s.t(bar, 0), 0, 0.4 * BASS_G, 0.03)
        s.chord(s.t(bar, 0), [n + 12 for n in ch], 16 * s.sd, 0.5, choir, 0.06, 0.6, 0.6)
        for i, st in enumerate((0, 6, 10)): s.add(musicbox(midi(ch[(i + bar) % 3] + 12) * 0.995, 0.7, 0.5), s.t(bar, st), 0.35 if i % 2 else -0.35, 0.11, 0.5, 0.3)
        if bar % 3 == 0: s.add(tbell(midi(48), 2.2, 0.6), s.t(bar, 8), -0.3, 0.08, 0.6)
        if bar % 2 == 1: s.drum(drip(0.7), s.t(bar, 13), 0.1, R.uniform(-0.6, 0.6), 0.5)
    s.render("shop_c", sc=0.0, rev_sec=3.0, rms=0.1, wow=0.003, extra=np.vstack([crackle(s.n, 4)] * 2))


def shop():
    """Злобный ларёк: зловещий ярмарочный вальс 3/4, 160 bpm, A минор. Туба «умпа», расстроенный аккордеон, дудка, хрипы."""
    s = Song(160, 24, steps=12)
    prog = [(45, [57, 60, 64]), (40, [56, 59, 62, 64]), (45, [57, 60, 64]), (38, [57, 62, 65]),
            (45, [57, 60, 64]), (41, [57, 60, 65]), (40, [56, 59, 62, 64]), (45, [57, 60, 64])]
    mel = [(0, 76, 4), (4, 75, 2), (6, 76, 2), (8, 80, 4), (12, 81, 6), (18, 77, 2), (20, 76, 4),
           (24, 75, 4), (28, 76, 2), (30, 72, 2), (32, 71, 4), (36, 68, 6), (42, 69, 6)]
    for bar in range(24):
        root, ch = prog[bar % 8]; sec = bar // 8
        s.add(tuba(midi(root - 12), 3 * s.sd, 1.0), s.t(bar, 0), 0, 0.35, 0.1)
        s.drum(kick(0.7), s.t(bar, 0), 0.6, is_kick=True)
        for st in (4, 8):
            s.chord(s.t(bar, st), ch, 2.5 * s.sd, 0.7, accordion, 0.06, 0.3, 0.5)
            s.drum(rim(0.5), s.t(bar, st), 0.1, 0.3, 0.1)
        if bar % 4 == 3: s.add(burp(0.6), s.t(bar, 8), 0.5, 0.08, 0.3)
        if sec >= 1 and bar % 4 == 0: melody(s, bar, mel, calliope, 0.12, -0.2, 0.35, 0.2)
        if sec == 2 and bar % 4 == 0: melody(s, bar, mel, theremin, 0.05, 0.3, 0.5, 0.3, -12)
    s.render("shop", sc=0.0, rms=0.115, wow=0.0035, extra=np.vstack([crackle(s.n, 4)] * 2))


def menu():
    """Кладбище: погребальный хорал, 58 bpm, D минор. Колокол, хор, орган, сердцебиение томом, ветер, ворона, шкатулка."""
    s = Song(58, 12)
    prog = [(38, [57, 62, 65]), (34, [58, 62, 65]), (43, [55, 58, 62]), (45, [57, 61, 64])]   # Dm - Bb - Gm - A
    box = [(0, 74, 4), (4, 73, 4), (8, 74, 2), (10, 77, 2), (12, 76, 8), (24, 70, 4), (28, 69, 4)]
    for bar in range(12):
        root, ch = prog[bar % 4]
        s.add(tbell(midi(50), 3.0, 0.9), s.t(bar, 0), -0.2, 0.15, 0.6)   # колокол бьёт раз в такт
        for st in (0, 2): s.drum(tom(70, 0.8 if st == 0 else 0.5), s.t(bar, 8 + st), 0.4, 0, 0.3)   # тук-тук сердца
        s.chord(s.t(bar, 0), [n + 12 for n in ch], 16 * s.sd, 0.6, choir, 0.08, 0.7, 0.6)
        s.chord(s.t(bar, 0), ch, 15 * s.sd, 0.45, organ, 0.04, 0.6, 0.5)
        s.add(ebass(midi(root - 12), 14 * s.sd, 0.8, 0.3), s.t(bar, 0), 0, 0.4, 0.05)
        if bar in (4, 8):
            for st, m, ln in box: s.add(musicbox(midi(m) * 0.995, 0.9, 0.6), s.t(bar, st), 0.35, 0.12 * LEAD_G, 0.6, 0.35)
    s.add(crow(), s.t(2, 6), -0.6, 0.2, 0.5); s.add(crow(0.7), s.t(9, 3), 0.6, 0.15, 0.6)
    w = wind(s.n)
    s.render("menu", sc=0.0, rev_sec=3.6, rms=0.1, wow=0.003, extra=np.vstack([crackle(s.n, 5) + w * 1.5, crackle(s.n, 5) + np.roll(w, 9000) * 1.5]))


# ---------------- звуки ----------------
def room(x, sec=0.6, wet=0.25):
    y = reverb(np.vstack([x, x]), sec)[0]
    return x + y * wet


# ---------------- звуки в тоне меню: ре минор, колокол, шкатулка, хор, орган, эхо склепа ----------------
DM = [62, 65, 69, 74, 77, 81, 86]   # ре минор: D F A D F A D
FREQUENT = ("shoot", "hit", "enemy_death", "swing", "pickup", "ui_move", "w_", "e_", "roulette_tick")


def graveyard(x, name, dark=5200.0):
    """Общая обработка всех звуков под меню: темнее (срез верха) и с эхом склепа. Частым - эха меньше, чтобы не мылило."""
    frequent = any(name.startswith(f) for f in FREQUENT)
    wet = 0.07 if frequent else 0.18
    x = filt(np.concatenate([x, np.zeros(N(0.05 if frequent else 0.35))]), hi=dark)
    return room(x, 0.6 if frequent else 1.1, wet)


def stack(parts, length):
    """Собрать звук из кусков (время, массив)."""
    out = np.zeros(N(length))
    for t0, x in parts:
        s0 = N(t0); e = min(s0 + len(x), len(out)); out[s0:e] += x[:e - s0]
    return out


def hymn_sfx():
    H = {}
    H["pickup"] = musicbox(midi(86), 0.12, 0.8)[:N(0.3)]                                   # шкатулка, D6 (в игре идёт вверх по ре-минорной пентатонике)
    H["level_up"] = stack([(i * 0.09, plus(0.5 * tbell(midi(m), 1.0, 0.8), 0.4 * musicbox(midi(m + 12), 0.4, 0.7))) for i, m in enumerate((62, 65, 69, 74))]
                          + [(0.3, 0.5 * choir(midi(62), 0.7, 0.8) + 0.0)], 1.6)               # колокола вверх по Dm и вздох хора
    H["combo"] = stack([(i * 0.06, musicbox(midi(m), 0.3, 0.8)) for i, m in enumerate((74, 77, 81, 86, 89))], 0.9)
    H["buy"] = stack([(0, tbell(midi(69), 0.6, 0.8)), (0.07, tbell(midi(74), 0.7, 0.7)), (0.0, filt(noise(N(0.08)), lo=4000, hi=7000) * np.exp(-T(N(0.08)) / 0.02) * 0.2)], 0.9)
    H["ui_select"] = stack([(0, tbell(midi(57), 0.3, 0.7)), (0.05, tbell(midi(62), 0.4, 0.7))], 0.5)
    H["warn"] = stack([(0, tbell(midi(69), 0.25, 0.8)), (0.11, tbell(midi(68), 0.3, 0.8))], 0.5)      # тревожная полутоновая пара
    H["wave_horn"] = stack([(0, tbell(midi(50), 1.6, 1.0)), (0, 1.2 * kick()), (0.05, 0.5 * choir(midi(62), 0.6, 0.9, "a")), (0.05, 0.4 * choir(midi(69), 0.6, 0.9, "a"))], 1.8)
    H["win"] = stack([(0, 0.6 * choir(midi(m), 1.6, 0.9, "a")) for m in (62, 66, 69, 74)] + [(i * 0.2, tbell(midi(m), 1.5, 0.7)) for i, m in enumerate((74, 78, 81, 86))], 2.6)   # ре мажор - светлый конец
    H["death"] = stack([(0, tbell(midi(38), 2.5, 1.0))] + [(0.15 + i * 0.4, 0.5 * choir(midi(m), 0.45, 0.8)) for i, m in enumerate((69, 68, 67, 62))], 2.6)   # похоронный колокол и хор вниз
    H["roulette_tick"] = (np.sin(TAU * 900 * T(N(0.04))) * np.exp(-T(N(0.04)) / 0.006) + 0.5 * np.sin(TAU * 450 * T(N(0.04))) * np.exp(-T(N(0.04)) / 0.012))
    H["roulette_win"] = stack([(i * 0.09, tbell(midi(m), 0.8 if i < 5 else 1.4, 0.7)) for i, m in enumerate(DM[:6])], 1.8)
    H["streak_break"] = stack([(0, tbell(midi(65), 0.4, 0.8)), (0.1, tbell(midi(61), 0.6, 0.8))], 0.8)   # минус серия: колокол съезжает вниз
    H["level_up"] = H["level_up"] / (np.max(np.abs(H["level_up"])) + 1e-9)
    coin = lambda: filt(noise(N(0.08)), lo=4000, hi=7000) * np.exp(-T(N(0.08)) / 0.02) * 0.2
    H["buy_2"] = stack([(0, tbell(midi(62), 0.5, 0.8)), (0.06, tbell(midi(69), 0.6, 0.7)), (0.12, musicbox(midi(86), 0.3, 0.6)), (0, coin())], 0.9)
    H["buy_3"] = stack([(0, 0.6 * choir(midi(74), 0.35, 0.9, "a")), (0, tbell(midi(77), 0.6, 0.6)), (0.04, coin())], 0.9)       # «а-а» хора и колокол
    H["buy_4"] = stack([(i * 0.05, musicbox(midi(m), 0.25, 0.7)) for i, m in enumerate((74, 77, 81))] + [(0, coin())], 0.8)     # шкатулка вверх
    H["buy_5"] = stack([(0, squelch(0.9) * 0.6), (0.05, tbell(midi(65), 0.5, 0.7)), (0.1, tbell(midi(74), 0.6, 0.7)), (0.02, coin())], 0.9)   # хлюп в кассу и звон
    H["buy_6"] = stack([(0, organ(midi(62), 0.18, 0.8) * 0.5), (0.0, organ(midi(69), 0.18, 0.7) * 0.4), (0.12, tbell(midi(81), 0.6, 0.6)), (0.1, coin())], 0.9)   # органный аккорд
    return H


def sfx():
    S = {}
    for i, f0 in enumerate((820, 920, 1020)):   # выстрел: мягкий «пиу-ток»
        n = N(0.1); t = T(n)
        S[f"shoot{'' if i == 0 else f'_{i + 1}'}"] = np.sin(phase(sweep(f0, f0 * 0.5, n, 0.025), n)) * np.exp(-t / 0.03) + 0.2 * filt(noise(n), lo=2000, hi=7000) * np.exp(-t / 0.006)
    for i, (a, b) in enumerate(((500, 2600), (700, 3200))):   # взмах: шорох воздуха
        n = N(0.17); t = T(n); x = noise(n); y = np.zeros(n); acc = 0.0
        fc = a + (b - a) * np.sin(np.pi * t / t[-1]) ** 2; k = 1 - np.exp(-TAU * fc / SR)
        for j in range(n): acc += k[j] * (x[j] - acc); y[j] = acc
        S[f"swing{'' if i == 0 else '_2'}"] = filt(y, lo=300) * np.sin(np.pi * t / t[-1]) ** 1.5
    for i, f0 in enumerate((210, 240, 185)):   # попадание: сочный «тук»
        n = N(0.08); t = T(n)
        S[f"hit{'' if i == 0 else f'_{i + 1}'}"] = np.tanh(2 * (np.sin(phase(sweep(f0, f0 * 0.5, n, 0.02), n)) * np.exp(-t / 0.03) + 0.4 * filt(noise(n), hi=3000) * np.exp(-t / 0.012)))
    n = N(0.18); t = T(n)
    S["hit_crit"] = np.tanh(2 * np.sin(phase(sweep(260, 120, n, 0.02), n)) * np.exp(-t / 0.035)) + 0.35 * bell(1568, 0.12)[:n]
    for i, (f0, f1) in enumerate(((170, 560), (150, 480), (200, 640))):   # смерть врага: «чпок» + хлюп
        n = N(0.24); t = T(n)
        pop = np.sin(phase(f1 + (f0 - f1) * np.exp(-t / 0.018), n)) * np.exp(-t / 0.045)
        squish = filt(noise(n), lo=200, hi=1600) * np.exp(-t / 0.07) * np.clip((t - 0.02) / 0.01, 0, 1)
        thud = np.sin(TAU * 85 * t) * np.exp(-t / 0.05)
        S[f"enemy_death{'' if i == 0 else f'_{i + 1}'}"] = np.tanh(1.5 * (0.8 * pop + 0.5 * squish + 0.5 * thud))
    for i, (f0, f1) in enumerate(((290, 170), (250, 150))):   # герою больно: «уф»
        n = N(0.2); t = T(n); f = sweep(f0, f1, n, 0.08) * (1 + 0.02 * np.sin(TAU * 18 * t)); ph = phase(f, n)
        x = sum(k ** -1.2 * np.sin(k * ph) * (1.6 if 500 < f0 * k < 1100 else 1.0) for k in range(1, 8))
        S[f"player_hurt{'' if i == 0 else '_2'}"] = x * gate(n, 0.15, 0.05, 0.005) + 0.6 * np.sin(TAU * 70 * t) * np.exp(-t / 0.05)
    n = N(0.14); t = T(n)
    S["pickup"] = (np.sin(TAU * 1046 * t) + 0.3 * np.sin(TAU * 2093 * t) * np.exp(-t / 0.03)) * np.exp(-t / 0.06) * np.minimum(t / 0.002, 1)
    lv = np.zeros(N(1.3))   # новый уровень: арпеджио электропиано + колокольчик
    for i, m in enumerate((72, 76, 79, 84, 88)):
        x = plus(0.6 * rhodes(midi(m), 0.5, 0.9), 0.4 * bell(midi(m + 12), 0.4)); s0 = N(i * 0.07); lv[s0:s0 + len(x)] += x[:len(lv) - s0]
    S["level_up"] = room(lv, 1.0, 0.35)
    n = N(0.18); t = T(n)
    S["dash"] = filt(noise(n), lo=1500, hi=6000) * np.sin(np.pi * t / t[-1]) ** 2 + 0.3 * np.sin(phase(np.linspace(300, 900, n), n)) * np.exp(-t / 0.06)
    n = N(0.8); t = T(n)   # взрыв: глубокий бум без треска
    boom = filt(noise(n), hi=700) * np.exp(-t / 0.22) + 0.9 * np.sin(phase(sweep(90, 34, n, 0.12), n)) * np.exp(-t / 0.3)
    S["explosion"] = room(np.tanh(1.8 * (boom + 0.3 * filt(noise(n), lo=2500) * np.exp(-t / 0.03))), 0.8, 0.2)
    w = np.zeros(N(0.35))
    for d in (0.0, 0.1): x = bell(880, 0.15); s0 = N(d); w[s0:s0 + len(x)] += x[:len(w) - s0]
    S["warn"] = w
    n = N(1.1); t = T(n)   # рёв босса: низкий рык с формантой
    f = sweep(78, 55, n, 0.4) * (1 + 0.03 * np.sin(TAU * 7 * t)); ph = phase(f, n)
    growl = sum(k ** -1.0 * np.sin(k * ph) * (2.2 if 400 < 70 * k < 1000 else 1.0) for k in range(1, 22))
    grit = filt(noise(n), hi=1200) * (0.6 + 0.4 * np.sin(TAU * 30 * t))
    S["boss_roar"] = room(np.tanh(1.5 * (growl * 0.25 + 0.4 * grit)) * gate(n, 0.85, 0.25, 0.08), 1.2, 0.3)
    n = N(0.7); t = T(n); hn = np.zeros(n)   # начало волны: тёплый «брасс»-аккорд
    for m in (62, 66, 69, 74):
        ph = TAU * midi(m) * t; br = np.minimum(t / 0.08, 1)
        hn += sum(k ** -1.0 * np.sin(k * ph) * np.exp(-k * (1.6 - br) * 0.6) for k in range(1, 10))
    hn = hn * gate(n, 0.45, 0.2, 0.02); kk = kick(); hn[:len(kk)] += 1.5 * kk
    S["wave_horn"] = room(hn, 1.0, 0.3)
    bu = np.zeros(N(0.45))
    for d, f in ((0, 1568), (0.06, 2093)): x = bell(f, 0.3); s0 = N(d); bu[s0:s0 + len(x)] += x[:len(bu) - s0]
    n = N(0.12); bu[:n] += filt(noise(n), lo=5000) * np.exp(-T(n) / 0.03) * 0.3
    S["buy"] = bu
    n = N(0.05); t = T(n)   # переключение пунктов: низкий мягкий «ток» (было 1400 Гц - пищало)
    S["ui_move"] = np.sin(phase(sweep(560, 420, n, 0.02), n)) * np.exp(-t / 0.018) + 0.25 * np.sin(TAU * 1100 * t) * np.exp(-t / 0.004)
    us = np.zeros(N(0.25))
    for d, f in ((0, 523), (0.05, 784)): x = bell(f, 0.12); s0 = N(d); us[s0:s0 + len(x)] += x[:len(us) - s0]
    S["ui_select"] = us
    de = []   # смерть: грустный тромбон, но мягкий
    for i, m in enumerate((67, 66, 65, 62)):
        d = 0.36 if i < 3 else 1.0; n = N(d); t = T(n)
        f = midi(m - 12) * (1 + (0.025 * np.sin(TAU * 5 * t) if i == 3 else 0)); ph = phase(f, n)
        x = sum(k ** -1.3 * np.sin(k * ph) * (1.5 if k in (3, 4) else 1) for k in range(1, 9))
        de.append(x * gate(n, d - 0.05, 0.05, 0.02) * (1 - 0.4 * (t / d) if i == 3 else 1))
    S["death"] = room(np.concatenate(de), 1.2, 0.3)
    wi = np.zeros(N(2.2))   # победа: аккорды C - F - G - C вверх
    for i, (t0, ch) in enumerate(((0, [60, 64, 67]), (0.22, [65, 69, 72]), (0.44, [67, 71, 74]), (0.7, [72, 76, 79, 84]))):
        for m in ch:
            x = plus(0.5 * rhodes(midi(m), 0.25 if i < 3 else 1.1, 0.9), 0.35 * bell(midi(m + 12), 0.3 if i < 3 else 0.9)); s0 = N(t0); wi[s0:s0 + len(x)] += x[:len(wi) - s0]
    S["win"] = room(wi, 1.4, 0.35)
    n = N(0.55); t = T(n); th = np.zeros(n)
    for f in (233, 277):
        ph = TAU * f * t; th += sum(k ** -1.0 * np.sin(k * ph) for k in (1, 3, 5, 7, 9))
    S["truck_horn"] = filt(np.tanh(th), hi=2500) * gate(n, 0.45, 0.08, 0.02)
    n = N(0.9); t = T(n)
    S["lightning"] = room(filt(noise(n), lo=2000) * np.exp(-t / 0.04) + 0.8 * filt(noise(n), hi=180) * np.exp(-t / 0.35) * np.minimum(t / 0.05, 1), 1.0, 0.3)
    co = np.zeros(N(0.7))
    for i, m in enumerate((79, 83, 86, 91, 95)): x = bell(midi(m), 0.25); s0 = N(i * 0.05); co[s0:s0 + len(x)] += x[:len(co) - s0]
    S["combo"] = room(co, 0.8, 0.3)
    for i, base in enumerate((62, 75)):   # пердёж: мерзкий, но не режет уши
        n = N(0.45); t = T(n); f = base + 15 * np.sin(TAU * 13 * t) + 8 * R.standard_normal(n).cumsum() / np.sqrt(n); ph = phase(f, n)
        buzz = sum(k ** -0.8 * np.sin(k * ph) for k in range(1, 14))
        S[f"fart{'' if i == 0 else '_2'}"] = filt(buzz, hi=1100) * (0.7 + 0.3 * np.sin(TAU * 21 * t)) * gate(n, 0.36, 0.08, 0.02) + 0.2 * filt(noise(n), hi=800) * np.exp(-t / 0.2)
    n = N(0.6); t = T(n)
    S["pipe"] = sum(a * np.sin(TAU * 420 * r * t) * np.exp(-t / d) for r, a, d in ((1, 1, 0.35), (2.76, 0.5, 0.18), (5.4, 0.3, 0.08), (8.9, 0.15, 0.04))) + 0.5 * filt(noise(n), hi=2000) * np.exp(-t / 0.01)
    n = N(2.0); t = T(n); fl = np.zeros(n)   # петля мух: бесшовная (целое число периодов за 2 с)
    for f, d, r in ((210, 6, 3), (224, 5, 4), (237.5, 7, 2)):
        ph = TAU * f * t + d / r * (1 - np.cos(TAU * r * t))
        fl += sum(k ** -1.0 * np.sin(k * ph) for k in range(1, 9))
    S["flies_loop"] = filt(fl, hi=2200) * (0.75 + 0.25 * np.sin(TAU * 3 * t))
    n = N(0.35); t = T(n)
    S["splat_pile"] = np.tanh(1.5 * (filt(noise(n), lo=150, hi=1300) * np.exp(-t / 0.12) + 0.7 * np.sin(phase(sweep(320, 70, n, 0.05), n)) * np.exp(-t / 0.1)))
    n = N(0.04); t = T(n); S["roulette_tick"] = np.sin(TAU * 2200 * t) * np.exp(-t / 0.005) + 0.5 * np.sin(TAU * 1100 * t) * np.exp(-t / 0.01)
    rw = np.zeros(N(1.4))
    for i, m in enumerate((67, 72, 76, 79, 84, 88)): x = bell(midi(m), 0.5 if i < 5 else 1.0); s0 = N(i * 0.08); rw[s0:s0 + len(x)] += x[:len(rw) - s0]
    S["roulette_win"] = room(rw, 1.0, 0.3)
    n = N(0.22); t = T(n); S["streak_break"] = np.sin(phase(sweep(720, 240, n, 0.07), n)) * np.exp(-t / 0.08)
    n = N(0.12); t = T(n)   # скребок монеткой по серебру лотерейного билета
    S["scratch"] = filt(noise(n), lo=2500, hi=7000) * (0.5 + 0.5 * (np.sin(TAU * 55 * t) > 0)) * np.sin(np.pi * t / t[-1]) * 0.8
    S.update(hymn_sfx())   # музыкальные звуки - в тоне кладбищенского хорала меню
    S = {k: graveyard(v, k) for k, v in S.items()}
    os.makedirs(OUT_SFX, exist_ok=True)
    vol = {"ui_move": 0.5, "pickup": 0.6, "hit": 0.7, "hit_2": 0.7, "hit_3": 0.7}
    for k, v in S.items():
        x = v * gate(len(v), len(v) / SR - 0.01, 0.01, 0.0005)   # без щелчков на краях
        save(f"{OUT_SFX}/{k}.wav", x, vol.get(k, 0.8))
    return list(S)


if __name__ == "__main__":
    names = sfx(); print("sfx:", len(names))
    os.makedirs(OUT_MUS, exist_ok=True)
    for fn in (battle_a, battle_b, battle_c, battle_d, battle_e, boss, shop, shop_b, shop_c, menu):
        fn()
