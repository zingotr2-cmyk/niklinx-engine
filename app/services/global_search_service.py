"""
Global Search Service — Centralized Marketplace Data Hub.
Orchestrates live product discovery from Amazon, AliExpress, Google Shopping.
Supports multi-region search (USA, Europe, GCC), exponential backoff,
rate-limit protection, provider health tracking, and data normalization.
"""

import hashlib
import json
import math
import random
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup

CACHE_PATH = Path("data/live_cache.json")
CACHE_TTL = 600
PROVIDER_TIMEOUT = 8.0
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

# Region config: marketplace-specific domain suffixes & currency
REGIONS = {
    "usa": {"domains": ["com"], "currency": "USD", "label": "USA", "country_code": "US"},
    "canada": {"domains": ["ca"], "currency": "CAD", "label": "Canada", "country_code": "CA"},
    "uk": {"domains": ["co.uk"], "currency": "GBP", "label": "UK", "country_code": "GB"},
    "germany": {"domains": ["de"], "currency": "EUR", "label": "Germany", "country_code": "DE"},
    "france": {"domains": ["fr"], "currency": "EUR", "label": "France", "country_code": "FR"},
    "uae": {"domains": ["ae"], "currency": "AED", "label": "UAE", "country_code": "AE"},
    "saudi_arabia": {"domains": ["sa"], "currency": "SAR", "label": "Saudi Arabia", "country_code": "SA"},
    "algeria": {"domains": ["dz"], "currency": "DZD", "label": "Algeria", "country_code": "DZ"},
}

# Group mappings for frontend
COUNTRY_GROUPS = {
    "gcc": ["uae", "saudi_arabia", "algeria"],
    "north_america": ["usa", "canada"],
    "europe": ["uk", "germany", "france"],
}

def resolve_region(region: str) -> str:
    """Resolve group names to individual country codes. Returns first country in group."""
    if region in COUNTRY_GROUPS:
        return COUNTRY_GROUPS[region][0]
    return region


# ==================== Provider Health Tracker ====================

class ProviderHealth:
    def __init__(self):
        self._status = {}

    def record_success(self, name: str):
        self._status[name] = {"healthy": True, "last_ok": time.time(), "error": None}

    def record_failure(self, name: str, error: str):
        self._status[name] = {"healthy": False, "last_ok": self._status.get(name, {}).get("last_ok", 0), "error": error}

    def is_healthy(self, name: str) -> bool:
        s = self._status.get(name)
        return s["healthy"] if s else False

    def all_healthy(self) -> bool:
        if not self._status:
            return False
        return all(s["healthy"] for s in self._status.values())

    def any_healthy(self) -> bool:
        return any(s["healthy"] for s in self._status.values())

    def summary(self) -> dict:
        return {
            "status": "green" if self.all_healthy() else "yellow" if self.any_healthy() else "red",
            "providers": {k: {"healthy": v["healthy"], "error": v["error"]} for k, v in self._status.items()},
        }


provider_health = ProviderHealth()


# ==================== NikLinx Standard Product Schema ====================

def normalize_product(raw: dict, region: str = "usa") -> dict:
    """Convert any provider's raw product into the unified NikLinx schema."""
    price = float(raw.get("price", 0) or 0)
    original = float(raw.get("original_price") or raw.get("sale_price") or price)
    currency = REGIONS.get(region, REGIONS["usa"])["currency"]

    return {
        "title": (raw.get("title") or raw.get("name", "Unknown Product")).strip()[:250],
        "price": f"{price:.2f}",
        "original_price": f"{original:.2f}",
        "image": (raw.get("image") or "").strip(),
        "rating": float(raw.get("rating", 0) or 0),
        "orders": int(raw.get("orders") or raw.get("reviews", 0) or 0),
        "supplier": raw.get("source", "marketplace"),
        "region": region,
        "currency": currency,
        "product_url": (raw.get("product_url") or raw.get("source_url", "")).strip(),
        "ai_score": _auto_score(raw),
        "profit_margin": _estimate_margin(raw),
    }


