"""Ad Creator Module — Generate ad creative packages."""

import random


def create_ads(ad_angles: list = None) -> list:
    """Package ad scripts into creatives."""
    if ad_angles is None:
        ad_angles = [
            {"title": "Skeptic Surrender"},
            {"title": "Aging Skin Rescue"},
            {"title": "Makeup Freedom"},
        ]

    return [
        {
            "angle": a["title"],
            "avatar_ready": {
                "avatar": "Denise",
                "settings": {"speed": 1.15, "similarity": 0.9},
                "total_characters": 250,
            },
            "compilation": {
                "total_duration": 90,
                "clips": [
                    {"source": "tiktok_compilation", "duration": 15},
                    {"source": "user_generated", "duration": 10},
                    {"source": "review_screenshot", "duration": 8},
                    {"source": "product_demo", "duration": 12},
                ],
            },
            "facebook_package": {
                "objective": "CONVERSIONS",
                "format": "VIDEO",
                "call_to_action": "Shop Now",
                "estimated_quality_score": random.randint(7, 10),
            },
        }
        for a in ad_angles
    ]


def generate_avatar_script(script: str, avatar: str = "Denise") -> dict:
    """Prepare script for AI avatar generation."""
    lines = [l.strip() for l in script.replace(". ", ".\n").replace("? ", "?\n").split("\n") if l.strip()]
    return {
        "avatar": avatar,
        "total_characters": len(script),
        "script_lines": lines[:20] if lines else ["Sample line"],
        "settings": {"speed": 1.15, "similarity": 0.9},
    }
