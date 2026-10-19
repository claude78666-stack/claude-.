# Plan: Gears of War E-Day explainer v2 (`sifa_eday_explainer_v2_1080p.mp4`)

Working method borrowed from Claudex Loop: recon → plan with acceptance criteria → build → independent
inspection by a reviewer that did not build it → findings log with a disposition for each → bounded rounds.

## Assumptions ledger (recon)

| # | Assumption | Source |
|---|---|---|
| A1 | The user wants Sifa without her room ("wallpaper") while gameplay plays, more motion graphics, hand gestures kept. | User messages, 19 Oct 2026 |
| A2 | No Blender in the final videos. | User: "don't do anything in blender" |
| A3 | Footage = Xbox's official E-Day trailers from the Steam store page, credited on screen; no YouTube downloads. | Earlier decision; Microsoft Game Content Usage Rules |
| A4 | Never Runway. | `CLAUDE.md` |
| A5 | Photoreal hand gestures / chair turn need a free image-to-video tool that is not reachable from this session; v2 keeps lip-sync + subtle drift only. | Veo 429 on free tier; HF Spaces not authenticated; Kling not signed in |
| A6 | Sifa's voice = Gemini TTS Laomedeia for sections, `voice.wav` for the intro. | Voice-match tests |

## Goals and acceptance criteria

1. **Cut-out Sifa**: in every gameplay section, Sifa appears bottom-left, waist-up, with no room, sign or
   chair visible behind her; neon glow; mouth moves with her words.
2. **Cold open** (≈10 s) before the talking intro: montage, slam-in title fully on screen, hook line audible.
3. **Chapter wipe** at the start of every section with the correct number and heading, fully legible.
4. **Fact badges** pop in one at a time, matching what she is saying, never overlapping captions or Sifa.
5. **Captions** word-by-word, the highlighted word matches the spoken word within about half a second,
   never cover Sifa, the badges or the footage credit.
6. **Subscribe reminder** appears twice and is not covered by the game HUD.
7. **Audio**: voice clearly above music and SFX, no clipping, integrated loudness −14 LUFS ± 1.5.
8. **Length** 8–9.5 minutes; ends on the SIFA SI sign-off.
9. **Credit** "Footage: Xbox / The Coalition" visible in every gameplay section.

## Verification (on the real output file)

- `ffprobe` duration; `ebur128` loudness.
- Frame samples every 10 s plus the first 2 s of every section (wipe) checked visually.
- Caption/voice sync spot-checked by transcribing 3 sections and comparing word times.

## Non-goals

- Photoreal hand gestures and chair turn (blocked, see A5).
- Re-voicing the script.

## Risks

- Proportional caption timing can drift inside long sentences.
- Segmentation edge halos around her hair on bright footage.

## Review rounds

Up to 2 inspection rounds; unresolved findings are reported to the user, not forced.

## Findings log

### Round 1 (independent reviewer, on the first full render)

| # | Severity | Criterion | Finding | Disposition |
|---|---|---|---|---|
| 1 | blocking | 7 | Audio clipped at section seams / whooshes (true peak +1.0 dBTP) | Fixed: `alimiter` after loudnorm (limit 0.79) |
| 2 | blocking | 5 | Captions drifted up to ~1.5 s (proportional timing) | Fixed: words aligned to the voice with local faster-whisper (`small.en`), numbers expanded to words before matching |
| 3 | minor | 6 | Subscribe pill sat on the game's ammo HUD | Fixed: moved down to y 270–350 |
| 4 | minor | 2 | Slam-in title ran off both edges for ~0.15 s | Fixed: start scale 1.06 instead of 1.6 |
| 5 | minor | 4 | Some badges early/late vs the words | Fixed: badges pop on the aligned time of their keyword |
| 6 | minor | 1/5 | Trailer title cards, ESRB card and black fades show through in a few cuts | Open: needs re-cutting `cuts.json`, reported to the user |
| 7 | minor | 9 | No footage credit in the cold open | Fixed: credit added |
| 8 | note | 3 | Chapters numbered 01–15 while ids say 02b/13 | No change: numbering is intended |
