#!/usr/bin/env python3
"""Check the skill is ready: ffmpeg and the Scrape Creators key (the balance call is free)."""
import json
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ok = True


def line(name, passed, detail=""):
    global ok
    ok &= passed
    print(f"{'ok  ' if passed else 'FAIL'} {name}{': ' + detail if detail else ''}")


try:
    import _ffmpeg
    _ffmpeg.ensure()
    line("ffmpeg", bool(shutil.which("ffmpeg") and shutil.which("ffprobe")))
except Exception as e:
    line("ffmpeg", False, f"{e} (re-run the pip install in INSTALL.md step 2)")

try:
    from pull_videos import api_key
    req = urllib.request.Request("https://api.scrapecreators.com/v1/credit-balance",
                                 headers={"x-api-key": api_key()})
    with urllib.request.urlopen(req, timeout=30) as r:
        credits = json.load(r).get("creditCount")
    line("scrape creators key", True, f"{credits} credits left")
except SystemExit as e:
    line("scrape creators key", False, str(e))
except urllib.error.HTTPError as e:
    line("scrape creators key", False, f"Scrape Creators said {e.code}; the key is wrong or was revoked")
except Exception as e:
    line("scrape creators key", False, str(e))

sys.exit(0 if ok else 1)
