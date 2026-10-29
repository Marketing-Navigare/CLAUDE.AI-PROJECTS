#!/usr/bin/env python3
"""Is there a music bed under the voice? A loudness-floor check, stdlib only.

Speech, even tightly jump-cut, keeps dropping to near-silence between words and
on stop consonants. A music bed (or loud room tone) fills those dips, so the
quietest moments of the track stay loud. This measures the quiet end of the
track in 50 ms windows and reports a verdict.

It is the weaker of two signals. pull_videos.py records the platform's own answer
(`track`: a licensed song attached, or original audio), which is definitive
for a licensed track. Original audio can still hide music mixed in an editor; this
check only rules that out when the floor drops to real silence.

Usage:
  python3 audio_check.py <video.mp4>
Prints one JSON line: floor_db (5th percentile), silent_share, verdict.
"""
import array
import json
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _ffmpeg  # noqa: E402

_ffmpeg.ensure()

RATE = 16000
WINDOW = 800  # 50 ms at 16 kHz: short enough to land inside the gap between two words
SILENT_DB = -45.0  # below this a 50 ms window is effectively silent on a phone mic
# Calibration on 30 talking-head reels: floors ran -45 to -28 dB on 29 reels Instagram
# lists as "original audio" and -28.9 dB on the one with a licensed track. A
# floor above -50 dB therefore can't separate a mixed-in bed from room tone or noise
# reduction, so only a floor below this counts as evidence of no bed.
NO_BED_FLOOR = -50.0


def levels(path):
    raw = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(RATE), "-f", "s16le", "-"],
        capture_output=True, check=True).stdout
    samples = array.array("h")
    samples.frombytes(raw[: len(raw) // 2 * 2])
    out = []
    for i in range(0, len(samples) - WINDOW, WINDOW):
        chunk = samples[i:i + WINDOW]
        rms = math.sqrt(sum(s * s for s in chunk) / WINDOW) / 32768
        out.append(20 * math.log10(rms + 1e-9))
    return out


def verdict(db):
    if not db:
        return {"floor_db": None, "silent_share": None, "verdict": "no audio track"}
    s = sorted(db)
    floor = s[int(len(s) * 0.05)]
    silent = sum(1 for d in db if d < SILENT_DB) / len(db)
    if floor < NO_BED_FLOOR:
        v = "no music bed: the voice drops to silence between words"
    else:
        v = ("not confirmable: the gaps never reach silence, which fits a mixed-in bed, "
             "room tone or noise reduction equally")
    return {"floor_db": round(floor, 1), "silent_share": round(silent, 3), "verdict": v}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: audio_check.py <video.mp4>")
    try:
        print(json.dumps(verdict(levels(sys.argv[1]))))
    except subprocess.CalledProcessError as e:
        print(json.dumps({"floor_db": None, "silent_share": None,
                          "verdict": f"ffmpeg failed: {e.stderr.decode()[:200]}"}))
