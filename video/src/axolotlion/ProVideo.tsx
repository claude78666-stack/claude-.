import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, interpolate, OffthreadVideo, random, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {body, C, display} from '../ui';
import MANE from './mane.json';

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
// jellyfish riding in the fur around the head: offsets are fractions of the frame width from the mane centre
const JELLIES = [
  {dx: -0.15, dy: -0.06, size: 0.15, hue: 300, front: false},
  {dx: 0.15, dy: -0.08, size: 0.17, hue: 190, front: false},
  {dx: -0.045, dy: -0.15, size: 0.13, hue: 270, front: false},
  {dx: -0.12, dy: -0.05, size: 0.1, hue: 330, front: true},
  {dx: 0.115, dy: -0.04, size: 0.09, hue: 210, front: true},
];
const Hero: React.FC<{t: number}> = ({t}) => {
  const ang = kf(t, [0, 4.6, 10, 18, 26, 34, 42, 44.5, 49.5], [0, 0, 120, 180, 90, 0, 0, 0, 0]);
  const f = Math.min(ang, 180) / 2.5, i0 = Math.min(72, Math.floor(f)), i1 = Math.min(72, i0 + 1), k = f - Math.floor(f);
  const src = (i: number) => staticFile(`axolotlion/tt/tt_${String(i).padStart(3, '0')}.webp`);
  const T = [0, 5.2, 6.4, 10, 11.2, 18, 19.2, 25.6, 26.8, 33, 34.2, 42.2, 43.4, 49.5];
  const X = kf(t, T, [0, 0, -340, -340, -350, -350, 0, 0, -350, -350, -350, -350, 0, 0]);
  const Y = kf(t, T, [165, 165, 40, 40, 40, 40, -85, -85, 20, 20, 20, 20, -150, -150]);
  const S = kf(t, T, [0.92, 0.92, 0.8, 0.8, 0.8, 0.8, 0.78, 0.78, 0.8, 0.8, 0.8, 0.8, 0.66, 0.66]);
  const bob = Math.sin(t * 1.6) * 5;
  const W = 1500, H = W * 764 / 1400;
  const m0 = MANE[i0], m1 = MANE[i1], mx = (m0[0] + (m1[0] - m0[0]) * k) * W, my = (m0[1] + (m1[1] - m0[1]) * k) * H;
  const box: React.CSSProperties = {position: 'absolute', left: 960 - W / 2, top: 540 - H / 2, width: W, height: H};
  return (
    <div style={{...box, transform: `translate(${X}px, ${Y + bob}px) scale(${S * (1 + Math.sin(t * 1.1) * 0.006)})`}}>
      {JELLIES.map((j, n) => !j.front && <Jelly key={n} t={t} seed={n + 1} hue={j.hue} size={j.size * W} x={mx + j.dx * W} y={my + j.dy * H} />)}
      <Img src={src(i0)} style={{...box, left: 0, top: 0, filter: 'drop-shadow(0 0 36px rgba(255,130,230,.4))'}} />
      {k > 0.02 && <Img src={src(i1)} style={{...box, left: 0, top: 0, opacity: k}} />}
      {JELLIES.map((j, n) => j.front && <Jelly key={n} t={t} seed={n + 1} hue={j.hue} size={j.size * W} x={mx + j.dx * W} y={my + j.dy * H} front />)}
    </div>
  );
};


