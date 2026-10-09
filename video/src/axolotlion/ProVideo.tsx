import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, interpolate, random, staticFile, useCurrentFrame} from 'remotion';
import {body, C, display} from '../ui';

export const PRO_FPS = 30;
export const PRO_TOTAL = 1500; // 50 seconds, narration is 49 s

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const inOut = Easing.inOut(Easing.cubic);
/** window opacity in seconds */
const win = (t: number, a: number, b: number, fade = 0.5) => interpolate(t, [a, a + fade, b - fade, b], [0, 1, 1, 0], clamp);
const rise = (t: number, a: number, d = 0.7, dist = 36) => ({
  opacity: interpolate(t, [a, a + d * 0.6], [0, 1], clamp),
  transform: `translateY(${interpolate(t, [a, a + d], [dist, 0], {...clamp, easing: Easing.out(Easing.cubic)})}px)`,
});
const kf = (t: number, ts: number[], vs: number[]) => interpolate(t, ts, vs, {...clamp, easing: inOut});

const GRAD = `linear-gradient(100deg, ${C.gold2}, #ff9be8 55%, ${C.cyan})`;
const gradText: React.CSSProperties = {backgroundImage: GRAD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'};

/* ---------- narration captions (timings measured from the voice track) ---------- */
const CAPS: Array<[number, number, string]> = [
  [1.0, 2.4, 'Meet Axolotlion.'],
  [2.85, 5.2, 'The first SI animal.'],
  [5.7, 7.9, 'Superior Intelligence.'],
  [8.4, 9.7, 'Not AI.'],
  [10.45, 12.6, 'He regrows what is lost.'],
  [13.35, 14.8, 'He leads the pack.'],
  [15.35, 17.5, 'And he glows in the dark.'],
  [18.65, 20.6, 'The axolotl regrows.'],
  [21.25, 22.8, 'The lion leads.'],
  [23.45, 25.3, 'The jellyfish glows.'],
  [25.9, 29.0, 'Three real strengths in one character.'],
  [29.8, 31.1, 'Built for Solana,'],
  [31.55, 33.0, 'with pump.fun.'],
  [33.65, 35.7, 'A coin about resilience.'],
  [36.25, 38.3, 'Regrow after every dip.'],
  [38.85, 40.4, 'Lead with conviction.'],
  [40.9, 42.0, 'Keep glowing.'],
  [42.55, 43.8, 'Join the pack.'],
  [44.55, 45.8, 'Axolotlion.'],
  [46.25, 48.6, 'The first SI animal.'],
];

/* ---------- hero: the 72-frame turntable, blended between neighbouring angles ---------- */
const Hero: React.FC<{t: number}> = ({t}) => {
  const ang = kf(t, [0, 4.6, 10, 18, 26, 34, 42, 44.5, 49.5], [0, 0, 100, 215, 330, 360, 360, 360, 360]);
  const f = ang / 5, i0 = Math.floor(f) % 72, i1 = (i0 + 1) % 72, k = f - Math.floor(f);
  const src = (i: number) => staticFile(`axolotlion/tt/tt_${String(i).padStart(3, '0')}.webp`);
  const T = [0, 5.2, 6.4, 10, 11.2, 18, 19.2, 25.6, 26.8, 33, 34.2, 42.2, 43.4, 49.5];
  const X = kf(t, T, [0, 0, -370, -370, -390, -390, 0, 0, -380, -380, -380, -380, 0, 0]);
  const Y = kf(t, T, [130, 130, 40, 40, 40, 40, -150, -150, 20, 20, 20, 20, -170, -170]);
  const S = kf(t, T, [0.92, 0.92, 0.8, 0.8, 0.8, 0.8, 0.84, 0.84, 0.8, 0.8, 0.8, 0.8, 0.7, 0.7]);
  const bob = Math.sin(t * 1.6) * 5;
  const W = 1500, H = W * 764 / 1400;
  const box: React.CSSProperties = {position: 'absolute', left: 960 - W / 2, top: 540 - H / 2, width: W, height: H};
  return (
    <div style={{...box, transform: `translate(${X}px, ${Y + bob}px) scale(${S * (1 + Math.sin(t * 1.1) * 0.006)})`}}>
      <Img src={src(i0)} style={{...box, left: 0, top: 0, filter: 'drop-shadow(0 0 30px rgba(255,120,225,.45)) drop-shadow(0 0 90px rgba(90,200,255,.32))'}} />
      {k > 0.02 && <Img src={src(i1)} style={{...box, left: 0, top: 0, opacity: k}} />}
    </div>
  );
};

const Particles: React.FC<{t: number}> = ({t}) => (
  <AbsoluteFill>
    {Array.from({length: 46}, (_, i) => {
      const x = random(`x${i}`) * 1920, sp = 8 + random(`s${i}`) * 26, size = 2 + random(`z${i}`) * 5;
      const y = (((random(`y${i}`) * 1200 - t * sp) % 1200) + 1200) % 1200 - 60;
      const hue = random(`h${i}`) > 0.5 ? '255,160,235' : '120,225,255';
      return <div key={i} style={{position: 'absolute', left: x + Math.sin(t * 0.7 + i) * 14, top: y, width: size, height: size, borderRadius: '50%', background: `rgba(${hue},${0.25 + random(`o${i}`) * 0.4})`, filter: 'blur(1px)'}} />;
    })}
  </AbsoluteFill>
);

const Kicker: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div style={{fontFamily: body, fontWeight: 600, fontSize: 24, letterSpacing: 7, textTransform: 'uppercase', color: C.muted, ...style}}>{children}</div>
);

