import React, { useEffect, useLayoutEffect, useRef, useState } from 'react';
import { AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import RiveCanvas, { type Artboard, type LinearAnimationInstance, type RiveCanvas as Rive } from '@rive-app/canvas-advanced';
import { Label } from './Label';

const SIZE = 900;

type Loaded = { rive: Rive; artboard: Artboard; animation: LinearAnimationInstance };

// Plays a Rive (.riv) file frame-accurately. The Rive engine (rive.wasm) is
// bundled in public/ so renders work offline. vehicles.riv is Rive's public
// sample file; replace it with your own export from the Rive editor.
export const RiveScene: React.FC<{ src?: string }> = ({ src = staticFile('vehicles.riv') }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [loaded, setLoaded] = useState<Loaded | null>(null);
  const [handle] = useState(() => delayRender('Loading Rive'));

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const rive = await RiveCanvas({ locateFile: () => staticFile('rive.wasm') });
      const bytes = new Uint8Array(await (await fetch(src)).arrayBuffer());
      const file = await rive.load(bytes);
      const artboard = file.defaultArtboard();
      const animation = new rive.LinearAnimationInstance(artboard.animationByIndex(0), artboard);
      if (!cancelled) setLoaded({ rive, artboard, animation });
    })().catch((err) => {
      console.error(err);
      continueRender(handle);
    });
    return () => {
      cancelled = true;
    };
  }, [src, handle]);

  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (!loaded || !canvas) return;
    const { rive, artboard, animation } = loaded;
    const renderer = rive.makeRenderer(canvas);
    // Seek to the exact time for this frame (frames may render out of order).
    animation.time = frame / fps;
    animation.apply(1);
    artboard.advance(0);
    renderer.clear();
    renderer.save();
    renderer.align(rive.Fit.contain, rive.Alignment.center, { minX: 0, minY: 0, maxX: SIZE, maxY: SIZE }, artboard.bounds);
    artboard.draw(renderer);
    renderer.restore();
    rive.resolveAnimationFrame();
    continueRender(handle);
  }, [loaded, frame, fps, handle]);

  return (
    <AbsoluteFill>
      <canvas ref={canvasRef} width={SIZE} height={SIZE} style={{ position: 'absolute', top: 380, left: 90 }} />
      <Label tool="Rive" what="Designer-made interactive animation" />
    </AbsoluteFill>
  );
};
