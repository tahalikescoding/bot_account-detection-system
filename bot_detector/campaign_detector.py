"""
Campaign Detector for CommentGuard AI.
Clusters flagged bot accounts that share near-identical comment text,
similar account creation dates, or posting within narrow time windows.
"""

from datetime import datetime, timezone
import re
from bot_detector.scoring_engine import text_similarity, parse_datetime
import difflib


def detect_campaign_clusters(scored_comments):
    """
    Analyzes scored comments and groups coordinated accounts into clusters.
    Returns:
      - clusters: list of cluster objects
      - coordinated_account_ids: set of author channel/comment IDs in campaigns
      - total_coordinated_accounts: count of coordinated accounts
    """
    if not scored_comments:
        return {
            "clusters": [],
            "total_coordinated_accounts": 0,
            "coordinated_comment_ids": []
        }

    # Only inspect accounts with suspicious or bot behavior or duplicate text
    candidates = [
        c for c in scored_comments
        if c.get("bot_score", 0) >= 35 or len(c.get("duplicate_matches", [])) > 0
    ]
    MAX_CLUSTER_CANDIDATES = 300  # hard cap to bound worst-case memory/CPU
    candidates = candidates[:MAX_CLUSTER_CANDIDATES]
    # Graph-based clustering: connect accounts that share high similarity
    # or identical external URLs or very narrow posting burst with identical pattern
    n = len(candidates)
    visited = set()
    clusters = []

    for i in range(n):
        if candidates[i]["comment_id"] in visited:
            continue

        cluster_members = [candidates[i]]
        visited.add(candidates[i]["comment_id"])

        for j in range(i + 1, n):
            c_j = candidates[j]
            if c_j["comment_id"] in visited:
                continue

            # Compare against any existing member in the cluster
            is_match = False
            for member in cluster_members:
                # 1. Direct text similarity
                m_norm = member.get("comment_text", "").lower().strip()
                cj_norm = c_j.get("comment_text", "").lower().strip()
                if m_norm and cj_norm:
                    quick_matcher = difflib.SequenceMatcher(None, m_norm, cj_norm)
                    if quick_matcher.quick_ratio() >= 0.65:
                        sim = text_similarity(member.get("comment_text", ""), c_j.get("comment_text", ""))
                        if sim >= 0.65:
                            is_match = True
                            break

                # 2. Shared link, telegram handle, or whatsapp
                m_text = member.get("comment_text", "").lower()
                cj_text = c_j.get("comment_text", "").lower()
                member_links = set(re.findall(r'(?:t\.me|wa\.me|bit\.ly|[a-zA-Z0-9-]+\.(?:com|xyz|top))/[^\s]+', m_text))
                cj_links = set(re.findall(r'(?:t\.me|wa\.me|bit\.ly|[a-zA-Z0-9-]+\.(?:com|xyz|top))/[^\s]+', cj_text))
                if member_links and cj_links and (member_links & cj_links):
                    is_match = True
                    break

                # 3. Synchronized burst (<30s) WITH shared intent/theme
                t_m = parse_datetime(member.get("published_at"))
                t_j = parse_datetime(c_j.get("published_at"))
                if t_m and t_j and abs((t_m - t_j).total_seconds()) <= 30:
                    # Must share at least one topical spam indicator
                    same_crypto = ("telegram" in m_text or "crypto" in m_text) and ("telegram" in cj_text or "crypto" in cj_text)
                    same_promo = ("check my" in m_text or "sub 4 sub" in m_text or "beats" in m_text) and ("check my" in cj_text or "sub 4 sub" in cj_text or "beats" in cj_text)
                    same_giveaway = ("giveaway" in m_text or "gift card" in m_text or "won" in m_text) and ("giveaway" in cj_text or "gift card" in cj_text or "won" in cj_text)
                    if (same_crypto or same_promo or same_giveaway) and member.get("bot_score", 0) >= 50 and c_j.get("bot_score", 0) >= 50:
                        is_match = True
                        break

            if is_match:
                cluster_members.append(c_j)
                visited.add(c_j["comment_id"])

        # Only consider groups of 2 or more as a coordinated campaign
        if len(cluster_members) >= 2:
            # Sort cluster members chronologically
            cluster_members.sort(key=lambda x: parse_datetime(x.get("published_at")) or datetime.min.replace(tzinfo=timezone.utc))

            # Compute cluster duration
            t_first = parse_datetime(cluster_members[0].get("published_at"))
            t_last = parse_datetime(cluster_members[-1].get("published_at"))
            time_span_seconds = 0
            if t_first and t_last:
                time_span_seconds = max(0, int((t_last - t_first).total_seconds()))

            # Determine dominant campaign signature
            sample_text = cluster_members[0].get("comment_text", "")
            shared_traits = []

            # Check shared links/telegram
            all_text = " ".join(c.get("comment_text", "") for c in cluster_members)
            if "t.me" in all_text or "telegram" in all_text.lower():
                shared_traits.append("Telegram Crypto Solicitation")
            if "wa.me" in all_text or "whatsapp" in all_text.lower():
                shared_traits.append("WhatsApp Scam Directing")
            if "bit.ly" in all_text or "giveaway" in all_text.lower():
                shared_traits.append("Phishing Giveaway Link")
            if "sub 4 sub" in all_text.lower() or "check my channel" in all_text.lower():
                shared_traits.append("Automated Channel Promo Ring")

            default_pfp_count = sum(1 for c in cluster_members if c.get("has_default_avatar"))
            if default_pfp_count == len(cluster_members):
                shared_traits.append("100% Default Profile Icons")
            elif default_pfp_count >= 2:
                shared_traits.append(f"{default_pfp_count}/{len(cluster_members)} Default Avatars")

            if time_span_seconds <= 60:
                shared_traits.append(f"Synchronized burst ({time_span_seconds}s span)")

            avg_score = round(sum(c.get("bot_score", 0) for c in cluster_members) / len(cluster_members), 1)

            # Assign cluster designation name
            cluster_letter = chr(65 + len(clusters))  # Cluster A, B, C...
            theme_title = "Coordinated Attack Group"
            if "Telegram Crypto" in " ".join(shared_traits):
                theme_title = "Crypto Recovery Ring"
            elif "Automated Channel" in " ".join(shared_traits):
                theme_title = "Channel Promotion Ring"
            elif "Phishing Giveaway" in " ".join(shared_traits):
                theme_title = "Giveaway Phishing Sybil"
            elif "Synchronized burst" in " ".join(shared_traits):
                theme_title = "Synchronized Bot Raid"

            clusters.append({
                "cluster_id": f"cluster_{cluster_letter.lower()}",
                "name": f"Cluster {cluster_letter}: {theme_title}",
                "account_count": len(cluster_members),
                "member_comment_ids": [c["comment_id"] for c in cluster_members],
                "members": [
                    {
                        "comment_id": c["comment_id"],
                        "author_name": c.get("author_name"),
                        "author_handle": c.get("author_handle"),
                        "author_avatar": c.get("author_avatar"),
                        "bot_score": c.get("bot_score"),
                        "published_at": c.get("published_at"),
                        "comment_text": c.get("comment_text")
                    }
                    for c in cluster_members
                ],
                "sample_text": sample_text,
                "time_span_seconds": time_span_seconds,
                "time_span_display": f"{time_span_seconds}s" if time_span_seconds < 60 else f"{round(time_span_seconds/60, 1)}m",
                "avg_bot_score": avg_score,
                "shared_traits": shared_traits,
                "threat_level": "CRITICAL" if avg_score >= 75 else "HIGH"
            })

    # Sort clusters by account count descending
    clusters.sort(key=lambda x: x["account_count"], reverse=True)

    all_coordinated_ids = set()
    for cl in clusters:
        for cid in cl["member_comment_ids"]:
            all_coordinated_ids.add(cid)

    return {
        "clusters": clusters,
        "total_coordinated_accounts": len(all_coordinated_ids),
        "coordinated_comment_ids": list(all_coordinated_ids)
    }
