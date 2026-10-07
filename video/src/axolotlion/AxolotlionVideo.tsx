import React from 'react';
import {AbsoluteFill, Audio, Easing, Img, interpolate, random, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {body, C, display, GOLD, Words} from '../ui';
import {RIG} from './rig';

export const AX_FPS = 30;
export const AX_TOTAL = 900; // 30 seconds

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ease = (f: number, a: number, b: number, from = 0, to = 1, e = Easing.out(Easing.cubic)) =>
  interpolate(f, [a, b], [from, to], {...clamp, easing: e});
const win = (f: number, a: number, b: number, fade = 12) => interpolate(f, [a, a + fade, b - fade, b], [0, 1, 1, 0], clamp);

export const RUN_W = 1851, RUN_H = 818, ST_W = 1406, ST_H = 976;
export const GLOW = 'drop-shadow(0 0 26px rgba(255,120,225,.55)) drop-shadow(0 0 70px rgba(90,200,255,.38))';

/* ---------- gallop pose: bounce, pitch, squash ---------- */
const gallop = (f: number) => {
  const t = f / AX_FPS;
  const h = Math.abs(Math.sin(t * Math.PI * 2.2));
  return {h, dy: -h * 34, rot: Math.sin(t * Math.PI * 4.4) * 2.4, sy: 1 + (h - 0.5) * 0.035};
};

/* ---------- rigged run cycle: body, tail, and four two-segment legs ---------- */
const LEG_ORDER = ['hindA', 'foreC', 'hindB', 'foreD'] as const;
// mean angle, swing, phase offset (radians) for the upper leg; lower leg flexes with a phase lead
const GAIT: Record<(typeof LEG_ORDER)[number], [number, number, number]> = {hindA: [-10, 20, 0], hindB: [-8, 18, 0.35], foreC: [5, 22, 3.3], foreD: [5, 20, 3.0]};
const rigImg = (name: string, b: {x: number; y: number; w: number; h: number}) => (
  <Img src={staticFile(`axolotlion/rig/${name}.png`)} style={{position: 'absolute', left: b.x, top: b.y, width: b.w, height: b.h}} />
);
export const RigBody: React.FC<{frame: number; fps?: number; freq?: number}> = ({frame, fps = AX_FPS, freq = 2.2}) => {
  const ph = (off: number) => 2 * Math.PI * ((frame / fps) * freq) + off;
  const full: React.CSSProperties = {position: 'absolute', left: 0, top: 0, width: RIG.w, height: RIG.h};
  return (
    <div style={{...full, transform: `rotate(${Math.sin(ph(0.6)) * 0.8}deg)`, transformOrigin: '60% 50%'}}>
      <Img src={staticFile('axolotlion/rig/base.png')} style={full} />
      <div style={{...full, transformOrigin: `${RIG.tail.pivot[0]}px ${RIG.tail.pivot[1]}px`, transform: `rotate(${6 * Math.sin(ph(1.0))}deg)`}}>{rigImg('tail', RIG.tail)}</div>
      {LEG_ORDER.map((n) => {
        const L = RIG.legs[n];
        const [mean, amp, off] = GAIT[n];
        const a1 = mean + amp * Math.sin(ph(off));
        const a2 = 18 * Math.sin(ph(off + 1.1));
        return (
          <div key={n} style={{...full, transformOrigin: `${L.hip[0]}px ${L.hip[1]}px`, transform: `rotate(${a1}deg)`}}>
            {rigImg(`${n}_up`, L.upper)}
            <div style={{...full, transformOrigin: `${L.knee[0]}px ${L.knee[1]}px`, transform: `rotate(${a2}deg)`}}>{rigImg(`${n}_lo`, L.lower)}</div>
          </div>
        );
      })}
    </div>
  );
};

type RunPose = {x: number; ground: number};

const Runner: React.FC<{pose: (f: number) => RunPose; scale: number; opacity?: number; rotExtra?: (f: number) => number; glow?: boolean}> = ({pose, scale, opacity = 1, rotExtra, glow = true}) => {
  const f = useCurrentFrame();
  const draw = (fr: number, o: number, blur: number, key: string, withGlow = true) => {
    const p = pose(fr), g = gallop(fr);
    const w = RUN_W * scale, h = RUN_H * scale;
    return (
      <div key={key} style={{position: 'absolute', left: p.x - w / 2, top: p.ground - h + g.dy, width: w, height: h, opacity: o, transform: `rotate(${g.rot + (rotExtra ? rotExtra(fr) : 0)}deg) scaleY(${g.sy})`, transformOrigin: '50% 90%', filter: `${blur ? `blur(${blur}px) ` : ''}${glow && withGlow ? GLOW : ''}`}}>
        <div style={{width: RUN_W, height: RUN_H, transform: `scale(${scale})`, transformOrigin: '0 0'}}><RigBody frame={fr} /></div>
      </div>
    );
  };
  const p = pose(f), g = gallop(f);
  const lap = (f / AX_FPS) * 2.2;
  const puffs = [0, 1, 2].map((i) => {
    const k = Math.floor(lap) - i;
    const age = lap - k;
    const fr = (k / 2.2) * AX_FPS;
    const px = pose(fr).x - RUN_W * scale * 0.18;
    return (
      <div key={`puff${i}`} style={{position: 'absolute', left: px - age * 150 - 40, top: p.ground - 26 - age * 46, width: 80 + age * 70, height: 50 + age * 40, borderRadius: '50%', background: 'radial-gradient(circle, rgba(235,225,200,.55), rgba(235,225,200,0) 70%)', opacity: (1 - age) * 0.8 * opacity, filter: 'blur(5px)'}} />
    );
  });
  return (
    <AbsoluteFill style={{opacity}}>
      {puffs}
      <div style={{position: 'absolute', left: p.x - RUN_W * scale * 0.4, top: p.ground - 22, width: RUN_W * scale * 0.8, height: 44, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(0,10,20,.55), rgba(0,10,20,0) 70%)', transform: `scale(${1 - g.h * 0.22})`, opacity: 0.6}} />
      {[8, 4].map((d, i) => draw(f - d, [0.1, 0.18][i], 5, `gh${i}`, false))}
      {draw(f, 1, 0, 'main')}
    </AbsoluteFill>
  );
};

const Stander: React.FC<{x: number; ground: number; scale: number; opacity?: number; pulse?: number; mane?: number}> = ({x, ground, scale, opacity = 1, pulse = 0, mane = 0}) => {
  const f = useCurrentFrame();
  const t = f / AX_FPS;
  const w = ST_W * scale, h = ST_H * scale;
  const breathe = 1 + Math.sin(t * 2.2) * 0.012;
  const tilt = Math.sin(t * 1.1) * 1.3;
  const glow = `drop-shadow(0 0 ${28 + pulse * 40}px rgba(255,120,225,${0.5 + pulse * 0.4})) drop-shadow(0 0 ${70 + pulse * 70}px rgba(90,200,255,${0.35 + pulse * 0.4}))`;
  return (
    <AbsoluteFill style={{opacity}}>
      <div style={{position: 'absolute', left: x - w * 0.42, top: ground - 24, width: w * 0.84, height: 48, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(0,10,20,.6), rgba(0,10,20,0) 70%)'}} />
      <div style={{position: 'absolute', left: x - w / 2, top: ground - h, width: w, height: h, transform: `rotate(${tilt}deg) scale(${breathe * (1 + mane * 0.05)})`, transformOrigin: '50% 100%', filter: glow}}>
        <Img src={staticFile('axolotlion/stand-cut.png')} style={{width: '100%', height: '100%'}} />
      </div>
    </AbsoluteFill>
  );
};

/* ---------- background: photo plate, light, particles, speed streaks ---------- */
const Background: React.FC<{speed: number}> = ({speed}) => {
  const f = useCurrentFrame();
  const pan = ease(f, 0, AX_TOTAL, 0, 150, Easing.linear);
  return (
    <AbsoluteFill style={{background: '#04121f'}}>
      <Img src={staticFile('axolotlion/bg.jpg')} style={{position: 'absolute', width: 1920 * 1.2, height: 1080 * 1.2, left: -115 - pan, top: -60, objectFit: 'cover', filter: 'saturate(1.1) contrast(1.05)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(2,10,25,.35) 0%, rgba(2,10,25,0) 35%, rgba(2,10,25,.5) 100%)'}} />
      {Array.from({length: 46}).map((_, i) => {
        const sp = 20 + random(`s${i}`) * 60 + speed * 260;
        const x = ((random(`x${i}`) * 2300 - f * sp * 0.22) % 2300 + 2300) % 2300 - 190;
        const y = 80 + random(`y${i}`) * 900 + Math.sin(f / 30 + i) * 10;
        const sz = 3 + random(`z${i}`) * 8;
        const streak = speed * (60 + random(`l${i}`) * 140);
        return <div key={i} style={{position: 'absolute', left: x, top: y, width: sz + streak, height: sz, borderRadius: sz, background: 'rgba(200,240,255,.5)', opacity: 0.25 + random(`o${i}`) * 0.5, filter: 'blur(1px)'}} />;
      })}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, rgba(0,0,0,0) 40%, rgba(0,5,15,.65) 100%)'}} />
    </AbsoluteFill>
  );
};

/* ---------- UI bits ---------- */
const Caption: React.FC<{lines: Array<[number, number, string]>}> = ({lines}) => {
  const f = useCurrentFrame();
  return (
    <>
      {lines.map(([a, b, text], i) => {
        const o = win(f, a, b, 8);
        if (o <= 0) return null;
        return (
          <div key={i} style={{position: 'absolute', left: 0, right: 0, bottom: 52, display: 'flex', justifyContent: 'center', opacity: o, transform: `translateY(${(1 - o) * 14}px)`}}>
            <div style={{padding: '16px 38px', borderRadius: 18, background: 'rgba(3,10,24,.72)', border: `1.5px solid ${C.line}`, fontFamily: body, fontWeight: 500, fontSize: 40, color: C.text, backdropFilter: 'blur(6px)'}}>{text}</div>
          </div>
        );
      })}
    </>
  );
};

const InfoCard: React.FC<{at: number; y: number; accent: string; kicker: string; text: string}> = ({at, y, accent, kicker, text}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: f - at, fps, config: {damping: 18, stiffness: 140}});
  return (
    <div style={{position: 'absolute', right: 110, top: y, width: 700, padding: '26px 34px', borderRadius: 26, background: 'linear-gradient(180deg, rgba(8,20,40,.82), rgba(6,14,30,.72))', border: `2px solid ${accent}88`, boxShadow: `0 0 50px -12px ${accent}`, opacity: p, transform: `translateX(${(1 - p) * 120}px)`}}>
      <div style={{fontFamily: body, fontWeight: 600, fontSize: 24, letterSpacing: '0.2em', textTransform: 'uppercase', color: accent}}>{kicker}</div>
      <div style={{fontFamily: display, fontWeight: 600, fontSize: 40, lineHeight: 1.15, letterSpacing: '-0.01em', marginTop: 8, color: C.text}}>{text}</div>
    </div>
  );
};

