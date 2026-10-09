import React, {useEffect, useState} from 'react';
import * as THREE from 'three';
import {ThreeCanvas} from '@remotion/three';
import {AbsoluteFill, Audio, continueRender, delayRender, Easing, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {body, display} from '../ui';
import {HeroTex, shotAt, SHOTS, World} from './si/World';

export const SI_FPS = 30;
export const SI_TOTAL = 64 * SI_FPS;

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const out = Easing.out(Easing.cubic);
const fade = (t: number, a: number, b: number, f = 0.6) => interpolate(t, [a, a + f, b - f, b], [0, 1, 1, 0], clamp);

/* load the 73 turntable frames (0-180 degrees, every 2.5 degrees) once */
const useHeroTextures = (): HeroTex | null => {
  const [tex, setTex] = useState<HeroTex | null>(null);
  const [handle] = useState(() => delayRender('Loading character frames'));
  useEffect(() => {
    const loader = new THREE.TextureLoader();
    Promise.all(
      Array.from({length: 73}, (_, i) =>
        loader.loadAsync(staticFile(`axolotlion/tt/tt_${String(i).padStart(3, '0')}.webp`)).then((t) => {
          t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.minFilter = THREE.LinearMipmapLinearFilter; return t;
        }),
      ),
    )
      .then((frames) => { setTex({frames}); continueRender(handle); })
      .catch((e) => { console.error(e); continueRender(handle); });
  }, [handle]);
  return tex;
};

const Mark: React.FC<{t: number; a: number; b: number; children: React.ReactNode; style?: React.CSSProperties}> = ({t, a, b, children, style}) => {
  const o = fade(t, a, b);
  if (o <= 0) return null;
  const y = interpolate(t, [a, a + 1.1], [16, 0], {...clamp, easing: out});
  const blur = interpolate(t, [a, a + 0.8], [8, 0], clamp);
  return <div style={{position: 'absolute', opacity: o, transform: `translateY(${y}px)`, filter: `blur(${blur}px)`, ...style}}>{children}</div>;
};
const Eyebrow: React.FC<{children: React.ReactNode}> = ({children}) => (
  <div style={{fontFamily: body, fontWeight: 500, fontSize: 21, letterSpacing: 12, textTransform: 'uppercase', color: 'rgba(225,245,255,.78)', textShadow: '0 2px 18px rgba(0,0,0,.7)'}}>{children}</div>
);
const Big: React.FC<{children: React.ReactNode; size?: number}> = ({children, size = 84}) => (
  <div style={{fontFamily: display, fontWeight: 500, fontSize: size, color: '#fff', marginTop: 12, letterSpacing: 2, textShadow: '0 4px 34px rgba(0,0,0,.7)'}}>{children}</div>
);
const Wordmark: React.FC<{size: number; spacing: number}> = ({size, spacing}) => (
  <div style={{fontFamily: display, fontWeight: 500, fontSize: size, letterSpacing: spacing, paddingLeft: spacing, color: '#fff', textShadow: '0 0 40px rgba(255,170,240,.6), 0 0 120px rgba(120,220,255,.4)'}}>AXOLOTLION</div>
);

export const SIFilm: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const t = frame / SI_FPS;
  const tex = useHeroTextures();
  const bars = 138;
  // dip to black on every cut
  const cutDip = Math.max(0, ...SHOTS.slice(1).map((s) => 1 - Math.abs(t - s.a) / 0.18)) * 0.9;
  const musicVol = interpolate(t, [0, 2, 56, 58.3, 61, 64], [0.5, 0.42, 0.42, 0.85, 0.8, 0], clamp);
  void shotAt;

  return (
    <AbsoluteFill style={{background: '#02070c'}}>
      <Audio src={staticFile('axolotlion/si/score.wav')} volume={musicVol} />
      <Audio src={staticFile('axolotlion/si/vo_fast.wav')} volume={1} />
      {tex && (
        <ThreeCanvas linear={false} width={width} height={height} gl={{antialias: true, preserveDrawingBuffer: true}} style={{filter: 'contrast(1.06) saturate(1.12)'}}>
          <World t={t} tex={tex} />
        </ThreeCanvas>
      )}

      {/* lens: vignette, top light, bottom shade, grain */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 46%, rgba(0,5,12,.66) 100%)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(120,230,255,.06), rgba(0,0,0,0) 35%, rgba(0,0,0,0) 72%, rgba(0,6,14,.55))'}} />
      <AbsoluteFill style={{mixBlendMode: 'overlay', opacity: 0.14}}>
        <svg width="1920" height="1080">
          <filter id={`g${frame % 6}`}><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame % 6} /><feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.4 -.2" /></filter>
          <rect width="1920" height="1080" filter={`url(#g${frame % 6})`} />
        </svg>
      </AbsoluteFill>

      {/* typography, timed to the narration */}
      <Mark t={t} a={17.3} b={20.0} style={{left: 0, right: 0, bottom: 180, textAlign: 'center'}}><Wordmark size={112} spacing={26} /></Mark>
      <Mark t={t} a={20.1} b={28.5} style={{left: 150, bottom: 200}}>
        <Eyebrow>The first SI animal</Eyebrow>
        <Big size={72}>
          <span style={{opacity: interpolate(t, [23.3, 24.0], [0, 1], clamp)}}>Superior Intelligence</span>
          <span style={{opacity: interpolate(t, [26.7, 27.4], [0, 1], clamp), color: 'rgba(255,255,255,.55)'}}> — not AI</span>
        </Big>
      </Mark>
      <Mark t={t} a={29.0} b={32.4} style={{left: 150, bottom: 200}}><Eyebrow>The axolotl</Eyebrow><Big>Regeneration</Big></Mark>
      <Mark t={t} a={32.7} b={35.6} style={{left: 150, bottom: 200}}><Eyebrow>The lion</Eyebrow><Big>Leadership</Big></Mark>
      <Mark t={t} a={35.9} b={39.3} style={{left: 150, bottom: 200}}><Eyebrow>The jellyfish</Eyebrow><Big>Light</Big></Mark>
      <Mark t={t} a={39.6} b={45.1} style={{left: 0, right: 0, bottom: 200, display: 'flex', justifyContent: 'center', gap: 100, alignItems: 'center'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
          <Eyebrow>Built on</Eyebrow>
          <Img src={staticFile('axolotlion/solana.svg')} style={{height: 52}} />
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: 22, opacity: interpolate(t, [42.0, 42.7], [0, 1], clamp)}}>
          <Eyebrow>Gathered on</Eyebrow>
          <Img src={staticFile('axolotlion/pumpfun.png')} style={{height: 56, width: 56, objectFit: 'contain'}} />
          <span style={{fontFamily: display, fontWeight: 500, fontSize: 46, color: '#fff'}}>pump.fun</span>
        </div>
      </Mark>
      <Mark t={t} a={45.4} b={56.0} style={{left: 150, bottom: 200}}>
        <Eyebrow>A community that</Eyebrow>
        <Big size={78}>
          <span style={{opacity: interpolate(t, [47.1, 47.8], [0, 1], clamp)}}>Regrows</span>
          <span style={{opacity: interpolate(t, [50.7, 51.4], [0, 1], clamp)}}> · Leads</span>
          <span style={{opacity: interpolate(t, [53.4, 54.1], [0, 1], clamp)}}> · Glows</span>
        </Big>
      </Mark>
      <Mark t={t} a={56.3} b={58.2} style={{left: 0, right: 0, bottom: 200, textAlign: 'center'}}><Eyebrow>Join the pack</Eyebrow></Mark>
      <Mark t={t} a={58.3} b={64.5} style={{left: 0, right: 0, top: 170, textAlign: 'center'}}>
        <Wordmark size={128} spacing={30} />
        <div style={{fontFamily: body, fontWeight: 500, fontSize: 24, letterSpacing: 14, paddingLeft: 14, textTransform: 'uppercase', color: 'rgba(230,245,255,.8)', marginTop: 22}}>The first SI animal</div>
      </Mark>

      {/* letterbox, cut dips, head and tail fades */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 0, height: bars, background: '#000'}} />
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 0, height: bars, background: '#000'}} />
      <AbsoluteFill style={{background: '#000', opacity: Math.max(cutDip, interpolate(frame, [0, 30, SI_TOTAL - 45, SI_TOTAL], [1, 0, 0, 1], clamp))}} />
    </AbsoluteFill>
  );
};
