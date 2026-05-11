"""
DRO API Routes — FastAPI application with all endpoints.
"""

import sys
import os
# Ensure project root is in path for gunicorn/uvicorn production
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional
import json

from licensing import license_manager
from config import config
from app.modules import product_research, store_analyzer, copywriter, image_generator, ad_creator, campaign_manager
from app.services.scraper_service import scraper

# ==================== FastAPI App ====================

app = FastAPI(
    title="DRO — Agentic Commerce Engine",
    description="Enterprise dropshipping automation system powered by AI",
    version="2.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ==================== Request Models ====================

class SearchRequest(BaseModel):
    category: Optional[str] = None
    max_price: float = 100
    min_rating: float = 0

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

class ScrapeRequest(BaseModel):
    url: str

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
    return await product_research.ai_search(request.category, request.max_price, request.min_rating)

@app.post("/api/research/analyze")
def research_analyze(request: AnalyzeRequest):
    result = product_research.analyze(request.product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result

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

# ==================== Scraper API ====================

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
    return {
        "status": "healthy",
        "ai_service": config.active_ai_service,
        "licensed": license_manager.is_licensed(),
        "modules": ["research", "store", "copywriting", "images", "ads", "campaign"],
    }
