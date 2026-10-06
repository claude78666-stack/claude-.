import React from 'react';
import {AbsoluteFill, Audio, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {linearTiming, TransitionSeries} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {Backdrop, body, C} from './ui';
import {Hook} from './scenes/Hook';
import {WhatIs} from './scenes/WhatIs';
import {Tiers} from './scenes/Tiers';
import {MoneyFlow} from './scenes/MoneyFlow';
import {Tools} from './scenes/Tools';
import {Honest} from './scenes/Honest';
import {Outro} from './scenes/Outro';

export const FPS = 30;
export const TRANSITION = 12;
// Scene lengths in frames. Total = sum - TRANSITION * (scenes - 1) = 1800 frames = 60 seconds.
const SCENES = [
  {C: Hook, len: 180},
  {C: WhatIs, len: 270},
  {C: Tiers, len: 330},
  {C: MoneyFlow, len: 360},
  {C: Tools, len: 330},
  {C: Honest, len: 240},
  {C: Outro, len: 162},
];
export const TOTAL = SCENES.reduce((a, s) => a + s.len, 0) - TRANSITION * (SCENES.length - 1);

export const Video: React.FC = () => {
  const f = useCurrentFrame();
  const out = interpolate(f, [TOTAL - 24, TOTAL - 1], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: '#06040f', color: C.text, fontFamily: body}}>
      <Backdrop />
      <TransitionSeries>
        {SCENES.flatMap((s, i) => {
          const items = [
            <TransitionSeries.Sequence key={`s${i}`} durationInFrames={s.len}>
              <s.C />
            </TransitionSeries.Sequence>,
          ];
          if (i < SCENES.length - 1) items.push(<TransitionSeries.Transition key={`t${i}`} presentation={fade()} timing={linearTiming({durationInFrames: TRANSITION})} />);
          return items;
        })}
      </TransitionSeries>
      <AbsoluteFill style={{background: '#06040f', opacity: out}} />
      <Audio src={staticFile('music.wav')} volume={(frame) => interpolate(frame, [0, 36, TOTAL - 70, TOTAL - 1], [0, 0.85, 0.85, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
    </AbsoluteFill>
  );
};