const Ring: React.FC<{x: number; y: number; at: number; color: string}> = ({x, y, at, color}) => {
  const f = useCurrentFrame();
  const a = ease(f, at, at + 40, 0, 1);
  if (f < at || f > at + 44) return null;
  return <div style={{position: 'absolute', left: x - 90 * a - 20, top: y - 90 * a - 20, width: 180 * a + 40, height: 180 * a + 40, borderRadius: '50%', border: `5px solid ${color}`, opacity: 1 - a, boxShadow: `0 0 40px ${color}`}} />;
};

const Line: React.FC<{from: [number, number]; to: [number, number]; at: number; color: string}> = ({from, to, at, color}) => {
  const f = useCurrentFrame();
  const a = ease(f, at, at + 18, 0, 1);
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0, pointerEvents: 'none'}}>
      <line x1={from[0]} y1={from[1]} x2={from[0] + (to[0] - from[0]) * a} y2={from[1] + (to[1] - from[1]) * a} stroke={color} strokeWidth={3} strokeDasharray="8 8" />
      <circle cx={from[0]} cy={from[1]} r={10 * a} fill={color} />
    </svg>
  );
};

/* ---------- chart helpers (illustrative, not real prices) ---------- */
const priceAt = (u: number) => interpolate(u, [0, 0.22, 0.4, 0.52, 1], [0.1, 0.5, 0.26, 0.4, 1], clamp);
const chartY = (u: number) => 880 - 560 * priceAt(u) + 10 * Math.sin(u * 40);
const chartPts = (a: number, b: number, n: number): Array<[number, number]> => Array.from({length: n + 1}, (_, i) => {
  const u = a + ((b - a) * i) / n;
  return [110 + u * 1700, chartY(u)];
});

