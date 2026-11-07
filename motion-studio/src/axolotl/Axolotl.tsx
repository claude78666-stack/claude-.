import React from 'react';

// Hand-drawn SVG axolotl. `t` drives the gill wave and tail sway (seconds),
// `leg` scales the front-right leg (0 = missing, 1 = fully regrown).
export const Axolotl: React.FC<{ t: number; leg?: number; size?: number; gillWave?: number }> = ({
  t,
  leg = 1,
  size = 600,
  gillWave = 1,
}) => {
  const gill = (i: number) => Math.sin(t * 4 + i * 0.9) * 8 * gillWave;
  const tail = Math.sin(t * 2.2) * 10;
  const blink = (t * 1000) % 3200 < 140 ? 0.1 : 1;
  const pink = '#f6a6c1';
  const dark = '#c2577f';
  return (
    <svg width={size} height={size * 0.75} viewBox="0 0 400 300">
      {/* tail */}
      <path d={`M120 170 Q40 ${150 + tail} 10 ${170 + tail * 1.5} Q60 ${200 + tail} 120 195 Z`} fill={pink} stroke={dark} strokeWidth={4} />
      {/* back legs */}
      <ellipse cx={150} cy={210} rx={14} ry={28} fill={pink} stroke={dark} strokeWidth={4} transform="rotate(25 150 210)" />
      {/* body */}
      <ellipse cx={210} cy={180} rx={110} ry={48} fill={pink} stroke={dark} strokeWidth={4} />
      {/* front legs; the right one regrows */}
      <ellipse cx={265} cy={218} rx={13} ry={26} fill={pink} stroke={dark} strokeWidth={4} transform="rotate(-15 265 218)" />
      <g transform={`translate(240 205) scale(${leg}) translate(-240 -205)`}>
        <ellipse cx={240} cy={222} rx={13} ry={26} fill={pink} stroke={dark} strokeWidth={4} transform="rotate(-15 240 222)" />
      </g>
      {/* head */}
      <ellipse cx={305} cy={150} rx={72} ry={58} fill={pink} stroke={dark} strokeWidth={4} />
      {/* gills: three frilly stalks on each side */}
      {[0, 1, 2].map((i) => (
        <g key={i}>
          <path
            d={`M265 ${118 + i * 18} q-45 ${-30 + i * 14 + gill(i)} -60 ${-18 + i * 18}`}
            stroke="#e5608f"
            strokeWidth={11}
            strokeLinecap="round"
            fill="none"
          />
          <path
            d={`M345 ${110 + i * 16} q40 ${-34 + i * 14 - gill(i)} 58 ${-24 + i * 16}`}
            stroke="#e5608f"
            strokeWidth={11}
            strokeLinecap="round"
            fill="none"
          />
        </g>
      ))}
      {/* face */}
      <ellipse cx={285} cy={140} rx={7} ry={7 * blink} fill="#2a1a22" />
      <ellipse cx={330} cy={140} rx={7} ry={7 * blink} fill="#2a1a22" />
      <path d="M288 170 Q307 184 326 170" stroke="#2a1a22" strokeWidth={4} fill="none" strokeLinecap="round" />
      <circle cx={272} cy={160} r={8} fill="#ff7aa6" opacity={0.5} />
      <circle cx={342} cy={160} r={8} fill="#ff7aa6" opacity={0.5} />
    </svg>
  );
};
