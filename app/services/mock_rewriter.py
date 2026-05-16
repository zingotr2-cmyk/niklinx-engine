import json
import random

random.seed(42)

PRODUCT_HEADLINES = {
    "beauty": "Transform Your Look Instantly",
    "makeup": "Flawless in Seconds",
    "health": "Feel the Difference Today",
    "home": "Upgrade Your Everyday",
    "fashion": "Style That Speaks Volumes",
    "fitness": "Stronger Every Day",
    "pet": "Because They Deserve the Best",
    "baby": "Gentle Care for Little Ones",
    "electronics": "Smarter Living Starts Here",
    "kitchen": "Cook Like a Pro",
}

PRODUCT_SUBHEADLINES = {
    "beauty": "Professional-grade results without the salon price tag.",
    "makeup": "Effortless beauty that stays perfect all day.",
    "health": "Clinically tested, naturally inspired wellness.",
    "home": "Thoughtfully designed for modern living.",
    "fashion": "Timeless pieces for the confident you.",
    "fitness": "Engineered for performance, built to last.",
    "pet": "Premium care for your furry family member.",
    "baby": "Parent-tested, baby-approved essentials.",
    "electronics": "Cutting-edge technology made simple.",
    "kitchen": "Tools that make cooking a joy.",
}

DEFAULT_HEADLINE = "Discover Something Extraordinary"
DEFAULT_SUBHEADLINE = "Quality you can trust, value you deserve."

FEATURES = [
    "Premium quality materials for lasting durability",
    "Designed with expert craftsmanship and attention to detail",
    "Easy to use — no complicated setup required",
    "Perfect for everyday use at home or on the go",
    "Backed by thousands of satisfied customers",
    "Versatile design complements any lifestyle",
    "Lightweight and portable for maximum convenience",
    "Eco-friendly materials you can feel good about",
]

HOOKS = [
    "Why are thousands of customers switching?",
    "The secret your friends won't tell you about.",
    "Stop overpaying — get the same quality for less.",
    "You've been doing it wrong. Here's the right way.",
    "The product that sells itself.",
]

GUARANTEES = [
    "30-Day Risk-Free Trial",
    "60-Day Money-Back Guarantee",
    "100% Satisfaction Guaranteed",
    "Lifetime Warranty Included",
]

URGENCIES = [
    "Limited stock available — order now!",
    "Sale ends soon. Don't miss out.",
    "While supplies last — selling fast!",
    "Exclusive offer for new customers.",
]

TESTIMONIAL_TEMPLATES = [
    {"text": "I was skeptical at first, but this exceeded all my expectations. Highly recommended!", "name": "Sarah M.", "rating": 5},
    {"text": "Game changer! I've been using it for a month and the results are incredible.", "name": "James L.", "rating": 5},
    {"text": "Best purchase I've made this year. The quality is outstanding.", "name": "Emma R.", "rating": 5},
    {"text": "I've tried many similar products, but nothing compares to this. Truly premium.", "name": "Michael T.", "rating": 5},
    {"text": "Exactly what I was looking for. Fast shipping and perfect packaging.", "name": "Lisa K.", "rating": 5},
]

FAQ_TEMPLATES = [
    {"q": "How does this product work?", "a": "Simply follow the included instructions. Most users see results within the first week of regular use."},
    {"q": "Is it suitable for all skin types?", "a": "Yes, our formula is dermatologist-tested and suitable for all skin types including sensitive skin."},
    {"q": "What is your return policy?", "a": "We offer a 30-day money-back guarantee. If you're not satisfied, we'll refund your purchase — no questions asked."},
    {"q": "How long does shipping take?", "a": "Orders are processed within 24 hours and delivered within 5-8 business days."},
    {"q": "Is this product safe for daily use?", "a": "Absolutely. Our product is made with high-quality, safe ingredients and has been tested for daily use."},
]

PAIN_HOOKS = [
    "Tired of products that promise the world and deliver nothing?",
    "Frustrated with paying more for less?",
    "Wish there was a simpler, better way?",
    "Done with settling for mediocre quality?",
    "Ready to experience what premium really feels like?",
]


