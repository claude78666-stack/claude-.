import React from 'react';
import { interpolate, useCurrentFrame } from 'remotion';
import { SCENE, theme } from '../theme';

// Small caption naming the tool that drives the scene.
export const Label: React.FC<{ tool: string; what: string }> = ({ tool, what }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 10, SCENE - 10, SCENE], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 160,
        width: '100%',
        textAlign: 'center',
        fontFamily: theme.font,
        opacity,
      }}
    >
      <div style={{ color: theme.accent, fontSize: 34, letterSpacing: 8, fontWeight: 700 }}>
        {tool.toUpperCase()}
      </div>
      <div style={{ color: theme.ink, fontSize: 46, fontWeight: 800, marginTop: 12 }}>{what}</div>
    </div>
  );
};
