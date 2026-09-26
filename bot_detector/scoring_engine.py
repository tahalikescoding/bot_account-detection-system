"""
Bot Scoring Engine for CommentGuard AI.
Calculates transparent 0-100 bot scores based on weighted behavioral,
metadata, and linguistic signals.
"""
from collections import defaultdict
from datetime import datetime, timezone
import re
import difflib

# Regex patterns for signal detection
URL_REGEX = re.compile(
    r'(https?://[^\s]+|bit\.ly/[^\s]+|t\.me/[^\s]+|wa\.me/[^\s]+|tinyurl\.com/[^\s]+|[a-zA-Z0-9-]+\.(?:com|xyz|top|io|club|link)/[^\s]*)',
    re.IGNORECASE
)

SPAM_KEYWORDS = [
    "check my channel", "check out my channel", "sub 4 sub", "sub4sub",
    "telegram", "whatsapp", "wa.me", "t.me", "forex", "crypto", "bitcoin",
    "ethereum", "passive income", "airdrop", "presale", "recover my money",
    "recovered my", "guaranteed profit", "free gift card", "won an iphone",
    "congratulations you won", "claim your prize", "dm me on", "text me on",
    "whatsapp me", "check my bio", "link in bio"
]

GENERIC_USERNAME_REGEX = re.compile(
    r'^(?:user|bot|guest|member)?[_-]?[0-9]{5,}|[a-zA-Z]+[0-9]{5,}$|(?:crypto|forex|deal|beats?|free|sub|trade)[_-]?[a-zA-Z0-9]*[0-9]{3,}',
    re.IGNORECASE
)

EMOJI_REGEX = re.compile(
    r'[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf]',
    flags=re.UNICODE
)


def normalize_text_for_comparison(text):
    """Normalizes comment text to detect copy-paste variants."""
    text = text.lower()
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    return ' '.join(text.split())


def text_similarity(text1, text2):
    """Calculates SequenceMatcher similarity between two normalized strings."""
    norm1 = normalize_text_for_comparison(text1)
    norm2 = normalize_text_for_comparison(text2)
    if not norm1 or not norm2:
        return 0.0
    if norm1 == norm2:
        return 1.0
    return difflib.SequenceMatcher(None, norm1, norm2).ratio()

def calculate_duplicate_matrix(comments):
    duplicates_map = {c["comment_id"]: [] for c in comments}
    normalized = [normalize_text_for_comparison(c.get("comment_text", "")) for c in comments]

    SIM_THRESHOLD = 0.70
    BUCKET_SIZE = 10
    MAX_BUCKET_SPAN = 150  # hard cap — prevents runaway memory/CPU on huge similar-length clusters

    buckets = defaultdict(list)
    for i, norm in enumerate(normalized):
        if norm:
            buckets[len(norm) // BUCKET_SIZE].append(i)

    checked_pairs = set()

    for bucket_key, idxs in buckets.items():
        candidates = idxs + buckets.get(bucket_key + 1, [])
        if len(candidates) > MAX_BUCKET_SPAN:
            candidates = candidates[:MAX_BUCKET_SPAN]  # cap comparisons in oversized buckets

        for i in idxs:
            if i not in candidates and i not in idxs[:MAX_BUCKET_SPAN]:
                continue
            for j in candidates:
                if j <= i:
                    continue
                pair = (i, j)
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)

                norm1, norm2 = normalized[i], normalized[j]
                if not norm1 or not norm2:
                    continue
                if norm1 == norm2:
                    sim = 1.0
                else:
                    matcher = difflib.SequenceMatcher(None, norm1, norm2)
                    if matcher.quick_ratio() < SIM_THRESHOLD:
                        continue
                    sim = matcher.ratio()

                if sim >= SIM_THRESHOLD:
                    c1, c2 = comments[i], comments[j]
                    id1, id2 = c1["comment_id"], c2["comment_id"]
                    if len(duplicates_map[id1]) < 20:  # cap stored matches per comment too
                        duplicates_map[id1].append({"id": id2, "author": c2.get("author_name"), "sim": round(sim, 2)})
                    if len(duplicates_map[id2]) < 20:
                        duplicates_map[id2].append({"id": id1, "author": c1.get("author_name"), "sim": round(sim, 2)})

    return duplicates_map


