# SI Agents token explainer video (Remotion)

A 60 second, 1920x1080, 30 fps video explaining the planned SI Agents token. Built with Remotion (React + TypeScript). The music is synthesized by a small Python script. No voiceover: the message is carried by on-screen text, so it works muted on social.

| Time | Scene | Message |
|---|---|---|
| 0:00 | Hook | Ten robots. Ten egos. One token. |
| 0:06 | What is it | A pass to use the SI Agents tools |
| 0:14 | What you get | Free for everyone, extras for holders (planned) |
| 0:25 | The plan | Tool use, USDC fee, half buys back the token, burn (with a made-up worked example) |
| 0:36 | Real tools | Coin Sniffer, Judge SI, Banker SI, Professor SI |
| 0:47 | The honest part | Not an investment, no dividends, not launched, may change |
| 0:55 | Outro | SI Agents. Pick an agent. |

Everything said about the token matches the website's Treasury page: it is a planned pass to use the tools, not an investment, and no coin exists yet.

## Render

```bash
cd video
npm install
npm run music        # writes public/music.wav (about 20 seconds, plain Python)
npm run render       # out/si-agents-token.mp4
npm run studio       # live preview in the browser
```

Node 20+ and Python 3 are needed. Fonts (Space Grotesk, Inter) and the character images are bundled in `public/`, so rendering needs no internet. If Remotion cannot find a browser it downloads one on first run.

## Change things

- Text and timing: each scene is a file in `src/scenes/`. Scene lengths are listed in `src/Video.tsx` (the total must stay 1800 frames for 60 seconds; the music script reads the same cut times).
- Colours, fonts and shared pieces: `src/ui.tsx`.
- Characters: `public/characters/*.jpg` (made from `character/realistic/`).
- Music: `scripts/make_music.py`. Re-run `npm run music` after changing scene lengths so the risers still land on the cuts.
- Renaming the project: search for "SI Agents" in `src/`.
