"""
TikTok Trends Intelligence Service — Real-time viral product discovery.
Scrapes TikTok's public search/general API endpoint for trending video data
related to product keywords. Returns engagement metrics, hashtags, creator info.
"""

import json
import logging
import random
import re
import time
from typing import Optional
from datetime import datetime

import httpx

logger = logging.getLogger("tiktok_trends")

CACHE_PATH = None
CACHE_TTL = 600
REQUEST_TIMEOUT = 12.0
MAX_VIDEOS = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
}

TT_COUNTRIES = {
    "usa": "US", "canada": "CA", "uk": "GB", "germany": "DE",
    "france": "FR", "saudi_arabia": "SA", "uae": "AE", "algeria": "DZ",
}


class TikTokTrendsService:
    def __init__(self):
        self._client = httpx.Client(follow_redirects=True, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        self._last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self._last_request
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._last_request = time.time()

    def search_trends(self, query: str, region: str = "usa", max_videos: int = MAX_VIDEOS) -> list:
        """Search TikTok for trending videos related to a product keyword."""
        region_code = TT_COUNTRIES.get(region, "US")
        results = []

        # Try TikTok API endpoint (used by web client)
        api_results = self._try_api_search(query, region_code, max_videos)
        if api_results:
            results.extend(api_results)

        # Try scraping hashtag page as supplementary
        if len(results) < max_videos:
            hashtag_results = self._try_hashtag_search(query, region_code)
            if hashtag_results:
                existing_urls = {v.get("video_url", "") for v in results}
                for v in hashtag_results:
                    if v.get("video_url", "") not in existing_urls and len(results) < max_videos:
                        results.append(v)

        return results[:max_videos]

    def _try_api_search(self, query: str, region_code: str, max_videos: int) -> list:
        """Use TikTok's internal search/general API endpoint."""
        self._rate_limit()
        try:
            url = "https://www.tiktok.com/api/search/general/"
            params = {
                "keyword": query,
                "search_source": "normal_search",
                "count": min(max_videos * 2, 30),
                "offset": 0,
                "device_platform": "web",
                "aid": "1988",
            }
            resp = self._client.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                return []

            data = resp.json()
            videos = []
            for item in data.get("data", []) or []:
                if not isinstance(item, dict):
                    continue
                video = self._parse_api_item(item)
                if video:
                    videos.append(video)
            return videos
        except Exception as e:
            logger.debug(f"TikTok API search failed: {e}")
            return []

    def _parse_api_item(self, item: dict) -> Optional[dict]:
        """Parse a single TikTok API response item into normalized format."""
        try:
            author = item.get("author", {}) or {}
            stats = item.get("stats", {}) or {}
            video = item.get("video", {}) or {}
            music = item.get("music", {}) or {}
            hashtags_raw = item.get("challenges", []) or []

            views = int(stats.get("playCount", 0) or 0)
            likes = int(stats.get("diggCount", 0) or 0)
            comments = int(stats.get("commentCount", 0) or 0)
            shares = int(stats.get("shareCount", 0) or 0)

            if views < 100:
                return None

            hashtags = []
            for h in hashtags_raw:
                name = h.get("title", "") if isinstance(h, dict) else str(h)
                if name:
                    hashtags.append(name)

            return {
                "platform": "tiktok",
                "video_title": item.get("desc", "")[:300],
                "video_url": f"https://www.tiktok.com/@{author.get('uniqueId', 'user')}/video/{item.get('id', '')}",
                "view_count": views,
                "like_count": likes,
                "comment_count": comments,
                "share_count": shares,
                "engagement_rate": round((likes + comments + shares) / max(views, 1) * 100, 2),
                "trending_hashtags": hashtags[:10],
                "creator_name": author.get("uniqueId", ""),
                "creator_followers": int(author.get("followerCount", 0) or 0),
                "region": "",
                "published_at": item.get("createTime", 0),
                "music_title": music.get("title", "") if isinstance(music, dict) else "",
            }
        except Exception:
            return None

    def _try_hashtag_search(self, query: str, region_code: str) -> list:
        """Try scraping the TikTok tag page for a query."""
        self._rate_limit()
        try:
            tag = query.replace(" ", "").lower()[:30]
            url = f"https://www.tiktok.com/tag/{tag}"
            resp = self._client.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                return []
            return []
        except Exception:
            return []


# Singleton
tiktok_trends = TikTokTrendsService()


def search_tiktok_trends(query: str, region: str = "usa", max_videos: int = 10) -> dict:
    """Search TikTok for trending content related to a product keyword."""
    videos = tiktok_trends.search_trends(query, region, max_videos)
    avg_engagement = 0
    total_views = 0
    all_hashtags = {}

    for v in videos:
        total_views += v.get("view_count", 0)
        avg_engagement += v.get("engagement_rate", 0)
        for h in v.get("trending_hashtags", []):
            all_hashtags[h] = all_hashtags.get(h, 0) + 1

    avg_engagement = round(avg_engagement / max(len(videos), 1), 2)
    top_hashtags = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)[:15]

    return {
        "query": query,
        "region": region,
        "total_videos": len(videos),
        "total_views": total_views,
        "avg_engagement_rate": avg_engagement,
        "viral_velocity": _calc_viral_velocity(videos),
        "top_hashtags": [{"tag": h, "count": c} for h, c in top_hashtags],
        "videos": videos,
        "trending": len(videos) > 0 and avg_engagement > 5.0,
    }


def _calc_viral_velocity(videos: list) -> float:
    """Calculate viral momentum based on engagement/view ratio and recency."""
    if not videos:
        return 0.0
    scores = []
    for v in videos:
        views = v.get("view_count", 0)
        likes = v.get("like_count", 0)
        comments = v.get("comment_count", 0)
        shares = v.get("share_count", 0)
        if views > 0:
            virality = (likes * 1.0 + comments * 2.0 + shares * 3.0) / views * 100
            scores.append(min(virality, 100))
    return round(sum(scores) / len(scores), 1) if scores else 0.0
