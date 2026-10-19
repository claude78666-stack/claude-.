#!/usr/bin/env python3
"""Living Sifa for the explainer: real head movement, blinks and expressions instead of a still photo.

  python3 sifa_motion.py <liveportrait_output.mp4>
    -> build/v2/sifa_loop.mp4, a seamless forward+backward loop that render_v2.py lip-syncs (Wav2Lip, moving
       video mode) and cuts out frame by frame.

The motion comes from LivePortrait (open source, run locally on CPU) driving cut_rgb.png with a calm
to-camera talking clip. mask_video() makes the per-frame cut-out matte with MediaPipe's selfie segmenter.
"""
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build" / "v2"
LOOP = BUILD / "sifa_loop.mp4"
SEG_MODEL = BUILD / "selfie_multiclass_256x256.tflite"
SEG_URL = ("https://storage.googleapis.com/mediapipe-models/image_segmenter/selfie_multiclass_256x256/"
           "float32/latest/selfie_multiclass_256x256.tflite")
FPS = 24
HEAD_Y = 300   # neck line in cut_rgb.png: above it the head moves, below it the body stays put


def run(cmd):
    subprocess.run(cmd, check=True)


def make_loop(src):
    """Forward then backward, so the end meets the start with no jump."""
    run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex",
         f"[0:v]fps={FPS},split[a][b];[b]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[r];[a][r]concat=n=2:v=1[v]",
         "-map", "[v]", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(LOOP)])
    return LOOP


def frames(path):
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=width,height", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    w, h = map(int, probe.stdout.strip().split(","))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE)
    while True:
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    p.wait()


def mask_video(src, out, clean, still):
    """Per-frame matte of Sifa as lossless gray video. Only her head moves in the LivePortrait loop, so the body
    keeps the clean still matte (`still`, no chair) and the per-frame matte is used around the head only, and
    only inside a slightly widened copy of the still outline, so the purple chair back never comes along."""
    if out.exists():
        return out
    from scipy import ndimage
    ref = np.asarray(still).astype(float) / 255
    near = ndimage.gaussian_filter(ndimage.grey_dilation(ref, size=(25, 25)), 3)
    h = ref.shape[0]
    head = np.clip((HEAD_Y + 20 - np.arange(h)) / 40.0, 0, 1)[:, None]   # 1 above the neck, 0 below
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    if not SEG_MODEL.exists():
        urllib.request.urlretrieve(SEG_URL, SEG_MODEL)
    opts = vision.ImageSegmenterOptions(base_options=BaseOptions(model_asset_path=str(SEG_MODEL)),
                                        output_confidence_masks=True)
    enc = None
    with vision.ImageSegmenter.create_from_options(opts) as seg:
        for f in frames(src):
            conf = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f))).confidence_masks
            p = sum(conf[k].numpy_view() for k in (1, 2, 3, 4)) + 0.6 * conf[5].numpy_view()
            p = np.clip((np.squeeze(p) - 0.45) / 0.25, 0, 1)
            from PIL import Image
            live = np.asarray(clean(Image.fromarray((p * 255).astype(np.uint8), "L"))).astype(float) / 255
            m = head * np.minimum(live, near) + (1 - head) * ref
            m = (np.clip(m, 0, 1) * 255).astype(np.uint8)
            if enc is None:
                h, w = m.shape
                enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
                                        "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-", "-c:v", "ffv1", str(out)],
                                       stdin=subprocess.PIPE)
            enc.stdin.write(m.tobytes())
    enc.stdin.close()
    enc.wait()
    return out


if __name__ == "__main__":
    print("wrote", make_loop(sys.argv[1]))
