import { Circle, Line, makeScene2D, Rect, Txt } from '@motion-canvas/2d';
import { all, createRef, waitFor } from '@motion-canvas/core';

// A tiny explainer diagram: idea -> code -> video, drawn and connected step by step.
export default makeScene2D(function* (view) {
  view.fill('#0b1014');
  const steps = ['Idea', 'Code', 'Video'];
  const colors = ['#2f8f83', '#d9a521', '#e2603f'];
  const nodes = steps.map(() => createRef<Circle>());
  const links = [createRef<Line>(), createRef<Line>()];

  view.add(
    <>
      {links.map((ref, i) => (
        <Line ref={ref} points={[[-420 + i * 420, 0], [i * 420, 0]]} stroke="#f3ead6" lineWidth={10} end={0} />
      ))}
      {steps.map((label, i) => (
        <Circle ref={nodes[i]} x={-420 + i * 420} size={0} fill={colors[i]}>
          <Txt text={label} fill="#0b1014" fontFamily="Inter" fontWeight={900} fontSize={56} />
        </Circle>
      ))}
      <Rect y={300} width={900} height={8} radius={4} fill="#f3ead6" opacity={0.2} />
    </>,
  );

  for (let i = 0; i < steps.length; i++) {
    yield* nodes[i]().size(260, 0.6);
    if (i < links.length) yield* links[i]().end(1, 0.5);
  }
  yield* all(...nodes.map((n) => n().scale(1.12, 0.3).to(1, 0.3)));
  yield* waitFor(1);
});