const MiniChart: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame();
  const prog = ease(f, at, at + 62, 0, 1, Easing.inOut(Easing.cubic));
  const W = 700, H = 320;
  const pts = Array.from({length: 81}, (_, i) => {
    const u = i / 80;
    return [u * W, H - 30 - interpolate(u, [0, 0.3, 0.5, 0.62, 1], [0.4, 0.8, 0.18, 0.34, 1], clamp) * (H - 70)] as [number, number];
  });
  const n = Math.max(2, Math.round(prog * 80));
  const shown = pts.slice(0, n);
  const last = shown[shown.length - 1];
  return (
    <svg width={W + 40} height={H + 50} style={{position: 'absolute', right: 110, top: 450}}>
      <polyline points={shown.map((p) => p.join(',')).join(' ')} fill="none" stroke={C.cyan} strokeWidth={8} strokeLinejoin="round" strokeLinecap="round" style={{filter: 'drop-shadow(0 0 14px #6ff2ff)'}} />
      <circle cx={last[0]} cy={last[1]} r={12} fill="#fff" />
      {prog > 0.5 && <text x={pts[40][0] - 30} y={pts[40][1] + 44} fontFamily={body} fontWeight={600} fontSize={28} fill="#ff9aa8">dip</text>}
      {prog > 0.9 && <text x={pts[72][0] - 70} y={pts[72][1] - 22} fontFamily={body} fontWeight={600} fontSize={28} fill={C.green}>regrows</text>}
      <text x={0} y={H + 36} fontFamily={body} fontSize={22} fill={C.muted}>Illustrative only. Not real prices.</text>
    </svg>
  );
};

