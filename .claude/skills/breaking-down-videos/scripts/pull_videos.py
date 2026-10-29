#!/usr/bin/env python3
"""Pull everything a breakdown needs for one or more Instagram reels or TikTok videos.

Per video: plays, likes, comments, duration, caption, posted date, the creator's
follower count, an outlier multiple against a ROLLING median, the spoken
transcript, and the mp4 itself (so watch.py can read frames from a local file).

Usage:
  python3 pull_videos.py --url https://www.instagram.com/reel/XXXX/ [--url ...] --out DIR
  python3 pull_videos.py --url https://www.tiktok.com/@handle/video/123... --out DIR
  python3 pull_videos.py --handle somecreator --top 5 --out DIR
  python3 pull_videos.py --handle somecreator --platform tiktok --top 5 --out DIR

--url auto-detects the platform (instagram.com vs tiktok.com, vm./vt.tiktok.com short links
resolved by following the redirect). URLs from both platforms can be mixed in one batch.

Writes DIR/<id>/video.json and DIR/<id>/video.mp4, plus DIR/summary.json. <id> is the
Instagram shortcode or the TikTok video id; the json key stays "shortcode" for both.
Key: SCRAPECREATORS_API_KEY from the environment, else the .env file in the skill folder.

Cost (Scrape Creators credits; each video.json records its own `credits_used`):
  Instagram: 1 per profile, 1 per 12 catalogue posts, 1 per transcript, 1 per --url lookup.
  TikTok --url: 1 video info (/v2/tiktok/video, native captions included free)
    + 1 per 10 catalogue posts, paging only from newest back to ROLLING_WINDOW posts past the
      target (so a video from last week costs ~2 pages; one ~140 posts back costs ~15)
    + 0 profile (follower count rides on the video's author object; 1 if it's missing)
    + 1 AI transcript fallback only when native captions are empty (0 if no speech found).
    Typical: 3-6 credits for a recent video, ~17 for one five months back on a daily poster.
  TikTok --handle: up to MAX_PAGES catalogue pages (cap 40 = 400 posts) once per creator,
    then 1 video info per top video (+1 fallback transcript where captions are missing).
  Catalogue pages are cached in DIR (_catalogue_tiktok_<handle>.json) and resumed, so a second
  video from the same creator only pays for pages it hasn't seen.
"""
import argparse
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://api.scrapecreators.com"
ENV_FALLBACK = Path(__file__).resolve().parent.parent / ".env"
# Six posts either side. A creator's audience grows, so a median over the whole
# catalogue punishes old posts and flatters new ones.
ROLLING_WINDOW = 6
# Scrape Creators paginates 12 posts per page. 40 pages = 480 posts.
MAX_PAGES = 40
TIMEOUT = 90  # transcript calls regularly take 30-60s
RETRIES = 2
# TikTok CDN refuses a bare urllib request.
TT_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36", "Referer": "https://www.tiktok.com/"}
CREDITS = [0]  # running total of credits_charged across every call this run


def api_key():
    key = os.environ.get("SCRAPECREATORS_API_KEY")
    if key:
        return key
    if ENV_FALLBACK.exists():
        for line in ENV_FALLBACK.read_text().splitlines():
            if line.startswith("SCRAPECREATORS_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"')
    sys.exit("No SCRAPECREATORS_API_KEY. Add it to the .env file in the skill folder (see INSTALL.md).")


def get(path, params, key):
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    last = None
    for attempt in range(RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"x-api-key": key})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                d = json.load(r)
            charged = d.get("credits_charged") if isinstance(d, dict) else None
            CREDITS[0] += charged if isinstance(charged, int) else 1
            return d
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last = e
            if isinstance(e, urllib.error.HTTPError) and e.code in (401, 402, 403):
                body = e.read().decode(errors="replace")[:200]
                if e.code == 402 or "credit" in body.lower():
                    sys.exit("Scrape Creators says you're out of credits. Top up at "
                             "https://app.scrapecreators.com (credits never expire).")
                sys.exit(f"Scrape Creators refused the key ({e.code}). Check SCRAPECREATORS_API_KEY.")
            if isinstance(e, urllib.error.HTTPError) and e.code in (400, 404):
                break  # private/deleted post: retrying won't help
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{path} failed: {last}")


