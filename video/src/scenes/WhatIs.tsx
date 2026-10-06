import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {body, C, CAST, display, Eyebrow, GOLD, usePop, Words} from '../ui';

const Card: React.FC<{i: number}> = ({i}) => {
  const f = useCurrentFrame();
  const c = CAST[i];
  const p = usePop(54 + i * 6, 16);
  const start = 130;
  const active = f >= start && Math.floor((f - start) / 11) % 10 === i && f < start + 110;
  const lift = active ? 1 : 0;
  return (
    <div style={{width: 320, opacity: p, transform: `translateY(${interpolate(p, [0, 1], [60, 0]) - lift * 10}px) scale(${1 + lift * 0.035})`, borderRadius: 26, overflow: 'hidden', background: 'rgba(255,255,255,.05)', border: `2.5px solid ${active ? c.accent : C.line}`, boxShadow: active ? `0 0 46px -6px ${c.accent}` : '0 20px 40px -24px rgba(0,0,0,.8)'}}>
      <Img src={staticFile(`characters/${c.id}.jpg`)} style={{width: '100%', height: 250, objectFit: 'cover', objectPosition: '50% 22%', display: 'block'}} />
      <div style={{padding: '12px 18px 16px'}}>
        <div style={{fontFamily: display, fontWeight: 700, fontSize: 28, letterSpacing: '-0.01em'}}>{c.name}</div>
        <div style={{fontFamily: body, fontWeight: 600, fontSize: 23, color: c.accent, marginTop: 2}}>{c.tool}</div>
      </div>
    </div>
  );
};

export const WhatIs: React.FC = () => {
  const f = useCurrentFrame();
  const sub = interpolate(f, [30, 50], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{padding: '64px 120px 0'}}>
      <Eyebrow text="So what is it?" />
      <div style={{height: 20}} />
      <Words text="A pass to use the SI Agents tools." size={78} delay={8} gradient={false} maxWidth={1500} />
      <div style={{fontFamily: body, fontSize: 31, color: C.muted, marginTop: 14, opacity: sub}}>
        Ten characters. Ten free tools. A planned token that unlocks the extras.
      </div>
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(5, 320px)', columnGap: 20, rowGap: 22, marginTop: 38, justifyContent: 'center'}}>
        {CAST.map((_, i) => (
          <Card key={i} i={i} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
