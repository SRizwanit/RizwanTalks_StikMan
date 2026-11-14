import React from "react";
import { Composition } from "remotion";
import { Video } from "./Video";
import { timeline } from "./timeline";

export const Root: React.FC = () => (
  <Composition
    id="Intro"
    component={Video}
    durationInFrames={timeline.durationInFrames}
    fps={timeline.fps}
    width={timeline.width}
    height={timeline.height}
  />
);
