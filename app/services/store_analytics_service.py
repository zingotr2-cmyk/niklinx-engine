"""
Store Analytics Service — Real-time analytics computed from marketplace data.
Singleton data loader: sample_data.json loaded once at module import.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

DATA_PATH = Path("data/sample_data.json")

_products_cache = None


def _get_products() -> list:
    global _products_cache
    if _products_cache is None:
        _products_cache = json.loads(DATA_PATH.read_text(encoding="utf-8"))["products"]
    return _products_cache


def get_product_analytics(product_id: Optional[str] = None, category: Optional[str] = None) -> dict:
    """
    Compute analytics from sample_data.json matching the AnalyticsData interface.
    When product_id is given, computes projected metrics scoped to that product.
    Always returns pure dict with flat keys plus extended sectioned data.
    """
    products = _get_products()

    total_sales = 0
    total_traffic = 0
    total_reviews = 0
    category_stats: dict = {}

    for p in products:
        cat = p.get("category", "General")
        if cat not in category_stats:
            category_stats[cat] = {
                "count": 0,
                "sales": 0,
                "traffic": 0,
                "reviews": 0,
                "ratings_sum": 0,
            }
        cs = category_stats[cat]
        cs["count"] += 1
        cs["reviews"] += p.get("reviews", 0)
        cs["ratings_sum"] += p.get("rating", 0)

        for store in p.get("competitor_stores", []):
            sales = store.get("monthly_sales", 0)
            traffic = store.get("monthly_traffic", 0)
            cs["sales"] += sales
            cs["traffic"] += traffic
            total_sales += sales
            total_traffic += traffic

        total_reviews += p.get("reviews", 0)

    product_count = max(len(products), 1)

    # Core metrics
    avg_order_value = 45.0
    total_orders = int(total_sales / avg_order_value) if avg_order_value else 0
    total_revenue = round(total_sales * 0.15, 2)
    conversion_rate = round(total_orders / max(total_traffic, 1) * 100, 2)
    avg_rating = round(sum(p.get("rating", 0) for p in products) / product_count, 2)
    top_category = max(category_stats.items(), key=lambda x: x[1]["sales"])[0] if category_stats else "General"

    # Growth (derived from review velocity)
    avg_reviews_per_product = total_reviews / product_count
    weekly_growth = round((avg_reviews_per_product * 0.03), 1)
    growth_pct = round(weekly_growth * 4.3, 1)

    # Category performance
    categories = [
        {
            "name": cat,
            "product_count": cs["count"],
            "total_sales": cs["sales"],
            "total_traffic": cs["traffic"],
            "avg_rating": round(cs["ratings_sum"] / max(cs["count"], 1), 2),
            "market_share": round(cs["sales"] / max(total_sales, 1) * 100, 1),
        }
        for cat, cs in sorted(category_stats.items(), key=lambda x: x[1]["sales"], reverse=True)
    ]

    # Top performing products
    top_products = sorted(
        [
            {
                "id": p["id"],
                "name": p["name"],
                "price": p.get("sale_price", p["price"]),
                "rating": p.get("rating", 0),
                "reviews": p.get("reviews", 0),
                "category": p.get("category", "General"),
                "estimated_monthly_sales": sum(
                    s.get("monthly_sales", 0) for s in p.get("competitor_stores", [])
                ),
                "estimated_monthly_traffic": sum(
                    s.get("monthly_traffic", 0) for s in p.get("competitor_stores", [])
                ),
            }
            for p in products
        ],
        key=lambda x: x["estimated_monthly_sales"],
        reverse=True,
    )[:10]

    # Customer insights
    repeat_rate = round(0.28 + (conversion_rate * 0.01), 2)
    review_velocity = int(avg_reviews_per_product * 0.7)

    flat = {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "conversion_rate": conversion_rate,
        "avg_order_value": avg_order_value,
        "top_category": top_category,
        "growth_percentage": growth_pct,
        "weekly_growth_pct": round(weekly_growth, 1),
        "monthly_growth_pct": growth_pct,
        "growth_direction": "up" if growth_pct > 0 else "down",
        "total_traffic": total_traffic,
        "total_products_analyzed": len(products),
        "review_velocity": review_velocity,
        "categories": categories,
        "top_products": top_products,
        "customer_insights": {
            "avg_rating": avg_rating,
            "total_reviews": total_reviews,
            "avg_reviews_per_product": round(avg_reviews_per_product, 1),
            "repeat_rate": repeat_rate,
            "top_category": top_category,
        },
        "active_product": None,
    }

    # When product_id is given, compute projected metrics
    if product_id:
        matched = next((p for p in products if p["id"] == product_id), None)
        if matched:
            competitor_sales = sum(
                s.get("monthly_sales", 0) for s in matched.get("competitor_stores", [])
            )
            competitor_traffic = sum(
                s.get("monthly_traffic", 0) for s in matched.get("competitor_stores", [])
            )
            price = float(matched.get("sale_price", matched["price"]))
            projected_orders = int(competitor_sales / avg_order_value * 0.12)
            projected_revenue = round(projected_orders * price * 1.15, 2)
            profit_margin = round(
                (1 - matched.get("supplier_price", 0) / max(price, 1)) * 100, 1
            )

            flat["active_product"] = {
                "id": matched["id"],
                "name": matched["name"],
                "price": price,
                "category": matched.get("category", "General"),
                "projected_orders": projected_orders,
                "projected_revenue": projected_revenue,
                "competitor_count": len(matched.get("competitor_stores", [])),
                "estimated_market_size": competitor_sales,
                "estimated_traffic": competitor_traffic,
                "avg_competitor_rating": matched.get("rating", 0),
                "profit_margin": profit_margin,
            }

    return flat


def compute_analytics(active_product: Optional[dict] = None) -> dict:
    """Legacy wrapper — delegates to get_product_analytics with backward compat."""
    return get_product_analytics(
        product_id=active_product.get("id") if active_product else None,
    )


def compute_performance_products(category: Optional[str] = None) -> list:
    """Return product-level performance data, optionally filtered by category."""
    products = _get_products()
    filtered = products
    if category:
        filtered = [p for p in products if category.lower() in p.get("category", "").lower()]

    return sorted(
        [
            {
                "id": p["id"],
                "name": p["name"],
                "price": p.get("sale_price", p["price"]),
                "rating": p.get("rating", 0),
                "reviews": p.get("reviews", 0),
                "category": p.get("category", "General"),
                "estimated_monthly_sales": sum(
                    s.get("monthly_sales", 0) for s in p.get("competitor_stores", [])
                ),
                "estimated_monthly_traffic": sum(
                    s.get("monthly_traffic", 0) for s in p.get("competitor_stores", [])
                ),
                "competitor_count": len(p.get("competitor_stores", [])),
                "profit_margin": round(
                    (1 - p.get("supplier_price", 0) / max(p["price"], 1)) * 100, 1
                ),
            }
            for p in filtered
        ],
        key=lambda x: x["estimated_monthly_sales"],
        reverse=True,
    )
