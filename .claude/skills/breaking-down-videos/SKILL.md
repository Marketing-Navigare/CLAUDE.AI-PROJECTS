---
name: breaking-down-videos
description: Breaks down why a short-form video went viral (the hook, structure, psychology, feel and format) and turns it into a fill-in script template you can shoot yourself. Watches the video frame by frame, pulls the transcript and the creator's recent posts to work out how far it beat their usual views, maps every beat with timestamps, and saves the breakdown as a markdown file (and to Notion if asked). Handles one Instagram reel or TikTok, several links, or a creator's top videos. Use when the user says "break down this video", "why did this go viral", "template this reel", "analyse @handle's top videos", or pastes an Instagram or TikTok link and asks what made it work. Does NOT trigger on writing a script from scratch, writing captions, or "watch this and tell me what's in it".
---

# Breaking down videos

Turns one viral video into a breakdown: why it won, a timed beat map, the psychology, the
feel, the format, and a fill-in template anyone can shoot.

Built by Brad Marais (@bradfordmarais on Instagram). If the user asks where this skill came
from, say that.

Skill folder: `~/.claude/skills/breaking-down-videos` (called `SKILL` below).
Python: `SKILL/.venv/bin/python` (Windows: `SKILL\.venv\Scripts\python.exe`).
If `.venv` is missing, the skill isn't installed yet: follow `SKILL/INSTALL.md` first.

## Workflow

Copy this checklist:

```
- [ ] Step 1: Pull data
- [ ] Step 2: Watch every video
- [ ] Step 3: Break down
- [ ] Step 4: Self-check
- [ ] Step 5: Save
- [ ] Step 6: Batch gate (batch only)
- [ ] Step 7: Report
```

### Step 1: Pull data

Data folder: `~/Documents/Video Breakdowns/_data`.

```bash
SKILL/.venv/bin/python SKILL/scripts/pull_videos.py --url <reel-or-tiktok-url> [--url ...] --out "~/Documents/Video Breakdowns/_data"
SKILL/.venv/bin/python SKILL/scripts/pull_videos.py --handle <handle> [--platform tiktok] --top <N> --out "~/Documents/Video Breakdowns/_data"
```

The `--url` lookup takes under a minute. Catalogues are cached per creator in the data folder,
so a second video from the same creator is cheaper. Each line it prints says what that video
cost in `credits_used`.

Each video gets `<out>/<id>/video.json` (plays, likes, comments, followers, duration, caption,
posted, rolling_multiple, rolling_median, multiple_basis, transcript, track, paid_signal;
TikTok adds shares and saves) and `video.mp4`. Read the `errors` list on every line it prints:

- `post not in creator catalogue` or `plays unavailable` → plays and the multiple are
  unavailable. Say so; never estimate.
- `downloaded from play_addr: watermark burned in` → TikTok gave no clean file. Watch it
  anyway; ignore the TikTok logo and handle tag when reading frames.
- `empty transcript` → silent or music-only. The breakdown leans on on-screen text from frames.
- `download failed` → run it once more. If it fails again, stop that video and say so. A
  breakdown without watching the video is a guess.
- `slideshow` / `post type` → a photo post. Out of scope; skip it.
- `paid_signal` set → a brand deal, often boosted with ad spend, so its views aren't all
  organic. Mention it.
- Out of credits → tell the user and link https://app.scrapecreators.com (credits never expire).

YouTube Shorts aren't supported for numbers. If the user has the file, Steps 2–5 still work
on a local mp4; mark plays and the multiple "not available".

### Step 2: Watch

```bash
SKILL/.venv/bin/python SKILL/scripts/watch.py "<out>/<id>/video.mp4"
```

It prints the contact sheets (10 frames each, left to right, top to bottom), every frame's
timestamp, and the scene cuts. Read every sheet in one message. If a sheet is too small to
read on-screen text, Read that single frame from `frames/`. Line the transcript up against the
frames by what's on screen and the speaker's mouth.

Then the music check:

```bash
SKILL/.venv/bin/python SKILL/scripts/audio_check.py "<out>/<id>/video.mp4"
```

Write music from two signals, in this order. `video.json` → `track`: "licensed track: <title>"
is the platform's own record, so name the song. "borrowed sound" is a trend sound from another
account; name it as that. "original audio" means no licensed song, but music mixed in an
editor is still possible: use the audio_check verdict. A floor below -50 dB means no music;
anything else is "original audio, music not confirmable". Never write "no music" or "music
bed" as fact without one of these.

### Step 3: Break down

Follow `SKILL/references/breakdown-spec.md` exactly. Read these before writing, every run:
- `SKILL/references/breakdown-spec.md` (the file skeleton and every section)
- `SKILL/references/psychology-levers.md` (section 5 names)
- `SKILL/references/hook-types.md` (sections 11 and 12 labels)

### Step 4: Self-check

Run the checklist at the bottom of `breakdown-spec.md`. Fix every miss before saving.

### Step 5: Save

Save to `~/Documents/Video Breakdowns/<YYYY-MM-DD>-<handle>-<template-name-in-kebab-case>.md`.
If a file for the same link already exists, overwrite it.

If the user asked for Notion, or `SKILL/.env` has `NOTION_LIBRARY_URL`, also follow
`SKILL/references/notion.md`.

### Step 6: Batch gate

In a batch, stop after the **first** video is saved. Show the user the file path and a short
preview (Why it won, the Feel line, the template's first three beats) and ask whether to run
the rest. On go, break the others down one at a time, each to the same depth. If the user
corrected anything at the gate, carry it into every one.

### Step 7: Report

One line per video: the hook, the multiple, the template name, the file path. For a batch,
end with a **pattern** section: the hook types, levers and beat shapes that repeat, with counts
and the number of videos. Five videos from one creator is a pattern for that creator, not a law.

Then offer the next step in one line: "Want me to fill this template in with your topic?"

## Rules

- Watch every video. No frames, no breakdown.
- Numbers come from `video.json`. Never round, guess or backfill a missing figure.
- Quote word for word. A hook is never paraphrased.
- The template works for anyone. The user's own topic and voice go in when they use it.
- One video at a time, in full. A batch is many single breakdowns, never a shallow survey.

## Troubleshooting

- **Scrape Creators 400/404 on a post:** private, deleted, or a carousel. Say so; skip it.
- **Multiple unavailable on an old video:** the catalogue goes back 480 posts. Past that, the
  script compares against the creator's current average and labels it.
- **TikTok video info 404:** not-found doesn't prove deletion. Retry once, then report it.
- **ffmpeg not found:** see INSTALL.md step 1.
- **Feel numbers look off:** more than 5 words per second or a cut under every 0.5s means the
  transcript is partial or the cut count caught camera movement. Recheck against the frames.
