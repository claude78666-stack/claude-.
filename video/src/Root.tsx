import React from 'react';
import {Composition} from 'remotion';
import {FPS, TOTAL, Video} from './Video';
import {AgentVideo, AGENT_FRAMES} from './agents/AgentVideo';
import {AGENTS} from './agents/data';
import {AxolotlionVideo, AX_FPS, AX_TOTAL} from './axolotlion/AxolotlionVideo';
import {SIFilm, SI_FPS, SI_TOTAL} from './axolotlion/SIFilm';
import {FilmVideo, FILM_FPS, FILM_TOTAL} from './axolotlion/FilmVideo';
import {ProVideo, PRO_FPS, PRO_TOTAL} from './axolotlion/ProVideo';
import {Banner, FaceLogo} from './axolotlion/Brand';
import {useCurrentFrame} from 'remotion';

const LogoStill: React.FC = () => <FaceLogo size={1000} t={0.25} />;
const BannerStill: React.FC = () => <Banner t={0.12} />;
const LogoLoop: React.FC = () => <FaceLogo size={512} t={useCurrentFrame() / 20} />;
const BannerLoop: React.FC = () => <Banner t={useCurrentFrame() / 20} />;

export const Root: React.FC = () => (
  <>
    <Composition id="SIAgentsToken" component={Video} durationInFrames={TOTAL} fps={FPS} width={1920} height={1080} />
    <Composition id="AxLogo" component={LogoStill} durationInFrames={1} fps={20} width={1000} height={1000} />
    <Composition id="AxBanner" component={BannerStill} durationInFrames={1} fps={20} width={1500} height={500} />
    <Composition id="AxLogoLoop" component={LogoLoop} durationInFrames={40} fps={20} width={512} height={512} />
    <Composition id="AxBannerLoop" component={BannerLoop} durationInFrames={40} fps={20} width={1500} height={500} />
    <Composition id="Axolotlion" component={AxolotlionVideo} durationInFrames={AX_TOTAL} fps={AX_FPS} width={1920} height={1080} />
    <Composition id="AxolotlionPro" component={ProVideo} durationInFrames={PRO_TOTAL} fps={PRO_FPS} width={1920} height={1080} />
    <Composition id="AxolotlionFilm" component={FilmVideo} durationInFrames={FILM_TOTAL} fps={FILM_FPS} width={1920} height={1080} />
    <Composition id="AxolotlionSI" component={SIFilm} durationInFrames={SI_TOTAL} fps={SI_FPS} width={1920} height={1080} />
    {AGENTS.map((a) => (
      <Composition key={a.id} id={`Agent-${a.id}`} component={AgentVideo} durationInFrames={AGENT_FRAMES} fps={FPS} width={1920} height={1080} defaultProps={{agent: a}} />
    ))}
  </>
);
