import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// three.js needs WebGL; "swangle" (software) works everywhere, including headless servers.
Config.setChromiumOpenGlRenderer('swangle');
