import React from 'react';
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from 'remotion';
import { ThreeCanvas } from '@remotion/three';
import { theme } from '../theme';
import { Label } from './Label';

// three.js scene written with React Three Fiber; @remotion/three keeps it
// in sync with Remotion's frame clock.
const Knot: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / 30;
  const scale = interpolate(frame, [0, 20], [0.2, 1], { extrapolateRight: 'clamp' });
  return (
    <mesh rotation={[t * 0.8, t * 1.2, 0]} scale={scale}>
      <torusKnotGeometry args={[1, 0.34, 220, 32]} />
      <meshStandardMaterial color={theme.accent} metalness={0.55} roughness={0.25} />
    </mesh>
  );
};

export const ThreeScene: React.FC = () => {
  const { width, height } = useVideoConfig();
  return (
    <AbsoluteFill>
      <ThreeCanvas width={width} height={height} camera={{ position: [0, 0, 7], fov: 45 }}>
        <ambientLight intensity={0.35} />
        <directionalLight position={[4, 6, 5]} intensity={2.2} color="#fff3d6" />
        <pointLight position={[-5, -3, 2]} intensity={40} color={theme.teal} />
        <Knot />
      </ThreeCanvas>
      <Label tool="three.js + React Three Fiber" what="3D scenes, cameras, lighting" />
    </AbsoluteFill>
  );
};
