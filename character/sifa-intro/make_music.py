#!/usr/bin/env python3
"""Synthesizes the music bed for the full Sifa intro -> music.wav

Run: python3 make_music.py [out.wav] [duration_s]
A minor synthwave, 112 BPM. Pads and arp while she walks in, a soft groove under her talking, then a
riser into a big hit and the full beat on "Let's get started!" (HIT seconds from the start).
"""
import sys
import wave

import numpy as np

SR = 44100
OUT = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 38.0
BPM = 112
BEAT = 60.0 / BPM
GROOVE_IN, HIT = 4.0, 22.5
rng = np.random.default_rng(7)
N = int(SR * DUR)
L, R = np.zeros(N), np.zeros(N)

freq = lambda m: 440.0 * 2 ** ((m - 69) / 12.0)
CHORDS = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]  # Am F C G, one bar each


def add(t, sig, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * (1 - pan) / 2 ** 0.5
    R[i:i + len(sig)] += sig * (1 + pan) / 2 ** 0.5


def env(n, a, r):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def saw(f, dur, voices=1, detune=0.0):
    t = np.arange(int(dur * SR)) / SR
    out = sum(2 * ((t * f * (1 + detune * (v - (voices - 1) / 2)) + rng.random()) % 1) - 1 for v in range(voices))
    return out / voices


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 45 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def snare():
    t = np.arange(int(0.25 * SR)) / SR
    n = rng.standard_normal(len(t))
    n = n - lowpass(n, 1500)
    return (0.7 * n + 0.4 * np.sin(2 * np.pi * 190 * t)) * np.exp(-t * 18)


def hat():
    t = np.arange(int(0.06 * SR)) / SR
    n = rng.standard_normal(len(t))
    return (n - lowpass(n, 7000)) * np.exp(-t * 60)


KICK, SNARE, HAT = kick(), snare(), hat()
bars = int(DUR / (4 * BEAT)) + 1
for b in range(bars):
    t0 = b * 4 * BEAT
    chord = CHORDS[b % 4]
    # pad: detuned saws through a soft filter, all the way through
    pad = sum(saw(freq(m), 4 * BEAT, voices=3, detune=0.004) for m in chord)
    pad = lowpass(pad, 1800 if t0 >= HIT else 1100) * env(len(pad), 0.4, 0.5)
    add(t0, pad, 0.10, pan=-0.1)
    # arp: 16ths over the chord, octave up
    notes = [m + 12 for m in chord] + [chord[1] + 24]
    for s in range(16):
        t = t0 + s * BEAT / 4
        n = saw(freq(notes[s % 4]), BEAT / 4) * env(int(BEAT / 4 * SR), 0.003, 0.08)
        add(t, lowpass(n, 3500), 0.05 if t < HIT else 0.07, pan=0.35 if s % 2 else -0.35)
    if t0 + 4 * BEAT <= GROOVE_IN:
        continue
    loud = t0 >= HIT
    for beat in range(4):
        t = t0 + beat * BEAT
        if t < GROOVE_IN:
            continue
        add(t, KICK, 0.55 if loud else 0.35)
        if beat % 2:
            add(t, SNARE, 0.30 if loud else 0.16)
        add(t + BEAT / 2, HAT, 0.10 if loud else 0.06, pan=0.3)
        # bass: 8th-note root pulse
        for h in range(2):
            bn = saw(freq(chord[0] - 24), BEAT / 2) * env(int(BEAT / 2 * SR), 0.005, 0.05)
            add(t + h * BEAT / 2, lowpass(bn, 600 if loud else 400), 0.30 if loud else 0.22)

# riser into the hit, then an impact
rise = 2.0
tr = np.arange(int(rise * SR)) / SR
noise = rng.standard_normal(len(tr))
add(HIT - rise, (noise - lowpass(noise, 2500)) * (tr / rise) ** 2, 0.25)
ti = np.arange(int(1.5 * SR)) / SR
add(HIT, np.sin(2 * np.pi * (40 + 60 * np.exp(-ti * 8)) * ti) * np.exp(-ti * 3), 0.7)
add(HIT, rng.standard_normal(len(ti)) * np.exp(-ti * 6), 0.12)

# fade in, fade out, normalise
fade = np.ones(N)
fade[: int(1.5 * SR)] = np.linspace(0, 1, int(1.5 * SR))
fade[-int(2.5 * SR):] *= np.linspace(1, 0, int(2.5 * SR))
mix = np.stack([L, R], 1) * fade[:, None]
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
mix *= 0.89 / np.abs(mix).max()
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", OUT, f"{DUR:.1f}s")
