import React from 'react';
import { AbsoluteFill, Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { Label } from './Label';

// The title card image is generated ahead of time by Satori (scripts/title-card.mjs);
// Remotion animates it in with a spring.
export const SatoriTitle: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame, fps, config: { damping: 14 } });
  return (
    <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
      <Img
        src={staticFile('title.svg')}
        style={{
          width: 900,
          transform: `scale(${interpolate(s, [0, 1], [0.6, 1])}) rotate(${interpolate(s, [0, 1], [-6, 0])}deg)`,
          opacity: s,
        }}
      />
      <Label tool="Satori + Remotion" what="Title card from code" />
    </AbsoluteFill>
  );
};
