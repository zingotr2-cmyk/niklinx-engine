"""
Smart Region Scraper — Triggers live regional scraping when local/API results are insufficient.
Automatically discovers trending products per market using region-specific providers.
"""

import logging
import re
import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("smart_region_scraper")

REQUEST_TIMEOUT = 15.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

REGION_MARKETPLACES = {
    "usa": {"amazon": "amazon.com", "aliexpress": "aliexpress.com", "currency": "USD"},
    "canada": {"amazon": "amazon.ca", "aliexpress": "aliexpress.com", "currency": "CAD"},
    "uk": {"amazon": "amazon.co.uk", "aliexpress": "aliexpress.com", "currency": "GBP"},
    "germany": {"amazon": "amazon.de", "aliexpress": "aliexpress.com", "currency": "EUR"},
    "france": {"amazon": "amazon.fr", "aliexpress": "aliexpress.com", "currency": "EUR"},
    "uae": {"amazon": "amazon.ae", "aliexpress": "aliexpress.ae", "currency": "AED"},
    "saudi_arabia": {"amazon": "amazon.sa", "aliexpress": "aliexpress.com", "currency": "SAR"},
    "algeria": {"amazon": "amazon.com", "aliexpress": "aliexpress.com", "currency": "DZD"},
}


class SmartRegionScraper:
    def __init__(self):
        self._client = httpx.Client(follow_redirects=True, timeout=REQUEST_TIMEOUT, headers=HEADERS)
        self._last_request = 0

    def _rate_limit(self):
        elapsed = time.time() - self._last_request
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        self._last_request = time.time()

    def discover_region_products(self, query: str, region: str, max_results: int = 10) -> list:
        """Discover trending products for a specific region."""
        products = []
        markets = REGION_MARKETPLACES.get(region, REGION_MARKETPLACES["usa"])

        # Try Amazon regional site
        amazon_products = self._scrape_amazon_region(query, markets["amazon"], region)
        if amazon_products:
            products.extend(amazon_products)

        # Try AliExpress regional
        if len(products) < max_results:
            ae_products = self._scrape_aliexpress_region(query, markets["aliexpress"], region)
            if ae_products:
                products.extend(ae_products)

        return products[:max_results]

    def _scrape_amazon_region(self, query: str, domain: str, region: str) -> list:
        """Scrape region-specific Amazon site."""
        self._rate_limit()
        try:
            q = query.replace(" ", "+")
            url = f"https://www.{domain}/s?k={q}&ref=nb_sb_noss"
            resp = self._client.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "lxml")
            products = []
            for item in soup.select("[data-component-type='s-search-result']"):
                name_el = item.select_one("h2 a span")
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                if not name or len(name) < 5:
                    continue

                price_el = item.select_one(".a-price-whole")
                img_el = item.select_one("img.s-image")
                rating_el = item.select_one("i[class*='a-icon-star'] span")
                url_el = item.select_one("h2 a")

                price = None
                if price_el:
                    try:
                        price = float(price_el.get_text(strip=True).replace(",", ""))
                    except ValueError:
                        pass

                image = img_el.get("src", "") if img_el else ""
                rating = None
                if rating_el:
                    try:
                        rating = float(re.search(r"[\d.]+", rating_el.get_text(strip=True)).group())
                    except (AttributeError, ValueError):
                        pass

                href = url_el.get("href", "") if url_el else ""
                product_url = f"https://www.{domain}{href}" if href.startswith("/") else href

                currency = REGION_MARKETPLACES.get(region, REGION_MARKETPLACES["usa"])["currency"]

                products.append({
                    "title": name[:250],
                    "price": price or 19.99,
                    "image": image,
                    "rating": rating or 4.0,
                    "source": "amazon",
                    "region": region,
                    "currency": currency,
                    "product_url": product_url,
                    "ai_score": 60.0,
                    "profit_margin": 45.0,
                })
                if len(products) >= max_results:
                    break
            return products
        except Exception as e:
            logger.debug(f"Amazon region scrape ({domain}) failed: {e}")
            return []

    def _scrape_aliexpress_region(self, query: str, domain: str, region: str) -> list:
        """Scrape region-specific AliExpress."""
        self._rate_limit()
        try:
            q = query.replace(" ", "+")
            url = f"https://www.{domain}/wholesale?SearchText={q}"
            resp = self._client.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "lxml")
            products = []
            for item in soup.select("[class*='product'], [class*='item'], [class*='card']"):
                name_el = item.select_one("[class*='title'] a, [class*='name'] a, h3 a")
                if not name_el:
                    continue
                name = name_el.get_text(strip=True)
                if not name or len(name) < 5:
                    continue

                price_el = item.select_one("[class*='price'], [class*='current']")
                img_el = item.select_one("img[src*='alicdn']")

                price = None
                if price_el:
                    m = re.search(r"[\d,.]+", price_el.get_text(strip=True).replace(",", ""))
                    if m:
                        try:
                            price = float(m.group().replace(",", ""))
                        except ValueError:
                            pass

                image = img_el.get("src", "") if img_el else ""
                if not image.startswith("http"):
                    image = f"https:{image}" if image.startswith("//") else ""

                currency = REGION_MARKETPLACES.get(region, REGION_MARKETPLACES["usa"])["currency"]

                products.append({
                    "title": name[:250],
                    "price": price or 14.99,
                    "image": image,
                    "rating": 4.0,
                    "source": "aliexpress",
                    "region": region,
                    "currency": currency,
                    "product_url": url,
                    "ai_score": 65.0,
                    "profit_margin": 50.0,
                })
                if len(products) >= max_results:
                    break
            return products
        except Exception as e:
            logger.debug(f"AliExpress region scrape ({domain}) failed: {e}")
            return []


# Singleton
smart_scraper = SmartRegionScraper()


def discover_region(query: str, region: str, max_results: int = 10) -> list:
    """Discover region-specific products. Public entry point."""
    return smart_scraper.discover_region_products(query, region, max_results)
