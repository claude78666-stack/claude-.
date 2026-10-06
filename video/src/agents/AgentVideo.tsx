import React from 'react';
import {AbsoluteFill, Audio, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Backdrop, body, byId, C, display, Eyebrow, Glass, GOLD, Logo, usePop, Words} from '../ui';
import {AgentInfo} from './data';

export const AGENT_FRAMES = 630; // 21 seconds at 30 fps

const Fade: React.FC<{from: number; to: number; children: React.ReactNode}> = ({from, to, children}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [from, from + 12, to - 12, to], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (f < from || f > to) return null;
  return <AbsoluteFill style={{opacity: o}}>{children}</AbsoluteFill>;
};

const Portrait: React.FC<{a: AgentInfo; size: number}> = ({a, size}) => {
  const accent = byId(a.id).accent;
  const p = usePop(0, 14);
  return (
    <div style={{width: size, height: size, borderRadius: 44, padding: 6, background: `linear-gradient(145deg, ${accent}, rgba(255,255,255,.12))`, boxShadow: `0 40px 90px -30px ${accent}88`, transform: `scale(${p})`, opacity: p, flex: 'none'}}>
      <div style={{width: '100%', height: '100%', borderRadius: 38, overflow: 'hidden', background: '#0a0620'}}>
        <Img src={staticFile(`characters/${a.id}.jpg`)} style={{width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 30%'}} />
      </div>
    </div>
  );
};

const Intro: React.FC<{a: AgentInfo}> = ({a}) => (
  <AbsoluteFill style={{padding: '0 130px', flexDirection: 'row', alignItems: 'center', gap: 100}}>
    <Portrait a={a} size={640} />
    <div style={{flex: 1}}>
      <Eyebrow text={a.role} delay={8} />
      <div style={{height: 24}} />
      <Words text={a.name} size={120} delay={14} gradient />
      <div style={{height: 26}} />
      <Words text={a.line} size={44} weight={400} color={C.muted} font={body} delay={40} stagger={2} maxWidth={900} />
      <div style={{height: 36}} />
      <ToolPill a={a} delay={90} />
    </div>
  </AbsoluteFill>
);

const ToolPill: React.FC<{a: AgentInfo; delay: number}> = ({a, delay}) => {
  const p = usePop(delay, 18);
  return (
    <div style={{display: 'inline-flex', alignItems: 'center', gap: 16, padding: '16px 30px', borderRadius: 999, border: '2px solid rgba(244,194,66,.55)', background: 'rgba(244,194,66,.1)', fontFamily: display, fontWeight: 700, fontSize: 36, color: C.gold2, opacity: p, transform: `scale(${interpolate(p, [0, 1], [0.8, 1])})`}}>
      Free tool: {a.tool}
    </div>
  );
};

const InOut: React.FC<{a: AgentInfo}> = ({a}) => {
  const p1 = usePop(6, 18), p2 = usePop(50, 18), pa = usePop(34, 20);
  const box = (label: string, text: string, p: number, tint: string) => (
    <Glass style={{flex: 1, padding: '48px 52px', opacity: p, transform: `translateY(${(1 - p) * 50}px)`, borderColor: tint}}>
      <div style={{fontFamily: body, fontWeight: 600, fontSize: 24, letterSpacing: '0.2em', textTransform: 'uppercase', color: tint, marginBottom: 20}}>{label}</div>
      <div style={{fontFamily: display, fontWeight: 700, fontSize: 56, lineHeight: 1.12, letterSpacing: '-0.02em'}}>{text}</div>
    </Glass>
  );
  return (
    <AbsoluteFill style={{padding: '0 130px', justifyContent: 'center'}}>
      <Eyebrow text="What it does" />
      <div style={{height: 40}} />
      <div style={{display: 'flex', alignItems: 'stretch', gap: 36}}>
        {box('You give', a.input, p1, C.cyan)}
        <div style={{alignSelf: 'center', fontSize: 80, color: C.gold, opacity: pa, fontFamily: display}}>→</div>
        {box('You get', a.output, p2, C.gold)}
      </div>
    </AbsoluteFill>
  );
};

const Steps: React.FC<{a: AgentInfo}> = ({a}) => (
  <AbsoluteFill style={{padding: '0 130px', justifyContent: 'center'}}>
    <Eyebrow text="How it works" />
    <div style={{height: 40}} />
    <div style={{display: 'flex', flexDirection: 'column', gap: 28}}>
      {a.steps.map((s, i) => <Step key={i} n={i + 1} text={s} delay={10 + i * 30} />)}
    </div>
  </AbsoluteFill>
);
const Step: React.FC<{n: number; text: string; delay: number}> = ({n, text, delay}) => {
  const p = usePop(delay, 18);
  return (
    <Glass style={{display: 'flex', alignItems: 'center', gap: 36, padding: '30px 44px', opacity: p, transform: `translateX(${(1 - p) * 90}px)`}}>
      <div style={{width: 84, height: 84, borderRadius: 24, display: 'grid', placeItems: 'center', background: GOLD, color: '#2a1a00', fontFamily: display, fontWeight: 700, fontSize: 52, flex: 'none'}}>{n}</div>
      <div style={{fontFamily: display, fontWeight: 600, fontSize: 56, letterSpacing: '-0.02em'}}>{text}</div>
    </Glass>
  );
};

const Example: React.FC<{a: AgentInfo}> = ({a}) => {
  const p = usePop(4, 18);
  return (
    <AbsoluteFill style={{padding: '0 130px', flexDirection: 'row', alignItems: 'center', gap: 80}}>
      <div style={{flex: 1}}>
        <Eyebrow text="Example" />
        <div style={{height: 30}} />
        <Words text="Here is a quick look at the result." size={84} delay={6} />
        <div style={{height: 36}} />
        <div style={{fontFamily: body, fontSize: 34, color: C.muted, opacity: p}}>Input</div>
        <div style={{fontFamily: display, fontWeight: 600, fontSize: 42, marginTop: 8, color: C.cyan, opacity: p, maxWidth: 760, lineHeight: 1.2}}>{a.exampleIn}</div>
      </div>
      <Glass style={{width: 860, padding: '46px 52px', display: 'flex', gap: 28, flexDirection: 'column'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 20}}>
          <Img src={staticFile(`characters/${a.id}.jpg`)} style={{width: 84, height: 84, borderRadius: 24, objectFit: 'cover', objectPosition: '50% 25%'}} />
          <div style={{fontFamily: display, fontWeight: 700, fontSize: 38, color: C.gold2}}>{a.name}</div>
        </div>
        {a.exampleOut.map((t, i) => <Out key={i} text={t} delay={24 + i * 22} first={i === 0} />)}
      </Glass>
    </AbsoluteFill>
  );
};
const Out: React.FC<{text: string; delay: number; first: boolean}> = ({text, delay, first}) => {
  const p = usePop(delay, 20);
  return <div style={{opacity: p, transform: `translateY(${(1 - p) * 24}px)`, fontFamily: display, fontWeight: first ? 700 : 500, fontSize: first ? 50 : 42, lineHeight: 1.15, color: first ? C.text : C.muted, padding: '14px 0', borderTop: first ? 'none' : `1.5px solid ${C.line}`}}>{text}</div>;
};

const Outro: React.FC<{a: AgentInfo}> = ({a}) => {
  const f = useCurrentFrame();
  const q = interpolate(f, [24, 44], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', textAlign: 'center'}}>
      <Logo size={150} uid="o" />
      <div style={{height: 26}} />
      <Words text={`${a.tool} is free.`} size={100} delay={4} align="center" gradient />
      <div style={{height: 20}} />
      <Words text="Meet the full SI Agents cabinet." size={46} weight={400} color={C.muted} font={body} delay={28} align="center" />
      <div style={{height: 44}} />
      <div style={{fontFamily: display, fontStyle: 'italic', fontSize: 48, color: C.gold2, opacity: q}}>{a.quip}</div>
      {a.note && <div style={{position: 'absolute', bottom: 60, fontFamily: body, fontSize: 28, color: C.muted, opacity: q}}>{a.note}</div>}
    </AbsoluteFill>
  );
};

export const AgentVideo: React.FC<{agent: AgentInfo}> = ({agent}) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [AGENT_FRAMES - 20, AGENT_FRAMES - 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: C.bg, color: C.text, fontFamily: body}}>
      <Backdrop />
      <Fade from={0} to={150}><Intro a={agent} /></Fade>
      <Fade from={138} to={288}><InOut a={agent} /></Fade>
      <Fade from={276} to={426}><Steps a={agent} /></Fade>
      <Fade from={414} to={534}><Example a={agent} /></Fade>
      <Fade from={522} to={AGENT_FRAMES}><Outro a={agent} /></Fade>
      <AbsoluteFill style={{background: C.bg, opacity: out}} />
      <Audio src={staticFile('music.wav')} volume={(fr) => interpolate(fr, [0, 30, AGENT_FRAMES - 60, AGENT_FRAMES - 1], [0, 0.6, 0.6, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
    </AbsoluteFill>
  );
};