/* ---------- bioluminescent jellyfish: pulsing translucent bell + trailing tentacles ---------- */
const Jelly: React.FC<{t: number; x: number; y: number; size: number; hue: number; seed: number; front?: boolean}> = ({t, x, y, size, hue, seed, front}) => {
  const ph = t * 1.5 + seed * 2.3;
  const pulse = Math.sin(ph), sq = 1 - pulse * 0.07, st = 1 + pulse * 0.05;
  const bx = Math.sin(t * 0.6 + seed) * size * 0.12, by = Math.sin(t * 0.8 + seed * 1.7) * size * 0.1;
  const col = `hsl(${hue},95%,72%)`, col2 = `hsl(${hue + 55},90%,65%)`;
  const strands = Array.from({length: 9}, (_, i) => {
    const sx = -34 + i * 8.5, len = 110 + (i % 3) * 38 + Math.sin(i * 3.1 + seed) * 16;
    let d = `M${sx},44`;
    for (let k = 1; k <= 6; k++) d += ` L${sx + Math.sin(ph * 0.9 - k * 0.8 + i) * (4 + k * 2.2)},${44 + (len * k) / 6}`;
    return <path key={i} d={d} fill="none" stroke={i % 2 ? col : col2} strokeWidth={i % 3 === 0 ? 2.4 : 1.4} strokeLinecap="round" opacity={0.55} />;
  });
  return (
    <svg width={size} height={size * 2.1} viewBox="-70 -10 140 290" style={{position: 'absolute', left: x - size / 2 + bx, top: y - size * 0.4 + by, overflow: 'visible', mixBlendMode: 'screen', filter: `drop-shadow(0 0 ${size * 0.2}px ${col})`, opacity: front ? 0.9 : 0.85}}>
      <defs>
        <radialGradient id={`jb${seed}`} cx="50%" cy="70%" r="65%">
          <stop offset="0%" stopColor={col2} stopOpacity="0.08" />
          <stop offset="60%" stopColor={col} stopOpacity="0.28" />
          <stop offset="100%" stopColor="#fff" stopOpacity="0.75" />
        </radialGradient>
      </defs>
      <g transform={`translate(0,0) scale(${st},${sq})`}>
        {strands}
        <path d="M-52,46 C-58,-10 -26,-12 0,-12 C26,-12 58,-10 52,46 C36,38 -36,38 -52,46 Z" fill={`url(#jb${seed})`} stroke={col} strokeWidth="1.6" strokeOpacity="0.8" />
        <path d="M-34,20 C-30,0 -10,-4 8,-3" fill="none" stroke="#fff" strokeOpacity="0.55" strokeWidth="3" strokeLinecap="round" />
        {[-22, -8, 8, 22].map((o, i) => <path key={i} d={`M${o},42 q${Math.sin(ph + i) * 10},40 ${Math.sin(ph * 0.8 + i * 2) * 8},${78 + i * 6}`} stroke="#fff" strokeOpacity="0.45" strokeWidth="5" fill="none" strokeLinecap="round" />)}
      </g>
    </svg>
  );
};


