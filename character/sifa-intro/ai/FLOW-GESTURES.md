# Sifa gesture clips in Google Flow

Eight short clips of Sifa sitting in her chair and making a hand gesture. I splice them into the E-Day explainer,
27 times in all (one every 15–30 s), lip-synced to her voice and cut out clean at the bottom left over the gameplay.

## Settings (the same for every clip)

| Setting | Value |
|---|---|
| Tool | Google Flow → **Frames to Video** |
| Model | **Veo 3.1 – Quality** (Fast is fine for tests, then remake the picks in Quality) |
| Start frame | `shot1_last_1080.png` (this folder) |
| End frame | **the same** `shot1_last_1080.png`, so every clip starts and ends on her rest pose |
| Aspect ratio | 16:9 (landscape) |
| Length | 8 s |
| Outputs per prompt | 2 (then keep the better one) |
| Download | **1080p** MP4 (Download → Upscaled 1080p) |

Audio does not matter. I replace it with her real voice and redo the lips with Wav2Lip.

## How to pick the take

Keep a take only if **all** of these are true:

1. The camera does not move or zoom, and the room stays the same.
2. Her face, hair, hoodie and headphones stay the same as the photo (no new jewellery, no colour change).
3. The hands look right: 5 fingers, no melting or extra hands.
4. The gesture happens in the **middle** of the clip (about 2–6 s), and her hands are back on the armrests by the end.
5. It looks calm and natural, like a streamer talking, not a dance.

If neither take passes, run the prompt again.

## The prompts

Paste each prompt into Flow exactly as written. Every prompt ends with the same "keep it steady" block.

### 1. `yes.mp4`: the "yes" gesture (4 uses, on lines like "absolutely", "finally", "worth it")

```
Photorealistic, natural streamer facecam. The young woman with long wavy blonde hair, black hoodie and headphones around her neck sits in the gaming chair in her purple-lit gaming room, hands resting on the armrests, talking to the camera with a warm smile. Around the two second mark she lifts her right hand to chest height, fingers loosely curled into a relaxed fist, and bobs it firmly down twice in a confident "yes, exactly" rhythm while nodding her head twice and smiling. Then she lowers the hand back onto the armrest and keeps talking calmly. Her lips move softly as if she is speaking. Locked-off static camera, no zoom, no camera movement, the room, lighting and her outfit stay exactly the same. Realistic hands with five fingers, smooth natural motion.
```

### 2. `yes2.mp4`: a second "yes" take (so the four "yes" moments don't all look the same)

```
Photorealistic, natural streamer facecam. The young woman with long wavy blonde hair, black hoodie and headphones around her neck sits in the gaming chair in her purple-lit gaming room, hands on the armrests, talking to the camera. Around the two second mark she gives one big approving nod, raises her right hand to shoulder height in a loose fist and gives a small, satisfied downward pump, like saying "yes, finally", with a bright smile. Then her hand returns to the armrest and she settles back, still talking. Her lips move softly as if she is speaking. Locked-off static camera, no zoom, no camera movement, the room, lighting and her outfit stay exactly the same. Realistic hands with five fingers, smooth natural motion.
```

### 3. `palm.mp4`: open-palm explaining gesture (11 uses, the most common one)

```
Photorealistic, natural streamer facecam. The young woman with long wavy blonde hair, black hoodie and headphones around her neck sits in the gaming chair in her purple-lit gaming room, hands on the armrests, explaining something to the camera. Around the two second mark she lifts her right hand a little off the armrest and turns it palm-up in a small, relaxed open-hand gesture, as if saying "so here's the thing", with a slight head tilt. After a moment the hand drifts back down onto the armrest. Her lips move softly as if she is speaking. Locked-off static camera, no zoom, no camera movement, the room, lighting and her outfit stay exactly the same. Realistic hands with five fingers, smooth natural motion.
```

### 4. `palm2.mp4`: second palm take (left hand, for variety)

