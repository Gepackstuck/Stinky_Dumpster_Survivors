#!/usr/bin/env python3
"""Звуки и музыка «Помойки»: всё синтезом (чиптюн + шум), мерзко и смешно. Без чужих сэмплов.
python3 tools/gen_audio.py  -> assets/sfx/*.wav (моно 22050), assets/music/*.wav (лупы)."""
import math, os, random, struct, wave
import numpy as np

SR = 22050
rng = np.random.default_rng(7)
OUT_SFX = "assets/sfx"; OUT_MUS = "assets/music"


def t(sec):
    return np.arange(int(SR * sec)) / SR


def env(n, a=0.005, d=0.1, s=0.0, r=0.05, sus=0.0):
    """ADSR по числу семплов; sus - длительность полки."""
    a_n, d_n, s_n, r_n = int(a * SR), int(d * SR), int(sus * SR), int(r * SR)
    e = np.concatenate([np.linspace(0, 1, max(a_n, 1)), np.linspace(1, s, max(d_n, 1)), np.full(s_n, s), np.linspace(s, 0, max(r_n, 1))])
    if len(e) < n: e = np.concatenate([e, np.zeros(n - len(e))])
    return e[:n]


def sq(freq, tt, duty=0.5):
    ph = np.cumsum(np.broadcast_to(freq, tt.shape) / SR) % 1.0
    return np.where(ph < duty, 1.0, -1.0)


def tri(freq, tt):
    ph = np.cumsum(np.broadcast_to(freq, tt.shape) / SR) % 1.0
    return 4 * np.abs(ph - 0.5) - 1


def noise(n, lp=1.0):
    x = rng.uniform(-1, 1, n)
    if lp < 1.0:   # простой НЧ-фильтр: мокрее, «пердежнее»
        y = np.zeros(n); acc = 0.0
        for i in range(n):
            acc += lp * (x[i] - acc); y[i] = acc
        x = y / (np.max(np.abs(y)) + 1e-9)
    return x


def crush(x, bits=6):
    q = 2 ** bits
    return np.round(x * q) / q


def save(path, x, vol=0.8):
    x = np.clip(x / (np.max(np.abs(x)) + 1e-9) * vol, -1, 1)
    data = (x * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())


def sfx():
    S = {}
    tt = t(0.12); S["shoot"] = crush(sq(np.linspace(900, 300, len(tt)), tt, 0.25) * env(len(tt), d=0.1))
    tt = t(0.18); S["swing"] = noise(len(tt), 0.35) * env(len(tt), a=0.03, d=0.15) * np.linspace(0.3, 1, len(tt))
    tt = t(0.1); S["hit"] = crush(noise(len(tt), 0.25) * env(len(tt), d=0.09) + 0.4 * sq(np.linspace(220, 90, len(tt)), tt) * env(len(tt), d=0.06), 5)
    tt = t(0.32)   # смерть врага: хлюп + пердёж
    fart = sq(70 + 25 * np.sin(2 * np.pi * 30 * tt), tt, 0.3) * env(len(tt), d=0.3)
    S["enemy_death"] = crush(0.7 * fart + 0.6 * noise(len(tt), 0.2) * env(len(tt), d=0.12), 5)
    tt = t(0.25); S["player_hurt"] = crush(sq(np.linspace(300, 120, len(tt)) + 20 * np.sin(2 * np.pi * 40 * tt), tt, 0.4) * env(len(tt), d=0.24), 5)
    tt = t(0.07); S["pickup"] = sq(np.linspace(1200, 1700, len(tt)), tt, 0.5) * env(len(tt), d=0.06)
    notes = [523, 659, 784, 1046]; S["level_up"] = np.concatenate([sq(f, t(0.08), 0.25) * env(len(t(0.08)), d=0.08) for f in notes])
    tt = t(0.14); S["dash"] = noise(len(tt), 0.5) * env(len(tt), a=0.01, d=0.13) * np.linspace(1, 0.2, len(tt)) + 0.3 * tri(np.linspace(400, 1200, len(tt)), tt) * env(len(tt), d=0.12)
    tt = t(0.5); S["explosion"] = crush(noise(len(tt), 0.08) * env(len(tt), d=0.45) + 0.6 * sq(np.linspace(80, 30, len(tt)), tt) * env(len(tt), d=0.4), 4)
    tt = t(0.12); S["warn"] = sq(880, tt, 0.5) * env(len(tt), d=0.11, s=0.6, sus=0.04) * 0.5
    tt = t(0.9); S["boss_roar"] = crush((sq(55 + 10 * np.sin(2 * np.pi * 6 * tt), tt, 0.3) + 0.5 * noise(len(tt), 0.1)) * env(len(tt), a=0.1, d=0.7), 4)
    tt = t(0.6); S["wave_horn"] = (sq(196, tt, 0.4) + sq(247, tt, 0.4)) * env(len(tt), a=0.04, d=0.5, s=0.3, sus=0.1)
    S["buy"] = np.concatenate([sq(1318, t(0.05), 0.5) * env(len(t(0.05)), d=0.05), sq(1760, t(0.12), 0.5) * env(len(t(0.12)), d=0.12)])
    tt = t(0.025); S["ui_move"] = sq(1500, tt, 0.5) * env(len(tt), d=0.025) * 0.5
    tt = t(0.06); S["ui_select"] = sq(np.linspace(800, 1200, len(tt)), tt, 0.5) * env(len(tt), d=0.06)
    tromb = [392, 370, 349, 294]; S["death"] = np.concatenate([tri(f + 6 * np.sin(2 * np.pi * 5 * t(0.35)), t(0.35)) * env(len(t(0.35)), a=0.02, d=0.33) for f in tromb])
    fan = [523, 523, 659, 784, 1046]; S["win"] = np.concatenate([sq(f, t(0.12 if i < 4 else 0.5), 0.25) * env(len(t(0.12 if i < 4 else 0.5)), d=0.12 if i < 4 else 0.5) for i, f in enumerate(fan)])
    tt = t(0.5); S["truck_horn"] = (sq(233, tt, 0.5) + sq(277, tt, 0.5)) * env(len(tt), a=0.02, d=0.4, s=0.5, sus=0.2)
    tt = t(0.35); S["lightning"] = crush(noise(len(tt), 0.9) * env(len(tt), a=0.001, d=0.3) + 0.5 * noise(len(tt), 0.05) * env(len(tt), d=0.33), 3)
    S["combo"] = np.concatenate([sq(f, t(0.06), 0.25) * env(len(t(0.06)), d=0.06) for f in [784, 988, 1175, 1568, 1976]])
    tt = t(0.45)   # старческий пердёж: низкий, дребезжащий, с хвостом
    S["fart"] = crush((sq(55 + 18 * np.sin(2 * np.pi * 22 * tt) + 10 * np.sin(2 * np.pi * 7 * tt), tt, 0.25) * env(len(tt), a=0.02, d=0.4) + 0.4 * noise(len(tt), 0.15) * env(len(tt), d=0.3)), 5)
    tt = t(0.3); S["pipe"] = sq(np.linspace(400, 90, len(tt)), tt, 0.5) * env(len(tt), d=0.28) + 0.3 * noise(len(tt), 0.3) * env(len(tt), d=0.2)
    tt = t(0.2); S["streak_break"] = sq(np.linspace(600, 150, len(tt)), tt, 0.5) * env(len(tt), d=0.2)
    os.makedirs(OUT_SFX, exist_ok=True)
    for k, v in S.items():
        save(f"{OUT_SFX}/{k}.wav", v, 0.7)
    return list(S)


