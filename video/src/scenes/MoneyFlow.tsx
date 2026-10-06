import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {body, C, display, Eyebrow, Glass, GOLD, Icon, usePop, Words} from '../ui';

const NODES = [
  {icon: 'bolt', title: 'A tool gets used', text: 'Free daily uses for everyone. Heavier use costs a few cents.', color: C.cyan},
  {icon: 'coin', title: 'USDC fee collected', text: 'Paid uses land in the project wallet.', color: C.green},
  {icon: 'wallet', title: 'Half buys back the token', text: 'A fixed share of earnings buys the token.', color: C.gold},
  {icon: 'flame', title: 'Bought tokens are burned', text: 'Every burn would link to its on-chain transaction.', color: C.red},
] as const;
const START = (i: number) => 46 + i * 52;

const Node: React.FC<{i: number}> = ({i}) => {
  const f = useCurrentFrame();
  const n = NODES[i];
  const p = usePop(START(i), 16);
  const active = f >= START(i) + 8;
  const glow = active ? 0.55 + 0.35 * Math.sin((f - START(i)) / 10) : 0;
  return (
    <Glass style={{width: 372, height: 388, padding: '38px 32px', opacity: p, transform: `translateY(${interpolate(p, [0, 1], [60, 0])}px) scale(${interpolate(p, [0, 1], [0.92, 1])})`, border: `2px solid ${active ? n.color : C.line}`, boxShadow: active ? `0 0 ${34 * glow + 10}px -8px ${n.color}` : 'none'}}>
      <div style={{width: 96, height: 96, borderRadius: 26, display: 'grid', placeItems: 'center', background: 'rgba(255,255,255,.07)', color: n.color, marginBottom: 26}}>
        <Icon name={n.icon} size={56} stroke={1.9} />
      </div>
      <div style={{fontFamily: display, fontWeight: 700, fontSize: 40, lineHeight: 1.1, letterSpacing: '-0.02em'}}>{n.title}</div>
      <div style={{fontFamily: body, fontSize: 27, lineHeight: 1.35, color: C.muted, marginTop: 12}}>{n.text}</div>
    </Glass>
  );
};

const Arrow: React.FC<{i: number}> = ({i}) => {
  const f = useCurrentFrame();
  const t = interpolate(f, [START(i) + 22, START(i) + 46], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{width: 84, display: 'grid', placeItems: 'center'}}>
      <svg width="84" height="40" viewBox="0 0 84 40" fill="none">
        <path d="M6 20H70" stroke={C.gold} strokeWidth="5" strokeLinecap="round" strokeDasharray="64" strokeDashoffset={64 * (1 - t)} />
        <path d="M58 8l14 12-14 12" stroke={C.gold} strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" opacity={t > 0.85 ? 1 : 0} />
      </svg>
    </div>
  );
};

const Count: React.FC<{to: number; from: number; prefix?: string}> = ({to, from, prefix = '$'}) => {
  const f = useCurrentFrame();
  const v = interpolate(f, [from, from + 36], [0, to], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <>{prefix}{Math.round(v).toLocaleString('en-US')}</>;
};

export const MoneyFlow: React.FC = () => {
  const f = useCurrentFrame();
  const panel = usePop(250, 18);
  return (
    <AbsoluteFill style={{padding: '60px 80px 0'}}>
      <div style={{paddingLeft: 40}}>
        <Eyebrow text="The plan" />
        <div style={{height: 18}} />
        <Words text="From tool use to token burn." size={80} delay={6} maxWidth={1700} />
      </div>
      <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', marginTop: 50}}>
        {NODES.map((_, i) => (
          <React.Fragment key={i}>
            <Node i={i} />
            {i < NODES.length - 1 ? <Arrow i={i} /> : null}
          </React.Fragment>
        ))}
      </div>
      <Glass style={{margin: '44px auto 0', width: 1700, padding: '32px 52px', opacity: panel, transform: `translateY(${interpolate(panel, [0, 1], [50, 0])}px)`, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
        <div>
          <div style={{fontFamily: body, fontWeight: 600, fontSize: 21, letterSpacing: '0.16em', textTransform: 'uppercase', color: C.gold}}>Example, per day</div>
          <div style={{fontFamily: body, fontSize: 36, color: C.text, marginTop: 10}}>500 uses · 20% paid · $0.10 each</div>
        </div>
        <Icon name="arrow" size={46} color={C.gold} />
        <div style={{textAlign: 'center'}}>
          <div style={{fontFamily: display, fontWeight: 700, fontSize: 78, letterSpacing: '-0.03em'}}><Count to={10} from={262} /></div>
          <div style={{fontFamily: body, fontSize: 22, color: C.muted}}>earned</div>
        </div>
        <Icon name="arrow" size={46} color={C.gold} />
        <div style={{textAlign: 'center'}}>
          <div style={{fontFamily: display, fontWeight: 700, fontSize: 78, letterSpacing: '-0.03em', background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}}><Count to={5} from={292} /></div>
          <div style={{fontFamily: body, fontSize: 22, color: C.muted}}>bought back and burned</div>
        </div>
      </Glass>
      <div style={{textAlign: 'center', fontFamily: body, fontSize: 27, color: C.muted, marginTop: 20, opacity: interpolate(f, [300, 322], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        A made-up example to show the math. Not a forecast or a promise.
      </div>
    </AbsoluteFill>
  );
};
