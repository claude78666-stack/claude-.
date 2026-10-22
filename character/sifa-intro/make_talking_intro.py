#!/usr/bin/env python3
"""Makes Sifa actually talk in the intro: lip-syncs her face to voice.wav -> sifa_intro_talking_1080p.mp4

Run: WAV2LIP=/path/to/Wav2Lip python3 make_talking_intro.py
Takes sifa_intro_ai_1080p.mp4 (she walks in, sits, and voice.wav plays from VOICE_AT), cuts a fixed
640x640 window around her face for the seated part, runs Wav2Lip on it with voice.wav, and pastes the
lip-synced window back in place. The window is cut from the same frames, so only her mouth changes; the
original titles, push-in, music and voice stay as they are.
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC, OUT = HERE / "sifa_intro_ai_1080p.mp4", HERE / "sifa_intro_talking_1080p.mp4"
TMP = HERE / "build" / "talk"
TMP.mkdir(parents=True, exist_ok=True)
WAV2LIP = Path(os.environ.get("WAV2LIP", "/tmp/Wav2Lip"))
VOICE_AT = 3.9                # when voice.wav starts in the intro
X, Y, SIZE = 700, 100, 640    # face window; she stays inside it through the push-in
DUR = 19.3                    # voice.wav length plus a little


def run(cmd, **kw):
    subprocess.run(cmd, check=True, **kw)


crop, lips = TMP / "crop.mp4", TMP / "lips.mp4"
if not lips.exists():
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(VOICE_AT), "-t", str(DUR), "-i", str(SRC), "-an",
         "-vf", f"crop={SIZE}:{SIZE}:{X}:{Y}", "-c:v", "libx264", "-crf", "12", "-r", "24", str(crop)])
    run([sys.executable, "inference.py", "--checkpoint_path", "checkpoints/wav2lip_gan.pth", "--face", str(crop),
         "--audio", str(HERE / "voice.wav"), "--outfile", str(lips), "--pads", "0", "15", "0", "0",
         "--face_det_batch_size", "8"], cwd=WAV2LIP)
run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-i", str(lips),
     "-filter_complex", f"[1:v]setpts=PTS-STARTPTS+{VOICE_AT}/TB[l];"
     f"[0:v][l]overlay={X}:{Y}:eof_action=pass:enable='between(t,{VOICE_AT},{VOICE_AT + DUR})'[v]",
     "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-c:a", "copy",
     "-movflags", "+faststart", str(OUT)])
print("wrote", OUT)
