"""Campaign Manager Module — Setup and launch ad campaigns."""

import random

DEFAULT_INTERESTS = [
    "Sephora", "MAC Cosmetics", "L'Oreal", "Maybelline",
    "Benefit Cosmetics", "Skincare", "Anti-aging",
    "Beauty influencers", "Makeup tutorials", "Organic beauty",
]


def setup_campaign(campaign_name: str, daily_budget: float = 20, interests: list = None, ads: list = None) -> dict:
    """Configure a Facebook Ads campaign."""
    interests = interests or DEFAULT_INTERESTS[:5]
    ads = ads or [{"creative_name": "Ad 1"}, {"creative_name": "Ad 2"}, {"creative_name": "Ad 3"}]
    total_budget = daily_budget * len(interests)

    est_purchases = int(total_budget * 10 * 0.02)

    return {
        "campaign_name": campaign_name,
        "objective": "CONVERSIONS",
        "budget_type": "ADSET_BUDGET",
        "status": "DRAFT",
        "total_daily_budget": total_budget,
        "adsets": [
            {
                "name": f"{i} - ${daily_budget}/day",
                "daily_budget": daily_budget,
                "interest_targeting": i,
                "age_range": "25-55",
                "gender": "female",
                "ads": ads,
            }
            for i in interests
        ],
        "estimated_reach": f"{random.randint(10000, 50000):,} - {random.randint(50000, 150000):,}",
        "estimated_daily_results": {
            "clicks": random.randint(50, 200),
            "purchases": est_purchases,
            "revenue": round(est_purchases * 29.99, 2),
            "roas": round(est_purchases * 29.99 / total_budget, 2) if total_budget > 0 else 0,
        },
    }


def launch_campaign(campaign: dict) -> dict:
    """Execute campaign launch."""
    return {
        "status": "ACTIVE",
        "launched_at": "2024-06-01T00:00:00Z",
        "note": "Campaign is live. Monitor performance in 24-48 hours.",
    }


def get_forecast(daily_budget: float = 20, product_price: float = 29.99, cvr: float = 0.02) -> dict:
    """Estimate campaign performance."""
    clicks = int(daily_budget * 10)
    purchases = int(clicks * cvr)
    revenue = round(purchases * product_price, 2)
    return {
        "daily_budget": daily_budget,
        "estimated_clicks": clicks,
        "estimated_purchases": purchases,
        "estimated_revenue": revenue,
        "estimated_roas": round(revenue / daily_budget, 2) if daily_budget > 0 else 0,
        "breakdown": {
            "cpc": round(daily_budget / clicks, 4) if clicks > 0 else 0,
            "cpa": round(daily_budget / purchases, 2) if purchases > 0 else 0,
        },
    }


def ab_test_plan() -> dict:
    """Get A/B testing recommendation."""
    return {
        "test_name": "Interest Targeting x Ad Creative",
        "variables": ["Interest (10 options)", "Ad Creative (3 angles)"],
        "duration_days": 7,
        "min_daily_budget": 10,
        "success_metric": "CPA (Cost Per Acquisition)",
        "decision_criteria": "Scale interests with CPA < $15 and ROAS > 2.0",
    }
