"""
Global Live Search — real-time product discovery from AliExpress, Amazon, and Google Shopping.
Falls back gracefully when providers fail, caches results for performance.
"""

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup

CACHE_PATH = Path("data/live_cache.json")
CACHE_TTL = 600  # 10 minutes
REQUEST_TIMEOUT = 15.0
MAX_RESULTS_PER_PROVIDER = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


class LiveSearchProvider:
    """Base provider with retry logic."""

    def __init__(self, name: str):
        self.name = name
        self._client = httpx.Client(follow_redirects=True, timeout=REQUEST_TIMEOUT, headers=HEADERS)

    def fetch(self, url: str, max_retries: int = 2) -> Optional[str]:
        for attempt in range(max_retries + 1):
            try:
                resp = self._client.get(url)
                if resp.status_code == 200:
                    return resp.text
                time.sleep(1 * (attempt + 1))
            except Exception:
                time.sleep(1 * (attempt + 1))
        return None

    def parse(self, html: str) -> list:
        raise NotImplementedError

    def search(self, query: str) -> list:
        url = self.build_url(query)
        html = self.fetch(url)
        if not html:
            return []
        try:
            return self.parse(html)
        except Exception:
            return []

    def build_url(self, query: str) -> str:
        raise NotImplementedError


class AliExpressProvider(LiveSearchProvider):
    def __init__(self):
        super().__init__("aliexpress")

    def build_url(self, query: str) -> str:
        q = query.replace(" ", "+")
        return f"https://www.aliexpress.com/wholesale?SearchText={q}"

    def parse(self, html: str) -> list:
        products = []
        soup = BeautifulSoup(html, "lxml")
        for item in soup.select("[class*='product'], [class*='item'], [class*='card'], li"):
            name_el = item.select_one("[class*='title'] a, [class*='name'] a, h3 a, a[class*='title']")
            price_el = item.select_one("[class*='price'], [class*='current']")
            img_el = item.select_one("img[src*='alicdn']")
            rating_el = item.select_one("[class*='rating'], [class*='star']")
            reviews_el = item.select_one("[class*='review'], [class*='sold']")
            url_el = name_el or item.select_one("a[href*='aliexpress']")

            if not name_el:
                continue

            name = name_el.get_text(strip=True)
            if not name or len(name) < 5:
                continue

            price = self._parse_price(price_el)
            image = img_el.get("src", "") if img_el else ""
            rating = self._parse_rating(rating_el)
            reviews = self._parse_reviews(reviews_el)
            product_url = url_el.get("href", "") if url_el else ""

            if not image.startswith("http"):
                image = f"https:{image}" if image.startswith("//") else ""

            products.append({
                "name": name[:200],
                "price": price or 19.99,
                "sale_price": price,
                "rating": rating or 4.0,
                "reviews": reviews or 0,
                "image": image or "https://placehold.co/400x400/FF6B6B/white?text=Product",
                "source": "aliexpress",
                "source_url": f"https://www.aliexpress.com{product_url}" if product_url.startswith("/") else product_url,
                "live": True,
            })
            if len(products) >= MAX_RESULTS_PER_PROVIDER:
                break
        return products

    def _parse_price(self, el) -> Optional[float]:
        if not el:
            return None
        text = el.get_text(strip=True)
        match = re.search(r"[\d,.]+", text.replace(",", ""))
        return float(match.group().replace(",", "")) if match else None

    def _parse_rating(self, el) -> Optional[float]:
        if not el:
            return None
        text = el.get_text(strip=True)
        match = re.search(r"[\d.]+", text)
        return float(match.group()) if match else None

    def _parse_reviews(self, el) -> Optional[int]:
        if not el:
            return None
        text = el.get_text(strip=True)
        match = re.search(r"[\d,.kKmMbB]+", text)
        if not match:
            return None
        val = match.group().lower()
        multiplier = 1
        if "k" in val:
            multiplier = 1000
        elif "m" in val:
            multiplier = 1000000
        elif "b" in val:
            multiplier = 1000000000
        num = float(re.search(r"[\d.]+", val).group())
        return int(num * multiplier)


class AmazonProvider(LiveSearchProvider):
    def __init__(self):
        super().__init__("amazon")

    def build_url(self, query: str) -> str:
        q = query.replace(" ", "+")
        return f"https://www.amazon.com/s?k={q}&ref=nb_sb_noss"

    def parse(self, html: str) -> list:
        products = []
        soup = BeautifulSoup(html, "lxml")
        for item in soup.select("[data-component-type='s-search-result'], .s-result-item"):
            name_el = item.select_one("h2 a span, h2 span, [class*='title']")
            price_whole = item.select_one(".a-price-whole")
            price_frac = item.select_one(".a-price-fraction")
            img_el = item.select_one("img.s-image")
            rating_el = item.select_one("[class*='a-star-small'] span, i[class*='a-icon-star'] span")
            reviews_el = item.select_one("[class*='a-size-small'] span, [class*='a-link-normal']")
            url_el = item.select_one("h2 a")

            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 5:
                continue

            price = None
            if price_whole:
                try:
                    price = float(price_whole.get_text(strip=True).replace(",", ""))
                    if price_frac:
                        price += float("0." + price_frac.get_text(strip=True))
                except ValueError:
                    pass

            rating = None
            if rating_el:
                try:
                    rating = float(re.search(r"[\d.]+", rating_el.get_text(strip=True)).group())
                except (AttributeError, ValueError):
                    pass

            reviews = None
            if reviews_el:
                try:
                    reviews = int(re.search(r"[\d,]+", reviews_el.get_text(strip=True)).group().replace(",", ""))
                except (AttributeError, ValueError):
                    pass

            image = img_el.get("src", "") if img_el else ""
            product_url = url_el.get("href", "") if url_el else ""

            products.append({
                "name": name[:200],
                "price": price or 24.99,
                "sale_price": price,
                "rating": rating or 4.0,
                "reviews": reviews or 0,
                "image": image,
                "source": "amazon",
                "source_url": f"https://www.amazon.com{product_url}" if product_url.startswith("/") else product_url,
                "live": True,
            })
            if len(products) >= MAX_RESULTS_PER_PROVIDER:
                break
        return products


