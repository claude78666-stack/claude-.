#!/usr/bin/env python3
"""Builds a Sifa walkthrough episode with her commentary over gameplay -> sifa_walkthrough_<n>.mp4

Run: WAV2LIP=/path/to/Wav2Lip python3 build_episode.py episode01.json
The episode file names the gameplay clip, the part of it to use, and Sifa's lines with the moment each
starts. Her lines are read in one Gemini TTS request (same voice as the explainer), split per line, and
placed at their moments; a lip-synced facecam sits bottom left. The game audio is kept and ducked under
her voice. Opens with the talking intro, a chapter card over the first seconds, ends on the SIFA SI outro.
"""
import base64
import io
import json
import os
import subprocess
import sys
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
INTRO_DIR, LONG = HERE.parent, HERE.parent / "longform"
EP_FILE = HERE / sys.argv[1]
ep = json.load(open(EP_FILE))
NUM = int("".join(c for c in EP_FILE.stem if c.isdigit()) or 1)
BUILD = HERE / "build" / EP_FILE.stem
BUILD.mkdir(parents=True, exist_ok=True)
OUT = HERE / f"sifa_walkthrough_{NUM:02d}.mp4"
W, H, FPS, SR = 1920, 1080, 30, 24000
FACE = 360
API = "https://generativelanguage.googleapis.com/v1beta/models/"
WAV2LIP = Path(os.environ.get("WAV2LIP", "/tmp/Wav2Lip"))
FONT = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
PURPLE, CYAN = (170, 80, 255), (40, 220, 255)


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


def gemini(model, body, timeout=300):
    for attempt in range(10):
        try:
            req = urllib.request.Request(API + model + ":generateContent", data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
            return json.load(urllib.request.urlopen(req, timeout=timeout))
        except Exception as e:  # noqa: BLE001 - rate limits and 5xx: wait and retry
            print("retry", e, flush=True)
            time.sleep(30)
    sys.exit("Gemini kept failing")


def wav_bytes(pcm):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.astype("<i2").tobytes())
    return buf.getvalue()


