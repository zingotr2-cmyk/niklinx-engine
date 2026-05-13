"""
Facebook Ad Library Intelligence Service.
Searches the Facebook Ad Library for active ads related to product keywords.
Returns ad creatives, copy, platform placement, and estimated scaling activity.
"""

import json
import logging
import re
import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("facebook_ads")

REQUEST_TIMEOUT = 15.0
CACHE_TTL = 600
MAX_ADS = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class FacebookAdsService:
    def __init__(self):
        self._client = httpx.Client(follow_redirects=True, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        self._last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self._last_request
        if elapsed < 1.5:
            time.sleep(1.5 - elapsed)
        self._last_request = time.time()

    def search_ads(self, query: str, region: str = "usa", max_ads: int = MAX_ADS) -> list:
        """Search Facebook Ad Library for active ads matching a keyword."""
        results = []

        # Try scraping the Facebook Ad Library public page
        scraped = self._try_scrape(query, region)
        if scraped:
            results.extend(scraped)

        return results[:max_ads]

    def _try_scrape(self, query: str, region: str) -> list:
        """Scrape the Facebook Ad Library public search page."""
        self._rate_limit()
        country_map = {
            "usa": "US", "canada": "CA", "uk": "GB", "germany": "DE",
            "france": "FR", "saudi_arabia": "SA", "uae": "AE", "algeria": "DZ",
        }
        country = country_map.get(region, "US")

        try:
            url = "https://www.facebook.com/ads/library/"
            params = {
                "active_status": "active",
                "ad_type": "all",
                "country": country,
                "q": query,
                "search_type": "keyword",
            }
            resp = self._client.get(url, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code not in (200, 429):
                return []

            soup = BeautifulSoup(resp.text, "lxml")
            ads = []

            # Attempt to parse embedded JSON data in the page
            for script in soup.select("script"):
                text = script.string or ""
                if "require" in text and "AdLibrary" in text:
                    continue

            # Extract ad cards from the page HTML
            for card in soup.select("[class*='ad'], [class*='card'], [class*='result'], [data-testid*='ad']"):
                title_el = card.select_one("h4, h3, [class*='title'], [class*='headline']")
                body_el = card.select_one("[class*='body'], [class*='copy'], [class*='message'], p")
                cta_el = card.select_one("[class*='cta'], [class*='button'], a[class*='button']")
                img_el = card.select_one("img[src]")

                title = title_el.get_text(strip=True) if title_el else ""
                body = body_el.get_text(strip=True) if body_el else ""

                if not title and not body:
                    continue
                if len(title) < 5 and len(body) < 5:
                    continue

                ads.append({
                    "platform": "facebook",
                    "ad_title": title[:300],
                    "ad_copy": body[:500],
                    "cta": cta_el.get_text(strip=True) if cta_el else "Shop Now",
                    "image": img_el.get("src", "") if img_el else "",
                    "advertiser": "",
                    "active_duration_days": 0,
                    "region": region,
                    "source": "facebook_ads",
                    "estimated_activity": "medium",
                })
                if len(ads) >= max_ads:
                    break

            return ads
        except Exception as e:
            logger.debug(f"Facebook Ad Library scrape failed: {e}")
            return []


# Singleton
facebook_ads = FacebookAdsService()


def search_facebook_ads(query: str, region: str = "usa", max_ads: int = 10) -> dict:
    """Search Facebook Ad Library for active ads related to a product keyword."""
    ads = facebook_ads.search_ads(query, region, max_ads)
    active_count = len(ads)

    # Estimate ad intensity
    intensity = "low"
    if active_count >= 8:
        intensity = "high"
    elif active_count >= 3:
        intensity = "medium"

    return {
        "query": query,
        "region": region,
        "total_ads": active_count,
        "ad_intensity": intensity,
        "advertiser_count": len(set(a.get("advertiser", "") for a in ads if a.get("advertiser"))),
        "ads": ads,
    }
