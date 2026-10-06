import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {body, C, display, Eyebrow, GOLD, Icon, usePop, Words} from '../ui';

const Line: React.FC<{text: string; delay: number}> = ({text, delay}) => {
  const p = usePop(delay, 18);
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 30, padding: '28px 36px', borderRadius: 24, background: 'rgba(255,255,255,.055)', border: `1.5px solid ${C.line}`, opacity: p, transform: `translateX(${interpolate(p, [0, 1], [80, 0])}px)`}}>
      <div style={{width: 70, height: 70, borderRadius: 20, display: 'grid', placeItems: 'center', background: 'rgba(255,107,122,.15)', color: C.red}}>
        <Icon name="x" size={38} stroke={2.6} />
      </div>
      <div style={{fontFamily: display, fontWeight: 600, fontSize: 45, letterSpacing: '-0.02em'}}>{text}</div>
    </div>
  );
};

export const Honest: React.FC = () => {
  const f = useCurrentFrame();
  const shield = usePop(6, 14);
  const end = interpolate(f, [170, 192], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{padding: '0 120px', flexDirection: 'row', alignItems: 'center', gap: 90}}>
      <div style={{width: 640}}>
        <div style={{width: 210, height: 210, borderRadius: 56, display: 'grid', placeItems: 'center', background: 'linear-gradient(145deg, rgba(244,194,66,.2), rgba(244,194,66,.05))', border: '2px solid rgba(244,194,66,.5)', color: C.gold, transform: `scale(${shield})`, opacity: shield, marginBottom: 34}}>
          <Icon name="shield" size={120} stroke={1.6} />
        </div>
        <Eyebrow text="Read this part" delay={6} />
        <div style={{height: 16}} />
        <Words text="The honest part." size={104} delay={10} />
      </div>
      <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 26}}>
        <Line text="Not an investment" delay={44} />
        <Line text="No dividends or promised returns" delay={68} />
        <Line text="The coin is not launched yet" delay={92} />
        <Line text="Name, ticker and plan may change" delay={116} />
        <div style={{marginTop: 22, fontFamily: display, fontWeight: 700, fontSize: 48, letterSpacing: '-0.02em', opacity: end, transform: `translateY(${(1 - end) * 20}px)`, background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}}>
          It is a pass to use the tools. Nothing more.
        </div>
      </div>
    </AbsoluteFill>
  );
};
