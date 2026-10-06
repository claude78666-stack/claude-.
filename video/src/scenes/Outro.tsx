import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Avatar, body, C, CAST, display, GOLD, Logo, usePop, Words} from '../ui';

export const Outro: React.FC = () => {
  const f = useCurrentFrame();
  const logo = usePop(4, 14);
  const foot = interpolate(f, [86, 108], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{display: 'flex', alignItems: 'center', gap: 36, transform: `scale(${logo})`, opacity: logo}}>
        <Logo size={190} uid="outro" />
        <div style={{fontFamily: display, fontWeight: 700, fontSize: 168, letterSpacing: '-0.04em', background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', lineHeight: 1}}>SI Agents</div>
      </div>
      <div style={{marginTop: 26}}>
        <Words text="Ten robots. Ten egos. Zero humility." size={62} delay={28} align="center" weight={500} color={C.text} maxWidth={1500} />
      </div>
      <div style={{display: 'flex', gap: 26, marginTop: 56}}>
        {CAST.map((c, i) => {
          const p = usePop(44 + i * 4, 14);
          return (
            <div key={c.id} style={{opacity: p, transform: `translateY(${interpolate(p, [0, 1], [50, 0])}px) scale(${interpolate(p, [0, 1], [0.6, 1])})`}}>
              <Avatar id={c.id} size={132} ring={c.accent} />
            </div>
          );
        })}
      </div>
      <div style={{marginTop: 50, fontFamily: body, fontWeight: 600, fontSize: 40, color: C.gold2, opacity: foot}}>Pick an agent.</div>
      <div style={{position: 'absolute', bottom: 46, fontFamily: body, fontSize: 24, color: C.muted, opacity: foot}}>Parody · Not financial advice · The coin has not launched</div>
    </AbsoluteFill>
  );
};