```
Photorealistic, natural streamer facecam. The young woman with long wavy blonde hair, black hoodie and headphones around her neck sits in the gaming chair in her purple-lit gaming room, hands on the armrests, chatting to the camera. Around the two second mark she raises her left hand slightly and opens it outward in a small, casual "you know?" gesture, eyebrows raised, then rests it back on the armrest. Her lips move softly as if she is speaking. Locked-off static camera, no zoom, no camera movement, the room, lighting and her outfit stay exactly the same. Realistic hands with five fingers, smooth natural motion.
```

### 5. `count.mp4`: counting on fingers (6 uses, on "one", "two", "three")

```
Photorealistic, natural streamer facecam. The young woman with long wavy blonde hair, black hoodie and headphones around her neck sits in the gaming chair in her purple-lit gaming room, hands on the armrests, talking to the camera. Around the two second mark she raises her right hand to chest height and counts on her fingers: first she holds up one finger, then two fingers, then three fingers, nodding slightly with each one, clearly listing points. Then she lowers the hand back to the armrest. Her lips move softly as if she is speaking. Locked-off static camera, no zoom, no camera movement, the room, lighting and her outfit stay exactly the same. Realistic hands with five fingers, smooth natural motion.
```

### 6. `count2.mp4`: second counting take (just "one" and "two")

```
Photorealistic, natural streamer facecam. The young woman with long wavy blonde hair, black hoodie and headphones around her neck sits in the gaming chair in her purple-lit gaming room, hands on the armrests, talking to the camera. Around the two second mark she lifts her left hand and taps her index finger against it, one point, then her middle finger, two points, as if listing reasons, with a small smile. Then both hands return to the armrests. Her lips move softly as if she is speaking. Locked-off static camera, no zoom, no camera movement, the room, lighting and her outfit stay exactly the same. Realistic hands with five fingers, smooth natural motion.
```

### 7. `point.mp4`: pointing at the gameplay (3 uses, on "look at this", "see that")

```
Photorealistic, natural streamer facecam. The young woman with long wavy blonde hair, black hoodie and headphones around her neck sits in the gaming chair in her purple-lit gaming room, hands on the armrests, talking to the camera. Around the two second mark she raises her right hand and points casually up and to her left side, toward something on a screen, glancing that way for a moment with an excited "look at this" expression. Then she looks back at the camera and lowers her hand to the armrest. Her lips move softly as if she is speaking. Locked-off static camera, no zoom, no camera movement, the room, lighting and her outfit stay exactly the same. Realistic hands with five fingers, smooth natural motion.
```

### 8. `both.mp4`: both hands, "this is huge" (3 uses, on "huge", "massive", "all of it")

```
Photorealistic, natural streamer facecam. The young woman with long wavy blonde hair, black hoodie and headphones around her neck sits in the gaming chair in her purple-lit gaming room, hands on the armrests, talking to the camera. Around the two second mark she lifts both hands from the armrests and spreads them apart in front of her chest, palms facing each other, as if showing something big, with an impressed, enthusiastic expression. Then she brings both hands back down onto the armrests. Her lips move softly as if she is speaking. Locked-off static camera, no zoom, no camera movement, the room, lighting and her outfit stay exactly the same. Realistic hands with five fingers, smooth natural motion.
```

If you only have credits for five, make 1, 3, 5, 7 and 8. The second takes (2, 4, 6) are only for variety.

## Sending them to me

Name the files exactly as in the headings (`yes.mp4`, `palm.mp4`, …), then do either one of these:

- **GitHub (best):** open
  https://github.com/claude78666-stack/claude-./tree/ccr-30384992-9yfph0/character/sifa-intro/ai → **Add file** →
  **Upload files**, drag the MP4s in, and click **Commit changes** (keep "Commit directly to the
  `ccr-30384992-9yfph0` branch" selected). Each file must be under 25 MB, which an 8 s Flow clip is.
- **Google Drive:** put them in a folder, set sharing to "Anyone with the link", and paste the link to me.

Then tell me "gestures uploaded". I will:

1. Cut out the 1–2 s gesture from the middle of each clip and match its colours and position to the facecam.
2. Crossfade each one into the head-movement loop at the planned times in `longform/gestures.json`, so she is
   always back in the rest pose between gestures.
3. Lip-sync her voice over it, cut her out frame by frame (the hands included), re-render the whole video and send
   it to you.
