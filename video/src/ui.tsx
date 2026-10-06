import React from 'react';
import {AbsoluteFill, continueRender, delayRender, Img, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// Fonts ship inside public/fonts so rendering never depends on the network.
export const display = "'SpaceGroteskLocal', system-ui, sans-serif";
export const body = "'InterLocal', system-ui, sans-serif";
const FACES: Array<[string, string, string]> = [
  ['SpaceGroteskLocal', 'space-grotesk-latin-500-normal.woff2', '500'],
  ['SpaceGroteskLocal', 'space-grotesk-latin-700-normal.woff2', '700'],
  ['InterLocal', 'inter-latin-400-normal.woff2', '400'],
  ['InterLocal', 'inter-latin-500-normal.woff2', '500'],
  ['InterLocal', 'inter-latin-600-normal.woff2', '600'],
];
if (typeof document !== 'undefined') {
  const handle = delayRender('Loading fonts');
  Promise.all(
    FACES.map(async ([family, file, weight]) => {
      const face = new FontFace(family, `url(${staticFile(`fonts/${file}`)})`, {weight});
      await face.load();
      document.fonts.add(face);
    }),
  )
    .catch((e) => console.error('Font load failed', e))
    .finally(() => continueRender(handle));
}

export const C = {
  bg: '#06040f',
  panel: 'rgba(255,255,255,0.055)',
  line: 'rgba(255,255,255,0.13)',
  text: '#f5f2ea',
  muted: '#b4acd6',
  gold: '#f4c242',
  gold2: '#ffe08a',
  cyan: '#6ff2ff',
  violet: '#8b5cf6',
  pink: '#e85dd8',
  green: '#4ee3a0',
  red: '#ff6b7a',
  amber: '#ffb454',
};
export const GOLD = 'linear-gradient(180deg,#ffe9a3 0%,#f4c242 55%,#c8921e 100%)';

export const CAST = [
  {id: 'judge', name: 'Judge SI', tool: 'SI Court', accent: '#f4c242'},
  {id: 'sniffles', name: 'Detective Sniffles', tool: 'Coin Sniffer', accent: '#d0a064'},
  {id: 'chef', name: 'Chef SI', tool: 'Fridge Roaster', accent: '#ff7a45'},
  {id: 'coach', name: 'Coach SI', tool: 'Roast-Me Workout', accent: '#ff5468'},
  {id: 'doctor', name: 'Dr. Heartbreak', tool: 'Text-Back Doctor', accent: '#4fd1c5'},
  {id: 'anchor', name: 'Anchor SI', tool: 'Breaking News Maker', accent: '#5b9bff'},
  {id: 'professor', name: 'Professor SI', tool: 'Fine-Print Finder', accent: '#a78bfa'},
  {id: 'dj', name: 'DJ SI', tool: 'Rap Battle Roast', accent: '#ff4fd8'},
  {id: 'banker', name: 'Banker SI', tool: 'Can I Afford It?', accent: '#3ddc97'},
  {id: 'astronaut', name: 'Astronaut SI', tool: 'Space Horoscope', accent: '#7aa7ff'},
] as const;
export const byId = (id: string) => CAST.find((c) => c.id === id)!;

/* ---------- icons ---------- */
const ICONS: Record<string, string> = {
  bolt: 'M13 2L4 14h7l-1 8 9-12h-7z',
  coin: 'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v10M9.5 9.5h3.7a1.8 1.8 0 0 1 0 3.6h-2.6a1.8 1.8 0 0 0 0 3.6h3.9',
  wallet: 'M3 7.5A2.5 2.5 0 0 1 5.5 5H17v3M3 7.5V17a2.5 2.5 0 0 0 2.5 2.5H20V8H5.5A2.5 2.5 0 0 1 3 7.5zM16 13.5h2',
  flame: 'M12 2.5s5.5 4.2 5.5 9.3a5.5 5.5 0 0 1-11 0c0-2.2 1-3.4 2.1-4.4 0 2 .9 3 2 3 0-3.2-1-5 1.4-7.9z',
  check: 'M5 12.5l4.5 4.5L19 7.5',
  shield: 'M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6zM9 12l2 2 4-4',
  x: 'M6 6l12 12M18 6L6 18',
  arrow: 'M5 12h14M13 6l6 6-6 6',
};
export const Icon: React.FC<{name: keyof typeof ICONS | string; size: number; color?: string; stroke?: number}> = ({name, size, color = 'currentColor', stroke = 1.8}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" style={{flex: 'none'}}>
    <path d={ICONS[name]} />
  </svg>
);

export const Logo: React.FC<{size: number; uid?: string}> = ({size, uid = 'a'}) => (
  <svg width={size} height={size} viewBox="0 0 40 40">
    <defs>
      <linearGradient id={`lg-${uid}`} x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stopColor="#ffe9a3" />
        <stop offset=".55" stopColor="#f4c242" />
        <stop offset="1" stopColor="#b8841a" />
      </linearGradient>
    </defs>
    <path d="M20 2.5l15.5 5.8v11.4c0 8.6-6.2 14.4-15.5 17.8C10.7 34.1 4.5 28.3 4.5 19.7V8.3z" fill="#120b30" stroke={`url(#lg-${uid})`} strokeWidth="2.4" strokeLinejoin="round" />
    <text x="20" y="25" textAnchor="middle" fontFamily={display} fontWeight={700} fontSize="14" fill={`url(#lg-${uid})`}>SI</text>
    <circle cx="20" cy="2.5" r="2" fill="#6ff2ff" />
  </svg>
);

/* ---------- background ---------- */
export const Backdrop: React.FC = () => {
  const f = useCurrentFrame();
  const t = f / 30;
  const dots = Array.from({length: 36}, (_, i) => {
    const x = random(`x${i}`) * 100;
    const speed = 6 + random(`s${i}`) * 14;
    const y = 110 - (((random(`y${i}`) * 140 + t * speed) % 140) as number);
    const size = 3 + random(`z${i}`) * 5;
    const tw = 0.25 + 0.55 * Math.abs(Math.sin(t * (0.6 + random(`t${i}`)) + i));
    return {x, y, size, tw, gold: random(`g${i}`) > 0.6};
  });
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(1100px 800px at ${72 + Math.sin(t * 0.5) * 8}% ${8 + Math.cos(t * 0.4) * 6}%, rgba(139,92,246,.36), transparent 70%),
            radial-gradient(900px 700px at ${4 + Math.cos(t * 0.35) * 6}% ${72 + Math.sin(t * 0.3) * 8}%, rgba(232,93,216,.18), transparent 70%),
            radial-gradient(1000px 700px at 55% 112%, rgba(111,242,255,.12), transparent 70%)`,
        }}
      />
      <AbsoluteFill
        style={{
          opacity: 0.55,
          backgroundImage: 'radial-gradient(rgba(255,255,255,.11) 1.6px, transparent 1.6px)',
          backgroundSize: '46px 46px',
          backgroundPosition: `${(t * 6) % 46}px ${(t * 3) % 46}px`,
          WebkitMaskImage: 'linear-gradient(180deg,#000,transparent 80%)',
          maskImage: 'linear-gradient(180deg,#000,transparent 80%)',
        }}
      />
      {dots.map((d, i) => (
        <div key={i} style={{position: 'absolute', left: `${d.x}%`, top: `${d.y}%`, width: d.size, height: d.size, borderRadius: '50%', background: d.gold ? C.gold : C.cyan, opacity: d.tw * 0.55, filter: 'blur(0.6px)'}} />
      ))}
    </AbsoluteFill>
  );
};

/* ---------- text ---------- */
export const Words: React.FC<{
  text: string;
  size: number;
  delay?: number;
  weight?: number;
  color?: string;
  gradient?: boolean;
  align?: 'left' | 'center';
  stagger?: number;
  maxWidth?: number;
  font?: string;
}> = ({text, size, delay = 0, weight = 700, color = C.text, gradient, align = 'left', stagger = 4, maxWidth, font = display}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <div style={{display: 'flex', flexWrap: 'wrap', justifyContent: align === 'center' ? 'center' : 'flex-start', columnGap: size * 0.26, rowGap: size * 0.06, fontFamily: font, fontSize: size, fontWeight: weight, lineHeight: 1.08, letterSpacing: font === display ? '-0.03em' : 0, color, maxWidth}}>
      {text.split(' ').map((w, i) => {
        const p = spring({frame: f - delay - i * stagger, fps, config: {damping: 20, stiffness: 150}});
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              opacity: p,
              transform: `translateY(${interpolate(p, [0, 1], [size * 0.5, 0])}px)`,
              filter: `blur(${interpolate(p, [0, 1], [12, 0])}px)`,
              ...(gradient ? {background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'} : {}),
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

export const Eyebrow: React.FC<{text: string; delay?: number}> = ({text, delay = 0}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: f - delay, fps, config: {damping: 200}});
  return (
    <div style={{display: 'inline-flex', alignItems: 'center', gap: 14, fontFamily: body, fontWeight: 600, fontSize: 24, letterSpacing: '0.2em', textTransform: 'uppercase', color: C.gold, opacity: p, transform: `translateY(${(1 - p) * 14}px)`}}>
      <span style={{width: 44, height: 3, background: GOLD, borderRadius: 3}} />
      {text}
    </div>
  );
};

/* ---------- pieces ---------- */
export const Avatar: React.FC<{id: string; size: number; ring?: string; style?: React.CSSProperties}> = ({id, size, ring = C.gold, style}) => (
  <div style={{width: size, height: size, borderRadius: '50%', padding: Math.max(3, size * 0.035), background: `linear-gradient(145deg, ${ring}, rgba(255,255,255,.16))`, boxShadow: `0 ${size * 0.12}px ${size * 0.3}px -${size * 0.08}px rgba(0,0,0,.7)`, flex: 'none', ...style}}>
    <div style={{width: '100%', height: '100%', borderRadius: '50%', overflow: 'hidden', background: '#0a0620'}}>
      <Img src={staticFile(`characters/${id}.jpg`)} style={{width: '100%', height: '100%', objectFit: 'cover', transform: 'scale(1.25)', transformOrigin: '50% 36%'}} />
    </div>
  </div>
);

export const Glass: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <div style={{background: 'linear-gradient(180deg, rgba(255,255,255,.075), rgba(255,255,255,.025))', border: `1.5px solid ${C.line}`, borderRadius: 32, ...style}}>{children}</div>
);

export const usePop = (delay = 0, damping = 16) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - delay, fps, config: {damping, stiffness: 150}});
};
