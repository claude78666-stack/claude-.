import React from 'react';
import { AbsoluteFill, Sequence } from 'remotion';
import { SCENE, theme } from './theme';
import { SatoriTitle } from './scenes/SatoriTitle';
import { GsapText } from './scenes/GsapText';
import { AnimeGrid } from './scenes/AnimeGrid';
import { ThreeScene } from './scenes/ThreeScene';
import { RiveScene } from './scenes/RiveScene';

const scenes = [SatoriTitle, GsapText, AnimeGrid, ThreeScene, RiveScene];
export const SHOWCASE_FRAMES = SCENE * scenes.length;

// One scene per tool, three seconds each.
export const Showcase: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: theme.bg }}>
    {scenes.map((Scene, i) => (
      <Sequence key={i} from={i * SCENE} durationInFrames={SCENE} premountFor={30}>
        <Scene />
      </Sequence>
    ))}
  </AbsoluteFill>
);
