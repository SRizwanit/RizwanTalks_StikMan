import React from "react";
import { interpolate, Easing } from "remotion";
import { loadFont as loadPoppins } from "@remotion/google-fonts/Poppins";
import { loadFont as loadBengali } from "@remotion/google-fonts/NotoSansBengali";

const poppins = loadPoppins("italic", { weights: ["500"], subsets: ["latin"] });
const bengali = loadBengali("normal", { weights: ["500"], subsets: ["bengali"] });

type Props = { text: string; localFrame: number; big: boolean };

export const Caption: React.FC<Props> = ({ text, localFrame, big }) => {
  if (!text) return null;

  const pop = interpolate(localFrame, [0, 5], [0.65, 1], {
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(1.7)),
  });
  const underline = interpolate(localFrame, [10, 24], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top: 24,
        left: 0,
        right: 0,
        textAlign: "center",
        transform: `scale(${pop})`,
        transformOrigin: "50% 0",
      }}
    >
      <div
        style={{
          display: "inline-block",
          fontFamily: `${poppins.fontFamily}, ${bengali.fontFamily}, sans-serif`,
          fontStyle: "italic",
          fontWeight: 500,
          fontSize: big ? 54 : 36,
          color: "#3c3c3c",
          letterSpacing: 0.5,
          lineHeight: 1.2,
        }}
      >
        {text}
        {big && (
          <svg
            width="100%"
            height={10}
            viewBox="0 0 400 10"
            preserveAspectRatio="none"
            style={{ display: "block", marginTop: 4 }}
          >
            <path
              d="M0 5 Q25 0 50 5 T100 5 T150 5 T200 5 T250 5 T300 5 T350 5 T400 5"
              fill="none"
              stroke="#141414"
              strokeWidth={2.4}
              strokeLinecap="round"
              vectorEffect="non-scaling-stroke"
              pathLength={1}
              strokeDasharray={1}
              strokeDashoffset={underline}
            />
          </svg>
        )}
      </div>
    </div>
  );
};