const Card: React.FC<{t: number; at: number; title: string; sub: string; accent: string; icon: string; style?: React.CSSProperties}> = ({t, at, title, sub, accent, icon, style}) => (
  <div style={{...rise(t, at), padding: '26px 30px', borderRadius: 26, background: 'linear-gradient(160deg,rgba(255,255,255,.1),rgba(255,255,255,.035))', border: `1px solid ${C.line}`, boxShadow: `0 20px 60px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.18), 0 0 50px ${accent}22`, backdropFilter: 'blur(14px)', ...style}}>
    <div style={{display: 'flex', alignItems: 'center', gap: 20}}>
      <div style={{width: 74, height: 74, borderRadius: 22, display: 'grid', placeItems: 'center', fontSize: 40, background: `${accent}26`, border: `1px solid ${accent}77`}}>{icon}</div>
      <div>
        <div style={{fontFamily: display, fontWeight: 700, fontSize: 44, color: C.text, lineHeight: 1}}>{title}</div>
        <div style={{fontFamily: body, fontWeight: 500, fontSize: 25, color: C.muted, marginTop: 8}}>{sub}</div>
      </div>
    </div>
  </div>
);

const Badge: React.FC<{t: number; at: number; src: string; label: string; sub: string; round?: boolean}> = ({t, at, src, label, sub, round}) => (
  <div style={{...rise(t, at), display: 'flex', alignItems: 'center', gap: 26, padding: '24px 34px', borderRadius: 30, background: 'rgba(255,255,255,.07)', border: `1px solid ${C.line}`, boxShadow: '0 20px 60px rgba(0,0,0,.4)', width: 640}}>
    <Img src={staticFile(src)} style={{width: 92, height: 92, objectFit: 'contain', borderRadius: round ? 24 : 0}} />
    <div>
      <div style={{fontFamily: display, fontWeight: 700, fontSize: 52, color: C.text, lineHeight: 1}}>{label}</div>
      <div style={{fontFamily: body, fontWeight: 500, fontSize: 26, color: C.muted, marginTop: 8}}>{sub}</div>
    </div>
  </div>
);

