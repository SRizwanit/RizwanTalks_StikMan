import React from "react";
import type { Mood } from "./timeline";

const INK = "#141414";
const GRAY = "#c8c8c8";
const SW = 2.6; // constant on-screen stroke width (non-scaling-stroke)

type Props = {
  frame: number;
  fps: number;
  mood: Mood;
  speaking: boolean;
  pop: number; // 0..1+ (spring) scale from the feet
};

const Stroke: React.FC<{ d: string }> = ({ d }) => (
  <path
    d={d}
    fill="none"
    stroke={INK}
    strokeWidth={SW}
    strokeLinecap="round"
    strokeLinejoin="round"
    vectorEffect="non-scaling-stroke"
  />
);

// Casual motion: tiny breathing, slight sway, small slow wave. Nothing big.
export const Character: React.FC<Props> = ({ frame, fps, mood, speaking, pop }) => {
  const t = frame / fps;
  const breathe = Math.sin(t * Math.PI * 2 * 0.4) * 1.2; // px
  const look = Math.sin(t * 1.3) * 2;
  const blink = frame % 96 >= 44 && frame % 96 <= 46;

  const hx = 360;
  const hy = 225 + breathe;

  // arms (shoulders at y=312)
  const sway = Math.sin(t * Math.PI * 2 * 0.3) * 2;
  const leftHand = { x: 310 + sway, y: 405 };
  let rightPath: string;
  if (mood === "wave") {
    // small casual wave: forearm swings about +-10 degrees only
    const a = Math.sin(t * Math.PI * 2 * 1.1) * 0.18;
    const elbow = { x: 436, y: 330 };
    const hand = { x: elbow.x + 40 * Math.sin(a), y: elbow.y - 40 * Math.cos(a) };
    rightPath = `M398 312 L${elbow.x} ${elbow.y} L${hand.x} ${hand.y}`;
  } else {
    rightPath = `M398 312 Q414 362 ${410 - sway} 405`;
  }

  // mouth
  const amp = speaking ? 0.45 + 0.55 * Math.abs(Math.sin(frame * 0.7)) : 0;
  const mx = hx + look;
  const my = hy + 30;
  const mw = 12;
  const mh = 4 + 11 * amp;

  const happyEyes = mood === "happy";
  const brow = mood === "idle" ? 0 : 2;

  return (
    <g transform={`translate(360 520) scale(${pop}) translate(-360 -520)`}>
      <defs>
        <clipPath id="headClip">
          <circle cx={360} cy={225} r={70} />
        </clipPath>
        <clipPath id="bodyClip">
          <path d="M318 430 V322 Q318 292 348 292 H372 Q402 292 402 322 V430 Z" />
        </clipPath>
      </defs>

      {/* ground shadow + legs */}
      <ellipse cx={360} cy={520} rx={48} ry={5} fill="#dedede" />
      <Stroke d="M342 428 V516" />
      <Stroke d="M378 428 V516" />

      {/* body with gray crescent */}
      <g clipPath="url(#bodyClip)">
        <rect x={300} y={280} width={120} height={160} fill={GRAY} />
        <g transform="translate(14 -8)">
          <path
            d="M318 430 V322 Q318 292 348 292 H372 Q402 292 402 322 V430 Z"
            fill="#fff"
          />
        </g>
      </g>
      <path
        d="M318 430 V322 Q318 292 348 292 H372 Q402 292 402 322 V430 Z"
        fill="none"
        stroke={INK}
        strokeWidth={SW}
        vectorEffect="non-scaling-stroke"
      />

      {/* arms */}
      <Stroke d={`M322 312 Q306 362 ${leftHand.x} ${leftHand.y}`} />
      <Stroke d={rightPath} />

      {/* head */}
      <g transform={`translate(0 ${breathe})`}>
        <g clipPath="url(#headClip)">
          <circle cx={360} cy={225} r={70} fill={GRAY} />
          <circle cx={374} cy={216} r={70} fill="#fff" />
        </g>
        <circle
          cx={360}
          cy={225}
          r={70}
          fill="none"
          stroke={INK}
          strokeWidth={SW}
          vectorEffect="non-scaling-stroke"
        />
      </g>

      {/* face (uses hy so it rides with the head) */}
      {[-1, 1].map((s) => {
        const ex = hx + s * 24 + look;
        if (happyEyes) {
          return <Stroke key={s} d={`M${ex - 8} ${hy - 3} Q${ex} ${hy - 12} ${ex + 8} ${hy - 3}`} />;
        }
        if (blink) {
          return <Stroke key={s} d={`M${ex - 6} ${hy - 2} H${ex + 6}`} />;
        }
        return (
          <g key={s}>
            <Stroke d={`M${ex} ${hy - 12} V${hy + 2}`} />
            <Stroke d={`M${ex - 9} ${hy - 22 - brow} H${ex + 9}`} />
          </g>
        );
      })}

      {amp > 0.05 ? (
        <g>
          <path
            d={`M${mx - mw} ${my} L${mx + mw} ${my} A${mw} ${mh} 0 0 1 ${mx - mw} ${my} Z`}
            fill={INK}
          />
          <rect x={mx - mw * 0.6} y={my} width={mw * 1.2} height={mh * 0.22} fill="#fff" />
        </g>
      ) : (
        <Stroke d={`M${mx - 9} ${my + 2} H${mx + 9}`} />
      )}
    </g>
  );
};
