import raw from "../data/timeline.json";

export type Mood = "idle" | "wave" | "happy" | "talk";

export type Shot = {
  from: number;
  to: number;
  speakTo: number;
  text: string;
  camera: { cx: number; cy: number; z: number };
  mood: Mood;
  push: number;
  big: boolean;
};

export type Timeline = {
  fps: number;
  width: number;
  height: number;
  durationInFrames: number;
  audio: string | null;
  shots: Shot[];
};

export const timeline = raw as unknown as Timeline;

export const shotAt = (frame: number): Shot =>
  timeline.shots.find((s) => frame >= s.from && frame < s.to) ??
  timeline.shots[timeline.shots.length - 1];
