#!/usr/bin/env python3
"""Synthesizes the long, calm music bed that sits under Sifa's explainer narration -> out.wav

Run: python3 make_bed.py out.wav duration_s
A minor, 96 BPM: warm pads and a soft arp throughout, a light kick and hat groove that drops out every
16 bars so it never gets tiring, and a gentle fade in and out.
"""
import sys
import wave

import numpy as np
from scipy.signal import lfilter

SR = 44100
OUT, DUR = sys.argv[1], float(sys.argv[2])
BEAT = 60.0 / 96
N = int(SR * DUR)
rng = np.random.default_rng(11)
L, R = np.zeros(N), np.zeros(N)
freq = lambda m: 440.0 * 2 ** ((m - 69) / 12.0)
PROG = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62), (57, 60, 64), (53, 57, 60), (55, 59, 62), (52, 55, 59)]


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    return lfilter([1 - a], [1, -a], x)


def add(t, sig, gain, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * (1 - pan)
    R[i:i + len(sig)] += sig * (1 + pan)


def env(n, a, r):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def saw(f, dur, voices=1, detune=0.0):
    t = np.arange(int(dur * SR)) / SR
    return sum(2 * ((t * f * (1 + detune * (v - (voices - 1) / 2)) + rng.random()) % 1) - 1
               for v in range(voices)) / voices


t = np.arange(int(0.3 * SR)) / SR
KICK = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t * 10)
th = np.arange(int(0.05 * SR)) / SR
HAT = rng.standard_normal(len(th))
HAT = (HAT - lowpass(HAT, 7000)) * np.exp(-th * 70)

bar = 4 * BEAT
for b in range(int(DUR / bar) + 1):
    t0 = b * bar
    chord = PROG[b % len(PROG)]
    pad = sum(saw(freq(m), bar + 0.4, voices=3, detune=0.005) for m in chord)
    add(t0, lowpass(pad, 900) * env(len(pad), 0.6, 0.8), 0.07, -0.1)
    sub = np.sin(2 * np.pi * freq(chord[0] - 24) * np.arange(int(bar * SR)) / SR) * env(int(bar * SR), 0.05, 0.3)
    add(t0, sub, 0.10)
    notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 24]
    for s in range(8):
        n = saw(freq(notes[s % 4]), BEAT / 2) * env(int(BEAT / 2 * SR), 0.004, 0.2)
        add(t0 + s * BEAT / 2, lowpass(n, 2400), 0.035, 0.4 if s % 2 else -0.4)
    if (b // 16) % 2 == 0 and b % 16 < 14:  # groove, with a breather every other 16 bars
        for beat in range(4):
            add(t0 + beat * BEAT, KICK, 0.22)
            add(t0 + beat * BEAT + BEAT / 2, HAT, 0.05, 0.3)

fade = np.ones(N)
fade[: int(3 * SR)] = np.linspace(0, 1, int(3 * SR))
fade[-int(4 * SR):] *= np.linspace(1, 0, int(4 * SR))
mix = np.stack([L, R], 1) * fade[:, None]
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix *= 0.85 / np.abs(mix).max()
with wave.open(OUT, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", OUT, f"{DUR:.1f}s")
