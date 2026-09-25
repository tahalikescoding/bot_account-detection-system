"""
CommentGuard AI - Main Flask Server
A bot detection dashboard for content creators to analyze video comment sections
and identify likely bot accounts and coordinated spam campaigns.
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timezone
import os

from bot_detector.scoring_engine import score_comment_batch
from bot_detector.campaign_detector import detect_campaign_clusters
from bot_detector.youtube_service import fetch_youtube_comments, extract_video_id
from bot_detector.mock_data import get_mock_comments, generate_injection, PRESET_VIDEOS

app = Flask(__name__)


@app.route("/")
def index():
    """Serves the main single-page CommentGuard AI dashboard."""
    return render_template("index.html")


@app.route("/api/presets", methods=["GET"])
def get_presets():
    """Returns metadata for built-in demo video presets."""
    return jsonify({
        "status": "success",
        "presets": PRESET_VIDEOS
    })


@app.route("/api/analyze", methods=["POST"])
def analyze_comments():
    """
    Analyzes comments for a given YouTube URL or demo preset.
    Combines YouTube API data or realistic mock dataset with the Bot Scoring Engine
    and Campaign Detector.
    """
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    api_key = data.get("api_key", "").strip() or os.environ.get("YOUTUBE_API_KEY", "")
    preset = data.get("preset", "crypto_attack")
    # max_comments=0 means fetch ALL (up to the 2000 safety ceiling)
    raw_max = data.get("max_comments", 0)
    max_results = int(raw_max) if str(raw_max).isdigit() else 0

    video_id = extract_video_id(url) if url else None

    if video_id:
        # Real URL pasted → scrape real comments (works with OR without an API key)
        fetched_data = fetch_youtube_comments(
            video_id=video_id,
            api_key=api_key if api_key else None,
            max_results=max_results
        )
    else:
        # No URL → load the selected demo preset
        target_preset = preset if preset in PRESET_VIDEOS else "crypto_attack"
        fetched_data = get_mock_comments(preset=target_preset)
        fetched_data["data_source"] = "preset_demo"
        fetched_data["source_notice"] = f"Demo dataset: {fetched_data['video']['title']}"

    raw_comments = fetched_data.get("comments", [])
    video_info = fetched_data.get("video", {})

    # 1. Run through Bot Scoring Engine
    scoring_result = score_comment_batch(raw_comments)
    scored_comments = scoring_result["comments"]
    summary = scoring_result["summary"]
    explainability = scoring_result["explainability"]

    # 2. Run through Campaign Detector
    campaign_result = detect_campaign_clusters(scored_comments)
    clusters = campaign_result["clusters"]
    coordinated_ids = set(campaign_result["coordinated_comment_ids"])

    # Annotate comments with cluster memberships
    for c in scored_comments:
        c["is_in_campaign"] = c["comment_id"] in coordinated_ids
        c["campaign_cluster_names"] = [
            cl["name"] for cl in clusters if c["comment_id"] in cl["member_comment_ids"]
        ]

    # Update summary with coordinated account count
    summary["coordinated_accounts_count"] = campaign_result["total_coordinated_accounts"]

    return jsonify({
        "status": "success",
        "video": video_info,
        "summary": summary,
        "comments": scored_comments,
        "clusters": clusters,
        "explainability": explainability,
        "data_source": fetched_data.get("data_source", "mock_fallback"),
        "source_notice": fetched_data.get("source_notice", "")
    })


@app.route("/api/inject", methods=["POST"])
def inject_bot_pattern():
    """
    Live fraud injection endpoint for interactive demos.
    Injects synthetic bot patterns into the active feed, re-scores in real-time,
    and recalculates campaign clusters.
    """
    data = request.get_json() or {}
    injection_type = data.get("injection_type", "spam_bot")
    current_comments = data.get("current_comments", [])

    # Generate synthetic injection comments
    injected_items = generate_injection(injection_type)
    injected_ids = [item["comment_id"] for item in injected_items]

    # Merge with existing comments (avoiding duplicates)
    existing_ids = {c["comment_id"] for c in current_comments}
    merged_comments = [c for c in current_comments]

    for item in injected_items:
        if item["comment_id"] not in existing_ids:
            merged_comments.append(item)

    # Re-score the entire batch to update cross-comment duplication & burst rates
    scoring_result = score_comment_batch(merged_comments)
    scored_comments = scoring_result["comments"]
    summary = scoring_result["summary"]
    explainability = scoring_result["explainability"]

    # Re-cluster with Campaign Detector
    campaign_result = detect_campaign_clusters(scored_comments)
    clusters = campaign_result["clusters"]
    coordinated_ids = set(campaign_result["coordinated_comment_ids"])

    for c in scored_comments:
        c["is_in_campaign"] = c["comment_id"] in coordinated_ids
        c["campaign_cluster_names"] = [
            cl["name"] for cl in clusters if c["comment_id"] in cl["member_comment_ids"]
        ]

    summary["coordinated_accounts_count"] = campaign_result["total_coordinated_accounts"]

    return jsonify({
        "status": "success",
        "injected_count": len(injected_items),
        "injected_ids": injected_ids,
        "injection_type": injection_type,
        "summary": summary,
        "comments": scored_comments,
        "clusters": clusters,
        "explainability": explainability
    })


if __name__ == "__main__":
    # Local dev server
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] CommentGuard AI running on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
