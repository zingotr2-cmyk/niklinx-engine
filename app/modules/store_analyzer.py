"""Store Analyzer Module — Analyze and clone successful stores."""

import json
from pathlib import Path
from app.services.ai_service import ai
from app.services.scraper_service import scraper

DATA_PATH = Path("data/sample_data.json")


def _load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


async def analyze_store(url: str) -> dict:
    """Analyze a competitor store by URL (real scraping + fallback)."""
    scraped = None
    if url and url.startswith("http"):
        scraped = scraper.analyze(url)

    data = _load_data()
    store = next(
        (s for s in data["store_templates"] if url and url.lower().find(s["name"].lower()) >= 0),
        None,
    ) or data["store_templates"][0]

    sections = [
        {"name": s, "placeholder": f"[{s.upper().replace(' ', '_')}]"}
        for s in store["sections"]
    ]

    ai_insights = None
    if scraped and not scraped.get("error") and ai.active_service != "mock":
        prompt = (
            f"Store analysis: {scraped.get('title')}. "
            f"Niche: {scraped.get('estimated_niche')}. "
            f"Sections: {', '.join(scraped.get('success_architecture', []) or [])}. "
            f"Give 3 specific recommendations to clone this store."
        )
        ai_insights = ai.generate(prompt)

    return {
        "store": store,
        "sections": sections,
        "scraped": scraped if scraped and not scraped.get("error") else None,
        "ai_insights": ai_insights,
        "ai_active": ai.active_service != "mock",
    }


def clone_store(brand_name: str = "MyBrand", store_id: str = None) -> dict:
    """Generate a white-label clone of a winning store."""
    data = _load_data()
    store = next(
        (s for s in data["store_templates"] if s["id"] == store_id), None
    ) or data["store_templates"][0]

    design = store["design_elements"]
    html = (
        f"<!DOCTYPE html><html><head><title>{brand_name}</title>"
        f"<style>:root {{--primary: {design['color_palette'][1]}; --bg: {design['color_palette'][0]};}}"
        f"* {{margin:0;padding:0;box-sizing:border-box;}}"
        f"body {{font-family: {design['font_family']}, sans-serif;background: var(--bg);}}</style>"
        f"</head><body><h1>[HERO_HEADLINE]</h1>"
        + "\n".join(f"<section>{s}</section>" for s in store["sections"])
        + "</body></html>"
    )

    return {
        "brand_name": brand_name,
        "cloned_from": store["name"],
        "sections": store["sections"],
        "design_specs": design,
        "html_outline": html,
    }