export const ProVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / PRO_FPS;
  const cap = CAPS.find(([a, b]) => t >= a && t < b + 0.15);
  const capT = cap ? t - cap[0] : 0;
  const R: React.CSSProperties = {position: 'absolute', right: 120, width: 760};

  return (
    <AbsoluteFill style={{background: C.bg, overflow: 'hidden'}}>
      <Audio src={staticFile('axolotlion/pro/vo.mp3')} />
      <Img src={staticFile('axolotlion/bg.jpg')} style={{position: 'absolute', inset: -40, width: 2000, height: 1160, objectFit: 'cover', opacity: 0.55, transform: `scale(${1.06 + t * 0.0012}) translateX(${Math.sin(t * 0.25) * 22}px)`}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 55%, rgba(120,60,200,.22), rgba(6,4,15,.78) 70%), linear-gradient(180deg, rgba(6,4,15,.55), rgba(6,4,15,.2) 40%, rgba(6,4,15,.8))'}} />
      <Particles t={t} />

      {/* floor glow under the hero */}
      <div style={{position: 'absolute', left: 560, top: 870, width: 800, height: 90, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(255,140,230,.28), transparent 70%)', filter: 'blur(14px)', opacity: win(t, 0, 43, 1)}} />

      <Hero t={t} />

      {/* A: title */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 78, textAlign: 'center', opacity: win(t, 0.2, 5.4, 0.7)}}>
        <Kicker style={rise(t, 0.4)}>Introducing</Kicker>
        <div style={{...rise(t, 0.7, 1), fontFamily: display, fontWeight: 700, fontSize: 168, letterSpacing: -4, lineHeight: 1.02, ...gradText}}>AXOLOTLION</div>
      </div>

      {/* B: SI not AI */}
      <div style={{...R, top: 270, opacity: win(t, 5.5, 10.2, 0.6)}}>
        <Kicker style={rise(t, 5.7)}>The first SI animal</Kicker>
        <div style={{...rise(t, 5.8, 0.9), fontFamily: display, fontWeight: 700, fontSize: 104, lineHeight: 1.0, color: C.text, marginTop: 18}}>Superior<br />Intelligence</div>
        <div style={{...rise(t, 8.4, 0.8), display: 'flex', alignItems: 'center', gap: 24, marginTop: 40}}>
          <div style={{fontFamily: display, fontWeight: 700, fontSize: 96, ...gradText}}>SI</div>
          <div style={{fontFamily: display, fontWeight: 500, fontSize: 56, color: C.muted}}>is not</div>
          <div style={{fontFamily: display, fontWeight: 700, fontSize: 96, color: C.muted, textDecoration: 'line-through', textDecorationColor: C.red, textDecorationThickness: 8}}>AI</div>
        </div>
      </div>

      {/* C: regrow / lead / glow */}
      <div style={{...R, top: 230, opacity: win(t, 10.2, 18.2, 0.6), display: 'grid', gap: 26}}>
        <Kicker style={rise(t, 10.3)}>What makes him different</Kicker>
        <Card t={t} at={10.5} title="Regrows" sub="What is lost comes back stronger" accent={C.pink} icon="🌱" />
        <Card t={t} at={13.4} title="Leads" sub="The mane of a pack leader" accent={C.gold} icon="👑" />
        <Card t={t} at={15.4} title="Glows" sub="Bioluminescent light in the dark" accent={C.cyan} icon="✨" />
      </div>

      {/* D: three animals */}
      <div style={{position: 'absolute', left: 120, right: 120, top: 720, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 34, opacity: win(t, 18.3, 25.8, 0.6)}}>
        <Card t={t} at={18.7} title="Axolotl" sub="Regrowth" accent={C.pink} icon="🦎" />
        <Card t={t} at={21.3} title="Lion" sub="Leadership" accent={C.gold} icon="🦁" />
        <Card t={t} at={23.5} title="Jellyfish" sub="Glow" accent={C.cyan} icon="🪼" />
      </div>

      {/* E: three strengths, one character, built for Solana with pump.fun */}
      <div style={{...R, top: 210, opacity: win(t, 25.9, 33.4, 0.6)}}>
        <Kicker style={rise(t, 26)}>Three real strengths</Kicker>
        <div style={{...rise(t, 26.1, 0.9), fontFamily: display, fontWeight: 700, fontSize: 88, lineHeight: 1.02, color: C.text, margin: '16px 0 44px'}}>One <span style={gradText}>character</span></div>
        <div style={{display: 'grid', gap: 26}}>
          <Badge t={t} at={29.8} src="axolotlion/solana.svg" label="Solana" sub="Fast and low-cost network" />
          <Badge t={t} at={31.55} src="axolotlion/pumpfun.png" label="pump.fun" sub="Where the community gathers" round />
        </div>
      </div>

      {/* F: coin about resilience */}
      <div style={{...R, top: 200, opacity: win(t, 33.5, 42.4, 0.6)}}>
        <Kicker style={rise(t, 33.7)}>The idea behind the coin</Kicker>
        <div style={{...rise(t, 33.8, 0.9), fontFamily: display, fontWeight: 700, fontSize: 92, lineHeight: 1.02, color: C.text, margin: '16px 0 40px'}}>A coin about<br /><span style={gradText}>resilience</span></div>
        <div style={{display: 'grid', gap: 22}}>
          <Card t={t} at={36.3} title="Regrow" sub="after every dip" accent={C.pink} icon="1" />
          <Card t={t} at={38.9} title="Lead" sub="with conviction" accent={C.gold} icon="2" />
          <Card t={t} at={40.95} title="Glow" sub="keep going" accent={C.cyan} icon="3" />
        </div>
      </div>

      {/* G: sign-off */}
      <div style={{position: 'absolute', left: 0, right: 0, top: 640, textAlign: 'center', opacity: interpolate(t, [42.5, 43.4], [0, 1], clamp)}}>
        <div style={{...rise(t, 42.6, 1), fontFamily: display, fontWeight: 700, fontSize: 150, letterSpacing: -3, lineHeight: 1, ...gradText}}>AXOLOTLION</div>
        <div style={{...rise(t, 44.5, 1), fontFamily: body, fontWeight: 600, fontSize: 38, letterSpacing: 9, textTransform: 'uppercase', color: C.text, marginTop: 20}}>The first SI animal</div>
        <div style={{...rise(t, 46.2, 1), fontFamily: body, fontWeight: 500, fontSize: 28, letterSpacing: 4, color: C.muted, marginTop: 18}}>Superior Intelligence · Regrows · Leads · Glows</div>
      </div>

      {/* captions */}
      {cap && (
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 58, textAlign: 'center', opacity: interpolate(capT, [0, 0.18], [0, 1], clamp) * (t > cap[1] ? interpolate(t, [cap[1], cap[1] + 0.15], [1, 0], clamp) : 1)}}>
          <span style={{display: 'inline-block', padding: '12px 34px', borderRadius: 18, background: 'rgba(6,4,15,.62)', border: `1px solid ${C.line}`, fontFamily: display, fontWeight: 500, fontSize: 46, color: C.text, backdropFilter: 'blur(10px)'}}>{cap[2]}</span>
        </div>
      )}

      {/* fade in / out */}
      <AbsoluteFill style={{background: '#000', opacity: interpolate(frame, [0, 18, PRO_TOTAL - 24, PRO_TOTAL], [1, 0, 0, 1], clamp), pointerEvents: 'none'}} />
    </AbsoluteFill>
  );
};
