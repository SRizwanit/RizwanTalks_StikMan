#!/usr/bin/env python3
"""data/script.json  ->  data/timeline.json  (+ public/voice.mp3 with --voice)

Without --voice : timing comes from each line's "seconds".
With    --voice : edge-tts speaks voice.say; word boundaries decide when each
                  caption chunk starts, so captions match the voice.
                  Each line's "n" = how many spoken words that caption covers.
"""
import argparse, asyncio, json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAMERAS = {  # cx, cy, zoom  (world is 720x720, character feet at y=520)
    "wide":   {"cx": 360, "cy": 345, "z": 1.0},
    "close":  {"cx": 360, "cy": 225, "z": 3.0},
    "xclose": {"cx": 360, "cy": 215, "z": 3.6},
}


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)], text=True)
    return float(out.strip())


async def synth(text, voice, rate, mp3: Path):
    import edge_tts
    try:
        com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    except TypeError:  # older edge-tts: word boundaries are the default
        com = edge_tts.Communicate(text, voice, rate=rate)
    words = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7
                words.append((s, s + ch["duration"] / 1e7))
    return words


def voice_timing(cfg, lines):
    """Return (starts[], speak_ends[], audio_end_sec) per line, in seconds."""
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is required for --voice")
    lead = cfg["lead_in"]
    cache = ROOT / "python" / ".cache"; cache.mkdir(parents=True, exist_ok=True)
    raw = cache / "raw.mp3"
    v = cfg["voice"]
    words = asyncio.run(synth(v["say"], v["name"], v.get("rate", "+0%"), raw))
    dur = probe_duration(raw)
    need = sum(l["n"] for l in lines)
    if len(words) != need:  # boundaries missing -> spread evenly
        step = dur / max(1, need)
        words = [(i * step, (i + 1) * step) for i in range(need)]
    (ROOT / "public").mkdir(exist_ok=True)
    ms = int(lead * 1000)
    subprocess.check_call(
        ["ffmpeg", "-y", "-v", "error", "-i", str(raw),
         "-af", f"adelay={ms}|{ms}", str(ROOT / "public" / "voice.mp3")])
    starts, ends, i = [], [], 0
    for l in lines:
        if l["n"] == 0:
            starts.append(0.0); ends.append(lead); continue
        a = words[i][0] + lead
        b = words[i + l["n"] - 1][1] + lead
        starts.append(a); ends.append(b); i += l["n"]
    return starts, ends, dur + lead


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", action="store_true")
    args = ap.parse_args()

    cfg = json.loads((ROOT / "data" / "script.json").read_text(encoding="utf-8"))
    fps, lines = cfg["fps"], cfg["lines"]
    audio_end = 0.0

    if args.voice:
        starts, speak_ends, audio_end = voice_timing(cfg, lines)
        # a chunk lasts until the next one starts (hard cuts, like the reference)
        starts[0] = 0.0
        for i in range(1, len(lines)):
            starts[i] = max(starts[i], starts[i - 1] + 0.3)
        ends = starts[1:] + [max(cfg["min_seconds"], audio_end + cfg["tail"])]
    else:
        t, starts, ends, speak_ends = 0.0, [], [], []
        for l in lines:
            starts.append(t); t += l["seconds"]; ends.append(t)
            speak_ends.append(t)
        ends[-1] = max(ends[-1], cfg["min_seconds"])
        speak_ends[-1] = starts[-1] + 2.0

    total = round(ends[-1] * fps)
    shots = []
    for l, a, b, sp in zip(lines, starts, ends, speak_ends):
        shots.append({
            "from": round(a * fps),
            "to": round(b * fps),
            "speakTo": min(round(sp * fps), round(b * fps)),
            "text": l["text"],
            "camera": CAMERAS[l["shot"]],
            "mood": l["mood"],
            "push": l.get("push", 0.0),
            "big": l.get("big", False),
        })
    shots[-1]["to"] = total

    out = {
        "fps": fps, "width": cfg["width"], "height": cfg["height"],
        "durationInFrames": total,
        "audio": "voice.mp3" if args.voice else None,
        "shots": shots,
    }
    (ROOT / "data" / "timeline.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"timeline.json: {total} frames ({total / fps:.2f}s), voice={args.voice}")


if __name__ == "__main__":
    main()
