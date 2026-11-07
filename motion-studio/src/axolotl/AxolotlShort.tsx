import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  Sequence,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import lines from '../../public/axolotl/lines.json';
import { theme } from '../theme';
import { Axolotl } from './Axolotl';

// 30-second vertical short: "the animal that regrows almost anything".
// Narration: local Kokoro voice. Music, whoosh and pop: synthesized locally.
export const FPS = 30;
export const AXOLOTL_FRAMES = 30 * FPS;

const sceneFrames = (() => {
  const f = lines.map((l) => Math.ceil(l.seconds * FPS));
  const used = f.reduce((a, b) => a + b, 0);
  f[f.length - 1] += AXOLOTL_FRAMES - used; // last scene holds until 0:30
  return f;
})();
const sceneStart = sceneFrames.map((_, i) => sceneFrames.slice(0, i).reduce((a, b) => a + b, 0));

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

const Bubbles: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {Array.from({ length: 22 }).map((_, i) => {
        const x = (i * 197) % 1080;
        const speed = 2 + (i % 5);
        const y = 1920 - ((frame * speed + i * 211) % 2200);
        const r = 6 + (i % 4) * 5;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: x + Math.sin((frame + i * 20) / 18) * 14,
              top: y,
              width: r * 2,
              height: r * 2,
              borderRadius: r,
              border: '3px solid rgba(220,255,250,0.35)',
            }}
          />
        );
      })}
    </>
  );
};

const Title: React.FC<{ children: React.ReactNode; color?: string; top?: number; size?: number }> = ({
  children,
  color = theme.ink,
  top = 260,
  size = 100,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 12 } });
  return (
    <div
      style={{
        position: 'absolute',
        top,
        width: '100%',
        textAlign: 'center',
        fontFamily: theme.font,
        fontWeight: 900,
        fontSize: size,
        lineHeight: 1.02,
        color,
        transform: `translateY(${(1 - s) * 80}px) scale(${0.8 + s * 0.2})`,
        opacity: s,
        textShadow: '0 6px 0 rgba(0,0,0,0.25)',
        padding: '0 60px',
      }}
    >
      {children}
    </div>
  );
};

const Pill: React.FC<{ text: string; delay: number; top: number }> = ({ text, delay, top }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 10 } });
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        transform: `scale(${s})`,
      }}
    >
      <div
        style={{
          background: theme.ink,
          color: '#13353a',
          fontFamily: theme.font,
          fontWeight: 900,
          fontSize: 58,
          padding: '18px 44px',
          borderRadius: 60,
        }}
      >
        {text}
      </div>
    </div>
  );
};

// ---- scenes ----
const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const x = interpolate(frame, [0, 40], [-700, 0], { ...clamp, easing: (v) => 1 - (1 - v) ** 3 });
  return (
    <AbsoluteFill>
      <Title>
        Can regrow
        <br />
        <span style={{ color: theme.accent }}>almost anything</span>
      </Title>
      <div style={{ position: 'absolute', top: 680, left: 90 + x, transform: `translateY(${Math.sin(frame / 10) * 14}px)` }}>
        <Axolotl t={frame / FPS} size={900} />
      </div>
    </AbsoluteFill>
  );
};

const Regrow: React.FC = () => {
  const frame = useCurrentFrame();
  const leg = interpolate(frame, [15, 55], [0, 1], clamp);
  const glow = interpolate(frame, [15, 55, 75], [0, 1, 0], clamp);
  return (
    <AbsoluteFill>
      <Title size={92}>Lose a leg?</Title>
      <div style={{ position: 'absolute', top: 470, left: 90 }}>
        <div
          style={{
            position: 'absolute',
            left: 490,
            top: 430,
            width: 160,
            height: 160,
            borderRadius: 80,
            background: theme.accent,
            filter: 'blur(40px)',
            opacity: glow * 0.8,
          }}
        />
        <Axolotl t={frame / FPS} leg={leg} size={900} />
      </div>
      <Pill text="LEG ✓" delay={50} top={1180} />
      <Pill text="HEART ✓" delay={70} top={1300} />
      <Pill text="BRAIN ✓" delay={90} top={1420} />
    </AbsoluteFill>
  );
};

const Baby: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Title>
        Forever
        <br />
        <span style={{ color: '#f6a6c1' }}>a baby</span>
      </Title>
      <div style={{ position: 'absolute', top: 640, left: 90, transform: `rotate(${Math.sin(frame / 12) * 4}deg)` }}>
        <Axolotl t={frame / FPS} size={900} gillWave={2.2} />
      </div>
      <Pill text="KEEPS ITS GILLS FOR LIFE" delay={40} top={1360} />
    </AbsoluteFill>
  );
};

const MapScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const draw = interpolate(frame, [5, 70], [1, 0], clamp);
  const pin = spring({ frame: frame - 55, fps, config: { damping: 9 } });
  const canals = [
    'M120 300 C300 260 420 420 620 380 S900 300 980 420',
    'M100 520 C260 560 460 470 640 560 S880 640 990 600',
    'M300 160 C330 320 280 480 360 640 S420 820 380 900',
    'M700 150 C680 300 760 460 700 620 S640 800 720 900',
  ];
  return (
    <AbsoluteFill>
      <Title size={88}>
        Lives in just
        <br />
        <span style={{ color: theme.accent }}>one place</span>
      </Title>
      <svg width={1080} height={1000} viewBox="0 0 1080 1000" style={{ position: 'absolute', top: 560 }}>
        <rect x={80} y={120} width={920} height={820} rx={40} fill="#1d5a55" opacity={0.55} />
        {canals.map((d, i) => (
          <path key={i} d={d} stroke="#7fd3e0" strokeWidth={26} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={draw} />
        ))}
        <g transform={`translate(520 470) scale(${pin}) translate(0 -60)`}>
          <path d="M0 60 C-40 10 -46 -20 -46 -34 A46 46 0 1 1 46 -34 C46 -20 40 10 0 60 Z" fill={theme.coral} />
          <circle cx={0} cy={-34} r={18} fill={theme.ink} />
        </g>
      </svg>
      <Pill text="XOCHIMILCO · MEXICO CITY" delay={75} top={1440} />
    </AbsoluteFill>
  );
};