const Crowd: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame();
  return (
    <>
      {Array.from({length: 14}).map((_, i) => {
        const ang = (i / 14) * Math.PI * 2;
        const a = ease(f, at + i * 2, at + 50 + i * 2, 0, 1);
        const sx = 1300 + Math.cos(ang) * 520, sy = 640 + Math.sin(ang) * 330;
        const tx = 1300 + Math.cos(ang) * 190, ty = 640 + Math.sin(ang) * 120;
        return <div key={i} style={{position: 'absolute', left: sx + (tx - sx) * a - 22, top: sy + (ty - sy) * a - 22, width: 44, height: 44, borderRadius: '50%', background: `hsl(${i * 25 + 10},80%,62%)`, border: '3px solid #fff', boxShadow: '0 0 20px rgba(255,255,255,.4)', opacity: Math.min(1, a * 3)}} />;
      })}
      <div style={{position: 'absolute', left: 1300 - 70, top: 640 - 40, width: 140, height: 80, display: 'grid', placeItems: 'center', fontFamily: display, fontWeight: 700, fontSize: 30, color: C.gold2}}>THE PRIDE</div>
    </>
  );
};

const Memes: React.FC<{at: number}> = ({at}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const tiles = [['gm', '#0f3b66'], ['LFG', '#4a1a5e'], ['wen?', '#0d4d44'], ['regrow', '#5a2a12']];
  return (
    <>
      {tiles.map(([t, bg], i) => {
        const p = spring({frame: f - at - i * 6, fps, config: {damping: 14, stiffness: 160}});
        return (
          <div key={i} style={{position: 'absolute', left: 1010 + i * 195, top: 500 + (i % 2) * 36, width: 175, height: 215, borderRadius: 22, overflow: 'hidden', background: bg as string, border: '3px solid rgba(255,255,255,.7)', transform: `scale(${p}) rotate(${(i - 1.5) * 4}deg)`, opacity: p, boxShadow: '0 20px 40px -14px rgba(0,0,0,.7)'}}>
            <Img src={staticFile('axolotlion/stand-cut.png')} style={{position: 'absolute', left: 4, top: 22 + (i % 2) * 6, width: 168, height: 173, objectFit: 'cover', objectPosition: '60% 30%'}} />
            <div style={{position: 'absolute', left: 0, right: 0, bottom: 8, textAlign: 'center', fontFamily: display, fontWeight: 700, fontSize: 30, color: '#fff', textShadow: '0 2px 6px #000'}}>{t}</div>
          </div>
        );
      })}
    </>
  );
};

