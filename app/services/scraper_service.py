"""
DRO Scraper Service — Real competitor store analysis via HTTP.
"""

import re
import httpx
from bs4 import BeautifulSoup


class ScraperService:
    """Real-time competitor store analyzer."""

    NICHE_KEYWORDS = {
        "Beauty & Makeup": ["makeup", "cosmetic", "beauty", "foundation", "skincare", "lipstick"],
        "Health & Wellness": ["health", "wellness", "supplement", "vitamin", "organic"],
        "Weight Loss": ["weight", "fat", "slim", "burn", "diet", "calorie"],
        "Skincare": ["skin", "moisturizer", "serum", "anti-aging", "wrinkle", "pore"],
        "Fashion": ["fashion", "wear", "clothing", "dress", "shirt", "style"],
        "Fitness": ["fitness", "workout", "gym", "exercise", "training"],
        "Pet Supplies": ["pet", "dog", "cat", "animal", "veterinary"],
        "Electronics": ["electronic", "gadget", "device", "tech", "digital"],
    }

    SECTION_PATTERNS = [
        "hero", "testimonial", "feature", "benefit", "how it works",
        "before", "after", "ingredient", "review", "faq",
        "guarantee", "shipping", "contact", "about", "footer",
    ]

    def __init__(self):
        self._client = httpx.Client(
            follow_redirects=True,
            timeout=15.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            },
        )

    def analyze(self, url: str) -> dict:
        """Analyze a competitor store from its URL."""
        try:
            resp = self._client.get(url)
            resp.raise_for_status()
            html = resp.text
            soup = BeautifulSoup(html, "lxml")

            return {
                "url": url,
                "title": self._extract_title(soup),
                "description": self._extract_meta(soup, "description"),
                "main_heading": self._extract_h1(soup),
                "og_image": self._extract_meta(soup, "og:image"),
                "estimated_niche": self._detect_niche(html),
                "product_count": self._count_products(soup),
                "has_cart": self._has_feature(html, ["cart", "add to cart", "shopify", "checkout"]),
                "has_reviews": self._has_feature(html, ["review", "testimonial"]),
                "has_faq": self._has_feature(html, ["faq", "frequently asked"]),
                "has_before_after": html.lower().count("before") > 2 and html.lower().count("after") > 2,
                "success_architecture": self._extract_sections(html),
                "total_length_kb": round(len(html) / 1024, 1),
                "status": 200,
            }
        except httpx.HTTPStatusError as e:
            return {"url": url, "error": f"HTTP {e.response.status_code}", "status": e.response.status_code}
        except Exception as e:
            return {"url": url, "error": str(e), "status": 0}

    def _extract_title(self, soup: BeautifulSoup) -> str:
        return soup.title.string.strip() if soup.title else ""

    def _extract_meta(self, soup: BeautifulSoup, name: str) -> str:
        tag = soup.find("meta", property=name) or soup.find("meta", attrs={"name": name})
        return tag.get("content", "") if tag else ""

    def _extract_h1(self, soup: BeautifulSoup) -> str:
        h1 = soup.find("h1")
        return h1.get_text(strip=True) if h1 else ""

    def _detect_niche(self, html: str) -> str:
        h = html.lower()
        best = ("General", 0)
        for niche, keywords in self.NICHE_KEYWORDS.items():
            count = sum(h.count(kw) for kw in keywords)
            if count > best[1]:
                best = (niche, count)
        return best[0]

    def _count_products(self, soup: BeautifulSoup) -> int:
        product_classes = soup.find_all(class_=re.compile(r"product|item", re.I))
        return max(len(product_classes), 1) if product_classes else 1

    def _has_feature(self, html: str, keywords: list) -> bool:
        h = html.lower()
        return any(kw in h for kw in keywords)

    def _extract_sections(self, html: str) -> list:
        h = html.lower()
        return [s.capitalize() for s in self.SECTION_PATTERNS if s in h]


scraper = ScraperService()
