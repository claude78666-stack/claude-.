import React, { useLayoutEffect, useRef } from 'react';
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from 'remotion';
import { animate, stagger, type JSAnimation } from 'animejs';
import { theme } from '../theme';
import { Label } from './Label';

const COLS = 9;
const ROWS = 12;

// anime.js runs with autoplay off; Remotion seeks it (in ms) on every frame.
export const AnimeGrid: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const root = useRef<HTMLDivElement>(null);
  const anim = useRef<JSAnimation | null>(null);

  useLayoutEffect(() => {
    const dots = root.current?.querySelectorAll('.dot');
    if (!dots) return;
    anim.current = animate(dots, {
      scale: [{ to: 1.9, ease: 'outSine', duration: 450 }, { to: 0.6, ease: 'inOutQuad', duration: 900 }],
      backgroundColor: [{ to: theme.teal }, { to: theme.accent }],
      translateY: [{ to: -40 }, { to: 0 }],
      delay: stagger(70, { grid: [COLS, ROWS], from: 'center' }),
      loop: true,
      alternate: true,
      autoplay: false,
    });
    return () => {
      anim.current?.revert();
    };
  }, []);

  useLayoutEffect(() => {
    anim.current?.seek((frame / fps) * 1000);
  }, [frame, fps]);

  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
      <div
        ref={root}
        style={{ display: 'grid', gridTemplateColumns: `repeat(${COLS}, 70px)`, gap: 26, marginTop: -160 }}
      >
        {Array.from({ length: COLS * ROWS }).map((_, i) => (
          <div key={i} className="dot" style={{ width: 70, height: 70, borderRadius: 35, background: theme.coral }} />
        ))}
      </div>
      <Label tool="anime.js" what="Staggered icon & UI motion" />
    </AbsoluteFill>
  );
};
