"""
CommentGuard AI - Bot Account Detection Package
"""

from bot_detector.scoring_engine import score_comment_batch, score_single_comment
from bot_detector.campaign_detector import detect_campaign_clusters
from bot_detector.youtube_service import fetch_youtube_comments, extract_video_id
from bot_detector.mock_data import get_mock_comments, generate_injection, PRESET_VIDEOS

__all__ = [
    "score_comment_batch",
    "score_single_comment",
    "detect_campaign_clusters",
    "fetch_youtube_comments",
    "extract_video_id",
    "get_mock_comments",
    "generate_injection",
    "PRESET_VIDEOS"
]
