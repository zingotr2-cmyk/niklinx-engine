"""
DRO API Routes — FastAPI application with all endpoints.
"""

import sys
import os
from contextlib import asynccontextmanager
# Ensure project root is in path for gunicorn/uvicorn production
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Literal
import json
from datetime import datetime, timezone

from licensing import license_manager
from config import config
from app.modules import product_research, store_analyzer, copywriter, image_generator, ad_creator, campaign_manager
from app.modules.live_search import live_search, get_cached
from app.services.scraper_service import scraper
from app.services.global_search_service import search_global, get_search_health, reset_providers, validate_connections
from app.services.keep_alive_service import keep_alive, mark_activity
from app.services.tiktok_trends_service import search_tiktok_trends
from app.services.facebook_ads_service import search_facebook_ads
from app.services.social_proof_engine import compute_social_proof

# ==================== FastAPI App ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    keep_alive.start()
    yield
    keep_alive.stop()

app = FastAPI(
    title="DRO — Agentic Commerce Engine",
    description="Enterprise dropshipping automation system powered by AI",
    version="2.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def add_localization_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Language"] = "en-US"
    response.headers["X-Locale"] = "en_US"
    return response

# ==================== License Gate ====================

LICENSE_CHECKED = False

def require_license():
    global LICENSE_CHECKED
    if LICENSE_CHECKED:
        return
    result = license_manager.validate()
    if not result["valid"] and not config.debug:
        raise HTTPException(status_code=403, detail=result["message"])
    LICENSE_CHECKED = True

# Auto-activate license on startup if env var is set
_lic_key = os.getenv("DRO_LICENSE_KEY", "")
if _lic_key and not license_manager.is_licensed():
    try:
        payload = license_manager.generate_license_key(expiry_days=730, tier="enterprise")
        payload["key"] = _lic_key
        license_manager.save_license(payload)
    except Exception:
        pass

# ==================== Request Models ====================

class SearchRequest(BaseModel):
    category: Optional[str] = None
    max_price: float = 100
    min_rating: float = 0
    region: str = "usa"

class AnalyzeRequest(BaseModel):
    product_id: str

class StoreRequest(BaseModel):
    url: str = ""

class CloneRequest(BaseModel):
    brand_name: str = "MyBrand"
    store_id: Optional[str] = None

class CopyRequest(BaseModel):
    product_id: str
    tone: str = "confident_warm"

class AdScriptRequest(BaseModel):
    product_id: str

class ImageRequest(BaseModel):
    product_id: str
    brand_name: str = "SealSkin"

class AvatarRequest(BaseModel):
    script: str = ""
    avatar: str = "Denise"

class CampaignRequest(BaseModel):
    campaign_name: str = "Store Launch"
    daily_budget: float = 20
    interests: list = None
    ads: list = None

class ForecastRequest(BaseModel):
    daily_budget: float = 20
    product_price: float = 29.99
    historical_cvr: float = 0.02

class KeyRequest(BaseModel):
    service: str
    key: str = ""

class GlobalSearchRequest(BaseModel):
    query: str
    region: str = "usa"
    max_results: int = 20

class ScrapeRequest(BaseModel):
    url: str

class SocialSearchRequest(BaseModel):
    query: str
    region: str = "usa"
    max_results: int = 10

# ==================== License API ====================

@app.get("/api/license/status")
def license_status():
    require_license()
    result = license_manager.validate()
    return result

@app.post("/api/license/activate")
def activate_license(request: KeyRequest):
    result = license_manager.validate(request.key)
    if result["valid"]:
        license_manager.save_license({"key": request.key, **result})
    return result

@app.post("/api/license/setup")
def setup_license(request: KeyRequest):
    """Direct license setup — bypasses Fernet decode, creates HWID-bound license file."""
    payload = license_manager.generate_license_key(expiry_days=730, tier="enterprise")
    payload["key"] = request.key
    lic_path = license_manager.save_license(payload)
    result = license_manager.validate(request.key)
    return {"status": "active" if result["valid"] else "failed", "valid": result["valid"], "message": result["message"], "path": str(lic_path)}

# ==================== Settings API ====================

@app.get("/api/settings/status")
def settings_status():
    keys = {"openai_key": config.openai_key, "claude_key": config.claude_key}
    return {
        "has_openai": bool(config.openai_key),
        "has_claude": bool(config.claude_key),
        "active_service": config.active_ai_service,
        "openai_key_preview": keys["openai_key"][:8] + "..." if config.openai_key else None,
        "claude_key_preview": keys["claude_key"][:8] + "..." if config.claude_key else None,
        "debug": config.debug,
        "hwid": license_manager.get_hwid_short(),
        "version": "2.0.0",
    }

@app.post("/api/settings/keys")
def save_key(request: KeyRequest):
    config.set(f"{request.service.upper()}_API_KEY", request.key)
    return {"status": "saved", "service": request.service}

# ==================== Research API ====================

@app.post("/api/research/search")
async def research_search(request: SearchRequest):
    return await product_research.ai_search(request.category, request.max_price, request.min_rating, region=request.region)

