import React from 'react';
import { Composition } from 'remotion';
import { Showcase, SHOWCASE_FRAMES } from './Showcase';
import { AxolotlShort, AXOLOTL_FRAMES } from './axolotl/AxolotlShort';
import { RobotRain, ROBOT_FRAMES } from './robot/RobotRain';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Showcase"
      component={Showcase}
      durationInFrames={SHOWCASE_FRAMES}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="AxolotlShort"
      component={AxolotlShort}
      durationInFrames={AXOLOTL_FRAMES}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="RobotRain"
      component={RobotRain}
      durationInFrames={ROBOT_FRAMES}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
);
