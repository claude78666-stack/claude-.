# Motion Studio

Make motion graphics by describing them to Claude Code. Claude writes the code and these tools render it to video.

| Tool | Used for | Where |
|---|---|---|
| [Remotion](https://www.remotion.dev) | Turns React code into MP4 video (the main engine) | `src/` |
| [Remotion Skills](https://github.com/remotion-dev/skills) | Official Claude Code skills for Remotion | `../.claude/skills/remotion-*` |
| [GSAP](https://gsap.com) | Text and timeline animation | `src/scenes/GsapText.tsx` |
| [anime.js](https://animejs.com) | Staggered icon and UI motion | `src/scenes/AnimeGrid.tsx` |
| [three.js](https://threejs.org) + [React Three Fiber](https://r3f.docs.pmnd.rs) | 3D scenes, cameras, lighting | `src/scenes/ThreeScene.tsx` |
| [Rive](https://rive.app) | Designer-made animations (`.riv` files) | `src/scenes/RiveScene.tsx` |
| [Satori](https://github.com/vercel/satori) | Title cards and images generated from code | `scripts/title-card.mjs` |
| [FFmpeg](https://ffmpeg.org) | Resizes renders to square and landscape | `scripts/resize.mjs` |
| [Motion Canvas](https://motioncanvas.io) | Explainer and diagram animations | `motion-canvas/` |

## Quick start

```bash
cd motion-studio
npm install
npm run studio      # live preview in the browser at http://localhost:3000
npm run render      # renders out/showcase.mp4 (1080x1920, 15s)
npm run resize      # makes out/showcase-square.mp4 and out/showcase-landscape.mp4 (needs ffmpeg)
```

Motion Canvas is a separate project:

```bash
cd motion-studio/motion-canvas
npm install
npm start           # opens the Motion Canvas editor; press RENDER there to export
```

## Using it with Claude Code

Open Claude Code in this repo and describe what you want, for example:

> Make a 10-second vertical Remotion video: the Axolotlion logo bounces in, then GSAP types "Coming soon" letter by letter.

The Remotion skills in `.claude/skills` load automatically and teach Claude Remotion's best practices (`/remotion-create`, `/remotion-render`, `/remotion-captions` and more).

## How the pieces stay in sync

Remotion renders each frame separately, sometimes out of order, so every animation library is driven by Remotion's frame number instead of its own clock:

- **GSAP**: a paused timeline, seeked with `tl.seek(frame / fps)`.
- **anime.js**: `autoplay: false`, seeked with `anim.seek(ms)`.
- **three.js**: `@remotion/three`'s `<ThreeCanvas>` passes the frame to the scene.
- **Rive**: the animation's `time` is set to `frame / fps` before each draw. The Rive engine (`public/rive.wasm`) is bundled so renders work offline.

## Licences to know about

- **Remotion** is free for individuals and companies with up to 3 people. Larger companies need a [company licence](https://www.remotion.pro/license).
- **GSAP** is free, including its plugins, under its own [standard licence](https://gsap.com/standard-license) (not MIT).
- **Rive**: the runtime is MIT. The Rive editor you design `.riv` files in has free and paid plans. `public/vehicles.riv` is Rive's public sample file.
- **Inter** font (`public/Inter-Black.otf`) is under the SIL Open Font License.
- Everything else here is MIT or similarly permissive.

## Axolotl short (30s example)

`npm run render:axolotl` renders `out/axolotl-short.mp4`: a 30-second vertical animal-facts short.

- Scenes: `src/axolotl/AxolotlShort.tsx`; the axolotl itself is a hand-drawn SVG in `src/axolotl/Axolotl.tsx`.
- Narration: `public/axolotl/line1-6.wav`, made with the free, local [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M) voice. Scene lengths follow `lines.json`, so re-recording a line re-times the video automatically.
- Music, whoosh and pop are synthesized in code, so there are no licensing worries.
