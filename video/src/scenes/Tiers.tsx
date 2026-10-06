import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Avatar, body, C, display, Eyebrow, Glass, GOLD, Icon, usePop, Words} from '../ui';

const Item: React.FC<{text: string; delay: number; gold?: boolean}> = ({text, delay, gold}) => {
  const p = usePop(delay, 18);
  return (
    <div style={{display: 'flex', alignItems: 'center', gap: 26, opacity: p, transform: `translateX(${interpolate(p, [0, 1], [-40, 0])}px)`}}>
      <div style={{width: 62, height: 62, borderRadius: 18, display: 'grid', placeItems: 'center', background: gold ? 'rgba(244,194,66,.18)' : 'rgba(78,227,160,.14)', color: gold ? C.gold : C.green}}>
        <Icon name="check" size={38} stroke={2.4} />
      </div>
      <div style={{fontFamily: body, fontWeight: 500, fontSize: 46, color: C.text}}>{text}</div>
    </div>
  );
};

export const Tiers: React.FC = () => {
  const f = useCurrentFrame();
  const left = usePop(40, 18);
  const right = usePop(70, 18);
  const note = interpolate(f, [240, 262], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const pulse = 0.5 + 0.5 * Math.sin(f / 16);
  return (
    <AbsoluteFill style={{padding: '64px 120px 0'}}>
      <Eyebrow text="What you get" />
      <div style={{height: 20}} />
      <Words text="Free to try. More for holders." size={84} delay={8} maxWidth={1600} />
      <div style={{display: 'flex', gap: 56, marginTop: 56, justifyContent: 'center'}}>
        <Glass style={{width: 800, height: 580, padding: '48px 54px', opacity: left, transform: `translateY(${interpolate(left, [0, 1], [70, 0])}px)`}}>
          <div style={{fontFamily: display, fontWeight: 700, fontSize: 52, letterSpacing: '-0.02em'}}>Everyone</div>
          <div style={{fontFamily: body, fontSize: 28, color: C.muted, marginTop: 4, marginBottom: 40}}>Free. No sign-up.</div>
          <div style={{display: 'flex', flexDirection: 'column', gap: 34}}>
            <Item text="All 10 tools" delay={84} />
            <Item text="A few free uses every day" delay={102} />
            <Item text="Share-ready result cards" delay={120} />
          </div>
        </Glass>
        <Glass style={{width: 800, height: 580, padding: '48px 54px', opacity: right, transform: `translateY(${interpolate(right, [0, 1], [70, 0])}px)`, border: `2.5px solid rgba(244,194,66,${0.55 + pulse * 0.3})`, boxShadow: `0 0 ${50 + pulse * 30}px -10px rgba(244,194,66,.55)`, background: 'linear-gradient(180deg, rgba(244,194,66,.13), rgba(255,255,255,.03))', position: 'relative'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 20}}>
            <div style={{fontFamily: display, fontWeight: 700, fontSize: 52, letterSpacing: '-0.02em', background: GOLD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}}>Token holders</div>
            <div style={{fontFamily: body, fontWeight: 700, fontSize: 20, letterSpacing: '0.12em', color: '#2a1a00', background: GOLD, padding: '6px 14px', borderRadius: 10}}>PLANNED</div>
          </div>
          <div style={{fontFamily: body, fontSize: 28, color: C.muted, marginTop: 4, marginBottom: 40}}>A pass to the extras.</div>
          <div style={{display: 'flex', flexDirection: 'column', gap: 34}}>
            <Item text="Unlimited uses" delay={116} gold />
            <Item text="Longer, funnier answers" delay={134} gold />
            <Item text="Custom share cards" delay={152} gold />
          </div>
          <div style={{position: 'absolute', right: 46, bottom: 26, display: 'flex'}}>
            <Avatar id="judge" size={96} ring="#f4c242" />
            <Avatar id="banker" size={96} ring="#3ddc97" style={{marginLeft: -22}} />
            <Avatar id="dj" size={96} ring="#ff4fd8" style={{marginLeft: -22}} />
          </div>
        </Glass>
      </div>
      <div style={{marginTop: 46, textAlign: 'center', fontFamily: body, fontWeight: 600, fontSize: 38, color: C.gold2, opacity: note}}>
        A pass to use the tools. Not an investment.
      </div>
    </AbsoluteFill>
  );
};
