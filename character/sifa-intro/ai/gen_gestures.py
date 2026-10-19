#!/usr/bin/env python3
"""Short photoreal gesture clips of seated Sifa -> ai/gestures/<name>.mp4

Run: python3 gen_gestures.py [name ...]
Wan 2.2 first-last-frame (free Hugging Face ZeroGPU Space, mcp-tools/wan-2-2-first-last-frame): every clip starts
and ends on the same rest pose (sifa_seat_crop.png), so the clips chain into one seamless facecam loop with only
small, occasional hand movement. Never Runway. render_v2.py lip-syncs and cuts her out of these clips.
"""
import shutil
import sys
from pathlib import Path

from gradio_client import Client, handle_file

HERE = Path(__file__).resolve().parent
OUT = HERE / "gestures"
OUT.mkdir(exist_ok=True)
FRAME = ("https://raw.githubusercontent.com/claude78666-stack/claude-./ccr-30384992-9yfph0/"
         "character/sifa-intro/ai/sifa_seat_crop.png")
LOOK = ("Photorealistic video. A young woman with long wavy blonde hair, black hoodie and headphones around her neck "
        "sits in a gaming chair and talks to the camera like a streamer. ")
STEADY = " Gentle natural head movement and blinking, friendly expression. Static camera, no zoom, steady lighting."
CLIPS = {
    "rest":   "She keeps both hands relaxed on the armrests and talks calmly, small nods.",
    "palm":   "While speaking she lifts her right hand slightly from the armrest, makes a small relaxed open-palm "
              "gesture, then lowers it back to rest.",
    "point":  "She briefly points with her right hand toward the side of the screen as if showing something, "
              "then rests her hand again.",
    "both":   "She lifts both hands a little and makes a short, natural explaining gesture, then puts them back on "
              "the armrests.",
    "nod":    "She nods and gives a small happy shrug of her shoulders, hands staying on the armrests.",
}


def main():
    client = Client("mcp-tools/wan-2-2-first-last-frame")
    for name in sys.argv[1:] or CLIPS:
        out = OUT / f"{name}.mp4"
        if out.exists():
            continue
        res = client.predict(start_image_pil=handle_file(FRAME), end_image_pil=handle_file(FRAME),
                             prompt=LOOK + CLIPS[name] + STEADY, duration_seconds=4, steps=8,
                             randomize_seed=False, seed=7, api_name="/generate_video")
        video = res[0] if isinstance(res, (list, tuple)) else res
        video = video.get("video", video) if isinstance(video, dict) else video
        shutil.copy(video, out)
        print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
