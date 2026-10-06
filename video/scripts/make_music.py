#!/usr/bin/env python3
"""Synthesizes the 60 second backing track (no dependencies) -> public/music.wav

A minor, 112 BPM. Builds in layers (pads -> kick + bass -> arp + snare -> full) and puts a riser and an
impact on every scene change so the music and the cuts line up. Scene change times come from src/Video.tsx.
"""
import math
import random
import struct
import wave
from pathlib import Path

SR = 44100
DUR = 60.0
N = int(SR * DUR)
BPM = 112
BEAT = 60.0 / BPM
random.seed(7)
buf = [0.0] * N

# Scene change times in seconds (scene lengths 180,270,330,360,330,240,162 frames; 12-frame overlaps; 30 fps).
CUTS = []
t_frames = 0
for length in (180, 270, 330, 360, 330, 240):
    t_frames += length - 12
    CUTS.append((t_frames + 6) / 30.0)

def freq(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)

def add(start, samples):
    i0 = int(start * SR)
    for k, v in enumerate(samples):
        i = i0 + k
        if i >= N:
            break
        if i >= 0:
            buf[i] += v

def tone(dur, f, amp, attack=0.01, release=0.05, harm=((1, 1.0),), decay=0.0):
    n = int(dur * SR)
    out = [0.0] * n
    w = 2 * math.pi * f / SR
    for i in range(n):
        t = i / SR
        env = min(1.0, t / attack) if attack > 0 else 1.0
        if t > dur - release:
            env *= max(0.0, (dur - t) / release)
        if decay:
            env *= math.exp(-t * decay)
        s = 0.0
        for h, a in harm:
            s += a * math.sin(w * i * h)
        out[i] = s * amp * env
    return out

def noise(dur, amp, decay, hp=True):
    n = int(dur * SR)
    out = [0.0] * n
    prev = 0.0
    for i in range(n):
        x = random.uniform(-1, 1)
        y = (x - prev) if hp else x
        prev = x
        out[i] = y * amp * math.exp(-i / SR * decay)
    return out

def kick():
    n = int(0.32 * SR)
    out = [0.0] * n
    ph = 0.0
    for i in range(n):
        t = i / SR
        f = 48 + 110 * math.exp(-t * 28)
        ph += 2 * math.pi * f / SR
        out[i] = math.sin(ph) * 0.55 * math.exp(-t * 13)
    return out

KICK = kick()

# chords: (bass midi, chord tones midi)
CHORDS = [(45, (57, 60, 64)), (41, (53, 57, 60)), (48, (60, 64, 67)), (43, (55, 59, 62))]
CHORD_LEN = 8 * BEAT

# pads
c = 0
t = 0.0
while t < DUR:
    _, tones = CHORDS[c % 4]
    for m in tones:
        add(t, tone(CHORD_LEN + 0.9, freq(m), 0.045, attack=0.7, release=0.9, harm=((1, 1.0), (2, 0.22))))
    t += CHORD_LEN
    c += 1

def chord_at(time):
    return CHORDS[int(time // CHORD_LEN) % 4]

# bass: eighth notes from 3.0s, with a pump on the beat
t = 3.0
while t < DUR - 2.5:
    bass_m, _ = chord_at(t)
    beat_pos = ((t / BEAT) * 2) % 2
    amp = 0.17 if beat_pos < 0.5 else 0.13
    add(t, tone(BEAT / 2 * 0.92, freq(bass_m - 12 + (12 if int(t / (BEAT / 2)) % 4 == 3 else 0)), amp, attack=0.008, release=0.05, harm=((1, 1.0), (2, 0.35))))
    t += BEAT / 2

# kick: four on the floor from the second scene until the outro
t = CUTS[0]
while t < CUTS[5] + 0.2:
    add(t, KICK)
    t += BEAT

# snare/clap on 2 and 4 from scene three, hats on the off-beat, 16th hats from scene four
t = CUTS[1]
beat_i = 0
while t < CUTS[5]:
    if beat_i % 2 == 1:
        add(t, noise(0.14, 0.14, 26, hp=True))
    add(t + BEAT / 2, noise(0.045, 0.07, 80))
    if t >= CUTS[2]:
        add(t + BEAT / 4, noise(0.03, 0.035, 90))
        add(t + BEAT * 3 / 4, noise(0.03, 0.035, 90))
    t += BEAT
    beat_i += 1

# arp: 16th notes from scene three
t = CUTS[1]
step = BEAT / 4
k = 0
PATTERN = (0, 1, 2, 1, 2, 1, 0, 1)
while t < CUTS[5]:
    _, tones = chord_at(t)
    m = tones[PATTERN[k % len(PATTERN)]] + 12
    add(t, tone(0.22, freq(m), 0.06, attack=0.003, release=0.04, harm=((1, 1.0), (2, 0.4), (3, 0.15)), decay=11))
    t += step
    k += 1

# risers into every cut, impact on the cut
for cut in CUTS:
    rise = 1.0
    n = int(rise * SR)
    out = [0.0] * n
    prev = 0.0
    for i in range(n):
        x = i / n
        r = random.uniform(-1, 1)
        out[i] = (r - prev) * 0.16 * x * x + math.sin(2 * math.pi * (300 + 900 * x * x) * i / SR) * 0.03 * x * x
        prev = r
    add(cut - rise, out)
    n = int(0.9 * SR)
    hit = [0.0] * n
    ph = 0.0
    for i in range(n):
        tt = i / SR
        ph += 2 * math.pi * (34 + 60 * math.exp(-tt * 18)) / SR
        hit[i] = math.sin(ph) * 0.42 * math.exp(-tt * 4.5)
    add(cut, hit)
    add(cut, noise(0.25, 0.18, 14))

# master: fades, soft clip, normalize
peak = 0.0
for i in range(N):
    t = i / SR
    g = min(1.0, t / 0.6) * min(1.0, max(0.0, (DUR - t) / 2.8))
    v = math.tanh(buf[i] * g * 1.5)
    buf[i] = v
    peak = max(peak, abs(v))
scale = 0.82 / peak if peak else 1.0

out_path = Path(__file__).resolve().parent.parent / 'public' / 'music.wav'
out_path.parent.mkdir(parents=True, exist_ok=True)
with wave.open(str(out_path), 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(b''.join(struct.pack('<h', int(max(-1.0, min(1.0, v * scale)) * 32767)) for v in buf))
print(f'wrote {out_path} ({DUR:.0f}s, cuts at {[round(c, 2) for c in CUTS]})')
