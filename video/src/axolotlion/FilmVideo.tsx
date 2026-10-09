import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, interpolate, OffthreadVideo, random, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {body, display} from '../ui';

export const FILM_FPS = 30;
export const FILM_TOTAL = 1440; // 48 s

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const out = Easing.out(Easing.cubic);
const fade = (t: number, a: number, b: number, f = 0.7) => interpolate(t, [a, a + f, b - f, b], [0, 1, 1, 0], clamp);

/* ---------- shot list: every shot is AI-generated footage of the character or its world ---------- */
type Shot = {a: number; b: number; src: string; rate: number; zoom: number; fx?: number};
const SHOTS: Shot[] = [
  {a: 0, b: 7.2, src: 's1', rate: 0.85, zoom: 0.05},
  {a: 6.4, b: 11.8, src: 's2', rate: 0.95, zoom: 0.04},
  {a: 11.2, b: 17.9, src: 's3', rate: 0.9, zoom: 0.03},
  {a: 17.3, b: 22.9, src: 's4', rate: 0.9, zoom: 0.04},
  {a: 22.3, b: 29.0, src: 's5', rate: 0.9, zoom: 0.03},
  {a: 28.4, b: 35.6, src: 's6', rate: 0.84, zoom: 0.03},
  {a: 35.0, b: 42.2, src: 's7', rate: 0.84, zoom: 0.04},
];

const Footage: React.FC<{t: number}> = ({t}) => (
  <AbsoluteFill>
    {SHOTS.map((s, i) => {
      const pad = 0.7;
      const op = interpolate(t, [s.a, s.a + pad, s.b - pad, s.b], [i === 0 ? 1 : 0, 1, 1, 0], clamp);
      if (op <= 0) return null;
      const from = Math.max(0, Math.floor(s.a * FILM_FPS));
      const dur = Math.ceil((s.b - s.a) * FILM_FPS) + 1;
      const k = (t - s.a) / (s.b - s.a);
      return (
        <Sequence key={i} from={from} durationInFrames={dur} layout="none">
          <AbsoluteFill style={{opacity: op, transform: `scale(${1.02 + s.zoom * k})`}}>
            <OffthreadVideo src={staticFile(`axolotlion/pro/${s.src}.mp4`)} muted playbackRate={s.rate} style={{width: 1920, height: 1080, objectFit: 'cover'}} />
          </AbsoluteFill>
        </Sequence>
      );
    })}
    {/* end card plate: the pack key art, slow push-in */}
    <AbsoluteFill style={{opacity: interpolate(t, [41.2, 42.4], [0, 1], clamp)}}>
      <Img src={staticFile('axolotlion/pro/k5.jpg')} style={{width: 1920, height: 1080, transform: `translateY(48px) scale(${1.07 + Math.max(0, t - 41.2) * 0.012})`}} />
    </AbsoluteFill>
  </AbsoluteFill>
);

