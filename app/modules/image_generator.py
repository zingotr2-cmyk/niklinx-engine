"""Image Generator Module — Plan and generate product images."""

import json
from pathlib import Path
from app.services.ai_service import ai

DATA_PATH = Path("data/sample_data.json")


def _load_data() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


async def generate_plan(product_id: str, brand_name: str = "SealSkin") -> dict:
    """Generate image plan with AI-powered prompts."""
    data = _load_data()
    product = next((p for p in data["products"] if p["id"] == product_id), None) or data["products"][0]

    image_prompts = []
    if ai.active_service != "mock":
        prompt = (
            f"Create 5 detailed AI image generation prompts for '{product['name']}' by {brand_name}. "
            f"Types: 1) Hero product shot, 2) Product being used on skin, 3) Before/after, "
            f"4) Ingredient close-up, 5) Bundle packaging. "
            f"Describe lighting, composition, mood. Return as numbered list."
        )
        result = ai.generate(prompt)
        if result:
            image_prompts = [
                l.split(". ", 1)[1] if ". " in l else l
                for l in result.split("\n")
                if l.strip() and l[0].isdigit()
            ]

    images = []
    sections = ["Hero", "Transformation", "Features", "How It Works", "Results", "Bundle", "Testimonial", "Footer"]
    for i in range(16):
        bg = "FF6B6B" if i % 2 == 0 else "4ECDC4"
        images.append({
            "id": i + 1,
            "section": sections[i % 8],
            "type": f"image_{i + 1}",
            "url": f"https://placehold.co/400x400/{bg}/white?text={brand_name}+{i + 1}",
            "ai_prompt": image_prompts[i] if i < len(image_prompts) else None,
        })

    return {
        "brief": (
            f"Image Generation Brief for {brand_name}\n"
            f"Total: 16 images\nStyle: Clean e-commerce\n"
            f"AI Prompts: {'Available' if image_prompts else 'Using defaults'}"
        ),
        "image_plan": {"total_images_needed": 16, "images": images},
        "generated_previews": images,
        "ai_generated_prompts": image_prompts,
        "ai_active": ai.active_service != "mock",
    }