def parse_datetime(dt_val):
    """Helper to parse ISO datetime or datetime object."""
    if isinstance(dt_val, datetime):
        if dt_val.tzinfo is None:
            return dt_val.replace(tzinfo=timezone.utc)
        return dt_val
    if not dt_val:
        return None
    try:
        clean_str = str(dt_val).replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def score_single_comment(comment, duplicate_matches=None):
    """
    Scores a single comment dictionary against all weighted signals.
    Returns the scored comment object with explainable signals.
    """
    duplicate_matches = duplicate_matches or []
    signals = []
    category_scores = {
        "account_age": 0,
        "username_pattern": 0,
        "avatar": 0,
        "timing": 0,
        "suspicious_content": 0,
        "formatting": 0,
        "duplicate_text": 0
    }

    comment_text = comment.get("comment_text", "")
    author_name = comment.get("author_name", "")
    author_handle = comment.get("author_handle", "")
    has_default_avatar = comment.get("has_default_avatar", False)
    author_avatar = comment.get("author_avatar", "")

    now = datetime(2026, 9, 25, 18, 0, 0, tzinfo=timezone.utc)

    # 1. Account Age Signal
    created_at = parse_datetime(comment.get("account_created_at"))
    account_age_days = None
    if created_at:
        account_age_days = max(0, (now - created_at).days)
        if account_age_days <= 3:
            pts = 25
            category_scores["account_age"] = pts
            signals.append({
                "signal": "Account Age",
                "points": pts,
                "reason": f"+{pts} Brand new account (created {account_age_days} day{'s' if account_age_days != 1 else ''} ago)",
                "severity": "high"
            })
        elif account_age_days <= 14:
            pts = 18
            category_scores["account_age"] = pts
            signals.append({
                "signal": "Account Age",
                "points": pts,
                "reason": f"+{pts} Very new account (created {account_age_days} days ago)",
                "severity": "medium"
            })
        elif account_age_days <= 45:
            pts = 10
            category_scores["account_age"] = pts
            signals.append({
                "signal": "Account Age",
                "points": pts,
                "reason": f"+{pts} Recently registered account ({account_age_days} days old)",
                "severity": "low"
            })

    # 2. Generic/Random Username Pattern Signal
    has_generic_name = bool(
        GENERIC_USERNAME_REGEX.search(author_name) or
        GENERIC_USERNAME_REGEX.search(author_handle.lstrip('@')) or
        bool(re.search(r'[0-9]{5,}', author_name))
    )
    if has_generic_name:
        pts = 20
        category_scores["username_pattern"] = pts
        signals.append({
            "signal": "Username Pattern",
            "points": pts,
            "reason": f"+{pts} Auto-generated username pattern with long digit suffix",
            "severity": "medium"
        })

    # 3. Default/Missing Profile Picture Signal
    is_default_avatar = (
        has_default_avatar or
        "default_avatar" in author_avatar.lower() or
        "identicon" in author_avatar.lower()
    )
    if is_default_avatar:
        pts = 20
        category_scores["avatar"] = pts
        signals.append({
            "signal": "Avatar Profile",
            "points": pts,
            "reason": f"+{pts} Default or missing profile picture",
            "severity": "medium"
        })

    # 4. Comment Timing / Fast Burst Signal
    pub_time = parse_datetime(comment.get("published_at"))
    vid_pub_time = parse_datetime(comment.get("video_published_at"))
    seconds_after_upload = None
    if pub_time and vid_pub_time:
        diff_seconds = (pub_time - vid_pub_time).total_seconds()
        if diff_seconds >= 0:
            seconds_after_upload = int(diff_seconds)
            if seconds_after_upload <= 15:
                pts = 30
                category_scores["timing"] = pts
                signals.append({
                    "signal": "Publish Timing",
                    "points": pts,
                    "reason": f"+{pts} Posted {seconds_after_upload}s after video upload (instant bot burst)",
                    "severity": "high"
                })
            elif seconds_after_upload <= 60:
                pts = 20
                category_scores["timing"] = pts
                signals.append({
                    "signal": "Publish Timing",
                    "points": pts,
                    "reason": f"+{pts} Posted within 60s of video upload ({seconds_after_upload}s)",
                    "severity": "medium"
                })

    # 5. Suspicious Content (Links, Promo, Crypto, Giveaway Keywords)
    found_urls = URL_REGEX.findall(comment_text)
    has_link = bool(found_urls)
    lower_text = comment_text.lower()
    found_keywords = [kw for kw in SPAM_KEYWORDS if kw in lower_text]

    content_pts = 0
    if has_link:
        content_pts += 20
        signals.append({
            "signal": "External Link",
            "points": 20,
            "reason": f"+20 Contains external link/domain: {found_urls[0]}",
            "severity": "high"
        })
    if found_keywords:
        kw_pts = 15
        content_pts += kw_pts
        matched_str = ", ".join(f"'{k}'" for k in found_keywords[:3])
        signals.append({
            "signal": "Spam Keywords",
            "points": kw_pts,
            "reason": f"+{kw_pts} High-risk keywords detected: {matched_str}",
            "severity": "high"
        })

    category_scores["suspicious_content"] = min(35, content_pts)

    # Sleeper Account Check: Old account + sudden spam link
    if account_age_days and account_age_days > 700 and (has_link or len(found_keywords) >= 2):
        sleeper_pts = 15
        category_scores["account_age"] = max(category_scores["account_age"], sleeper_pts)
        signals.append({
            "signal": "Sleeper Hijack",
            "points": sleeper_pts,
            "reason": f"+{sleeper_pts} Sleeper account signature (dormant {account_age_days}d account posting spam)",
            "severity": "high"
        })

    # 6. Excessive Emojis or All-Caps Signal
    letters = [ch for ch in comment_text if ch.isalpha()]
    caps = [ch for ch in letters if ch.isupper()]
    formatting_pts = 0

    if len(letters) >= 12 and (len(caps) / len(letters)) >= 0.50:
        formatting_pts += 10
        signals.append({
            "signal": "Caps Lock",
            "points": 10,
            "reason": f"+10 Excessive all-caps text ({int(len(caps)/len(letters)*100)}% capital letters)",
            "severity": "low"
        })

    emoji_matches = EMOJI_REGEX.findall(comment_text)
    if len(emoji_matches) >= 4:
        formatting_pts += 10
        signals.append({
            "signal": "Emoji Density",
            "points": 10,
            "reason": f"+10 High emoji spam density ({len(emoji_matches)} emojis)",
            "severity": "low"
        })

    category_scores["formatting"] = min(15, formatting_pts)

    # 7. Near-Duplicate / Copy-Paste Text Signal
    if duplicate_matches:
        high_sim_matches = [m for m in duplicate_matches if m["sim"] >= 0.85]
        if high_sim_matches:
            pts = 25
            category_scores["duplicate_text"] = pts
            signals.append({
                "signal": "Copy-Paste Spam",
                "points": pts,
                "reason": f"+{pts} Near-identical duplicate text matched against {len(high_sim_matches)} other account(s)",
                "severity": "high"
            })
        else:
            pts = 15
            category_scores["duplicate_text"] = pts
            signals.append({
                "signal": "Text Repetition",
                "points": pts,
                "reason": f"+{pts} High text similarity matched with {len(duplicate_matches)} other comment(s)",
                "severity": "medium"
            })

    # Total Score Calculation
    raw_score = sum(category_scores.values())
    bot_score = min(100, max(0, raw_score))

    # Classification & Verdict
    if bot_score <= 30:
        verdict = "Likely Human"
        verdict_class = "human"
        verdict_color = "#10b981"  # Emerald green
    elif bot_score <= 65:
        verdict = "Suspicious"
        verdict_class = "suspicious"
        verdict_color = "#f59e0b"  # Amber
    else:
        verdict = "Likely Bot"
        verdict_class = "bot"
        verdict_color = "#ef4444"  # Crimson

    reasons = [s["reason"] for s in signals]
    if not reasons:
        reasons = ["No malicious signals detected (organic user behavior)"]

    return {
        **comment,
        "bot_score": bot_score,
        "verdict": verdict,
        "verdict_class": verdict_class,
        "verdict_color": verdict_color,
        "signals": signals,
        "category_scores": category_scores,
        "reasons": reasons,
        "duplicate_count": len(duplicate_matches),
        "duplicate_matches": duplicate_matches,
        "account_age_days": account_age_days,
        "seconds_after_upload": seconds_after_upload
    }