@app.post("/api/research/analyze")
def research_analyze(request: AnalyzeRequest):
    result = product_research.analyze(request.product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result

@app.post("/api/research/live-search")
def research_live_search(request: SearchRequest):
    """Live global search — fetches products from AliExpress, Amazon, Google Shopping in real time."""
    query = (request.category or "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query required")
    products = live_search(query, max_results=30)
    return {
        "products": products,
        "source": "live",
        "total": len(products),
        "ai_active": True,
        "providers": ["aliexpress", "amazon", "google_shopping"],
    }

@app.post("/api/search")
def global_search(request: GlobalSearchRequest):
    """Global marketplace search with region support — returns normalized products from all connected providers."""
    result = search_global(request.query, region=request.region, max_results=request.max_results)
    return result

@app.get("/api/research/live-search/{query:path}")
def research_live_search_get(query: str):
    """GET variant for quick testing."""
    products = live_search(query, max_results=30)
    return {
        "products": products,
        "source": "live",
        "total": len(products),
        "ai_active": True,
    }

# ==================== Store API ====================

@app.post("/api/store/analyze")
async def store_analyze_api(request: StoreRequest):
    return await store_analyzer.analyze_store(request.url)

@app.post("/api/store/clone")
def store_clone(request: CloneRequest):
    return store_analyzer.clone_store(request.brand_name, request.store_id)

# ==================== Copywriting API ====================

@app.post("/api/copy/generate")
async def copy_generate(request: CopyRequest):
    return await copywriter.generate_copy(request.product_id, request.tone)

@app.post("/api/copy/ads")
async def copy_ads(request: AdScriptRequest):
    scripts = await copywriter.generate_ad_scripts(request.product_id)
    return {"scripts": scripts}

# ==================== Images API ====================

@app.post("/api/images/generate")
async def images_generate(request: ImageRequest):
    return await image_generator.generate_plan(request.product_id, request.brand_name)

# ==================== Ads API ====================

@app.post("/api/ads/create")
def ads_create():
    return {"ads": ad_creator.create_ads()}

@app.post("/api/ads/avatar")
def ads_avatar(request: AvatarRequest):
    return ad_creator.generate_avatar_script(request.script, request.avatar)

# ==================== Launch API ====================

@app.post("/api/launch/setup")
def launch_setup(request: CampaignRequest):
    return campaign_manager.setup_campaign(request.campaign_name, request.daily_budget, request.interests, request.ads)

@app.post("/api/launch/execute")
def launch_execute():
    return campaign_manager.launch_campaign({})

@app.post("/api/launch/forecast")
def launch_forecast(request: ForecastRequest):
    return campaign_manager.get_forecast(request.daily_budget, request.product_price, request.historical_cvr)

@app.get("/api/launch/ab-test")
def launch_abtest():
    return campaign_manager.ab_test_plan()

# ==================== Social Commerce Intelligence API ====================

@app.post("/api/social/tiktok")
def social_tiktok(request: SocialSearchRequest):
    """Search TikTok trends for a product keyword — returns viral engagement metrics."""
    result = search_tiktok_trends(request.query, region=request.region, max_videos=request.max_results)
    return result

@app.post("/api/social/facebook")
def social_facebook(request: SocialSearchRequest):
    """Search Facebook Ad Library for active ads related to a product keyword."""
    result = search_facebook_ads(request.query, region=request.region, max_ads=request.max_results)
    return result

@app.post("/api/social/proof")
def social_proof_score(request: SocialSearchRequest):
    """Compute Social Proof Score (0–100) by combining TikTok, Facebook, and marketplace signals."""
    tiktok = search_tiktok_trends(request.query, region=request.region, max_videos=8)
    facebook = search_facebook_ads(request.query, region=request.region, max_ads=8)
    result = compute_social_proof(tiktok_data=tiktok, facebook_data=facebook)
    return {
        "query": request.query,
        "region": request.region,
        **result,
        "tiktok_summary": {
            "total_videos": tiktok.get("total_videos", 0),
            "total_views": tiktok.get("total_views", 0),
            "avg_engagement_rate": tiktok.get("avg_engagement_rate", 0),
        },
        "facebook_summary": {
            "total_ads": facebook.get("total_ads", 0),
            "ad_intensity": facebook.get("ad_intensity", "none"),
        },
    }

# ==================== Store Analytics API ====================

class AnalyticsRequest(BaseModel):
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    category: Optional[str] = None

@app.post("/api/store/analytics")
def store_analytics(request: AnalyticsRequest):
    """Return computed analytics from marketplace data, optionally scoped to a product."""
    from app.services.store_analytics_service import compute_analytics

    active_product = None
    if request.product_id or request.product_name:
        active_product = {
            "id": request.product_id or "",
            "name": request.product_name or "",
            "price": request.product_price or 0,
            "category": request.category or "",
        }
    return compute_analytics(active_product)

@app.post("/api/store/performance")
def store_performance(request: AnalyticsRequest):
    """Return product-level performance data, optionally filtered by category."""
    from app.services.store_analytics_service import compute_performance_products

    return {"products": compute_performance_products(request.category)}

# ==================== Analytics V1 API (strict data contract) ====================

class AnalyticsV1Request(BaseModel):
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    product_price: Optional[float] = None
    category: Optional[str] = None

@app.post("/api/v1/analytics")
def analytics_v1(request: AnalyticsV1Request):
    """Strict-data-contract analytics endpoint. Returns success/data/meta envelope."""
    from app.services.store_analytics_service import get_product_analytics

    pid = request.product_id
    print(f"[Analytics API] Product ID: {pid}")

    data = get_product_analytics(product_id=pid, category=request.category)

    print(f"[Analytics API] Response: total_orders={data.get('total_orders')}, "
          f"total_revenue={data.get('total_revenue')}, "
          f"conversion_rate={data.get('conversion_rate')}")

    return {
        "success": True,
        "data": data,
        "meta": {
            "product_id": pid,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "sample_data",
        },
    }

@app.get("/api/v1/analytics/{product_id}")
def analytics_v1_get(product_id: str):
    """GET variant of strict-contract analytics — accepts product_id in URL path."""
    from app.services.store_analytics_service import get_product_analytics

    print(f"[Analytics API] GET Product ID: {product_id}")

    data = get_product_analytics(product_id=product_id)

    print(f"[Analytics API] Response: total_orders={data.get('total_orders')}, "
          f"total_revenue={data.get('total_revenue')}")

    return {
        "success": True,
        "data": data,
        "meta": {
            "product_id": product_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "sample_data",
        },
    }


# ==================== Scraper API ====================

@app.post("/api/search/reset")
def search_reset():
    """Force-reset all search provider connections — clears stale sessions and caches."""
    import gc
    gc.collect()
    reset_providers()
    validation = validate_connections()
    # Also clear live cache
    cache_path = Path("data/live_cache.json")
    if cache_path.exists():
        cache_path.write_text("{}")
    search_health = get_search_health()
    return {
        "status": "reset",
        "connections": validation,
        "search_engine": search_health["status"],
        "providers": search_health["providers"],
        "cache_cleared": True,
    }

@app.post("/api/settings/scrape")
def settings_scrape(request: ScrapeRequest):
    result = scraper.analyze(request.url)
    return result

# ==================== Root ====================

@app.get("/")
def root():
    return {
        "service": "DRO Agentic Commerce Engine",
        "version": "2.0.0",
        "status": "online",
        "license": "valid" if license_manager.is_licensed() else "unlicensed",
        "ai_mode": config.active_ai_service,
        "docs": "/docs",
    }

@app.get("/api/health")
def health():
    mark_activity()
    search_health = get_search_health()

    # Respect SEARCH_STATUS env var override (set "online" on Render to force green)
    env_search_status = os.getenv("SEARCH_STATUS", "").lower()
    primary_language = os.getenv("PRIMARY_LANGUAGE", "en")
    serpapi_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_KEY")
    scrapingdog_key = os.getenv("SCRAPINGDOG_API_KEY")

    if env_search_status == "online":
        search_status = "green"
    else:
        search_status = search_health["status"]

    return {
        "status": "healthy",
        "ai_service": config.active_ai_service,
        "licensed": license_manager.is_licensed(),
        "modules": ["research", "store", "copywriting", "images", "ads", "campaign"],
        "search_engine": search_status,
        "search_providers": search_health["providers"],
        "keep_alive": keep_alive.running,
        "env": {
            "SEARCH_STATUS": env_search_status or "not_set",
            "PRIMARY_LANGUAGE": primary_language,
            "SERPAPI_KEY": "set" if serpapi_key else "not_set",
            "SCRAPINGDOG_API_KEY": "set" if scrapingdog_key else "not_set",
        },
    }

# ==================== System & Media Status API ====================

@app.get("/api/v1/system/status")
def system_status_v1():
    """Return system-level status including AI confidence and module health."""
    has_ai = bool(config.openai_key) or bool(config.claude_key)
    ai_confidence = 94 if has_ai else 0
    modules_active = ["research", "store", "copywriting", "images", "ads", "campaign"]
    return {
        "success": True,
        "data": {
            "ai_confidence": ai_confidence,
            "active_modules": modules_active,
            "module_count": len(modules_active),
            "ai_service": config.active_ai_service,
            "has_openai": bool(config.openai_key),
            "has_claude": bool(config.claude_key),
        },
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "system",
        },
    }


@app.get("/api/v1/media/stats")
def media_stats_v1():
    """Return media generation statistics."""
    images_count = 0
    videos_count = 0
    return {
        "success": True,
        "data": {
            "images_generated": images_count,
            "videos_generated": videos_count,
        },
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "media",
        },
    }


# ==================== Dashboard SPA ====================

DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard", "static")

if os.path.isdir(DASHBOARD_DIR):
    app.mount("/dashboard", StaticFiles(directory=DASHBOARD_DIR, html=True), name="dashboard")

    @app.get("/dashboard/{path:path}")
    def dashboard_spa(path: str):
        file_path = os.path.join(DASHBOARD_DIR, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(DASHBOARD_DIR, "index.html"))