def detect_category(product_name: str, description: str = "") -> str:
    text = (product_name + " " + description).lower()
    for cat in PRODUCT_HEADLINES:
        if cat in text:
            return cat
    for kw, cat in [("skin", "beauty"), ("makeup", "makeup"), ("health", "health"),
                    ("home", "home"), ("kitchen", "kitchen"), ("fashion", "fashion"),
                    ("fit", "fitness"), ("pet", "pet"), ("baby", "baby"),
                    ("electronics", "electronics"), ("tech", "electronics")]:
        if kw in text:
            return cat
    return "general"


def headline(product_name: str, category: str = None) -> str:
    cat = category or detect_category(product_name)
    return PRODUCT_HEADLINES.get(cat, DEFAULT_HEADLINE)


def subheadline(product_name: str, category: str = None) -> str:
    cat = category or detect_category(product_name)
    return PRODUCT_SUBHEADLINES.get(cat, DEFAULT_SUBHEADLINE)


def bullet_features(product_name: str = "", count: int = 5) -> list:
    selected = random.sample(FEATURES, min(count, len(FEATURES)))
    return selected


def pain_hook(product_name: str = "") -> str:
    return random.choice(PAIN_HOOKS)


def testimonials(count: int = 3) -> list:
    return random.sample(TESTIMONIAL_TEMPLATES, min(count, len(TESTIMONIAL_TEMPLATES)))


def faq(count: int = 4) -> list:
    return random.sample(FAQ_TEMPLATES, min(count, len(FAQ_TEMPLATES)))


def guarantee() -> str:
    return random.choice(GUARANTEES)


def urgency() -> str:
    return random.choice(URGENCIES)


def generate_copy(product_name: str, description: str = "", price: float = 0, category: str = None) -> dict:
    cat = category or detect_category(product_name, description)
    return {
        "headline": headline(product_name, cat),
        "subheadline": subheadline(product_name, cat),
        "features": bullet_features(product_name),
        "pain_hook": pain_hook(product_name),
        "testimonials": testimonials(3),
        "faq": faq(4),
        "guarantee": guarantee(),
        "urgency": urgency(),
    }


def generate_ad_scripts(product_name: str, description: str = "") -> list:
    hooks = random.sample(HOOKS, min(3, len(HOOKS)))
    scripts = []
    for i, hook in enumerate(hooks):
        scripts.append({
            "title": f"Angle {i + 1}: {hook[:40]}",
            "hook": hook,
            "story": f"I discovered {product_name} and it changed everything. Here's why you need to try it too.",
            "solution": f"{product_name} delivers results you can see and feel.",
            "benefits": bullet_features(product_name, 3),
            "analogy": "It's like having a personal assistant for this exact problem.",
            "scarcity": random.choice(URGENCIES),
            "cta": "Get yours today with our risk-free guarantee.",
            "estimated_duration": "90s",
            "target_audience": "Adults 25-55",
        })
    return scripts


def store_hero(product_name: str = "") -> str:
    return f"{headline(product_name)} — {subheadline(product_name)}"


def generate_store_section(section_name: str, brand_name: str = "Our Store") -> dict:
    templates = {
        "hero": {
            "type": "hero",
            "content": {
                "headline": f"{brand_name} — Premium Quality, Trusted Worldwide",
                "subheadline": "Curated products selected for their exceptional quality and value.",
                "cta": "Shop Now",
            },
        },
        "featured_products": {
            "type": "featured_products",
            "content": {
                "title": "Bestsellers",
                "description": "Our most popular products, chosen by customers like you.",
            },
        },
        "testimonials": {
            "type": "testimonials",
            "content": {"items": testimonials(3)},
        },
        "benefits": {
            "type": "benefits",
            "content": {
                "title": "Why Shop With Us",
                "items": bullet_features("", 4),
            },
        },
        "guarantee": {
            "type": "guarantee",
            "content": {"text": guarantee(), "description": "Your satisfaction is our top priority."},
        },
        "faq": {
            "type": "faq",
            "content": {"items": faq(4)},
        },
        "cta": {
            "type": "cta",
            "content": {"headline": "Ready to Get Started?", "button": "Shop Collection"},
        },
    }
    return templates.get(section_name, {"type": section_name, "content": {"placeholder": f"[{section_name.upper()}]"}})