const Dna: React.FC = () => {
  const frame = useCurrentFrame();
  const grow = interpolate(frame, [10, 60], [0, 1], { ...clamp, easing: (v) => 1 - (1 - v) ** 3 });
  const bar = (label: string, value: string, width: number, color: string, top: number) => (
    <div style={{ position: 'absolute', top, left: 90, width: 900, fontFamily: theme.font }}>
      <div style={{ color: theme.ink, fontSize: 48, fontWeight: 800, marginBottom: 14 }}>
        {label} <span style={{ opacity: 0.7 }}>· {value}</span>
      </div>
      <div style={{ height: 80, width: width * grow, background: color, borderRadius: 40 }} />
    </div>
  );
  return (
    <AbsoluteFill>
      <Title size={250} top={300} color={theme.accent}>
        10×
      </Title>
      <Title size={70} top={580}>
        bigger DNA than you
      </Title>
      {bar('You', '3.1 billion letters', 90, theme.teal, 900)}
      {bar('Axolotl', '~32 billion letters', 900, '#f6a6c1', 1100)}
    </AbsoluteFill>
  );
};

const Endangered: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const stamp = spring({ frame: frame - 8, fps, config: { damping: 8, mass: 0.6 } });
  const cta = spring({ frame: frame - 70, fps, config: { damping: 12 } });
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', top: 260, left: 190, opacity: 0.8, transform: `translateY(${Math.sin(frame / 10) * 10}px)` }}>
        <Axolotl t={frame / FPS} size={700} />
      </div>
      <div
        style={{
          position: 'absolute',
          top: 860,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          transform: `rotate(-8deg) scale(${interpolate(stamp, [0, 1], [2.4, 1])})`,
          opacity: stamp,
        }}
      >
        <div
          style={{
            border: `12px solid ${theme.coral}`,
            color: theme.coral,
            fontFamily: theme.font,
            fontWeight: 900,
            fontSize: 92,
            lineHeight: 1,
            padding: '24px 36px',
            borderRadius: 24,
            textAlign: 'center',
            background: 'rgba(11,16,20,0.55)',
          }}
        >
          CRITICALLY
          <br />
          ENDANGERED
        </div>
      </div>
      <div
        style={{
          position: 'absolute',
          top: 1260,
          width: '100%',
          textAlign: 'center',
          fontFamily: theme.font,
          fontWeight: 900,
          fontSize: 64,
          color: theme.ink,
          opacity: cta,
          transform: `translateY(${(1 - cta) * 40}px)`,
        }}
      >
        Follow for more
        <br />
        <span style={{ color: theme.accent }}>wild animals 🐾</span>
      </div>
    </AbsoluteFill>
  );
};

const SCENES = [Intro, Regrow, Baby, MapScene, Dna, Endangered];
// scene-relative frames where a pop plays (pill/pin/stamp entrances)
const POPS: number[][] = [[], [50, 70, 90], [40], [55, 75], [60], [8, 70]];

// Word-by-word caption, four words at a time, synced to the spoken line.
const Caption: React.FC<{ text: string; spoken: number }> = ({ text, spoken }) => {
  const frame = useCurrentFrame();
  const words = text.split(' ');
  const n = Math.min(words.length, Math.floor((frame / Math.max(spoken, 1)) * words.length) + 1);
  const start = Math.floor((n - 1) / 4) * 4;
  const chunk = words.slice(start, n); // only words spoken so far, so the line stays centred
  return (
    <div
      style={{
        position: 'absolute',
        top: 1600,
        width: '100%',
        textAlign: 'center',
        fontFamily: theme.font,
        fontWeight: 900,
        fontSize: 66,
        padding: '0 70px',
        color: '#fff',
        WebkitTextStroke: '3px #0b1014',
        paintOrder: 'stroke',
      }}
    >
      {chunk.map((w, j) => (
        <span key={j} style={{ color: start + j === n - 1 ? theme.accent : '#fff', opacity: start + j < n ? 1 : 0 }}>
          {w}{' '}
        </span>
      ))}
    </div>
  );
};

export const AxolotlShort: React.FC = () => {
  const frame = useCurrentFrame();
  const hue = interpolate(frame, [0, AXOLOTL_FRAMES], [0, 25]);
  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(180deg, hsl(${185 + hue} 55% 22%) 0%, hsl(${195 + hue} 60% 9%) 100%)`,
      }}
    >
      <Audio src={staticFile('axolotl/music.mp3')} volume={0.45} />
      <Bubbles />
      {SCENES.map((Scene, i) => (
        <Sequence key={i} from={sceneStart[i]} durationInFrames={sceneFrames[i]}>
          <Scene />
          <Audio src={staticFile(`axolotl/line${i + 1}.wav`)} />
          <Audio src={staticFile('axolotl/whoosh.wav')} volume={0.5} />
          {POPS[i].map((p) => (
            <Sequence key={p} from={p} durationInFrames={10} layout="none">
              <Audio src={staticFile('axolotl/pop.wav')} volume={0.6} />
            </Sequence>
          ))}
          <Caption text={lines[i].text} spoken={Math.ceil((lines[i].seconds - 0.35) * FPS)} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
