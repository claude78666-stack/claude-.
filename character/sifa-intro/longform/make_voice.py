#!/usr/bin/env python3
"""Reads each section of script.json with Gemini TTS in Sifa's voice -> voice/<id>.wav

Run: python3 make_voice.py [section_id ...]
Sections are read two per request (the free tier allows 10 TTS requests a day) and split at the pause
between them.
Laomedeia is the voice that matches ../voice.wav (same pitch and the closest speaker embedding of the
Gemini voices). Existing files are kept, so re-running only fills in missing sections.
Auth is injected by the session proxy; set GEMINI_API_KEY to run elsewhere.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
URL = "https://generativelanguage.googleapis.com/v1beta/models/" + os.environ.get("TTS_MODEL", "gemini-3.8-flash-tts") + ":generateContent"
VOICE = "Laomedeia"
key = os.environ.get("GEMINI_API_KEY")
headers = {"Content-Type": "application/json", **({"x-goog-api-key": key} if key else {})}

sections = json.load(open(HERE / "script.json"))["sections"]
wanted = set(sys.argv[1:])
(HERE / "voice").mkdir(exist_ok=True)


def tts(text):
    body = {"contents": [{"parts": [{"text": text}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": VOICE}}}}}
    for attempt in range(12):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers=headers)
            d = json.load(urllib.request.urlopen(req, timeout=300))
            return np.frombuffer(base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]), "<i2")
        except (urllib.error.HTTPError, KeyError) as e:
            print("retry", getattr(e, "code", e), flush=True)
            time.sleep(30)
    sys.exit("TTS kept failing")


def split_point(pcm, ratio):
    """The longest pause within 15% of where the first section should end."""
    win = 2400  # 0.1 s at 24 kHz
    energy = np.sqrt(np.convolve(pcm.astype(float) ** 2, np.ones(win) / win, "same"))
    quiet = energy < 300
    lo, hi = int(len(pcm) * max(0, ratio - 0.15)), int(len(pcm) * min(1, ratio + 0.15))
    best, run, start = (0, int(len(pcm) * ratio)), 0, lo
    for i in range(lo, hi, 240):
        if quiet[i]:
            if run == 0:
                start = i
            run += 240
            if run > best[0]:
                best = (run, start + run // 2)
        else:
            run = 0
    return best[1]


def save(path, pcm):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        w.writeframes(pcm.astype("<i2").tobytes())
    print(path.name, f"{len(pcm) / 24000:.1f}s", flush=True)


todo = [s for s in sections if (not wanted or s["id"] in wanted) and not (HERE / "voice" / f"{s['id']}.wav").exists()]
for i in range(0, len(todo), 2):
    group = todo[i:i + 2]
    pcm = tts("\n\n".join(s["text"] for s in group))
    if len(group) == 1:
        save(HERE / "voice" / f"{group[0]['id']}.wav", pcm)
        continue
    ratio = len(group[0]["text"]) / (len(group[0]["text"]) + len(group[1]["text"]))
    cut = split_point(pcm, ratio)
    save(HERE / "voice" / f"{group[0]['id']}.wav", pcm[:cut])
    save(HERE / "voice" / f"{group[1]['id']}.wav", pcm[cut:])