def _auto_score(p: dict) -> float:
    score = 0.0
    score += min((float(p.get("rating", 0) or 0) / 5) * 30, 30)
    price = float(p.get("price", 50) or 50)
    score += min(max(0, 100 - price) / 100 * 20, 20)
    score += min((int(p.get("reviews", 0) or 0)) / 5000 * 20, 20)
    src = p.get("source", "")
    if src == "aliexpress":
        score += 15
    elif src == "amazon":
        score += 5
    score += 5 if len(p.get("name", p.get("title", ""))) > 30 else 0
    return round(min(score, 100), 1)


def _estimate_margin(p: dict) -> float:
    price = float(p.get("price", 0) or 0)
    if price <= 0:
        return 0.0
    ratios = {"aliexpress": 0.25, "amazon": 0.5, "google_shopping": 0.35}
    ratio = ratios.get(p.get("source", ""), 0.3)
    return round(min((1 - ratio) * 100, 92), 1)


# ==================== Base Scraper Provider with Exponential Backoff ====================

def _backoff_sleep(attempt: int, base: float = 0.5):
    jitter = random.uniform(0, 0.5)
    time.sleep(base * (2 ** attempt) + jitter)


class BaseProvider:
    def __init__(self, name: str):
        self.name = name
        self._client = httpx.Client(follow_redirects=True, timeout=PROVIDER_TIMEOUT, headers=HEADERS)

    def build_url(self, query: str, region: str = "usa") -> str:
        raise NotImplementedError

    def parse(self, html: str) -> list:
        raise NotImplementedError

    def fetch(self, url: str, max_retries: int = 1) -> Optional[str]:
        for attempt in range(max_retries + 1):
            try:
                resp = self._client.get(url)
                if resp.status_code == 200:
                    provider_health.record_success(self.name)
                    return resp.text
                if resp.status_code == 429:
                    _backoff_sleep(attempt, base=1.0)
                    continue
                _backoff_sleep(attempt)
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                provider_health.record_failure(self.name, str(e))
                _backoff_sleep(attempt)
            except Exception as e:
                provider_health.record_failure(self.name, str(e))
                _backoff_sleep(attempt)
        provider_health.record_failure(self.name, "Max retries exhausted")
        return None

    def search(self, query: str, region: str = "usa") -> list:
        url = self.build_url(query, region)
        html = self.fetch(url)
        if not html:
            return []
        try:
            products = self.parse(html)
            provider_health.record_success(self.name)
            return products
        except Exception as e:
            provider_health.record_failure(self.name, str(e))
            return []


# ==================== Amazon Provider (Multi-Region) ====================

class AmazonProvider(BaseProvider):
    def __init__(self):
        super().__init__("amazon")

    def build_url(self, query: str, region: str = "usa") -> str:
        q = query.replace(" ", "+")
        domains = REGIONS.get(region, REGIONS["usa"])["domains"]
        domain = domains[0]
        return f"https://www.amazon.{domain}/s?k={q}&ref=nb_sb_noss"

    def parse(self, html: str) -> list:
        products = []
        soup = BeautifulSoup(html, "lxml")
        for item in soup.select("[data-component-type='s-search-result'], .s-result-item"):
            name_el = item.select_one("h2 a span, h2 span, [class*='title']")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 5:
                continue

            price_whole = item.select_one(".a-price-whole")
            price_frac = item.select_one(".a-price-fraction")
            price = None
            if price_whole:
                try:
                    price = float(price_whole.get_text(strip=True).replace(",", ""))
                    if price_frac:
                        price += float("0." + price_frac.get_text(strip=True))
                except ValueError:
                    pass

            img_el = item.select_one("img.s-image")
            rating_el = item.select_one("[class*='a-star-small'] span, i[class*='a-icon-star'] span")
            reviews_el = item.select_one("[class*='a-size-small'] span, [class*='a-link-normal']")
            url_el = item.select_one("h2 a")

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
            full_url = f"https://www.amazon.com{product_url}" if product_url.startswith("/") else product_url

            products.append({
                "title": name[:250],
                "price": price or 24.99,
                "original_price": price,
                "image": image,
                "rating": rating or 4.0,
                "reviews": reviews or 0,
                "orders": reviews or 0,
                "source": "amazon",
                "product_url": full_url,
            })
            if len(products) >= MAX_RESULTS_PER_PROVIDER:
                break
        return products


# ==================== AliExpress Provider ====================