def shortcode(url):
    m = re.search(r"/(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)", url)
    if not m:
        raise ValueError(f"Not an Instagram post URL: {url}")
    return m.group(1)


def caption_text(p):
    c = p.get("caption")
    if isinstance(c, dict):
        return c.get("text") or ""
    return c or ""


def catalogue(handle, key, cache_dir, target=None):
    """The creator's posts, newest first. With target (a shortcode), stop paging once the target
    and ROLLING_WINDOW older posts are in hand, so one video costs a few pages, not the whole
    catalogue. Without it (--handle ranking), page to MAX_PAGES. Cached and resumable."""
    cache = cache_dir / f"_catalogue_{handle}.json"
    c = json.loads(cache.read_text()) if cache.exists() else {"posts": [], "next": None, "complete": False, "pages": 0}

    def enough():
        codes = [p.get("code") for p in c["posts"]]
        return target in codes and len(codes) - codes.index(target) - 1 >= ROLLING_WINDOW

    # One video stops at 10 pages (120 posts); older than that falls back to the current median.
    limit = 10 if target else MAX_PAGES
    while not c["complete"] and c["pages"] < limit and not (target and enough()):
        params = {"handle": handle}
        if c["next"]:
            params["next_max_id"] = c["next"]
        d = get("/v2/instagram/user/posts", params, key)
        c["pages"] += 1
        items = d.get("items") or []
        c["posts"] += items
        c["next"] = d.get("next_max_id")
        if not d.get("more_available") or not c["next"] or not items:
            c["complete"] = True
        cache.write_text(json.dumps(c))
    return own_posts(c["posts"], handle)


def own_posts(posts, handle):
    """Drop collabs another account owns. They show on this grid but their reach comes from the
    owner's audience."""
    def owner(p):
        return (p.get("user") or {}).get("username") or (p.get("owner") or {}).get("username")
    return [p for p in posts if owner(p) in (None, handle)]


PAID_RE = re.compile(r"#(ad|sponsored\w*|\w*partner)\b|paid partnership", re.I)


def paid_signal(p):
    """Brand deals are often boosted with ad spend, so their plays aren't organic reach."""
    if p.get("is_paid_partnership") or p.get("sponsor_tags"):
        return "paid partnership flag"
    m = PAID_RE.search(caption_text(p))
    return f"caption tag {m.group(0)}" if m else None


def followers(handle, key):
    try:
        d = get("/v1/instagram/profile", {"handle": handle}, key)
        return d["data"]["user"]["edge_followed_by"]["count"]
    except Exception:
        return None


def multiples(posts):
    """Return {shortcode: (rolling_multiple, rolling_median)} for posts with plays."""
    reels = sorted((p for p in posts if p.get("play_count")), key=lambda p: p["taken_at"])
    out = {}
    for i, p in enumerate(reels):
        window = reels[max(0, i - ROLLING_WINDOW):i] + reels[i + 1:i + 1 + ROLLING_WINDOW]
        if not window:
            continue
        med = statistics.median(x["play_count"] for x in window)
        out[p["code"]] = (round(p["play_count"] / med, 1), int(med))
    return out


def transcript(code, key):
    try:
        d = get("/v2/instagram/media/transcript",
                {"url": f"https://www.instagram.com/reel/{code}/"}, key)
    except RuntimeError as e:
        return None, str(e)
    t = d.get("transcripts") or d.get("transcript")
    if isinstance(t, list):
        t = " ".join((x.get("text") or "") if isinstance(x, dict) else str(x) for x in t)
    t = " ".join(str(t or "").split())
    return (t or None), (None if t else "empty transcript (likely no speech)")


def download(url, dest):
    if not url:
        return "no video url"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as r, open(dest, "wb") as f:
            f.write(r.read())
        return None
    except Exception as e:
        return f"download failed: {e}"


