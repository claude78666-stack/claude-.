import React from 'react';
import {AbsoluteFill, Img, random, staticFile} from 'remotion';
import {body, C, display} from '../ui';
import {GLOW, RigBody, RUN_H, RUN_W} from './AxolotlionVideo';

// Everything here is built to loop: all motion is periodic with LOOP_S seconds.
export const LOOP_S = 2;
const TAU = Math.PI * 2;

const Water: React.FC<{w: number; h: number; t: number; offsetY: number; scale: number}> = ({w, h, t, offsetY, scale}) => (
  <AbsoluteFill style={{background: '#04121f'}}>
    <Img src={staticFile('axolotlion/bg.jpg')} style={{position: 'absolute', left: (w - 1920 * scale) / 2, top: -offsetY, width: 1920 * scale, height: 1080 * scale, filter: 'saturate(1.12) contrast(1.05)'}} />
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 0%, rgba(120,255,235,${0.16 + 0.05 * Math.sin((t / LOOP_S) * TAU)}), rgba(0,0,0,0) 60%)`}} />
    <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,6,16,.7) 100%)'}} />
  </AbsoluteFill>
);

const Bubbles: React.FC<{w: number; h: number; t: number; count: number; seed: string; maxSize?: number}> = ({w, h, t, count, seed, maxSize = 16}) => (
  <>
    {Array.from({length: count}).map((_, i) => {
      const n = 1 + Math.floor(random(`${seed}n${i}`) * 2); // whole number of laps per loop keeps the GIF seamless
      const x = random(`${seed}x${i}`) * w + Math.sin((t / LOOP_S) * TAU * n + i) * 10;
      const y = (((random(`${seed}y${i}`) - (t / LOOP_S) * n) % 1) + 1) % 1 * (h + 60) - 30;
      const s = 4 + random(`${seed}s${i}`) * maxSize;
      return <div key={i} style={{position: 'absolute', left: x, top: y, width: s, height: s, borderRadius: '50%', border: '1.5px solid rgba(210,245,255,.7)', background: 'radial-gradient(circle at 35% 30%, rgba(255,255,255,.55), rgba(255,255,255,0) 60%)', opacity: 0.25 + random(`${seed}o${i}`) * 0.5}} />;
    })}
  </>
);

/* ---------- face-only logo (1:1) ---------- */
export const FaceLogo: React.FC<{size: number; t: number}> = ({size, t}) => {
  const k = size / 1000;
  const ph = (t / LOOP_S) * TAU;
  const pulse = 0.5 + 0.5 * Math.sin(ph);
  const face = 840 * k;
  return (
    <AbsoluteFill style={{background: '#050c1c', overflow: 'hidden'}}>
      <AbsoluteFill style={{background: 'radial-gradient(circle at 50% 46%, #2a1a63 0%, #14305e 38%, #06182c 78%)'}} />
      <AbsoluteFill style={{background: 'conic-gradient(from 0deg at 50% 46%, rgba(111,242,255,.0), rgba(111,242,255,.16), rgba(255,120,225,.0), rgba(255,120,225,.14), rgba(111,242,255,.0))', transform: `rotate(${(t / LOOP_S) * 360}deg)`, filter: 'blur(14px)', opacity: 0.9}} />
      <div style={{position: 'absolute', left: size / 2 - 430 * k, top: size * 0.46 - 430 * k, width: 860 * k, height: 860 * k, borderRadius: '50%', background: `radial-gradient(circle, rgba(255,150,230,${0.34 + 0.2 * pulse}), rgba(90,200,255,${0.18 + 0.12 * pulse}) 55%, rgba(0,0,0,0) 72%)`}} />
      <Bubbles w={size} h={size} t={t} count={22} seed="logo" maxSize={22 * k} />
      <div style={{position: 'absolute', left: size / 2 - face / 2, top: size * 0.47 - face / 2, width: face, height: face, transform: `rotate(${Math.sin(ph) * 2.2}deg) scale(${1 + 0.018 * Math.sin(ph + 1.2)})`, filter: `drop-shadow(0 0 ${26 * k + 20 * k * pulse}px rgba(255,120,225,.75)) drop-shadow(0 0 ${60 * k + 40 * k * pulse}px rgba(90,200,255,.55))`}}>
        <Img src={staticFile('axolotlion/face.png')} style={{width: '100%', height: '100%'}} />
      </div>
      <AbsoluteFill style={{boxShadow: `inset 0 0 ${120 * k}px rgba(0,0,0,.55)`}} />
    </AbsoluteFill>
  );
};

/* ---------- banner (3:1) ---------- */
export const Banner: React.FC<{t: number; w?: number; h?: number}> = ({t, w = 1500, h = 500}) => {
  const frame = t * 20; // the rig counts frames at 20 fps, 2 strides per second = 10 frames per stride
  const ph = (t / LOOP_S) * TAU;
  const scale = 0.5, rw = RUN_W * scale, rh = RUN_H * scale;
  const cx = 1010, ground = 452;
  const gal = Math.abs(Math.sin(t * Math.PI * 2.0));
  const dy = -gal * 22;
  const lap = t * 2.0;
  return (
    <AbsoluteFill style={{background: '#04121f', overflow: 'hidden'}}>
      <Water w={w} h={h} t={t} offsetY={290} scale={w / 1920} />
      {/* speed streaks, whole laps per loop */}
      {Array.from({length: 26}).map((_, i) => {
        const n = 1 + (i % 3);
        const len = 80 + random(`sl${i}`) * 160;
        const x = ((((random(`sx${i}`) + (t / LOOP_S) * n * 0.5) % 1) + 1) % 1) * (w + 400) - 200;
        const y = 30 + random(`sy${i}`) * (h - 60);
        return <div key={i} style={{position: 'absolute', left: w - x - len, top: y, width: len, height: 3, borderRadius: 3, background: 'rgba(200,240,255,.45)', opacity: 0.2 + random(`so${i}`) * 0.4, filter: 'blur(1px)'}} />;
      })}
      <Bubbles w={w} h={h} t={t} count={16} seed="ban" />
      {/* dust puffs trailing the paws */}
      {[0, 1, 2].map((i) => {
        const k = Math.floor(lap) - i, age = lap - k;
        return <div key={i} style={{position: 'absolute', left: cx - rw * 0.2 - age * 130 - 30, top: ground - 22 - age * 34, width: 60 + age * 60, height: 36 + age * 30, borderRadius: '50%', background: 'radial-gradient(circle, rgba(235,225,200,.5), rgba(235,225,200,0) 70%)', opacity: (1 - age) * 0.75, filter: 'blur(4px)'}} />;
      })}
      <div style={{position: 'absolute', left: cx - rw * 0.4, top: ground - 16, width: rw * 0.8, height: 32, borderRadius: '50%', background: 'radial-gradient(ellipse, rgba(0,10,20,.55), rgba(0,10,20,0) 70%)', transform: `scale(${1 - gal * 0.2})`}} />
      <div style={{position: 'absolute', left: cx - rw / 2, top: ground - rh + dy, width: rw, height: rh, transform: `rotate(${Math.sin(ph * 2) * 1.6}deg)`, transformOrigin: '50% 90%', filter: GLOW}}>
        <div style={{width: RUN_W, height: RUN_H, transform: `scale(${scale})`, transformOrigin: '0 0'}}><RigBody frame={frame} fps={20} freq={2.0} /></div>
      </div>
      <AbsoluteFill style={{background: 'linear-gradient(90deg, rgba(2,8,20,.78) 0%, rgba(2,8,20,.35) 32%, rgba(2,8,20,0) 52%)'}} />
      <div style={{position: 'absolute', left: 84, top: 56}}>
        <div style={{fontFamily: body, fontWeight: 700, fontSize: 26, letterSpacing: '0.28em', textTransform: 'uppercase', color: C.cyan, textShadow: '0 2px 10px #000'}}>The first SI animal</div>
        <div style={{marginTop: 6, fontFamily: display, fontWeight: 700, fontSize: 118, letterSpacing: '-0.035em', lineHeight: 1.05, background: 'linear-gradient(180deg,#ffe9a3 0%,#f4c242 55%,#c8921e 100%)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', filter: 'drop-shadow(0 4px 18px rgba(0,0,0,.6))'}}>Axolotlion</div>
        <div style={{marginTop: 8, fontFamily: display, fontWeight: 600, fontSize: 38, letterSpacing: '-0.01em', color: '#fff', textShadow: '0 2px 12px #000'}}>Superior Intelligence. <span style={{color: '#ff9ae0'}}>Not AI.</span></div>
        <div style={{marginTop: 10, fontFamily: body, fontWeight: 600, fontSize: 30, letterSpacing: '0.04em', color: C.gold2, textShadow: '0 2px 10px #000'}}>Regrows. Leads. Glows.</div>
      </div>
      <div style={{position: 'absolute', left: 84, bottom: 34, display: 'flex', alignItems: 'center', gap: 30}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 12, padding: '8px 18px 8px 14px', borderRadius: 999, background: 'rgba(3,10,24,.72)', border: `1.5px solid ${C.line}`}}>
          <Img src={staticFile('axolotlion/solana.svg')} style={{width: 34, height: 30}} />
          <span style={{fontFamily: display, fontWeight: 700, fontSize: 26, color: '#fff'}}>Solana</span>
        </div>
        <div style={{display: 'flex', alignItems: 'center', gap: 10, padding: '4px 20px 4px 12px', borderRadius: 999, background: 'rgba(3,10,24,.72)', border: `1.5px solid ${C.line}`}}>
          <Img src={staticFile('axolotlion/pumpfun.png')} style={{width: 46, height: 46}} />
          <span style={{fontFamily: display, fontWeight: 700, fontSize: 26, color: '#fff'}}>pump.fun</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
