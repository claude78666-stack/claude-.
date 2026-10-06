import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Avatar, body, byId, C, display, Eyebrow, Glass, GOLD, usePop, Words} from '../ui';

const Shell: React.FC<{id: string; delay: number; children: React.ReactNode}> = ({id, delay, children}) => {
  const c = byId(id);
  const p = usePop(delay, 17);
  return (
    <Glass style={{width: 850, height: 340, padding: '30px 36px', display: 'flex', gap: 30, alignItems: 'center', opacity: p, transform: `translateY(${interpolate(p, [0, 1], [70, 0])}px) scale(${interpolate(p, [0, 1], [0.94, 1])})`, border: `2px solid ${c.accent}55`}}>
      <Avatar id={id} size={206} ring={c.accent} />
      <div style={{flex: 1, minWidth: 0}}>
        <div style={{fontFamily: body, fontWeight: 600, fontSize: 21, letterSpacing: '0.14em', textTransform: 'uppercase', color: c.accent}}>{c.name} · {c.tool}</div>
        {children}
      </div>
    </Glass>
  );
};

const Chip: React.FC<{t: string; tone?: string}> = ({t, tone = C.amber}) => (
  <span style={{fontFamily: body, fontWeight: 600, fontSize: 22, color: tone, background: 'rgba(255,255,255,.07)', border: `1.5px solid ${tone}66`, borderRadius: 12, padding: '5px 13px'}}>{t}</span>
);

const Stamp: React.FC<{text: string; size?: number}> = ({text, size = 42}) => (
  <div style={{display: 'inline-block', marginTop: 12, fontFamily: display, fontWeight: 700, fontSize: size, color: '#2a1a00', background: GOLD, padding: '8px 22px', borderRadius: 14, letterSpacing: '-0.01em'}}>{text}</div>
);

export const Tools: React.FC = () => {
  const f = useCurrentFrame();
  const meter = interpolate(f, [70, 120], [0, 80], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{padding: '60px 120px 0'}}>
      <Eyebrow text="Real tools" />
      <div style={{height: 18}} />
      <Words text="Not just a meme." size={84} delay={6} maxWidth={1600} />
      <div style={{display: 'grid', gridTemplateColumns: 'repeat(2, 850px)', gap: 44, marginTop: 44, justifyContent: 'center'}}>
        <Shell id="sniffles" delay={40}>
          <div style={{fontFamily: display, fontWeight: 700, fontSize: 44, letterSpacing: '-0.02em', marginTop: 10}}>Stink meter <span style={{color: C.red}}>{Math.round(meter)}/100</span></div>
          <div style={{height: 14, borderRadius: 9, background: 'rgba(255,255,255,.1)', overflow: 'hidden', margin: '12px 0 14px'}}>
            <div style={{width: `${meter}%`, height: '100%', background: `linear-gradient(90deg, ${C.amber}, ${C.red})`, borderRadius: 9}} />
          </div>
          <div style={{display: 'flex', gap: 10, flexWrap: 'wrap'}}>
            <Chip t="Copycat ticker" />
            <Chip t="Thin pool" />
            <Chip t="Nobody selling" />
          </div>
        </Shell>
        <Shell id="judge" delay={78}>
          <div style={{fontFamily: body, fontSize: 28, color: C.muted, marginTop: 8}}>Sam v. Alex · Case SI-1548</div>
          <Stamp text="GUILTY: Sam" />
          <div style={{fontFamily: body, fontSize: 27, color: C.text, marginTop: 12, lineHeight: 1.3}}>Sentence: buy the whole household a pizza.</div>
        </Shell>
        <Shell id="banker" delay={116}>
          <div style={{fontFamily: body, fontSize: 28, color: C.muted, marginTop: 8}}>New headphones · $250</div>
          <Stamp text="ONE MONTH OF DISCIPLINE" size={34} />
          <div style={{fontFamily: body, fontSize: 27, color: C.text, marginTop: 12}}>That is 83% of one month's free money.</div>
        </Shell>
        <Shell id="professor" delay={154}>
          <div style={{fontFamily: display, fontWeight: 700, fontSize: 44, letterSpacing: '-0.02em', marginTop: 10}}>7 clauses to read twice</div>
          <div style={{display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 14}}>
            <Chip t="Auto-renewal" tone={C.amber} />
            <Chip t="Arbitration" tone={C.red} />
            <Chip t="No refunds" tone={C.amber} />
            <Chip t="Late fees" tone={C.amber} />
          </div>
        </Shell>
      </div>
      <div style={{textAlign: 'center', marginTop: 30, fontFamily: body, fontWeight: 600, fontSize: 32, color: C.gold2, opacity: interpolate(f, [250, 272], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
        Ten tools. Real uses. That is what the token unlocks.
      </div>
    </AbsoluteFill>
  );
};
