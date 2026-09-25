"""
YouTube service for CommentGuard AI.
Priority order:
  1. youtube-comment-downloader (no API key needed, scrapes real YouTube comments)
  2. YouTube Data API v3 (if API key is explicitly provided)
  3. Mock dataset fallback (if all else fails)
"""

import re
import requests
import dateparser
from datetime import datetime, timezone, timedelta
from itertools import islice
from bot_detector.mock_data import get_mock_comments, AVATAR_BOT_DEFAULT


def extract_video_id(url_or_id):
    """
    Extracts an 11-character YouTube video ID from various URL formats or a bare ID.
    """
    if not url_or_id:
        return None
    url_or_id = url_or_id.strip()

    # Already a bare 11-char ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id

    patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
    ]
    for p in patterns:
        m = re.search(p, url_or_id)
        if m:
            return m.group(1)

    return None


def is_default_youtube_avatar(avatar_url):
    """Detects default/generic YouTube profile pictures."""
    if not avatar_url:
        return True
    low = avatar_url.lower()
    return (
        "default_avatar" in low
        or ("photo.jpg" in low and "yt3.ggpht.com" in low)
        or "identicon" in low
    )


def fetch_video_metadata_oembed(video_id):
    """
    Fetches video title, channel name, and thumbnail via YouTube's free oEmbed endpoint.
    No API key required.
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    try:
        r = requests.get(
            f"https://www.youtube.com/oembed?url={video_url}&format=json",
            timeout=6
        )
        if r.status_code == 200:
            data = r.json()
            return {
                "id": video_id,
                "title": data.get("title", "YouTube Video"),
                "channel_title": data.get("author_name", "Unknown Channel"),
                "video_id": video_id,
                "published_at": datetime.now(timezone.utc).isoformat(),
                "view_count": "N/A",
                "like_count": "N/A",
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            }
    except Exception:
        pass

    # Bare minimum fallback
    return {
        "id": video_id,
        "title": f"YouTube Video ({video_id})",
        "channel_title": "Unknown Channel",
        "video_id": video_id,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "view_count": "N/A",
        "like_count": "N/A",
        "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
    }


def parse_relative_time(time_str):
    """
    Converts relative YouTube time strings like '3 hours ago', '2 weeks ago' etc.
    to an ISO 8601 datetime string.
    """
    if not time_str:
        return None
    try:
        parsed = dateparser.parse(str(time_str), settings={"RETURN_AS_TIMEZONE_AWARE": True})
        if parsed:
            return parsed.isoformat()
    except Exception:
        pass
    return None


# Hard safety ceiling to prevent hanging on videos with millions of comments
MAX_COMMENTS_CEILING = 2000


def fetch_real_comments(video_id, max_results=0):
    """
    Fetches ALL YouTube comments without an API key using youtube-comment-downloader.
    max_results=0 means no limit (up to MAX_COMMENTS_CEILING).
    Returns a list of normalized comment dicts ready for the scoring engine.
    """
    from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    video_info = fetch_video_metadata_oembed(video_id)
    video_published_at = video_info["published_at"]

    downloader = YoutubeCommentDownloader()

    # Use the ceiling: if user sets a custom limit use that, otherwise fetch all up to ceiling
    limit = max_results if max_results and max_results > 0 else MAX_COMMENTS_CEILING
    raw = list(islice(
        downloader.get_comments_from_url(video_url, sort_by=SORT_BY_RECENT),
        limit
    ))

    comments = []
    for idx, c in enumerate(raw):
        author_name = c.get("author", "Anonymous")
        channel_id = c.get("channel", "")
        avatar_url = c.get("photo") or AVATAR_BOT_DEFAULT
        comment_text = c.get("text", "")
        time_str = c.get("time", "")
        votes = c.get("votes", 0)
        cid = c.get("cid") or f"scraped_{idx}"

        published_at = parse_relative_time(time_str)
        if not published_at:
            # If we can't parse, assume it was posted within the hour to be safe
            published_at = (datetime.now(timezone.utc) - timedelta(minutes=idx * 2)).isoformat()

        has_default = is_default_youtube_avatar(avatar_url)

        # Build handle from channel ID or author name
        handle = f"@{re.sub(r'[^a-zA-Z0-9_]', '', author_name.lower())}"

        comments.append({
            "comment_id": cid,
            "author_name": author_name,
            "author_handle": handle,
            "author_channel_id": channel_id,
            "author_avatar": avatar_url,
            "has_default_avatar": has_default,
            "account_created_at": None,  # Not available from scraper
            "comment_text": comment_text,
            "published_at": published_at,
            "video_published_at": video_published_at,
            "like_count": votes,
            "is_reply": c.get("reply", False),
        })

    return video_info, comments


def fetch_youtube_api_comments(video_id, api_key, max_results=100):
    """
    Fetches comments via YouTube Data API v3 (requires a valid API key).
    """
    try:
        # Fetch video metadata
        v_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"part": "snippet,statistics", "id": video_id, "key": api_key},
            timeout=8
        )
        if v_resp.status_code != 200:
            raise Exception(f"YouTube Videos API returned {v_resp.status_code}")

        v_items = v_resp.json().get("items", [])
        if not v_items:
            raise Exception("Video not found or is private.")

        snippet = v_items[0]["snippet"]
        statistics = v_items[0]["statistics"]
        video_info = {
            "id": video_id,
            "title": snippet.get("title", "Untitled Video"),
            "channel_title": snippet.get("channelTitle", "Unknown Channel"),
            "video_id": video_id,
            "published_at": snippet.get("publishedAt", datetime.now(timezone.utc).isoformat()),
            "view_count": f"{int(statistics.get('viewCount', 0)):,}",
            "like_count": f"{int(statistics.get('likeCount', 0)):,}",
            "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        }

        # Fetch comments
        c_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/commentThreads",
            params={
                "part": "snippet",
                "videoId": video_id,
                "maxResults": min(max_results, 100),
                "textFormat": "plainText",
                "order": "time",
                "key": api_key
            },
            timeout=10
        )
        if c_resp.status_code != 200:
            raise Exception(f"YouTube Comments API returned {c_resp.status_code}")

        comments = []
        for item in c_resp.json().get("items", []):
            top = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            avatar = top.get("authorProfileImageUrl", "")
            comments.append({
                "comment_id": item.get("id"),
                "author_name": top.get("authorDisplayName", "Anonymous"),
                "author_handle": f"@{top.get('authorDisplayName', '').lower().replace(' ', '')}",
                "author_channel_id": top.get("authorChannelId", {}).get("value", ""),
                "author_avatar": avatar or AVATAR_BOT_DEFAULT,
                "has_default_avatar": is_default_youtube_avatar(avatar),
                "account_created_at": None,
                "comment_text": top.get("textDisplay", ""),
                "published_at": top.get("publishedAt"),
                "video_published_at": video_info["published_at"],
                "like_count": top.get("likeCount", 0),
                "is_reply": False,
            })

        return video_info, comments

    except Exception as e:
        raise Exception(str(e))


def fetch_youtube_comments(video_id=None, api_key=None, max_results=100):
    """
    Main entry point for comment fetching.
    Priority:
      1. If API key provided → YouTube Data API v3
      2. If video_id provided (no API key) → youtube-comment-downloader (real scraping, no quota)
      3. Fallback → curated mock dataset
    """
    # --- Path 1: API key provided ---
    if video_id and api_key:
        try:
            video_info, comments = fetch_youtube_api_comments(video_id, api_key, max_results)
            return {
                "video": video_info,
                "comments": comments,
                "data_source": "live_youtube_api",
                "source_notice": f"Fetched {len(comments)} live comments via YouTube Data API v3.",
            }
        except Exception as e:
            # Fall through to scraper on API failure
            pass

    # --- Path 2: Real scraping via youtube-comment-downloader (no key needed) ---
    if video_id:
        try:
            # max_results=0 → fetch all (up to safety ceiling)
            video_info, comments = fetch_real_comments(video_id, max_results=max_results)
            return {
                "video": video_info,
                "comments": comments,
                "data_source": "live_scrape",
                "source_notice": f"Fetched {len(comments)} real comments from YouTube (no API key required).",
            }
        except Exception as e:
            # Fall through to mock on scraping failure
            error_msg = str(e)[:100]

    # --- Path 3: Mock fallback ---
    dataset = get_mock_comments(preset="crypto_attack")
    dataset["data_source"] = "mock_fallback"
    dataset["source_notice"] = "Could not fetch live comments. Showing curated demo dataset."
    return dataset