/* ---------- main ---------- */
export const AxolotlionVideo: React.FC = () => {
  const f = useCurrentFrame();
  const out = ease(f, AX_TOTAL - 22, AX_TOTAL - 1, 0, 1, Easing.linear);
  const speed = interpolate(f, [0, 120, 160, 330, 345, 600, 625, 780, 800], [1, 0.9, 0.05, 0.05, 1, 1, 0.8, 0.8, 0], clamp);

  // S1: runs in, S3: runs in place, S4: runs along the chart line
  const s1 = win(f, 0, 175, 14), s1o = f < 150 ? 1 : 1 - ease(f, 150, 175, 0, 1);
  const s2 = win(f, 150, 345, 14);
  const s3 = win(f, 330, 612, 14);
  const s4 = win(f, 600, 790, 14);
  const s5 = win(f, 775, AX_TOTAL + 20, 14);

  const run1 = (fr: number): RunPose => ({x: ease(fr, 0, 110, -700, 640, Easing.out(Easing.quad)) + (fr > 110 ? (fr - 110) * 1.2 : 0), ground: 900});
  const run3 = (fr: number): RunPose => ({x: 520 + Math.sin(fr / 40) * 26, ground: 905});
  const u4 = (fr: number) => ease(fr, 612, 775, 0.02, 0.97, Easing.inOut(Easing.quad));
  const run4 = (fr: number): RunPose => {
    const u = u4(fr);
    return {x: 110 + u * 1700, ground: chartY(u) + 48};
  };
  const slope4 = (fr: number) => {
    const u = u4(fr), du = 0.01;
    return (Math.atan2(chartY(u + du) - chartY(u), 1700 * du) * 180) / Math.PI * 0.8;
  };

  const f4 = Math.max(612, f);
  const shownChart = chartPts(0, u4(f4), 90);

  const cap: Array<[number, number, string]> = [
    [10, 70, 'Meet Axolotlion.'],
    [75, 165, 'A hybrid mascot: axolotl, lion and a jellyfish glow.'],
    [170, 245, 'The axolotl is the salamander that regrows its limbs.'],
    [248, 300, "The lion's mane makes him the leader of the pride."],
    [303, 345, 'And the glow makes him impossible to miss.'],
    [350, 428, 'Why a crypto mascot? It always comes back.'],
    [431, 508, 'A leader gives a community something to rally around.'],
    [511, 600, 'And a glowing face is easy to turn into memes.'],
    [612, 780, 'The lore: he regrows after every dip and never stops running.'],
    [790, 890, 'Axolotlion. Regrows. Leads. Glows.'],
  ];

  return (
    <AbsoluteFill style={{background: C.bg, color: C.text, fontFamily: body}}>
      <Background speed={speed} />

      {/* S1 */}
      <AbsoluteFill style={{opacity: s1 * s1o}}>
        <Runner pose={run1} scale={0.52} />
        <div style={{position: 'absolute', right: 120, top: 120, textAlign: 'right'}}>
          <div style={{fontFamily: body, fontWeight: 600, fontSize: 28, letterSpacing: '0.24em', textTransform: 'uppercase', color: C.gold, opacity: ease(f, 24, 44)}}>Meet</div>
          <Words text="Axolotlion" size={190} delay={30} gradient align="center" />
        </div>
      </AbsoluteFill>

      {/* S2 */}
      <AbsoluteFill style={{opacity: s2}}>
        <Stander x={520} ground={930} scale={0.7} pulse={ease(f, 300, 320, 0, 1) * (1 - ease(f, 322, 340, 0, 1))} mane={ease(f, 252, 262, 0, 1) * (1 - ease(f, 264, 276, 0, 1))} opacity={ease(f, 150, 180, 0, 1)} />
        <Line from={[894, 404]} to={[1090, 215]} at={178} color="#ff9ae0" />
        <Line from={[727, 267]} to={[1090, 425]} at={252} color="#ffd166" />
        <Line from={[933, 677]} to={[1090, 635]} at={305} color="#6ff2ff" />
        <Ring x={894} y={404} at={180} color="#ff9ae0" />
        <Ring x={727} y={267} at={252} color="#ffd166" />
        <Ring x={933} y={677} at={305} color="#6ff2ff" />
        <InfoCard at={178} y={125} accent="#ff9ae0" kicker="The axolotl" text="A salamander famous for regrowing lost limbs." />
        <InfoCard at={252} y={335} accent="#ffd166" kicker="The lion" text="The mane of a leader. Main-character energy." />
        <InfoCard at={305} y={545} accent="#6ff2ff" kicker="The jellyfish glow" text="A bioluminescent shine that stands out in the dark." />
      </AbsoluteFill>

      {/* S3 */}
      <AbsoluteFill style={{opacity: s3}}>
        <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(2,8,20,0) 40%, rgba(2,8,20,.6) 100%)'}} />
        <Runner pose={run3} scale={0.5} />
        <div style={{position: 'absolute', right: 110, top: 110, width: 800}}>
          <div style={{fontFamily: body, fontWeight: 600, fontSize: 26, letterSpacing: '0.22em', textTransform: 'uppercase', color: C.gold, opacity: ease(f, 336, 352), textShadow: '0 2px 10px #000'}}>Why it works as a crypto mascot</div>
          {[[345, 428, 'It comes back.', C.cyan], [428, 508, 'It leads.', C.gold2], [508, 600, 'It glows.', '#ff9ae0']].map(([a, b, t, col], i) => (
            <div key={i} style={{position: 'absolute', top: 54, left: 0, width: 800, opacity: win(f, a as number, b as number, 10), transform: `translateY(${(1 - win(f, a as number, b as number, 10)) * 20}px)`}}>
              <div style={{fontFamily: display, fontWeight: 700, fontSize: 104, letterSpacing: '-0.03em', color: col as string, textShadow: `0 0 40px ${col}66`}}>{t}</div>
              <div style={{fontFamily: body, fontSize: 36, color: C.text, maxWidth: 780, lineHeight: 1.3, marginTop: 4}}>
                {['Like an axolotl regrows a limb, a mascot story can show a recovery after every dip.', 'A lion gives a community a face to gather around.', 'Hard to miss and easy to remix into stickers, banners and memes.'][i]}
              </div>
            </div>
          ))}
        </div>
        {f >= 345 && f < 440 && <MiniChart at={352} />}
        {f >= 428 && f < 520 && <Crowd at={434} />}
        {f >= 508 && f < 612 && <Memes at={514} />}
      </AbsoluteFill>

      {/* S4 */}
      <AbsoluteFill style={{opacity: s4}}>
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(2,8,20,.62), rgba(2,8,20,.4))'}} />
        <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
          <polyline points={shownChart.map((p) => p.join(',')).join(' ')} fill="none" stroke="#6ff2ff" strokeWidth={8} strokeLinejoin="round" strokeLinecap="round" style={{filter: 'drop-shadow(0 0 16px #6ff2ff)'}} />
        </svg>
        <Runner pose={run4} scale={0.3} rotExtra={slope4} />
        <div style={{position: 'absolute', left: 110, top: 100}}>
          <div style={{fontFamily: body, fontWeight: 600, fontSize: 26, letterSpacing: '0.22em', textTransform: 'uppercase', color: C.gold}}>Lore file</div>
          {[['Hybrid', 'axolotl + lion + jellyfish glow', 640], ['Power', 'regrows after every dip', 676], ['Flaw', 'cannot stop running', 712]].map(([k, v, at], i) => (
            <div key={i} style={{display: 'flex', gap: 22, marginTop: 14, opacity: ease(f, at as number, (at as number) + 14), transform: `translateX(${(1 - ease(f, at as number, (at as number) + 14)) * -40}px)`}}>
              <span style={{fontFamily: display, fontWeight: 700, fontSize: 44, color: C.gold2, minWidth: 190}}>{k}</span>
              <span style={{fontFamily: display, fontWeight: 500, fontSize: 44}}>{v}</span>
            </div>
          ))}
        </div>
        <div style={{position: 'absolute', right: 110, bottom: 150, fontFamily: body, fontSize: 24, color: C.muted}}>Illustrative path. Not real prices.</div>
      </AbsoluteFill>

      {/* S5 */}
      <AbsoluteFill style={{opacity: s5}}>
        <Stander x={500} ground={945} scale={0.58} pulse={0.35 + Math.sin(f / 10) * 0.2} />
        <div style={{position: 'absolute', right: 110, top: 190, width: 900}}>
          <Words text="Axolotlion" size={170} delay={782} gradient />
          <div style={{height: 24}} />
          <Words text="Regrows. Leads. Glows." size={56} weight={500} font={body} delay={800} stagger={5} color={C.gold2} />
          
        </div>
      </AbsoluteFill>

      <Caption lines={cap} />
      <AbsoluteFill style={{background: '#02070f', opacity: out}} />
      <Audio src={staticFile('music.wav')} loop volume={(fr) => interpolate(fr, [0, 30, AX_TOTAL - 60, AX_TOTAL - 1], [0, 0.6, 0.6, 0], clamp)} />
    </AbsoluteFill>
  );
};
