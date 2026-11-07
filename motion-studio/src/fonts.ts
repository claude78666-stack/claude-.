import { continueRender, delayRender, staticFile } from 'remotion';

// Bundle Inter (SIL Open Font License) so renders look the same on any machine.
export const FONT_FAMILY = 'InterStudio';

if (typeof document !== 'undefined') {
  const handle = delayRender('Loading Inter font');
  const face = new FontFace(FONT_FAMILY, `url(${staticFile('Inter-Black.otf')})`);
  face
    .load()
    .then((loaded) => {
      document.fonts.add(loaded);
      continueRender(handle);
    })
    .catch((err) => {
      console.error('Font failed to load, falling back to system font', err);
      continueRender(handle);
    });
}
