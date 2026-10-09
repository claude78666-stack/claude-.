"""Synthesize the Axolotlion trailer score (64 s, 48 kHz stereo) from scratch: drone, pads, bells, pulse, taiko, swell."""
import numpy as np, wave, sys
SR = 48000; T = 64.0; N = int(SR * T)
rng = np.random.default_rng(7)
t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)

def env(a, d, s, r, length):
    n = int(length * SR); e = np.ones(n) * s
    na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na); e[na:na + nd] = np.linspace(1, s, nd)
    e[-nr:] *= np.linspace(1, 0, nr); return e

def lowpass(x, fc):
    # one-pole smoothing, run twice for 12 dB/oct
    a = np.exp(-2 * np.pi * fc / SR); y = x.copy()
    for _ in range(2):
        from scipy.signal import lfilter
        y = lfilter([1 - a], [1, -a], y)
    return y

def add(sig, start, pan=0.0, gain=1.0):
    s = int(start * SR); e = min(N, s + len(sig)); sig = sig[:e - s] * gain
    L[s:e] += sig * np.sqrt(0.5 * (1 - pan)); R[s:e] += sig * np.sqrt(0.5 * (1 + pan))

def midi(n): return 440 * 2 ** ((n - 69) / 12)

def saw_stack(f, length, detune=(-7, -2, 3, 8)):
    n = int(length * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    for c in detune:
        ff = f * 2 ** (c / 1200); ph = rng.random()
        out += 2 * ((tt * ff + ph) % 1) - 1
    return out / len(detune)

# 1. sub drone: A1 + E2, swelling
drone = (np.sin(2 * np.pi * 55 * t) * 0.6 + np.sin(2 * np.pi * 82.41 * t) * 0.25 + np.sin(2 * np.pi * 110 * t) * 0.15)
drone *= np.interp(t, [0, 6, 17, 40, 56, 60, 64], [0, .5, .65, .75, .9, .6, 0])
add(drone, 0, 0, 0.32)

# 2. pads: Am - F - C - G (8 s each), brighter as it builds
chords = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
for i in range(8):
    start = i * 8.0; ch = chords[i % 4]; length = 8.6
    bright = 600 + i * 260
    for j, n in enumerate(ch):
        s = saw_stack(midi(n), length) * env(2.2, 1.0, 0.85, 2.4, length)
        s = lowpass(s, bright)
        add(s, start, pan=(-0.5 + j / 3), gain=0.09 * (0.5 + 0.5 * min(1, i / 3)))

# 3. shimmering bells (A minor pentatonic), sparse early, denser later
pent = [69, 72, 74, 76, 79, 81, 84, 86, 88]
bt = 1.2
while bt < 60:
    n = pent[rng.integers(len(pent))]; f = midi(n); length = 3.5
    tt = np.arange(int(length * SR)) / SR
    s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.01 * tt) + 0.12 * np.sin(2 * np.pi * f * 3.98 * tt)) * np.exp(-tt * 1.6)
    add(s, bt, pan=rng.uniform(-0.8, 0.8), gain=0.05)
    bt += rng.uniform(1.4, 2.6) if bt < 30 else rng.uniform(0.7, 1.4)

# 4. heartbeat pulse from "Meet Axolotlion" (17.3 s), quickening
def thump(f0=55, length=0.6, gain=1.0):
    tt = np.arange(int(length * SR)) / SR
    f = f0 * (1 + 2.5 * np.exp(-tt * 30))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7) * gain
bpm_pts = [(17.3, 64), (40, 76), (56, 90)]
x = 17.3
while x < 57.5:
    bpm = np.interp(x, [p[0] for p in bpm_pts], [p[1] for p in bpm_pts])
    add(thump(52), x, 0, 0.35); add(thump(48, gain=0.6), x + 0.22, 0, 0.25)
    x += 60 / bpm

# 5. taiko hits on key beats + big impacts
def taiko(gain=1.0):
    length = 2.2; tt = np.arange(int(length * SR)) / SR
    body = np.sin(2 * np.pi * np.cumsum(70 * (1 + 1.2 * np.exp(-tt * 18))) / SR) * np.exp(-tt * 3.2)
    noise = lowpass(rng.standard_normal(len(tt)), 900) * np.exp(-tt * 14) * 0.6
    return (body + noise) * gain
for hit in [17.3, 28.9, 32.7, 35.9, 39.6, 42.1, 47.1, 50.7, 53.4, 56.3]:
    add(taiko(), hit, rng.uniform(-.2, .2), 0.42)
for big in [17.3, 58.3]:
    add(taiko(1.6), big, 0, 0.5); add(thump(36, 2.5, 1.6), big, 0, 0.55)

# 6. string swell (high octave) for the climax 40-60 s
for n, pan in [(81, -0.4), (84, 0.4), (88, 0.0)]:
    length = 20; s = saw_stack(midi(n), length, (-9, -3, 4, 10))
    s = lowpass(s, 2400) * np.interp(np.arange(len(s)) / SR, [0, 12, 17, 20], [0, 1, 0.8, 0])
    add(s, 40, pan, 0.045)

# 7. low risers/whooshes into key moments
for at in [17.0, 41.8, 58.0]:
    length = 2.5; tt = np.arange(int(length * SR)) / SR
    s = (lowpass(rng.standard_normal(len(tt)), 400) * (1 - (tt / length)) + lowpass(rng.standard_normal(len(tt)), 2500) * (tt / length)) * (tt / length) ** 2
    add(s, at - length + 0.3, 0, 0.18)

# reverb: stereo exponential-noise impulse, 3.2 s
from scipy.signal import fftconvolve
irn = int(3.2 * SR); it = np.arange(irn) / SR
irL = rng.standard_normal(irn) * np.exp(-it * 2.1); irR = rng.standard_normal(irn) * np.exp(-it * 2.1)
irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
wetL = fftconvolve(L, irL)[:N]; wetR = fftconvolve(R, irR)[:N]
outL = L * 0.75 + wetL * 0.55; outR = R * 0.75 + wetR * 0.55
fade = np.interp(t, [0, 0.5, T - 3, T], [0, 1, 1, 0])
mix = np.stack([outL, outR], 1) * fade[:, None]
mix = np.tanh(mix / np.abs(mix).max() * 1.4) / np.tanh(1.4) * 0.9
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('score written', T, 's')
