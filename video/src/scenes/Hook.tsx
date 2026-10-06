import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Avatar, body, C, CAST, Eyebrow, Logo, usePop, Words} from '../ui';

export const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const S = 880;
  const R = S * 0.385;
  const A = S * 0.2;
  const logoPop = usePop(4, 14);
  const glow = 0.55 + 0.25 * Math.sin(f / 14);
  return (
    <AbsoluteFill style={{padding: '0 110px', flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between'}}>
      <div style={{width: 900}}>
        <Eyebrow text="The token, explained" />
        <div style={{height: 30}} />
        <Words text="Ten robots." size={132} delay={10} />
        <Words text="Ten egos." size={132} delay={32} />
        <Words text="One token." size={132} delay={54} gradient />
        <div style={{height: 38}} />
        <Words text="SI Agents: a cabinet of Superior Intelligences with a free tool each." size={40} weight={400} color={C.muted} font={body} delay={92} stagger={2} maxWidth={780} />
      </div>
      <div style={{position: 'relative', width: S, height: S}}>
        <div style={{position: 'absolute', inset: S * 0.12, borderRadius: '50%', background: `radial-gradient(circle, rgba(139,92,246,${glow}), rgba(232,93,216,.15) 60%, transparent 72%)`, filter: 'blur(26px)'}} />
        <div style={{position: 'absolute', inset: S * 0.06, borderRadius: '50%', border: '2px dashed rgba(244,194,66,.4)', transform: `rotate(${f * 0.12}deg)`}} />
        <div style={{position: 'absolute', inset: S * 0.2, borderRadius: '50%', border: '2px solid rgba(255,255,255,.12)'}} />
        {CAST.map((c, i) => {
          const a = -Math.PI / 2 + (i / CAST.length) * Math.PI * 2 + f * 0.0036;
          const p = usePop(10 + i * 5, 13);
          return (
            <div key={c.id} style={{position: 'absolute', left: S / 2 + R * Math.cos(a) - A / 2, top: S / 2 + R * Math.sin(a) - A / 2, opacity: p, transform: `scale(${interpolate(p, [0, 1], [0.2, 1])})`}}>
              <Avatar id={c.id} size={A} ring={c.accent} />
            </div>
          );
        })}
        <div style={{position: 'absolute', left: S / 2 - 150, top: S / 2 - 150, transform: `scale(${logoPop})`, opacity: logoPop}}>
          <Logo size={300} uid="hook" />
        </div>
      </div>
    </AbsoluteFill>
  );
};
