# Install (instructions for Claude)

You are installing the `breaking-down-videos` skill for someone who may never have used a
terminal. Do every step yourself. Only ask them for what you can't do (their Scrape Creators key, a
click in a browser). Explain each step in one plain sentence, and never show them a wall of
terminal output.

Works on Mac and Windows with Claude Code. Commands below are Mac/Linux; Windows equivalents
are noted.

## 1. Check Python 3 and git

```bash
python3 --version && git --version
```

- Python 3.10 or newer and git both print a version: carry on.
- **Mac, either missing:** run `xcode-select --install`. A macOS window pops up: tell them to
  click **Install** and wait for it to finish (about 5 minutes), then check again.
- **Windows:** use `py --version`. If Python is missing, have them install it from
  https://www.python.org/downloads/ and tick **"Add python.exe to PATH"** on the first screen.
  Git: https://git-scm.com/download/win with all defaults.

## 2. Download the skill

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/bradford-marais/video-breakdown-skill.git ~/.claude/skills/breaking-down-videos
```

If the folder already exists, update it instead: `git -C ~/.claude/skills/breaking-down-videos pull`.

Then install its Python packages into its own private environment (this touches nothing else
on their computer):

```bash
cd ~/.claude/skills/breaking-down-videos
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt
```

Windows: `py -m venv .venv` then `.venv\Scripts\pip install -q -r requirements.txt`.

## 3. Their Scrape Creators key

The skill reads views, likes, transcripts and the creator's recent posts through Scrape
Creators. A free account comes with 100 credits and no card. One breakdown uses about 4–8
credits, so that's roughly 15 breakdowns. Credits never expire, and the dashboard offers more
free ones for leaving feedback.

Walk them through it, one step at a time:

1. Open https://app.scrapecreators.com and sign up (Google sign-in works).
2. Copy the API key shown on the dashboard.
3. Paste it here in the chat.

When they paste it, write it to the skill's `.env` file. **Never repeat the key back to them
or print it in a command's output.**

```bash
printf 'SCRAPECREATORS_API_KEY=%s\n' '<the key>' > ~/.claude/skills/breaking-down-videos/.env
```

## 4. Check everything works

```bash
~/.claude/skills/breaking-down-videos/.venv/bin/python ~/.claude/skills/breaking-down-videos/scripts/check.py
```

Windows: `.venv\Scripts\python.exe scripts\check.py` from the skill folder.

The first run downloads ffmpeg (about 70 MB), so it can take a minute. Tell them that before
you run it. Every line should say `ok`. If the Scrape Creators line fails, the key was pasted
wrong: ask for it again.

## 5. Done

Tell them, in these words or close to them:

> You're set. Paste any Instagram reel or TikTok link and say "break this down". Your
> breakdowns save to the **Video Breakdowns** folder in Documents.

Then ask if they want to try it now on a video they've been wanting to copy.
