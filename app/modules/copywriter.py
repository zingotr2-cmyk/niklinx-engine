"""AI Copywriter Module — Generate product copy and ad scripts."""

import json
from pathlib import Path
from app.services.ai_service import ai

DATA_PATH = Path("data/sample_data.json")


def _load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


async def generate_copy(product_id: str, tone: str = "confident_warm") -> dict:
    """Generate product copy using AI (with mock fallback)."""
    data = _load_data()
    product = next((p for p in data["products"] if p["id"] == product_id), None) or data["products"][0]
    t = data["copy_templates"]

    if ai.active_service != "mock":
        prompt = (
            f"Write e-commerce copy for '{product['name']}' (${product['sale_price']}, was ${product['price']}). "
            f"Target: women 25-55. Tone: {tone}. Description: {product['description']}.\n"
            f"Include: 1) Hero headline, 2) Subheadline, 3) 5 bullet features, "
            f"4) Pain point hook, 5) 2 testimonials, 6) 3 FAQ items, 7) Guarantee, 8) Urgency.\n"
            f"Return valid JSON only with keys: headline, subheadline, features (array), "
            f"pain_hook, testimonials (array of {{text, name}}), faq (array of {{q, a}}), "
            f"guarantee, urgency."
        )
        result = ai.generate(prompt)
        if result:
            try:
                ai_copy = json.loads(result)
                return _format_response(product, t, ai_copy, ai_generated=True)
            except (json.JSONDecodeError, KeyError):
                pass

    return _format_response(product, t, {}, ai_generated=False)


def _format_response(product: dict, t: dict, ai_copy: dict, ai_generated: bool) -> dict:
    features = ai_copy.get("features", None) or t["bullet_features"]
    testimonials = ai_copy.get("testimonials", None) or [
        {"text": t["testimonial_1"].split(" - ")[0], "name": "Sarah K.", "rating": 5},
        {"text": t["testimonial_2"].split(" - ")[0], "name": "Maria G.", "rating": 5},
    ]
    if isinstance(testimonials, list) and len(testimonials) > 0 and isinstance(testimonials[0], str):
        testimonials = [{"text": tt, "name": "Verified Buyer", "rating": 5} for tt in testimonials]

    faq = ai_copy.get("faq", None) or [
        {"q": "How does color change work?", "a": "Smart microcapsules react to your skin's pH."},
        {"q": "Will it work for my skin tone?", "a": "Yes, works for all skin tones."},
        {"q": "Return policy?", "a": "30-day money-back guarantee."},
    ]

    return {
        "product": product["name"],
        "ai_generated": ai_generated,
        "target_audience": {"age": "25-55", "gender": "Female"},
        "copy_sections": {
            "hero": {
                "headline": ai_copy.get("headline", None) or t["hero_headline"],
                "subheadline": ai_copy.get("subheadline", None) or t["hero_subheadline"],
                "cta": "Shop Now",
            },
            "pain_hook": {"question": ai_copy.get("pain_hook", None) or t["pain_hook"], "agitation": "You deserve better."},
            "brand_statement": t["brand_statement"],
            "mechanisms": t["mechanisms"],
            "features": [{"title": f, "icon": "✓"} for f in features],
            "testimonials": testimonials[:3],
            "faq": faq[:4],
            "guarantee": ai_copy.get("guarantee", None) or "30-Day Risk-Free Trial",
            "urgency": ai_copy.get("urgency", None) or "Limited stock available!",
        },
    }


async def generate_ad_scripts(product_id: str) -> list:
    """Generate 3 ad scripts using AI (with fallback)."""
    data = _load_data()
    product = next((p for p in data["products"] if p["id"] == product_id), None) or data["products"][0]

    if ai.active_service != "mock":
        prompt = (
            f"Write 3 Facebook ad scripts for '{product['name']}' (${product['sale_price']}). "
            f"Description: {product['description']}. Target: women 25-55, 60-90 seconds each.\n"
            f"For each include: ANGLE, HOOK, STORY, SOLUTION, 3-4 BENEFITS, ANALOGY, SCARCITY, CTA. "
            f"Separate each angle with ---"
        )
        result = ai.generate(prompt)
        if result:
            angles = []
            blocks = [b.strip() for b in result.split("---") if b.strip()]
            for block in blocks[:3]:
                angle = {"title": "", "hook": "", "story": "", "solution": "", "benefits": [], "analogy": "", "scarcity": "", "cta": ""}
                for line in block.split("\n"):
                    line = line.strip()
                    for key in angle:
                        if line.lower().startswith(key.lower() + ":"):
                            val = line.split(":", 1)[1].strip()
                            if key == "benefits":
                                angle[key] = [b.strip() for b in val.split(",")]
                            else:
                                angle[key] = val
                if angle["title"]:
                    angle["estimated_duration"] = "90s"
                    angle["target_audience"] = "Women 25-55"
                    angles.append(angle)
            if len(angles) >= 2:
                return angles

    # Fallback
    return [
        {"title": "The Skeptic's Surrender", "hook": "I didn't believe it...", "story": "I thought it was fake. Then I tried it.", "solution": "It matches perfectly.", "benefits": ["Natural look", "All-day wear", "SPF 30"], "analogy": "Like sunscreen that knows your shade.", "scarcity": "Selling fast!", "cta": "Try it risk-free."},
        {"title": "The Aging Skin Rescue", "hook": "After 50, foundation is a nightmare.", "story": "Everything looked cakey.", "solution": "Hydrates AND matches.", "benefits": ["Anti-aging", "Perfect match", "Lightweight"], "analogy": "Skincare + makeup.", "scarcity": "Limited stock.", "cta": "Get your match."},
        {"title": "Why I Stopped Wearing Makeup", "hook": "I stopped wearing makeup.", "story": "One product does it all.", "solution": "One stick. That's all.", "benefits": ["Quick", "Easy", "Perfect"], "analogy": "The only product you need.", "scarcity": "While supplies last.", "cta": "Join thousands."},
    ]