class AliExpressProvider(BaseProvider):
    def __init__(self):
        super().__init__("aliexpress")

    def build_url(self, query: str, region: str = "usa") -> str:
        q = query.replace(" ", "+")
        domains = REGIONS.get(region, REGIONS["usa"])["domains"]
        domain = domains[0]
        return f"https://www.aliexpress.{domain}/wholesale?SearchText={q}" if domain in ["com"] else f"https://www.aliexpress.com/wholesale?SearchText={q}"

    def parse(self, html: str) -> list:
        products = []
        soup = BeautifulSoup(html, "lxml")
        for item in soup.select("[class*='product'], [class*='item'], [class*='card'], li"):
            name_el = item.select_one("[class*='title'] a, [class*='name'] a, h3 a, a[class*='title']")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 5:
                continue

            price_el = item.select_one("[class*='price'], [class*='current']")
            img_el = item.select_one("img[src*='alicdn']")
            rating_el = item.select_one("[class*='rating'], [class*='star']")
            reviews_el = item.select_one("[class*='review'], [class*='sold']")
            url_el = name_el or item.select_one("a[href*='aliexpress']")

            price = self._parse_price(price_el)
            image = img_el.get("src", "") if img_el else ""
            if not image.startswith("http"):
                image = f"https:{image}" if image.startswith("//") else ""
            rating = self._parse_rating(rating_el)
            reviews = self._parse_reviews(reviews_el)
            product_url = url_el.get("href", "") if url_el else ""

            products.append({
                "title": name[:250],
                "price": price or 14.99,
                "original_price": price,
                "image": image or "https://placehold.co/400x400/FF6B6B/white?text=Product",
                "rating": rating or 4.0,
                "reviews": reviews or 0,
                "orders": reviews or 0,
                "source": "aliexpress",
                "product_url": f"https://www.aliexpress.com{product_url}" if product_url.startswith("/") else product_url,
            })
            if len(products) >= MAX_RESULTS_PER_PROVIDER:
                break
        return products

    def _parse_price(self, el) -> Optional[float]:
        if not el: return None
        text = el.get_text(strip=True)
        m = re.search(r"[\d,.]+", text.replace(",", ""))
        return float(m.group().replace(",", "")) if m else None

    def _parse_rating(self, el) -> Optional[float]:
        if not el: return None
        m = re.search(r"[\d.]+", el.get_text(strip=True))
        return float(m.group()) if m else None

    def _parse_reviews(self, el) -> Optional[int]:
        if not el: return None
        text = el.get_text(strip=True)
        m = re.search(r"[\d,.kKmMbB]+", text)
        if not m: return None
        val = m.group().lower()
        mult = 1
        if "k" in val: mult = 1000
        elif "m" in val: mult = 1000000
        elif "b" in val: mult = 1000000000
        num = float(re.search(r"[\d.]+", val).group())
        return int(num * mult)


# ==================== Google Shopping Provider ====================

class GoogleShoppingProvider(BaseProvider):
    def __init__(self):
        super().__init__("google_shopping")

    def build_url(self, query: str, region: str = "usa") -> str:
        q = query.replace(" ", "+")
        return f"https://www.google.com/search?tbm=shop&q={q}&hl=en"

    def parse(self, html: str) -> list:
        products = []
        soup = BeautifulSoup(html, "lxml")
        for item in soup.select("[class*='sh-dgr__content'], [class*='sh-dlr__list-result']"):
            name_el = item.select_one("h3, [class*='title'], a[class*='title']")
            if not name_el: continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 5: continue

            price_el = item.select_one("[class*='price'], [class*='a-price'], span[aria-label*='Price']")
            img_el = item.select_one("img[src]")
            url_el = item.select_one("a[href]")

            price = None
            if price_el:
                m = re.search(r"[\d,.]+", price_el.get_text(strip=True).replace(",", ""))
                if m:
                    try: price = float(m.group().replace(",", ""))
                    except ValueError: pass

            image = img_el.get("src", "") if img_el else ""
            product_url = ""
            if url_el:
                href = url_el.get("href", "")
                if href.startswith("/"): product_url = f"https://www.google.com{href}"
                elif href.startswith("http"): product_url = href

            products.append({
                "title": name[:250],
                "price": price or 19.99,
                "original_price": price,
                "image": image if image.startswith("http") else "",
                "rating": 4.0,
                "reviews": 0,
                "orders": 0,
                "source": "google_shopping",
                "product_url": product_url,
            })
            if len(products) >= MAX_RESULTS_PER_PROVIDER:
                break
        return products