class GoogleShoppingProvider(LiveSearchProvider):
    def __init__(self):
        super().__init__("google_shopping")

    def build_url(self, query: str) -> str:
        q = query.replace(" ", "+")
        return f"https://www.google.com/search?tbm=shop&q={q}&hl=en"

    def parse(self, html: str) -> list:
        products = []
        soup = BeautifulSoup(html, "lxml")
        for item in soup.select("[class*='sh-dgr__content'], [class*='sh-dlr__list-result'], .sh-pr__product"):
            name_el = item.select_one("h3, [class*='title'], a[class*='title']")
            price_el = item.select_one("[class*='price'], [class*='a-price'], span[aria-label*='Price']")
            img_el = item.select_one("img[src*='data:image']")
            rating_el = item.select_one("[class*='rating'], [class*='stars']")
            url_el = item.select_one("a[href]")

            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 5:
                continue

            price = None
            if price_el:
                text = price_el.get_text(strip=True)
                match = re.search(r"[\d,.]+", text.replace(",", ""))
                if match:
                    try:
                        price = float(match.group().replace(",", ""))
                    except ValueError:
                        pass

            rating = None
            if rating_el:
                try:
                    rating = float(re.search(r"[\d.]+", rating_el.get_text(strip=True)).group())
                except (AttributeError, ValueError):
                    pass

            image = img_el.get("src", "") if img_el else ""
            product_url = ""
            if url_el:
                href = url_el.get("href", "")
                if href.startswith("/"):
                    product_url = f"https://www.google.com{href}"
                elif href.startswith("http"):
                    product_url = href

            products.append({
                "name": name[:200],
                "price": price or 24.99,
                "sale_price": price,
                "rating": rating or 4.0,
                "reviews": 0,
                "image": image if image.startswith("http") else "",
                "source": "google_shopping",
                "source_url": product_url,
                "live": True,
            })
            if len(products) >= MAX_RESULTS_PER_PROVIDER:
                break
        return products


# ==================== Cache Layer ====================

def _cache_key(query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest()


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(cache: dict):
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def get_cached(query: str) -> Optional[list]:
    cache = _load_cache()
    entry = cache.get(_cache_key(query))
    if entry and time.time() - entry.get("ts", 0) < CACHE_TTL:
        return entry.get("results")
    return None


def set_cached(query: str, results: list):
    cache = _load_cache()
    cache[_cache_key(query)] = {"ts": time.time(), "results": results}
    # Keep cache under 500 entries
    if len(cache) > 500:
        sorted_keys = sorted(cache.keys(), key=lambda k: cache[k]["ts"])
        for k in sorted_keys[:100]:
            del cache[k]
    _save_cache(cache)


# ==================== Provider Registry ====================

PROVIDERS = [
    AliExpressProvider(),
    AmazonProvider(),
    GoogleShoppingProvider(),
]

# ==================== Main Search ====================

def live_search(query: str, max_results: int = 30) -> list:
    """Search across all live providers, merge and deduplicate results."""
    cached = get_cached(query)
    if cached is not None:
        return cached[:max_results]

    all_products = []
    seen_names = set()

    for provider in PROVIDERS:
        try:
            results = provider.search(query)
            for p in results:
                key = p["name"].lower().strip()[:60]
                if key not in seen_names:
                    seen_names.add(key)
                    all_products.append(p)
        except Exception:
            continue

    # Deduplicate by normalized name
    unique = {}
    for p in all_products:
        key = p["name"].lower().strip()[:60]
        if key not in unique or p["rating"] > unique[key]["rating"]:
            unique[key] = p

    merged = list(unique.values())

    # Auto-score products
    for p in merged:
        p["winning_score"] = _auto_score(p)
        p["profit_margin"] = _estimate_margin(p)

    merged.sort(key=lambda x: x.get("winning_score", 0), reverse=True)

    if merged:
        set_cached(query, merged)

    return merged[:max_results]


def _auto_score(p: dict) -> float:
    """Estimate a winning score for a product without AI API keys."""
    score = 0.0
    score += min((p.get("rating", 0) / 5) * 30, 30)
    score += min(max(0, 100 - (p.get("price", 50) or 50)) / 100 * 20, 20)
    score += min((p.get("reviews", 0) or 0) / 5000 * 20, 20)
    if p.get("source") == "aliexpress":
        score += 15  # Usually cheaper = better margin for dropshipping
    elif p.get("source") == "amazon":
        score += 5
    score += len(p.get("name", "")) > 30 and 5 or 0
    return round(min(score, 100), 1)


def _estimate_margin(p: dict) -> float:
    """Estimate profit margin for a product."""
    price = p.get("price", 0) or 0
    if price <= 0:
        return 0
    est_supplier_ratio = {
        "aliexpress": 0.25,
        "amazon": 0.5,
        "google_shopping": 0.35,
    }
    ratio = est_supplier_ratio.get(p.get("source", ""), 0.3)
    margin = (1 - ratio) * 100
    return round(min(margin, 92), 1)
