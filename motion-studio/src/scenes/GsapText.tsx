import React, { useLayoutEffect, useRef } from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import gsap from 'gsap';
import { theme } from '../theme';
import { Label } from './Label';

const WORD = 'MOTION';

// GSAP builds a paused timeline once; every frame Remotion seeks it to the
// matching time, so renders are deterministic frame by frame.
export const GsapText: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const root = useRef<HTMLDivElement>(null);
  const tl = useRef<gsap.core.Timeline | null>(null);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      tl.current = gsap
        .timeline({ paused: true })
        .from('.letter', { y: 260, rotate: 40, opacity: 0, duration: 0.7, ease: 'back.out(1.8)', stagger: 0.08 })
        .to('.letter', { color: theme.accent, duration: 0.3, stagger: 0.05 }, '+=0.2')
        .to('.bar', { scaleX: 1, duration: 0.6, ease: 'power3.inOut' }, '<');
    }, root);
    return () => ctx.revert();
  }, []);

  useLayoutEffect(() => {
    tl.current?.seek(frame / fps, false);
  }, [frame, fps]);

  return (
    <AbsoluteFill ref={root} style={{ alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ display: 'flex', fontFamily: theme.font, fontWeight: 900, fontSize: 190, color: theme.ink }}>
        {WORD.split('').map((ch, i) => (
          <span key={i} className="letter" style={{ display: 'inline-block' }}>
            {ch}
          </span>
        ))}
      </div>
      <div
        className="bar"
        style={{ width: 760, height: 18, background: theme.coral, borderRadius: 9, marginTop: 30, transform: 'scaleX(0)' }}
      />
      <Label tool="GSAP" what="Text & timeline animation" />
    </AbsoluteFill>
  );
};
