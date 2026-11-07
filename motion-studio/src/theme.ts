import { FONT_FAMILY } from './fonts';

export const theme = {
  bg: '#0b1014',
  ink: '#f3ead6',
  accent: '#d9a521',
  teal: '#2f8f83',
  coral: '#e2603f',
  font: `${FONT_FAMILY}, Inter, sans-serif`,
} as const;

export const SCENE = 90; // 3 seconds at 30fps per scene
