import React from 'react';
import {Composition} from 'remotion';
import {FPS, TOTAL, Video} from './Video';
import {AgentVideo, AGENT_FRAMES} from './agents/AgentVideo';
import {AGENTS} from './agents/data';
import {AxolotlionVideo, AX_FPS, AX_TOTAL} from './axolotlion/AxolotlionVideo';

export const Root: React.FC = () => (
  <>
    <Composition id="SIAgentsToken" component={Video} durationInFrames={TOTAL} fps={FPS} width={1920} height={1080} />
    <Composition id="Axolotlion" component={AxolotlionVideo} durationInFrames={AX_TOTAL} fps={AX_FPS} width={1920} height={1080} />
    {AGENTS.map((a) => (
      <Composition key={a.id} id={`Agent-${a.id}`} component={AgentVideo} durationInFrames={AGENT_FRAMES} fps={FPS} width={1920} height={1080} defaultProps={{agent: a}} />
    ))}
  </>
);