def lines_audio():
    """All lines in one TTS request, cut back into one clip per line."""
    cache = BUILD / "lines.npz"
    if cache.exists():
        return list(np.load(cache).values())
    texts = [l["text"] for l in ep["lines"]]
    d = gemini("gemini-3.8-flash-tts", {"contents": [{"parts": [{"text": "\n\n".join(texts)}]}],
               "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {
                   "prebuiltVoiceConfig": {"voiceName": "Laomedeia"}}}}})
    pcm = np.frombuffer(base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]), "<i2")
    ask = ("This audio reads these lines in order. Reply with only a JSON list of the start time in seconds "
           "(0.1 s precision) of each line:\n" + "\n".join(f"{i + 1}. {t}" for i, t in enumerate(texts)))
    r = gemini("gemini-3.5-flash", {"contents": [{"parts": [
        {"inlineData": {"mimeType": "audio/wav", "data": base64.b64encode(wav_bytes(pcm)).decode()}}, {"text": ask}]}]})
    reply = r["candidates"][0]["content"]["parts"][-1]["text"]
    starts = json.loads(reply[reply.index("["):reply.rindex("]") + 1])
    # snap each boundary to the quietest point within 0.6 s
    win = SR // 20
    energy = np.convolve(pcm.astype(float) ** 2, np.ones(win) / win, "same")
    cuts = [0]
    for s in starts[1:]:
        c = int(s * SR)
        lo, hi = max(cuts[-1] + SR // 2, c - int(0.6 * SR)), min(len(pcm) - 1, c + int(0.2 * SR))
        cuts.append(lo + int(np.argmin(energy[lo:hi])) if hi > lo else c)
    cuts.append(len(pcm))
    clips = [pcm[a:b] for a, b in zip(cuts, cuts[1:])]
    np.savez(cache, *clips)
    return clips


def trim_silence(clip):
    loud = np.where(np.abs(clip.astype(int)) > 500)[0]
    return clip[max(0, loud[0] - SR // 20):loud[-1] + SR // 10] if len(loud) else clip


def narration_track(clips, length):
    track = np.zeros(int(length * SR), dtype=np.int32)
    t_free = 0.0
    for line, clip in zip(ep["lines"], clips):
        clip = trim_silence(clip)
        t = max(line["at"] - ep["start"], t_free + 0.4)
        i = int(t * SR)
        track[i:i + len(clip)] += clip[: max(0, len(track) - i)]
        t_free = t + len(clip) / SR
        print(f"line at {t + ep['start']:6.1f}s demo, {len(clip) / SR:4.1f}s", flush=True)
    path = BUILD / "narration.wav"
    path.write_bytes(wav_bytes(np.clip(track, -32768, 32767)))
    return path


def chapter_png():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    big, small = ImageFont.truetype(FONT.format("Black"), 64), ImageFont.truetype(FONT.format("Bold"), 28)
    kicker, title = f"WALKTHROUGH  |  EPISODE {NUM}", ep["chapter"].upper()
    x, y = W // 2, 470
    width = max(d.textlength(title, font=big), d.textlength(kicker, font=small)) + 100
    d.rounded_rectangle([x - width / 2, y - 70, x + width / 2, y + 90], 18, fill=(8, 6, 18, 200))
    d.text((x, y - 30), kicker, font=small, fill=(*CYAN, 255), anchor="mm")
    d.text((x, y + 30), title, font=big, fill=(255, 255, 255, 255), anchor="mm")
    d.text((W - 70, H - 36), "Footage: Xbox / The Coalition", anchor="rm",
           font=ImageFont.truetype(FONT.format("Medium"), 20), fill=(255, 255, 255, 160))
    img.save(BUILD / "chapter.png")
    credit = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(credit).text((W - 70, H - 36), "Footage: Xbox / The Coalition", anchor="rm",
                                font=ImageFont.truetype(FONT.format("Medium"), 20), fill=(255, 255, 255, 160))
    credit.save(BUILD / "credit.png")


def main():
    length = ep["end"] - ep["start"]
    narration = narration_track(lines_audio(), length)
    face = BUILD / "face.mp4"
    if not face.exists():
        run([sys.executable, "inference.py", "--checkpoint_path", "checkpoints/wav2lip_gan.pth",
             "--face", str(LONG / "facecam_src.png"), "--audio", str(narration), "--outfile", str(face),
             "--static", "True", "--fps", str(FPS), "--pads", "0", "15", "0", "0"],
            cwd=WAV2LIP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    chapter_png()
    a = LONG / "build"
    fx, fy = 60, H - FACE - 70
    graph = ";".join([
        f"[0:v]fps={FPS},scale={W}:{H},setsar=1,format=yuva420p[g]",
        f"[1:v]scale={FACE + 16}:{FACE + 16},crop={FACE}:{FACE}:x='8+6*sin(t*0.9)':y='8+5*sin(t*0.6)',format=rgba[fc]",
        "[2:v]format=gray[fm]", "[fc][fm]alphamerge[fcm]",
        f"[g][fcm]overlay={fx}:{fy}:shortest=1[s1]",
        f"[s1][3:v]overlay={fx - 12}:{fy - 12}[s2]", f"[s2][4:v]overlay={fx + 16}:{fy - 64}[s3]",
        "[s3][5:v]overlay=60:40[s4]", "[s4][7:v]overlay=0:0[s5]",
        "[6:v]format=rgba,fade=t=in:st=0.3:d=0.5:alpha=1,fade=t=out:st=5.5:d=0.6:alpha=1[ch]",
        f"[s5][ch]overlay=0:0:enable='lt(t,6.2)',fade=t=in:st=0:d=0.4,fade=t=out:st={length - 0.6}:d=0.6,"
        "format=yuv420p[v]",
        "[8:a]aresample=48000,aformat=channel_layouts=stereo,asplit=2[vox][key]",
        "[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.8[game]",
        "[game][key]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=500[duck]",
        f"[duck][vox]amix=inputs=2:normalize=0:weights='1 1.6',afade=t=out:st={length - 1}:d=1[a]",
    ])
    body = BUILD / "body.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ep["start"]), "-t", str(length), "-i", str((HERE / ep["gameplay"])),
         "-i", str(face), "-loop", "1", "-i", str(a / "face_mask.png"), "-loop", "1", "-i", str(a / "face_frame.png"),
         "-loop", "1", "-i", str(a / "face_tag.png"), "-loop", "1", "-i", str(a / "watermark.png"),
         "-loop", "1", "-i", str(BUILD / "chapter.png"), "-loop", "1", "-i", str(BUILD / "credit.png"),
         "-i", str(narration), "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-t", str(length),
         "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "pcm_s16le", str(body)])
    parts = []
    intro = next(INTRO_DIR / n for n in ("sifa_intro_full_1080p.mp4", "sifa_intro_talking_1080p.mp4",
                                         "sifa_intro_ai_1080p.mp4") if (INTRO_DIR / n).exists())
    for i, src in enumerate((intro, body, INTRO_DIR / "sifa_si_outro.mp4")):
        part = BUILD / f"part{i}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"scale={W}:{H},fps={FPS},setsar=1,format=yuv420p",
             "-af", "aresample=48000,aformat=channel_layouts=stereo", "-c:v", "libx264", "-crf", "17",
             "-preset", "medium", "-c:a", "pcm_s16le", str(part)])
        parts.append(part)
    (BUILD / "parts.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(BUILD / "parts.txt"),
         "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "libx264", "-crf", "24", "-preset", "slow",
         "-maxrate", "2500k", "-bufsize", "5000k", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(OUT)])
    print("wrote", OUT)


if __name__ == "__main__":
    main()
