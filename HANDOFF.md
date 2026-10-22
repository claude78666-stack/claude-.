# Handoff: Sifa E-Day explainer (read this first in a new session)

Branch: `ccr-30384992-9yfph0` (PR #1, base `claude/busy-davinci-0rym9a`). Work only on this branch.

## Who / what

Sifa is an "SI agent" AI YouTube host (long wavy blonde hair, black hoodie, headphones, purple-neon gaming room).
The current deliverable is an ~9 min **Gears of War: E-Day explainer (v2)**:
`character/sifa-intro/longform/sifa_eday_explainer_v2_1080p.mp4` (the committed copy is re-encoded to stay under GitHub's 100 MB limit).

What the owner wants (keep all of it):

- Motion graphics, fact badges and word-aligned captions. Gameplay fills the screen, and Sifa is cut out at the
  bottom left: **clean, with no wallpaper and no purple glow**.
- Natural human head movement, blinks and breathing, done.
- **Hand gestures every 15–30 s that fit the script.** One of them is the "yes" gesture (fist bobbing with a nod)
  from the owner's reference Short. The plan is in `longform/gestures.json` (27 gestures).
- Best possible quality and realism.

## Hard rules

- **Never use Runway** (see `CLAUDE.md`). No Blender work.
- Never ask the owner to paste tokens into chat. Tokens go in the environment settings only (`HF_TOKEN` is set).
- The owner's free Hugging Face ZeroGPU quota, Veo (Gemini API, no billing) and Kling (no credits) all fail, so
  the owner makes the gesture clips themselves in **Google Flow**. The prompts and settings are in
  `character/sifa-intro/ai/FLOW-GESTURES.md`.

## Pipeline (`character/sifa-intro/longform/`)

| File | Role |
|---|---|
| `render_v2.py` | Main renderer: sections (gameplay, cut-out Sifa, captions, badges) → cold open, intro, outro, music bed, loudnorm −14 LUFS → `build/v2/sifa_eday_explainer_v2_master.mp4` (crf 17) and the 1250k git copy |
| `sifa_motion.py` | LivePortrait head-motion loop (`build/v2/sifa_loop.mp4`, copy committed in `cache/`) and the per-frame MediaPipe matte (`mask_video`, gesture-aware) |
| `sifa_gestures.py` | Gestures: registers each Flow clip back onto `ai/shot1_last_1080.png` (SIFT; removes Veo's camera zoom), crops the 700x640 facecam box (680,150,1380,790), colour-matches it, keeps the gesture span (`SPANS`, picked by eye from `build/v2/gest_<clip>_sheet.jpg`), and crossfades it into the loop at the `gestures.json` times → `build/v2/track_<sid>.mp4` |
| `plan_gestures.py` | Writes `gestures.json` from the aligned words (yes / count / point / both / palm rules) |
| `make_gameplay_cuts.py` + `cuts.json` | Gameplay backdrops `gameplay/<sid>.mp4` from the official Xbox trailers (Steam), skipping black frames |
| `make_voice.py` | Gemini TTS, voice Laomedeia |

Lip-sync is Wav2Lip (`WAV2LIP=<checkout>`, checkpoint `checkpoints/wav2lip_gan.pth`). **Fixed bug:** Wav2Lip's `--static`
uses `type=bool`, so the flag is only passed for stills. Before the fix the head motion never reached the video.

### Rebuilding in a fresh container (build/ and gameplay/ are git-ignored)

1. `pip install mediapipe opencv-python scipy faster-whisper gradio_client` and clone Wav2Lip, with
   `wav2lip_gan.pth` and `s3fd` face detection weights.
2. `mkdir -p longform/build/v2 && cp longform/cache/sifa_loop.mp4 longform/cache/align_*.json longform/build/v2/`
3. Voices: `python3 make_voice.py` (or use `longform/voice/*.wav`, which is committed). Gameplay:
   `python3 make_gameplay_cuts.py`.
4. Render: `WAV2LIP=... python3 render_v2.py`. Use `python3 render_v2.py <section_id>` for one test section.
   The cached `face_*`, `mask_*` and `section_*` files in `build/v2` must be deleted to re-render.

## Status (2026-10-22)

- Done: v2.2 render (aligned captions, clean cut-out, no clipping, gameplay with black frames skipped).
- Done: the gesture pipeline, tested with the owner's first Flow clip `ai/gestures/flow_yes.mp4`
  (preview: `longform/test_yes_gesture.mp4`, section 02_when, on the word "finally").
- Waiting on the owner for the Flow clips `palm.mp4` (11 uses), `count.mp4` (6), `point.mp4` (3) and `both.mp4` (3),
  plus the optional `yes2` / `palm2` / `count2`. For each new clip: put it in `ai/gestures/`, check its contact
  sheet, add its `SPANS` entry, and add it to `KINDS` if the file name differs.
- To do: a sliver of the purple chair sometimes shows at her left shoulder (screen right) in the live matte, so
  tighten the matte there. Then do the full re-render (a few hours on CPU), send the video to the owner, and
  commit the 1250k copy.
- PR #1: no reviews and no CI. The safety-net check-ins have stopped.