def instagram_track(p):
    """Instagram's own audio record: a licensed song, or the creator's original audio."""
    cm = p.get("clips_metadata") or {}
    asset = (cm.get("music_info") or {}).get("music_asset_info") or {}
    if asset.get("title"):
        return f"licensed track: {asset['title']} - {asset.get('display_artist') or 'unknown artist'}"
    if cm.get("original_sound_info"):
        return "original audio (music mixed in an editor can't be ruled out; run audio_check.py)"
    return None


def video_url(p):
    vv = p.get("video_versions") or []
    return vv[0].get("url") if vv else p.get("video_url")


def resolve_handle(code, key):
    d = get("/v2/instagram/post", {"url": f"https://www.instagram.com/reel/{code}/"}, key)
    user = d.get("user") or {}
    handle = user.get("username")
    if not handle:
        raise RuntimeError(f"Could not read the creator for {code} (private or removed?)")
    return handle, d


CURRENT_WINDOW = 12


def apply_current_median(rec, posts):
    """For a post older than the catalogue reaches: plays over the median of the creator's 12
    newest posts. For a growing account that's a stricter test than the rolling median, so a 3x
    here is at least a 3x in its own era. Labelled in multiple_basis; never presented as rolling."""
    recent = sorted((p for p in posts if p.get("play_count") and p.get("code") != rec["shortcode"]),
                    key=lambda p: p.get("taken_at") or 0, reverse=True)[:CURRENT_WINDOW]
    if len(recent) < 6:
        return False
    med = statistics.median(p["play_count"] for p in recent)
    if not med:
        return False
    rec["rolling_multiple"] = round(rec["plays"] / med, 1)
    rec["rolling_median"] = int(med)
    rec["multiple_basis"] = "current median (post older than the catalogue reaches)"
    return True


def ig_v1_post(code, key):
    try:
        m = (get("/v1/instagram/post", {"url": f"https://www.instagram.com/reel/{code}/"}, key)
             .get("data") or {}).get("xdt_shortcode_media") or {}
    except RuntimeError:
        return None
    if not m:
        return None
    cap = ((m.get("edge_media_to_caption") or {}).get("edges") or [{}])[0]
    return {"code": code, "play_count": m.get("video_play_count"),
            "like_count": (m.get("edge_media_preview_like") or {}).get("count"),
            "comment_count": (m.get("edge_media_to_comment") or m.get("edge_media_to_parent_comment") or {}).get("count"),
            "video_duration": m.get("video_duration"), "caption": {"text": (cap.get("node") or {}).get("text") or ""},
            "taken_at": m.get("taken_at_timestamp"), "video_url": m.get("video_url"),
            "is_paid_partnership": m.get("is_paid_partnership")}


def build(code, handle, posts, mult, fcount, key, out, single_post=None):
    p = next((x for x in posts if x.get("code") == code), None)
    vdir = out / code
    vdir.mkdir(parents=True, exist_ok=True)
    errors = []
    out_of_reach = p is None
    if p is None:
        # Older than the catalogue reaches, or a non-reel post. /v2/instagram/post has no play
        # count, so read the v1 GraphQL shape for plays and the video file (1 credit).
        p = ig_v1_post(code, key) or single_post or {}
        if not p.get("play_count"):
            errors.append("post not in creator catalogue: plays and multiple unavailable")
    rec = {
        "shortcode": code,
        "link": f"https://www.instagram.com/reel/{code}/",
        "creator": handle,
        "followers": fcount,
        "posted": datetime.fromtimestamp(p["taken_at"], timezone.utc).date().isoformat()
        if p.get("taken_at") else (datetime.fromtimestamp(p["created_at"], timezone.utc).date().isoformat()
        # The single-post fallback returns created_at as epoch seconds, not a string.
        if isinstance(p.get("created_at"), (int, float)) else (p.get("created_at") or "")[:10] or None),
        "plays": p.get("play_count"),
        "likes": p.get("like_count"),
        "comments": p.get("comment_count"),
        "duration_s": round(p.get("video_duration") or 0) or None,
        "caption": caption_text(p),
        "rolling_multiple": mult.get(code, (None, None))[0],
        "rolling_median": mult.get(code, (None, None))[1],
        "catalogue_size": len(posts),
        "track": instagram_track(p),
        "paid_signal": paid_signal(p),
    }
    rec["multiple_basis"] = "rolling" if rec["rolling_multiple"] is not None else None
    if out_of_reach and rec["plays"] and apply_current_median(rec, posts):
        errors[:] = [e for e in errors if "multiple unavailable" not in e]
    if rec["plays"] is None and not errors:
        # In the catalogue but Scrape Creators sent no play count. Say so, or the
        # bar check reads a blank multiple as a pass.
        errors.append("plays unavailable: multiple unavailable")
    rec["transcript"], terr = transcript(code, key)
    if terr:
        errors.append(terr)
    derr = download(video_url(p), vdir / "video.mp4")
    if derr:
        errors.append(derr)
    rec["video_path"] = str(vdir / "video.mp4") if not derr else None
    rec["errors"] = errors
    (vdir / "video.json").write_text(json.dumps(rec, indent=1))
    return rec


