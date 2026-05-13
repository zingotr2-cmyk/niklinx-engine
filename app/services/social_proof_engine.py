"""
Social Proof Intelligence Engine.
Combines TikTok trends, Facebook ad activity, and marketplace signals
into a unified Social Proof Score (0–100) for each product.

Scoring factors:
  - TikTok engagement (views, likes, comments, shares, virality)
  - Facebook ad activity (active ads, intensity, advertiser diversity)
  - Marketplace signals (order velocity, review density, rating)
  - Trend acceleration (viral velocity, hashtag momentum)
"""

import logging
from typing import Optional

logger = logging.getLogger("social_proof")


class SocialProofEngine:
    def __init__(self):
        pass

    def score(
        self,
        tiktok_data: Optional[dict] = None,
        facebook_data: Optional[dict] = None,
        marketplace_product: Optional[dict] = None,
    ) -> dict:
        """
        Compute a comprehensive Social Proof Score (0–100) for a product.
        Returns detailed breakdown of all scoring factors.
        """
        factors = {}

        # Factor 1: TikTok Engagement (0–35 points)
        tiktok_score, tiktok_detail = self._score_tiktok(tiktok_data)
        factors["tiktok_engagement"] = tiktok_detail

        # Factor 2: Facebook Ad Activity (0–25 points)
        facebook_score, facebook_detail = self._score_facebook(facebook_data)
        factors["facebook_ads"] = facebook_detail

        # Factor 3: Marketplace Signals (0–25 points)
        marketplace_score, marketplace_detail = self._score_marketplace(marketplace_product)
        factors["marketplace_signals"] = marketplace_detail

        # Factor 4: Trend Acceleration (0–15 points)
        trend_score, trend_detail = self._score_trend_acceleration(tiktok_data)
        factors["trend_acceleration"] = trend_detail

        total = min(
            tiktok_score + facebook_score + marketplace_score + trend_score,
            100,
        )

        # Classification
        if total >= 85:
            classification = "Explosive Viral"
            label = "Viral Product"
            icon = "🔥"
        elif total >= 70:
            classification = "Strong Scaling"
            label = "High Opportunity"
            icon = "📈"
        elif total >= 50:
            classification = "Moderate Trend"
            label = "Trending"
            icon = "⚡"
        elif total >= 30:
            classification = "Emerging"
            label = "Early Signal"
            icon = "🌱"
        else:
            classification = "Low Momentum"
            label = "Normal"
            icon = "💤"

        return {
            "social_proof_score": round(total, 1),
            "classification": classification,
            "label": label,
            "icon": icon,
            "factors": factors,
            "viral_confidence": self._confidence_level(total),
        }

    def _score_tiktok(self, data: Optional[dict]) -> tuple:
        """Score TikTok engagement data (0–35)."""
        if not data or not data.get("videos"):
            return 0, {"score": 0, "total_videos": 0, "total_views": 0, "avg_engagement": 0, "status": "no_data"}

        videos = data.get("videos", [])
        total_videos = len(videos)
        total_views = data.get("total_views", 0)
        avg_engagement = data.get("avg_engagement_rate", 0)
        viral_velocity = data.get("viral_velocity", 0)

        score = 0.0

        # Video count (max 10 pts)
        score += min(total_videos * 2, 10)

        # View magnitude (max 10 pts)
        if total_views > 1000000:
            score += 10
        elif total_views > 500000:
            score += 8
        elif total_views > 100000:
            score += 6
        elif total_views > 10000:
            score += 3
        elif total_views > 1000:
            score += 1

        # Engagement rate (max 10 pts)
        score += min(avg_engagement, 10)

        # Viral velocity (max 5 pts)
        score += min(viral_velocity / 20, 5)

        return round(score, 1), {
            "score": round(score, 1),
            "total_videos": total_videos,
            "total_views": total_views,
            "avg_engagement": avg_engagement,
            "viral_velocity": viral_velocity,
            "status": "active" if total_videos > 0 else "no_data",
        }

    def _score_facebook(self, data: Optional[dict]) -> tuple:
        """Score Facebook Ad Library data (0–25)."""
        if not data or not data.get("ads"):
            return 0, {"score": 0, "total_ads": 0, "ad_intensity": "none", "status": "no_data"}

        ads = data.get("ads", [])
        total_ads = len(ads)
        intensity = data.get("ad_intensity", "low")
        advertiser_count = data.get("advertiser_count", 0)

        score = 0.0

        # Ad count (max 10 pts)
        score += min(total_ads * 1.5, 10)

        # Ad intensity (max 8 pts)
        intensity_map = {"high": 8, "medium": 5, "low": 2}
        score += intensity_map.get(intensity, 0)

        # Advertiser diversity (max 7 pts)
        score += min(advertiser_count * 2, 7)

        return round(score, 1), {
            "score": round(score, 1),
            "total_ads": total_ads,
            "ad_intensity": intensity,
            "advertiser_count": advertiser_count,
            "status": "active" if total_ads > 0 else "no_data",
        }

    def _score_marketplace(self, product: Optional[dict]) -> tuple:
        """Score marketplace signals (0–25)."""
        if not product:
            return 0, {"score": 0, "rating": 0, "orders": 0, "status": "no_data"}

        rating = float(product.get("rating", 0) or 0)
        orders = int(product.get("orders", 0) or product.get("reviews", 0) or 0)
        price = float(product.get("price", 0) or 0)

        score = 0.0

        # Rating quality (max 10 pts)
        score += min(rating * 2, 10)

        # Order volume (max 10 pts)
        if orders > 10000:
            score += 10
        elif orders > 5000:
            score += 8
        elif orders > 1000:
            score += 6
        elif orders > 500:
            score += 4
        elif orders > 100:
            score += 2
        elif orders > 10:
            score += 1

        # Price confidence (higher = more likely real product) (max 5 pts)
        if 10 <= price <= 200:
            score += 5
        elif 5 <= price <= 500:
            score += 3
        else:
            score += 1

        return round(score, 1), {
            "score": round(score, 1),
            "rating": rating,
            "orders": orders,
            "price": price,
            "status": "active" if orders > 0 else "low_data",
        }

    def _score_trend_acceleration(self, tiktok_data: Optional[dict]) -> tuple:
        """Score trend acceleration from TikTok data (0–15)."""
        if not tiktok_data:
            return 0, {"score": 0, "velocity": 0, "status": "no_data"}

        viral_velocity = tiktok_data.get("viral_velocity", 0)
        top_hashtags = tiktok_data.get("top_hashtags", [])
        total_videos = tiktok_data.get("total_videos", 0)

        score = 0.0

        # Viral velocity (max 8 pts)
        score += min(viral_velocity / 12.5, 8)

        # Hashtag diversity (max 4 pts)
        score += min(len(top_hashtags) * 0.4, 4)

        # Video momentum (max 3 pts)
        if total_videos >= 5:
            score += 3
        elif total_videos >= 3:
            score += 2
        elif total_videos >= 1:
            score += 1

        return round(score, 1), {
            "score": round(score, 1),
            "velocity": viral_velocity,
            "hashtag_count": len(top_hashtags),
            "video_count": total_videos,
            "status": "accelerating" if viral_velocity > 30 else "stable",
        }

    def _confidence_level(self, score: float) -> str:
        if score >= 70:
            return "high"
        elif score >= 40:
            return "medium"
        return "low"


# Singleton
social_proof = SocialProofEngine()


def compute_social_proof(
    tiktok_data: Optional[dict] = None,
    facebook_data: Optional[dict] = None,
    product: Optional[dict] = None,
) -> dict:
    """Compute Social Proof Score for a product given all signal sources."""
    return social_proof.score(tiktok_data, facebook_data, product)
