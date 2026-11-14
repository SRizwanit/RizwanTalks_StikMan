import React from "react";
import { AbsoluteFill, Audio, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Character } from "./Character";
import { Caption } from "./Caption";
import { shotAt, timeline } from "./timeline";

export const Video: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const shot = shotAt(frame);
  const local = frame - shot.from;
  const progress = local / Math.max(1, shot.to - shot.from);

  // hard cuts between shots, slow push-in inside a shot (casual, not flashy)
  const { cx, cy, z: baseZ } = shot.camera;
  const z = baseZ * (1 + shot.push * progress);

  // character pops in once at the start
  const pop = Math.max(
    0.01,
    spring({ frame, fps, config: { damping: 12, stiffness: 150 }, durationInFrames: 14 })
  );

  const speaking = frame < shot.speakTo && shot.mood !== "idle";

  return (
    <AbsoluteFill style={{ backgroundColor: "#ffffff" }}>
      {timeline.audio && <Audio src={staticFile(timeline.audio)} />}

      <svg width={width} height={height} viewBox="0 0 720 720">
        <g transform={`translate(360 360) scale(${z}) translate(${-cx} ${-cy})`}>
          <Character frame={frame} fps={fps} mood={shot.mood} speaking={speaking} pop={pop} />
        </g>
      </svg>

      <Caption text={shot.text} localFrame={local} big={shot.big} />
    </AbsoluteFill>
  );
};