/* ---------- grade: vignette, grain, soft bloom, letterbox ---------- */
const Grain: React.FC<{frame: number}> = ({frame}) => {
  const seed = frame % 6;
  return (
    <AbsoluteFill style={{mixBlendMode: 'overlay', opacity: 0.16, pointerEvents: 'none'}}>
      <svg width="1920" height="1080" style={{position: 'absolute', inset: 0}}>
        <filter id={`n${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={seed} stitchTiles="stitch" />
          <feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.4 -.2" />
        </filter>
        <rect width="1920" height="1080" filter={`url(#n${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};

const Mark: React.FC<{t: number; a: number; b: number; children: React.ReactNode; style?: React.CSSProperties}> = ({t, a, b, children, style}) => {
  const o = fade(t, a, b, 0.6);
  if (o <= 0) return null;
  const y = interpolate(t, [a, a + 1.0], [18, 0], {...clamp, easing: out});
  return <div style={{position: 'absolute', opacity: o, transform: `translateY(${y}px)`, ...style}}>{children}</div>;
};

const Eyebrow: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{fontFamily: body, fontWeight: 500, fontSize: 22, letterSpacing: 12, textTransform: 'uppercase', color: 'rgba(255,255,255,.78)', textShadow: '0 2px 18px rgba(0,0,0,.6)'}}>{children}</div>
);

const Wordmark: React.FC<{size: number; spacing: number}> = ({size, spacing}) => (
  <div style={{fontFamily: display, fontWeight: 500, fontSize: size, letterSpacing: spacing, color: '#fff', textShadow: '0 0 40px rgba(255,170,240,.55), 0 0 120px rgba(120,200,255,.35)', paddingLeft: spacing}}>AXOLOTLION</div>
);

export const FilmVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FILM_FPS;
  const bars = 138; // 2.39:1 letterbox
  const musicVol = interpolate(t, [0, 3, 41.4, 43, 46, 48], [0.35, 0.5, 0.5, 0.95, 0.9, 0], clamp);

  return (
    <AbsoluteFill style={{background: '#02050b', overflow: 'hidden'}}>
      <Audio src={staticFile('axolotlion/pro/score.mp3')} volume={musicVol} />
      <Audio src={staticFile('axolotlion/pro/vo2.mp3')} volume={1} startFrom={0} />
      <div style={{position: 'absolute', inset: 0, filter: 'contrast(1.07) saturate(1.08)'}}>
        <Footage t={t} />
      </div>

      {/* depth: vignette and bloom */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 48%, rgba(0,0,0,0) 45%, rgba(0,4,12,.62) 100%)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,8,20,.35), rgba(0,0,0,0) 30%, rgba(0,0,0,0) 70%, rgba(0,6,16,.5))'}} />
      <Grain frame={frame} />

      {/* typography */}
      <Mark t={t} a={14.7} b={17.6} style={{left: 0, right: 0, bottom: 175, textAlign: 'center'}}>
        <Wordmark size={110} spacing={26} />
      </Mark>
      <Mark t={t} a={17.5} b={22.6} style={{left: 150, bottom: 205}}>
        <Eyebrow>The first SI animal</Eyebrow>
        <div style={{fontFamily: display, fontWeight: 500, fontSize: 72, color: '#fff', marginTop: 16, letterSpacing: 2, textShadow: '0 4px 30px rgba(0,0,0,.6)'}}>
          Superior Intelligence<span style={{color: 'rgba(255,255,255,.55)'}}> — not AI</span>
        </div>
      </Mark>
      <Mark t={t} a={23.0} b={26.6} style={{left: 150, bottom: 205}}>
        <Eyebrow>The axolotl</Eyebrow>
        <div style={{fontFamily: display, fontWeight: 500, fontSize: 84, color: '#fff', marginTop: 12, letterSpacing: 2, textShadow: '0 4px 30px rgba(0,0,0,.6)'}}>Regeneration</div>
      </Mark>
      <Mark t={t} a={26.9} b={28.6} style={{left: 150, bottom: 205}}>
        <Eyebrow>The lion</Eyebrow>
        <div style={{fontFamily: display, fontWeight: 500, fontSize: 84, color: '#fff', marginTop: 12, letterSpacing: 2, textShadow: '0 4px 30px rgba(0,0,0,.6)'}}>Leadership</div>
      </Mark>
      <Mark t={t} a={28.8} b={31.0} style={{left: 150, bottom: 205}}>
        <Eyebrow>The jellyfish</Eyebrow>
        <div style={{fontFamily: display, fontWeight: 500, fontSize: 84, color: '#fff', marginTop: 12, letterSpacing: 2, textShadow: '0 4px 30px rgba(0,0,0,.6)'}}>Light</div>
      </Mark>
      <Mark t={t} a={31.1} b={35.6} style={{left: 0, right: 0, bottom: 190, display: 'flex', justifyContent: 'center', gap: 90, alignItems: 'center'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 22, opacity: interpolate(t, [31.1, 31.8], [0, 1], clamp)}}>
          <Eyebrow>Built on</Eyebrow>
          <Img src={staticFile('axolotlion/solana.svg')} style={{height: 54}} />
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: 22, opacity: interpolate(t, [33.0, 33.8], [0, 1], clamp)}}>
          <Eyebrow>Gathered on</Eyebrow>
          <Img src={staticFile('axolotlion/pumpfun.png')} style={{height: 58, width: 58, objectFit: 'contain', borderRadius: 14}} />
          <span style={{fontFamily: display, fontWeight: 500, fontSize: 46, color: '#fff'}}>pump.fun</span>
        </div>
      </Mark>
      <Mark t={t} a={36.0} b={41.3} style={{left: 150, bottom: 205}}>
        <Eyebrow>A community that</Eyebrow>
        <div style={{fontFamily: display, fontWeight: 500, fontSize: 78, color: '#fff', marginTop: 12, letterSpacing: 2, textShadow: '0 4px 30px rgba(0,0,0,.6)'}}>
          <span style={{opacity: interpolate(t, [36.1, 36.8], [0, 1], clamp)}}>Regrows</span>
          <span style={{opacity: interpolate(t, [38.0, 38.7], [0, 1], clamp)}}> · Leads</span>
          <span style={{opacity: interpolate(t, [39.6, 40.3], [0, 1], clamp)}}> · Glows</span>
        </div>
      </Mark>
      <Mark t={t} a={41.8} b={48.5} style={{left: 0, right: 0, top: 150, textAlign: 'center'}}>
        <Wordmark size={130} spacing={30} />
        <div style={{fontFamily: body, fontWeight: 500, fontSize: 26, letterSpacing: 14, textTransform: 'uppercase', color: 'rgba(255,255,255,.8)', marginTop: 26, paddingLeft: 14}}>The first SI animal</div>
      </Mark>

      {/* letterbox + fades */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: bars, background: '#000'}} />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: bars, background: '#000'}} />
      <AbsoluteFill style={{background: '#000', opacity: interpolate(frame, [0, 24, FILM_TOTAL - 36, FILM_TOTAL], [1, 0, 0, 1], clamp), pointerEvents: 'none'}} />
    </AbsoluteFill>
  );
};