/* ---------- AI-animated footage of the character (Runway Seedance), cut to the narration ---------- */
type Shot = {a: number; b: number; src: string; from: number; rate: number; x: number; y: number; s: number};
const SHOTS: Shot[] = [
  {a: 0, b: 5.6, src: 'clip1', from: 0, rate: 1, x: 40, y: 150, s: 0.86},
  {a: 5.6, b: 10.4, src: 'clip3', from: 0, rate: 1, x: -380, y: 80, s: 0.54},
  {a: 10.4, b: 18.4, src: 'clip2', from: 0, rate: 1, x: -400, y: 50, s: 0.72},
  {a: 18.4, b: 26.0, src: 'clip4', from: 0, rate: 1, x: 20, y: -70, s: 0.84},
  {a: 26.0, b: 33.6, src: 'clip5', from: 0, rate: 1, x: -400, y: 60, s: 0.72},
  {a: 33.6, b: 42.4, src: 'clip6', from: 0, rate: 0.8, x: -400, y: 60, s: 0.56},
  {a: 42.4, b: 50, src: 'clip7', from: 0, rate: 1, x: 0, y: -330, s: 0.5},
];
const Footage: React.FC<{t: number}> = ({t}) => (
  <AbsoluteFill style={{mixBlendMode: 'lighten'}}>
    {SHOTS.map((s, i) => {
      const fade = 0.6;
      const op = interpolate(t, [s.a - fade, s.a, s.b, s.b + fade], [i === 0 ? 1 : 0, 1, 1, i === SHOTS.length - 1 ? 1 : 0], clamp);
      if (op <= 0) return null;
      const from = Math.round((s.a - fade) * PRO_FPS);
      const dur = Math.round((s.b - s.a + fade * 2) * PRO_FPS);
      const k = (t - s.a) / (s.b - s.a);
      const drift = 1 + k * 0.035;
      return (
        <Sequence key={i} from={Math.max(0, from)} durationInFrames={dur} layout="none">
          <AbsoluteFill style={{opacity: op, transform: `translate(${s.x}px, ${s.y}px) scale(${s.s * drift})`, transformOrigin: '50% 80%'}}>
            <div style={{width: 1920, height: 1080, WebkitMaskImage: 'linear-gradient(90deg,transparent,#000 22%,#000 78%,transparent)', maskImage: 'linear-gradient(90deg,transparent,#000 22%,#000 78%,transparent)'}}>
              <div style={{width: 1920, height: 1080, WebkitMaskImage: 'linear-gradient(180deg,transparent,#000 20%,#000 82%,transparent)', maskImage: 'linear-gradient(180deg,transparent,#000 20%,#000 82%,transparent)'}}>
                <OffthreadVideo src={staticFile(`axolotlion/pro/${s.src}.mp4`)} muted startFrom={Math.round(s.from * PRO_FPS)} playbackRate={s.rate} style={{width: 1920, height: 1080}} />
              </div>
            </div>
          </AbsoluteFill>
        </Sequence>
      );
    })}
  </AbsoluteFill>
);

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
  <div style={{...rise(t, at), padding: '26px 30px', borderRadius: 26, background: 'linear-gradient(160deg,rgba(255,255,255,.1),rgba(255,255,255,.035))', border: `1px solid ${C.line}`, boxShadow: `0 20px 60px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.18), 0 0 50px ${accent}22`, ...style}}>
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

      <Footage t={t} />

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
      <div style={{position: 'absolute', left: 120, right: 120, top: 70, display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 34, opacity: win(t, 18.3, 25.8, 0.6)}}>
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
      <div style={{position: 'absolute', left: 0, right: 0, top: 585, textAlign: 'center', opacity: interpolate(t, [42.5, 43.4], [0, 1], clamp)}}>
        <div style={{...rise(t, 42.6, 1), fontFamily: display, fontWeight: 700, fontSize: 150, letterSpacing: -3, lineHeight: 1, ...gradText}}>AXOLOTLION</div>
        <div style={{...rise(t, 44.5, 1), fontFamily: body, fontWeight: 600, fontSize: 38, letterSpacing: 9, textTransform: 'uppercase', color: C.text, marginTop: 20}}>The first SI animal</div>
        <div style={{...rise(t, 46.2, 1), fontFamily: body, fontWeight: 500, fontSize: 28, letterSpacing: 4, color: C.muted, marginTop: 18}}>Superior Intelligence · Regrows · Leads · Glows</div>
      </div>

      {/* captions */}
      {cap && (
        <div style={{position: 'absolute', left: 0, right: 0, bottom: 58, textAlign: 'center', opacity: interpolate(capT, [0, 0.18], [0, 1], clamp) * (t > cap[1] ? interpolate(t, [cap[1], cap[1] + 0.15], [1, 0], clamp) : 1)}}>
          <span style={{display: 'inline-block', padding: '12px 34px', borderRadius: 18, background: 'rgba(6,4,15,.62)', border: `1px solid ${C.line}`, fontFamily: display, fontWeight: 500, fontSize: 46, color: C.text}}>{cap[2]}</span>
        </div>
      )}

      {/* fade in / out */}
      <AbsoluteFill style={{background: '#000', opacity: interpolate(frame, [0, 18, PRO_TOTAL - 24, PRO_TOTAL], [1, 0, 0, 1], clamp), pointerEvents: 'none'}} />
    </AbsoluteFill>
  );
};