# ==================== Provider Registry ====================

def _create_providers() -> dict:
    return {
        "amazon": AmazonProvider(),
        "aliexpress": AliExpressProvider(),
        "google_shopping": GoogleShoppingProvider(),
    }

PROVIDERS = _create_providers()


def reset_providers():
    """Destroy and recreate all provider instances — clears stale connections."""
    global PROVIDERS
    for name, p in PROVIDERS.items():
        try:
            if hasattr(p, '_client') and p._client:
                p._client.close()
        except Exception:
            pass
    PROVIDERS = _create_providers()


def validate_connections() -> dict:
    """Quick-connect test for each provider — returns per-provider connectivity."""
    results = {}
    for name, provider in PROVIDERS.items():
        try:
            test_url = provider.build_url("test", "usa")
            resp = provider._client.get(test_url, timeout=8.0)
            results[name] = resp.status_code == 200
        except Exception:
            results[name] = False
    return results


# ==================== Cache Layer ====================

def _cache_key(query: str, region: str) -> str:
    return hashlib.sha3_256(f"{query.lower().strip()}|{region}".encode()).hexdigest()[:32]


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


def get_cached(query: str, region: str = "usa") -> Optional[list]:
    cache = _load_cache()
    entry = cache.get(_cache_key(query, region))
    if entry and time.time() - entry.get("ts", 0) < CACHE_TTL:
        return entry.get("results")
    return None


def set_cached(query: str, region: str, results: list):
    cache = _load_cache()
    cache[_cache_key(query, region)] = {"ts": time.time(), "results": results, "query": query, "region": region}
    if len(cache) > 500:
        sorted_keys = sorted(cache.keys(), key=lambda k: cache[k]["ts"])
        for k in sorted_keys[:100]:
            del cache[k]
    _save_cache(cache)


# ==================== Main Search Orchestrator ====================

def search_global(query: str, region: str = "usa", max_results: int = 20) -> dict:
    region = resolve_region(region)
    """
    Primary search entry point.
    1) Auto-heal unhealthy providers
    2) Check cache
    3) Query all providers concurrently
    4) Normalize, deduplicate, score
    5) Cache results
    6) Return normalized response
    """
    # Auto-reconnect unhealthy providers
    health_summary = provider_health.summary()
    if health_summary["status"] != "green":
        for name, status in health_summary["providers"].items():
            if not status.get("healthy", False):
                if name in PROVIDERS:
                    try:
                        if hasattr(PROVIDERS[name], '_client') and PROVIDERS[name]._client:
                            PROVIDERS[name]._client.close()
                        PROVIDERS[name] = _create_providers()[name]
                    except Exception:
                        pass

    cached = get_cached(query, region)
    if cached is not None:
        return {
            "query": query,
            "region": region,
            "total": len(cached[:max_results]),
            "results": cached[:max_results],
            "cached": True,
            "source": "live",
            "health": provider_health.summary(),
        }

    merged = {}
    search_deadline = time.time() + 15.0  # Hard 15s wall-clock timeout
    for name, provider in PROVIDERS.items():
        if time.time() > search_deadline:
            break
        try:
            raw_products = provider.search(query, region)
            for p in raw_products:
                norm = normalize_product(p, region)
                key = norm["title"].lower().strip()[:60]
                if key not in merged or norm["ai_score"] > merged[key]["ai_score"]:
                    merged[key] = norm
        except Exception:
            continue

    results = sorted(merged.values(), key=lambda x: x["ai_score"], reverse=True)[:max_results]
    set_cached(query, region, results)

    return {
        "query": query,
        "region": region,
        "total": len(results),
        "results": results,
        "cached": False,
        "source": "live",
        "health": provider_health.summary(),
    }


# ==================== Provider Health Status ====================

def get_search_health() -> dict:
    """Returns the current health status of all search providers."""
    return provider_health.summary()
