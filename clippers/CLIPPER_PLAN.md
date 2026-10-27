# Auto-clipper plan (NOT installed yet)

Status: **planned only. Do not install or build until the user opens a new
Mac session and the repo files have been transferred there.** Then set it up
on the Mac (YouTube blocks downloads from the cloud).

Inspired by the free "Claude-Video-Clipper" skill (video: https://youtu.be/IY08-3TS2o8).
Do not buy the Skool course; build our own version.

## Pipeline
1. Download: yt-dlp (on the Mac only; never copy browser cookies elsewhere).
2. Transcribe: Whisper, local, with word-level timestamps.
3. Pick moments: read the full transcript; the clip must stand alone for a stranger,
   open with a hook (bold claim, surprising fact, contrarian take, story opener),
   skip warm-ups, and end on a payoff. Score each clip out of 10 and rank them.
4. Crop: OpenCV face tracking to 1080x1920, re-framing on each camera cut.
5. Edit (optional per campaign, see rules below): word-by-word captions in
   Mentor Archive gold #f6dc96, zooms at the ends of sentences, whoosh/click SFX
   (royalty-free only).
6. Output: ranked MP4s named after their titles, plus title, caption, hashtags and
   the target campaign for each clip.

## Campaign rules come first (money protection)
Before every batch, read the campaign brief on Whop/Vyro and set a profile:
- `effects`: zooms and SFX on or off. **Default OFF** unless the brief allows them.
- `captions`: our style, or the campaign's required style/font/position.
- Required tags, links, mentions, watermark or no-watermark, min/max length,
  allowed source videos, no music if banned.
- If a brief is unclear, ask the user before posting. A clip that breaks the rules
  gets rejected and earns $0, so never guess.
- One clip goes to one campaign only.
