"""Product Research Module — Live global search + local database fallback."""

import json
from pathlib import Path
from app.services.ai_service import ai
from app.modules.live_search import live_search as fetch_live

DATA_PATH = Path("data/sample_data.json")

CATEGORIES = [
    "Beauty & Makeup", "Health & Wellness", "Weight Loss",
    "Skincare", "Home & Kitchen", "Fashion", "Fitness",
    "Pet Supplies", "Baby & Kids", "Electronics", "Automotive", "Home Cleaning",
]


def _load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def local_search(category: str = None, max_price: float = 100, min_rating: float = 0) -> list:
    """Search local sample_data.json only (fallback)."""
    data = _load_data()
    results = []
    keyword = category.strip().lower() if category else ""
    for p in data["products"]:
        if keyword:
            keywords = keyword.split()
            match = False
            for kw in keywords:
                if kw in p["category"].lower():
                    match = True
                    break
                if kw in p["name"].lower():
                    match = True
                    break
                if kw in p["description"].lower():
                    match = True
                    break
                for tag in p.get("tags", []):
                    if kw in tag.lower():
                        match = True
                        break
                if match:
                    break
            if not match:
                continue
        if p["price"] > max_price:
            continue
        if p["rating"] < min_rating:
            continue
        total_sales = sum(s["monthly_sales"] for s in p.get("competitor_stores", []))
        p["estimated_potential"] = total_sales
        p["source"] = "local"
        results.append(p)
    results.sort(key=lambda x: x.get("estimated_potential", 0), reverse=True)
    return results


def analyze(product_id: str) -> dict | None:
    data = _load_data()
    product = next((p for p in data["products"] if p["id"] == product_id), None)
    if not product:
        return None

    total_sales = sum(s["monthly_sales"] for s in product.get("competitor_stores", []))
    total_traffic = sum(s["monthly_traffic"] for s in product.get("competitor_stores", []))

    score = min(product["rating"] / 5 * 30, 30)
    score += min(product["reviews"] / 1000 * 20, 20)
    score += min((100 - product["price"]) / 100 * 20, 20)
    score += min(total_sales / 10_000_000 * 30, 30)
    score = round(score, 1)

    return {
        "product": product,
        "analysis": {
            "winning_score": score,
            "total_competitor_traffic": total_traffic,
            "total_competitor_sales": total_sales,
            "profit_margin": round((1 - product["supplier_price"] / product["price"]) * 100, 1),
            "competition_level": "Low" if len(product.get("competitor_stores", [])) < 3 else "Medium",
            "recommendation": "🔥 Strong Buy" if score > 70 else "👍 Consider" if score > 50 else "👎 Skip",
            "estimated_monthly_profit": round(total_sales * 0.15, 2),
        },
    }


async def ai_search(category: str = None, max_price: float = 100, min_rating: float = 0) -> dict:
    """Search: live global markets first, local database fallback."""
    results = {"products": [], "source": "local", "ai_active": False}

    # 1) Try live search from global marketplaces
    if category and category.strip():
        try:
            live_results = fetch_live(category.strip(), max_results=25)
            if live_results:
                results["products"] = live_results
                results["source"] = "live"
                for p in live_results[:3]:
                    p["ai_insight"] = _mock_insight(p)
                results["ai_active"] = True
                return results
        except Exception:
            pass

    # 2) Fallback to local database
    products = local_search(category, max_price, min_rating)
    results["products"] = products

    ai_active = ai.active_service != "mock"
    results["ai_active"] = ai_active

    if ai_active and products:
        p = products[0]
        prompt = (
            f"Analyze this dropshipping product in 1 sentence: "
            f"{p['name']} (${p['price']}, rating {p['rating']}/5, {p['reviews']} reviews). "
            f"Category: {p['category']}. Why would this sell well?"
        )
        insight = ai.generate(prompt)
        if insight:
            products[0]["ai_insight"] = insight.strip().strip('"').strip("'")

    return results


def _mock_insight(p: dict) -> str:
    """Generate a brief market insight for a live product without real AI."""
    score = p.get("winning_score", 50)
    margin = p.get("profit_margin", 50)
    rating = p.get("rating", 4.0)
    src = p.get("source", "marketplace").replace("_", " ").title()

    if score >= 75:
        verdict = "Strong winning potential"
    elif score >= 55:
        verdict = "Good opportunity"
    else:
        verdict = "Niche product"

    return f"{verdict} from {src}. Rating {rating}/5 with ~{margin}% estimated margin. Trending in current market."
