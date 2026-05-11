"""Product Research Module — Find winning dropshipping products."""

import json
from pathlib import Path
from app.services.ai_service import ai

DATA_PATH = Path("data/sample_data.json")

CATEGORIES = [
    "Beauty & Makeup", "Health & Wellness", "Weight Loss",
    "Skincare", "Home & Kitchen", "Fashion", "Fitness",
    "Pet Supplies", "Baby & Kids", "Electronics", "Automotive",
]


def _load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def search(category: str = None, max_price: float = 100, min_rating: float = 0) -> list:
    data = _load_data()
    results = []
    keyword = category.strip().lower() if category else ""
    for p in data["products"]:
        if keyword:
            match = False
            if keyword in p["category"].lower():
                match = True
            if keyword in p["name"].lower():
                match = True
            if keyword in p["description"].lower():
                match = True
            for tag in p.get("tags", []):
                if keyword in tag.lower():
                    match = True
                    break
            if not match:
                continue
        if p["price"] > max_price:
            continue
        if p["rating"] < min_rating:
            continue
        total_sales = sum(s["monthly_sales"] for s in p.get("competitor_stores", []))
        p["estimated_potential"] = total_sales
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
    """Search products with optional AI-powered insights."""
    products = search(category, max_price, min_rating)
    ai_active = ai.active_service != "mock"

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

    return {"products": products, "ai_active": ai_active}