def score_comment_batch(comments):
    """
    Scores an entire batch of comments, computing cross-comment duplicate analysis
    and aggregate explainability statistics.
    """
    # 1. Compute duplicate matrix across batch
    dup_map = calculate_duplicate_matrix(comments)

    # 2. Score each comment individually
    scored_comments = []
    for c in comments:
        c_id = c.get("comment_id", "")
        matches = dup_map.get(c_id, [])
        scored = score_single_comment(c, duplicate_matches=matches)
        scored_comments.append(scored)

    # 3. Sort by highest bot score by default
    scored_comments.sort(key=lambda x: x["bot_score"], reverse=True)

    # 4. Compute overall explainability & aggregate weights
    total_comments = len(scored_comments)
    likely_bots = sum(1 for c in scored_comments if c["verdict_class"] == "bot")
    suspicious = sum(1 for c in scored_comments if c["verdict_class"] == "suspicious")
    likely_humans = sum(1 for c in scored_comments if c["verdict_class"] == "human")
    avg_score = round(sum(c["bot_score"] for c in scored_comments) / max(1, total_comments), 1)

    # Aggregate category weight contributions across flagged comments (bots + suspicious)
    flagged = [c for c in scored_comments if c["bot_score"] > 30]
    category_totals = {
        "suspicious_content": 0,
        "duplicate_text": 0,
        "timing": 0,
        "avatar": 0,
        "username_pattern": 0,
        "account_age": 0,
        "formatting": 0
    }
    for c in flagged:
        for cat, pts in c["category_scores"].items():
            category_totals[cat] = category_totals.get(cat, 0) + pts

    total_pts_earned = sum(category_totals.values()) or 1
    category_percentages = {
        cat: round((pts / total_pts_earned) * 100, 1)
        for cat, pts in category_totals.items()
    }

    explainability = {
        "feature_weights_config": {
            "suspicious_content": {"label": "Spam Links & Keywords", "max_pts": 35, "desc": "URLs, Telegram handles, crypto & giveaway keywords"},
            "timing": {"label": "Publish Timing / Burst", "max_pts": 30, "desc": "Comments posted within 60s or <15s of upload"},
            "duplicate_text": {"label": "Duplicate / Copy-Paste", "max_pts": 25, "desc": "Near-identical comment text across multiple accounts"},
            "avatar": {"label": "Default / Missing Avatar", "max_pts": 20, "desc": "Generic silhouette or placeholder profile image"},
            "username_pattern": {"label": "Generic Username Pattern", "max_pts": 20, "desc": "Auto-generated digit sequence or bot handle"},
            "account_age": {"label": "Account Age / Sleeper", "max_pts": 25, "desc": "New accounts (<14d) or sleeper account signature"},
            "formatting": {"label": "Emoji & Caps Spam", "max_pts": 15, "desc": ">50% uppercase letters or 4+ spam emojis"}
        },
        "aggregate_contributions": category_percentages,
        "category_totals": category_totals
    }

    return {
        "comments": scored_comments,
        "summary": {
            "total_comments": total_comments,
            "likely_bots_count": likely_bots,
            "likely_bots_percentage": round((likely_bots / max(1, total_comments)) * 100, 1),
            "suspicious_count": suspicious,
            "likely_humans_count": likely_humans,
            "avg_bot_score": avg_score
        },
        "explainability": explainability
    }
