#!/usr/bin/env python3
"""Turn a local video into frames Claude can read.

Pulls frames at a rate that suits the length (2 per second under 30s, 1 per second under 90s,
slower after that), tiles them 10 to a contact sheet in time order, and counts the cuts with
ffmpeg's scene detection.

Usage:
  python watch.py <video.mp4> [--fps N]
Writes <video folder>/frames/, <video folder>/sheets/ and prints JSON with the sheet paths,
each frame's timestamp, and the scene-cut timestamps.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import _ffmpeg  # noqa: E402

_ffmpeg.ensure()


def duration(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                          "csv=p=0", str(video)], capture_output=True, text=True, check=True).stdout
    return float(out.strip() or 0)


def auto_fps(seconds):
    if seconds <= 30:
        return 2.0
    if seconds <= 90:
        return 1.0
    return max(0.25, round(90 / seconds, 2))


def scene_cuts(video, threshold):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-vf",
                        f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [round(float(t), 2) for t in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--fps", type=float)
    a = ap.parse_args()
    video = Path(a.video).expanduser().resolve()
    base = video.parent
    frames, sheets = base / "frames", base / "sheets"
    for d in (frames, sheets):
        d.mkdir(exist_ok=True)
        for f in d.glob("*.jpg"):
            f.unlink()
    secs = duration(video)
    fps = a.fps or auto_fps(secs)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-vf",
                    f"fps={fps},scale=1024:-2", "-q:v", "3", str(frames / "frame_%04d.jpg")], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", "1", "-i",
                    str(frames / "frame_%04d.jpg"), "-vf", "scale=480:-1,tile=5x2:padding=4",
                    str(sheets / "sheet_%02d.jpg")], check=True)
    frame_files = sorted(frames.glob("frame_*.jpg"))
    stamps = [{"frame": f.name, "t": round(i / fps, 2)} for i, f in enumerate(frame_files)]
    cuts = scene_cuts(video, 0.3)
    if len(cuts) < 2:  # locked-off talking head: 0.3 misses punch-in jump cuts
        cuts = scene_cuts(video, 0.04)
    print(json.dumps({
        "duration_s": round(secs, 2), "fps": fps,
        "sheets": [str(s) for s in sorted(sheets.glob("sheet_*.jpg"))],
        "sheet_layout": "10 frames per sheet, left to right, top to bottom",
        "frames": stamps, "scene_cuts": cuts,
    }, indent=1))


if __name__ == "__main__":
    main()