def drum(kind, n):
    if kind == "k":
        tt = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(np.linspace(140, 40, n)) / SR) * env(n, d=0.12)
    if kind == "s":
        return noise(n, 0.6) * env(n, d=0.1) * 0.6
    if kind == "h":
        return noise(n, 1.0) * env(n, d=0.03) * 0.25
    return np.zeros(n)


def music(name, bpm, bars, bass, lead, drums, lead_duty=0.25, swing=0.0):
    """Луп: бас (треугольник), мелодия (квадрат), ударные (шум). bass/lead - списки частот по шестнадцатым (0 - пауза)."""
    step = 60.0 / bpm / 4; n_step = int(step * SR); total = n_step * 16 * bars
    out = np.zeros(total)
    for i in range(16 * bars):
        s0 = i * n_step; tt = np.arange(n_step) / SR
        b = bass[i % len(bass)]
        if b: out[s0:s0 + n_step] += 0.45 * tri(b, tt) * env(n_step, a=0.003, d=step * 0.9, s=0.2)
        l = lead[i % len(lead)]
        if l: out[s0:s0 + n_step] += 0.22 * sq(l, tt, lead_duty) * env(n_step, a=0.002, d=step * 0.8, s=0.3)
        d = drums[i % len(drums)]
        if d != ".": out[s0:s0 + n_step] += 0.5 * drum(d, n_step)
    os.makedirs(OUT_MUS, exist_ok=True)
    save(f"{OUT_MUS}/{name}.wav", crush(out, 7), 0.6)


def note(n):
    return 440.0 * 2 ** ((n - 69) / 12) if n else 0


if __name__ == "__main__":
    names = sfx()
    # бой: злой минорный рифф, 140 bpm, 8 тактов
    E2, G2, A2, B2, D3 = 40, 43, 45, 47, 50
    bass = [note(x) for x in [E2, 0, E2, E2, G2, 0, E2, 0, A2, 0, E2, E2, B2, 0, D3, 0]]
    lead = [note(x) for x in [64, 0, 67, 0, 71, 0, 69, 67, 64, 0, 62, 0, 64, 0, 0, 0, 76, 0, 74, 0, 71, 0, 69, 0, 67, 69, 71, 0, 64, 0, 0, 0]]
    drums = "k.h.s.h.k.k.s.hh"
    music("battle", 140, 8, bass, lead, drums)
    # ларёк: ленивый «лифтовый» грув, 96 bpm
    bass2 = [note(x) for x in [45, 0, 0, 52, 0, 0, 45, 0, 43, 0, 0, 50, 0, 0, 43, 0]]
    lead2 = [note(x) for x in [69, 0, 0, 72, 0, 76, 0, 0, 74, 0, 72, 0, 71, 0, 0, 0, 67, 0, 0, 71, 0, 74, 0, 0, 72, 0, 71, 0, 69, 0, 0, 0]]
    music("shop", 96, 4, bass2, lead2, "k...h...s...h..h", 0.5)
    print("sfx:", len(names), "music: 2")
