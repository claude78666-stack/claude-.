#!/usr/bin/env python3
"""Re-cuts each pair of narration files made by make_voice.py at the real section boundary.

Run: python3 fix_splits.py id_a id_b [id_c id_d ...]
Joins voice/<a>.wav + voice/<b>.wav back together, asks Gemini when the first words of section b are
spoken, snaps that to the nearest pause and writes both files again.
"""
import base64
import io
import json
import sys
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"
SR = 24000
text = {s["id"]: s["text"] for s in json.load(open(HERE / "script.json"))["sections"]}


def load(sid):
    with wave.open(str(HERE / "voice" / f"{sid}.wav")) as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2")


def save(sid, pcm):
    with wave.open(str(HERE / "voice" / f"{sid}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.astype("<i2").tobytes())
    print(sid, f"{len(pcm) / SR:.1f}s", flush=True)


def ask_start(pcm, words):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    prompt = (f'In this audio, at what time in seconds does the speaker begin saying "{words}"? '
              'Reply with only the number, to 0.1 s.')
    body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/wav",
                                                     "data": base64.b64encode(buf.getvalue()).decode()}},
                                    {"text": prompt}]}]}
    for attempt in range(6):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            reply = json.load(urllib.request.urlopen(req, timeout=240))["candidates"][0]["content"]["parts"][-1]["text"]
            return float(reply.strip().split()[0].rstrip("s"))
        except Exception as e:  # noqa: BLE001 - retry on rate limits and odd replies alike
            print("retry", e, flush=True)
            time.sleep(20)
    sys.exit("could not get a timestamp")


def nearest_pause(pcm, t):
    win = SR // 10
    energy = np.sqrt(np.convolve(pcm.astype(float) ** 2, np.ones(win) / win, "same"))
    quiet = energy < 300
    centre, best = int(t * SR), None
    i = max(0, centre - 2 * SR)
    while i < min(len(pcm), centre + SR):
        if quiet[i]:
            j = i
            while j < len(pcm) and quiet[j]:
                j += 1
            if j - i > SR // 10:
                mid = (i + j) // 2
                if best is None or abs(mid - centre) < abs(best - centre):
                    best = mid
            i = j
        i += 120
    return best or centre


ids = sys.argv[1:]
for a, b in zip(ids[::2], ids[1::2]):
    pcm = np.concatenate([load(a), load(b)])
    first_words = " ".join(text[b].split()[:5])
    t = ask_start(pcm, first_words)
    cut = nearest_pause(pcm, t - 0.15)
    print(f"{b} starts at {t:.1f}s, cut at {cut / SR:.2f}s")
    save(a, pcm[:cut])
    save(b, pcm[cut:])