# --------------------------------------------------------------------------------------------
# TikTok. Scrape Creators returns TikTok's raw "aweme" objects:
#   /v2/tiktok/video?url=&get_transcript=true  -> aweme_detail + transcript (WEBVTT, free)
#   /v3/tiktok/profile/videos?handle=&user_id=&max_cursor=&trim=true -> aweme_list (10/page),
#       has_more, max_cursor. Pinned posts come first on page 1, out of date order.
#   /v1/tiktok/video/transcript?url=&use_ai_as_fallback=true -> AI transcript, <=120s, 1 credit
#   /v1/tiktok/profile?handle= -> stats.followerCount (only if the author object lacks it)
# --------------------------------------------------------------------------------------------
TT_URL_RE = re.compile(r"tiktok\.com/@([^/?#]+)/(?:video|photo)/(\d+)")
TT_SHORT_RE = re.compile(r"(?:vm|vt)\.tiktok\.com/|tiktok\.com/t/")


def platform_of(url):
    if "tiktok.com" in url:
        return "tiktok"
    if "instagram.com" in url:
        return "instagram"
    raise ValueError(f"Not an Instagram or TikTok URL: {url}")


def tt_resolve_url(url):
    """Expand vm.tiktok.com / tiktok.com/t/ short links by following the redirect (no credits)."""
    if not TT_SHORT_RE.search(url):
        return url
    try:
        req = urllib.request.Request(url, headers=TT_HEADERS, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            final = r.geturl()
        return final if TT_URL_RE.search(final) else url
    except Exception:
        return url  # let Scrape Creators try the short link itself


def tt_norm(a):
    """A TikTok aweme in the fields multiples() and own_posts() read."""
    st = a.get("statistics") or {}
    return {"code": str(a.get("aweme_id") or ""), "play_count": st.get("play_count"),
            "taken_at": a.get("create_time") or 0,
            "user": {"username": (a.get("author") or {}).get("unique_id")}, "raw": a}


def tt_out_of_order(posts):
    """Ids sitting above a newer post in feed order: the pinned posts at the top of page 1."""
    pinned, newest_after = set(), 0
    for p in reversed(posts):
        if p["taken_at"] < newest_after:
            pinned.add(p["code"])
        newest_after = max(newest_after, p["taken_at"])
    return pinned


def tt_enough(posts, before_ts):
    """True once the catalogue holds ROLLING_WINDOW in-order posts older than before_ts."""
    pinned = tt_out_of_order(posts)
    return sum(1 for p in posts if p["code"] not in pinned and p["taken_at"] < before_ts) \
        >= ROLLING_WINDOW


def tt_catalogue(handle, user_id, key, cache_dir, before_ts=None):
    """Creator's own posts, newest first. With before_ts, stop paging as soon as the target's
    older neighbours are in hand; otherwise page to MAX_PAGES. Cached and resumable."""
    cache = cache_dir / f"_catalogue_tiktok_{handle}.json"
    c = json.loads(cache.read_text()) if cache.exists() else \
        {"posts": [], "cursor": None, "complete": False, "pages": 0}
    seen = {str(p.get("aweme_id")) for p in c["posts"]}
    while not c["complete"] and c["pages"] < MAX_PAGES:
        norm = [tt_norm(a) for a in c["posts"]]
        if before_ts is not None and norm and tt_enough(norm, before_ts):
            break
        params = {"handle": handle, "trim": "true"}
        if user_id:
            params["user_id"] = user_id
        if c["cursor"]:
            params["max_cursor"] = c["cursor"]
        d = get("/v3/tiktok/profile/videos", params, key)
        c["pages"] += 1
        items = d.get("aweme_list") or []
        c["posts"] += [a for a in items if str(a.get("aweme_id")) not in seen]
        seen |= {str(a.get("aweme_id")) for a in items}
        c["cursor"] = d.get("max_cursor")
        if not d.get("has_more") or not c["cursor"]:
            c["complete"] = True
        cache.write_text(json.dumps(c))
    posts = [tt_norm(a) for a in c["posts"]]
    return own_posts(posts, handle), c


def tt_paid_signal(a):
    if a.get("is_ad"):
        return "is_ad flag"
    if a.get("is_paid_partnership"):
        return "paid partnership flag"
    if ((a.get("commerce_info") or {}).get("branded_content_type") or 0) != 0:
        return "branded content flag"
    m = PAID_RE.search(a.get("desc") or "")
    return f"caption tag {m.group(0)}" if m else None


def tt_track(a, handle):
    """TikTok's own sound record. Borrowed 'original sound' from another account is a trend sound."""
    m = a.get("music") or {}
    title, owner = m.get("title") or "", (m.get("owner_handle") or "").lower()
    if not title:
        return None
    if m.get("is_original_sound") or title.lower().startswith("original sound"):
        if owner and owner != handle.lower():
            return f"borrowed sound: {title} (from @{owner})"
        return "original audio (music mixed in an editor can't be ruled out; run audio_check.py)"
    return f"licensed track: {title} - {m.get('author') or 'unknown artist'}"


def tt_video_url(a):
    """No-watermark first; play_addr only when TikTok says it carries no watermark."""
    v = a.get("video") or {}
    for field, ok in (("download_no_watermark_addr", True),
                      ("play_addr", v.get("has_watermark") is False),
                      ("download_addr", True), ("play_addr", True)):
        urls = (v.get(field) or {}).get("url_list") or []
        if ok and urls:
            return urls[0], field
    return None, None


def vtt_text(vtt):
    lines = []
    for ln in str(vtt or "").splitlines():
        ln = ln.strip()
        if not ln or ln == "WEBVTT" or "-->" in ln or ln.isdigit() or ln.startswith("NOTE"):
            continue
        lines.append(ln)
    return " ".join(" ".join(lines).split()) or None


def tt_transcript(detail_resp, link, key):
    t = vtt_text(detail_resp.get("transcript"))
    if t:
        return t, None
    try:
        d = get("/v1/tiktok/video/transcript", {"url": link, "use_ai_as_fallback": "true"}, key)
    except RuntimeError as e:
        return None, f"empty native captions; AI transcript failed: {e}"
    t = vtt_text(d.get("transcript"))
    if not t and isinstance(d.get("transcript_with_timestamp"), list):
        t = " ".join(str(s.get("text") or "") for s in d["transcript_with_timestamp"]).strip() or None
    return t, (None if t else "empty transcript (likely no speech)")


def tt_download(url, dest):
    if not url:
        return "no video url (slideshow or removed)"
    try:
        req = urllib.request.Request(url, headers=TT_HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            data = r.read()
        if len(data) < 5000:
            return f"download failed: only {len(data)} bytes"
        dest.write_bytes(data)
        return None
    except Exception as e:
        return f"download failed: {e}"


def tt_video_info(url, key):
    d = get("/v2/tiktok/video", {"url": url, "get_transcript": "true"}, key)
    a = d.get("aweme_detail") or {}
    if not a.get("aweme_id"):
        raise RuntimeError(f"Could not read TikTok {url} (private or removed?)")
    return d, a


def tt_followers(a, handle, key):
    n = (a.get("author") or {}).get("follower_count")
    if n:
        return n
    try:
        return get("/v1/tiktok/profile", {"handle": handle}, key)["stats"]["followerCount"]
    except Exception:
        return None


def tt_posts_total(a, handle, key):
    """The video-detail author record often says 0; the profile has the real count (1 credit)."""
    n = (a.get("author") or {}).get("aweme_count")
    if n:
        return n
    try:
        return get("/v1/tiktok/profile", {"handle": handle}, key)["stats"]["videoCount"]
    except Exception:
        return None


def tt_build(detail_resp, handle, posts, fcount, key, out):
    a = detail_resp["aweme_detail"]
    vid = str(a["aweme_id"])
    link = f"https://www.tiktok.com/@{handle}/video/{vid}"
    vdir = out / vid
    vdir.mkdir(parents=True, exist_ok=True)
    errors = []
    pinned = tt_out_of_order(posts)
    in_order = [p for p in posts if p["code"] not in pinned]
    out_of_reach = False
    if not any(p["code"] == vid for p in posts):
        # Scrape Creators warns profile feeds can skip posts. The detail call carries the plays,
        # so slot it in by date, but only if the catalogue reaches back past it.
        if in_order and min(p["taken_at"] for p in in_order) < (a.get("create_time") or 0):
            posts = posts + [tt_norm(a)]
        else:
            out_of_reach = True
            errors.append("post not in creator catalogue: multiple unavailable "
                          "(older than the catalogue reaches)")
    mult = multiples(posts)
    st = a.get("statistics") or {}
    dur_ms = (a.get("video") or {}).get("duration") or 0
    rec = {
        "shortcode": vid,
        "platform": "tiktok",
        "link": link,
        "creator": handle,
        "followers": fcount,
        "posted": datetime.fromtimestamp(a["create_time"], timezone.utc).date().isoformat()
        if a.get("create_time") else None,
        "plays": st.get("play_count"),
        "likes": st.get("digg_count"),
        "comments": st.get("comment_count"),
        "shares": st.get("share_count"),
        "saves": st.get("collect_count"),
        "duration_s": round(dur_ms / 1000) or None,
        "caption": a.get("desc") or "",
        "rolling_multiple": mult.get(vid, (None, None))[0],
        "rolling_median": mult.get(vid, (None, None))[1],
        "catalogue_size": len(posts),
        # catalogue_size stops at the pages needed for the multiple; this is the account's real total.
        "posts_total": tt_posts_total(a, handle, key),
        "track": tt_track(a, handle),
        "paid_signal": tt_paid_signal(a),
    }
    rec["multiple_basis"] = "rolling" if rec["rolling_multiple"] is not None else None
    if out_of_reach and rec["plays"] and apply_current_median(rec, posts):
        errors[:] = [e for e in errors if "multiple unavailable" not in e]
    if rec["plays"] is None and not errors:
        errors.append("plays unavailable: multiple unavailable")
    if a.get("image_post_info"):
        errors.append("slideshow: no mp4 (photo post, out of scope; skip it)")
    rec["transcript"], terr = tt_transcript(detail_resp, link, key)
    if terr:
        errors.append(terr)
    url, field = tt_video_url(a)
    derr = tt_download(url, vdir / "video.mp4")
    if derr:
        errors.append(derr)
    elif field != "download_no_watermark_addr" and (a.get("video") or {}).get("has_watermark"):
        errors.append(f"downloaded from {field}: watermark burned in")
    rec["video_path"] = str(vdir / "video.mp4") if not derr else None
    rec["errors"] = errors
    (vdir / "video.json").write_text(json.dumps(rec, indent=1))
    return rec


def tt_handle_jobs(handle, top, key, out):
    posts, _ = tt_catalogue(handle, None, key, out)
    organic = {p["code"] for p in posts if not tt_paid_signal(p["raw"])}
    ranked = sorted(((c, v) for c, v in multiples(posts).items() if c in organic),
                    key=lambda kv: -kv[1][0])[:top]
    return [f"https://www.tiktok.com/@{handle}/video/{c}" for c, _ in ranked]


def tt_run(url, key, out, cache):
    """One TikTok URL end to end. Returns the summary line."""
    url = tt_resolve_url(url)
    detail, a = tt_video_info(url, key)
    handle = (a.get("author") or {}).get("unique_id") or (TT_URL_RE.search(url) or [None, None])[1]
    user_id = (a.get("author") or {}).get("uid")
    posts, _ = tt_catalogue(handle, user_id, key, out, before_ts=a.get("create_time") or 0)
    if ("tt", handle) not in cache:
        cache[("tt", handle)] = tt_followers(a, handle, key)
    return tt_build(detail, handle, posts, cache[("tt", handle)], key, out)


SUMMARY_KEYS = ("shortcode", "creator", "plays", "rolling_multiple", "duration_s", "video_path",
                "errors", "credits_used")


def stamp_credits(rec, out, before):
    """Record what this video cost (its share of a creator's catalogue lands on the first one)."""
    rec["credits_used"] = CREDITS[0] - before
    p = out / str(rec["shortcode"]) / "video.json"
    if p.exists():
        p.write_text(json.dumps(rec, indent=1))
    return {k: rec.get(k) for k in SUMMARY_KEYS}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", action="append", default=[],
                    help="Instagram reel or TikTok video URL; platform is auto-detected")
    ap.add_argument("--handle")
    ap.add_argument("--platform", choices=("instagram", "tiktok"), default="instagram",
                    help="with --handle: which platform the handle is on")
    ap.add_argument("--top", type=int, default=5, help="with --handle: top N by rolling multiple")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if not a.url and not a.handle:
        ap.error("give --url (one or more) or --handle")
    key = api_key()
    out = Path(a.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)

    jobs = []  # (code, handle, single_post_response) -- Instagram
    tt_urls = []
    if a.handle and a.platform == "tiktok":
        tt_urls += tt_handle_jobs(a.handle.lstrip("@"), a.top, key, out)
    elif a.handle:
        handle = a.handle.lstrip("@")
        posts = catalogue(handle, key, out)
        organic = {p["code"] for p in posts if not paid_signal(p)}
        ranked = sorted(((c, v) for c, v in multiples(posts).items() if c in organic),
                        key=lambda kv: -kv[1][0])[: a.top]
        jobs = [(code, handle, None) for code, _ in ranked]
    results, cache = [], {}
    for u in a.url:
        try:
            if platform_of(u) == "tiktok":
                tt_urls.append(u)
                continue
            code = shortcode(u)
            lookup_from = CREDITS[0]
            handle, single = resolve_handle(code, key)
        except (ValueError, RuntimeError) as e:
            # Unreadable link: report it and carry on with the rest of the batch.
            results.append({"shortcode": None, "url": u, "errors": [str(e)]})
            print(json.dumps(results[-1]))
            continue
        jobs.append((code, handle, single, CREDITS[0] - lookup_from))
    jobs = [j if len(j) == 4 else j + (0,) for j in jobs]

    for code, handle, single, lookup_cost in jobs:
        before = CREDITS[0] - lookup_cost
        posts = catalogue(handle, key, out, target=code)
        if handle not in cache:
            cache[handle] = followers(handle, key)
        mult, fcount = multiples(posts), cache[handle]
        rec = build(code, handle, posts, mult, fcount, key, out, single)
        results.append(stamp_credits(rec, out, before))
        print(json.dumps(results[-1]))

    for u in tt_urls:
        before = CREDITS[0]
        try:
            rec = tt_run(u, key, out, cache)
        except (ValueError, RuntimeError) as e:
            results.append({"shortcode": None, "url": u, "errors": [str(e)],
                            "credits_used": CREDITS[0] - before})
            print(json.dumps(results[-1]))
            continue
        results.append(stamp_credits(rec, out, before))
        print(json.dumps(results[-1]))
    (out / "summary.json").write_text(json.dumps(results, indent=1))
    print(json.dumps({"credits_total": CREDITS[0]}))


if __name__ == "__main__":
    main()
