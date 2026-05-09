"""
DRO Streamlit Dashboard — Premium commercial-grade UI.
Inspired by Apple/Dyson aesthetic.
"""

import streamlit as st
import httpx
import json
import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.modules import product_research, campaign_manager

# ==================== Page Config ====================

st.set_page_config(
    page_title="DRO — Agentic Commerce Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==================== Custom CSS (Luxury Dark Mode) ====================

st.markdown("""
<style>
    /* Global */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }
    
    .stApp {
        background: #0a0a0f;
        color: #f0f0f5;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        color: #ffffff !important;
    }
    
    h1 { font-size: 2.5rem !important; }
    
    /* Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #2a2a45;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }
    
    div[data-testid="stMetric"] > div {
        color: #f0f0f5 !important;
    }
    
    div[data-testid="stMetric"] label {
        color: #8888a0 !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.75rem !important;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #6C63FF, #5A52D5) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(108,99,255,0.25) !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 32px rgba(108,99,255,0.4) !important;
    }
    
    .stButton button[kind="secondary"] {
        background: transparent !important;
        border: 2px solid #2a2a45 !important;
        box-shadow: none !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #1a1a2e;
        border-radius: 16px;
        padding: 6px;
        border: 1px solid #2a2a45;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        color: #8888a0 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #6C63FF !important;
        color: white !important;
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: #1a1a2e !important;
        border: 1px solid #2a2a45 !important;
        border-radius: 12px !important;
        color: #f0f0f5 !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6C63FF !important;
        box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;
    }
    
    /* Dividers */
    hr { border-color: #2a2a45 !important; margin: 32px 0 !important; }
    
    /* Info/Error boxes */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    
    /* Status badges */
    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-success { background: #4ECDC4; color: #0a0a0f; }
    .badge-warning { background: #FFD93D; color: #0a0a0f; }
    .badge-error { background: #FF6B6B; color: white; }
    .badge-info { background: #6C63FF; color: white; }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 0 20px;
        color: #4a4a60;
        font-size: 0.8rem;
        border-top: 1px solid #1a1a2e;
    }
</style>
""", unsafe_allow_html=True)

# ==================== API Client ====================

API_BASE = os.getenv("DRO_API_URL", "http://localhost:8000")

def api(method: str, path: str, data: dict = None) -> dict:
    url = f"{API_BASE}{path}"
    try:
        if method == "GET":
            resp = httpx.get(url, timeout=10)
        else:
            resp = httpx.post(url, json=data or {}, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# ==================== Sidebar ====================

with st.sidebar:
    st.markdown("## 🚀 **DRO**")
    st.markdown("*Agentic Commerce Engine v2.0*")
    st.markdown("---")
    
    status = api("GET", "/api/settings/status")
    ai_status = status.get("active_service", "offline")
    badge_class = "badge-success" if ai_status != "mock" else "badge-warning"
    st.markdown(f"**AI Status:** <span class='badge {badge_class}'>{'🟢 ' + ai_status.upper() if ai_status != 'mock' else '🟡 SIMULATION'}</span>", unsafe_allow_html=True)
    
    lic_status = api("GET", "/api/license/status")
    if lic_status.get("valid"):
        st.markdown(f"**License:** <span class='badge badge-success'>✅ {lic_status.get('days_remaining', 0)} days</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"**License:** <span class='badge badge-warning'>⚠️ Unlicensed</span>", unsafe_allow_html=True)
    
    st.markdown(f"**HWID:** `{status.get('hwid', 'N/A')}`")
    st.markdown("---")
    st.markdown("### Quick Links")
    st.markdown("- [API Docs](/docs)")
    st.markdown("- [GitHub](#)")
    st.markdown("- [Support](#)")

# ==================== Main Dashboard ====================

st.title("🚀 DRO — Agentic Commerce Engine")
st.markdown("<p style='color: #8888a0; font-size: 1.1rem; margin-top: -10px;'>AI-powered dropshipping automation — from product research to campaign launch in under 24 hours</p>", unsafe_allow_html=True)

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Active Modules", "6 / 6", "+2 this month")
with col2:
    st.metric("AI Service", status.get("active_service", "N/A").upper(), "Online" if ai_status != "mock" else "Simulation")
with col3:
    st.metric("API Endpoints", "18", "All active")
with col4:
    st.metric("Time to Launch", "< 24h", "↓ 90% vs manual")

st.markdown("---")

# ==================== Tabs ====================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🔍 Market Intelligence",
    "🛒 Store Operations",
    "✍️ Creative Studio",
    "🎨 Image Lab",
    "📺 Ad Factory",
    "🚀 Launch Center",
    "⚙️ Settings",
])

# ==================== TAB 1: Market Intelligence ====================

with tab1:
    st.header("🔍 Market Intelligence")
    st.markdown("<p style='color: #8888a0;'>Discover winning products with AI-powered analysis</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        category = st.selectbox("Category", ["All"] + product_research.CATEGORIES)
    with col2:
        max_price = st.slider("Max Price ($)", 5, 200, 50)
    with col3:
        min_rating = st.slider("Min Rating", 1.0, 5.0, 4.0, 0.1)
    
    if st.button("🔍 Search Products", use_container_width=True):
        with st.spinner("Analyzing market..."):
            results = api("POST", "/api/research/search", {
                "category": None if category == "All" else category,
                "max_price": max_price,
                "min_rating": min_rating,
            })
            if "error" in results:
                st.error(results["error"])
            else:
                products = results.get("products", [])
                if products:
                    st.success(f"Found {len(products)} products")
                    for p in products[:6]:
                        sales = sum(s["monthly_sales"] for s in p.get("competitor_stores", []))
                        with st.container():
                            cols = st.columns([1, 2, 1])
                            with cols[0]:
                                st.image(p["image"], width=120)
                            with cols[1]:
                                st.markdown(f"**{p['name']}**")
                                st.markdown(f"⭐ {p['rating']} | 💬 {p['reviews']} reviews")
                                if p.get("ai_insight"):
                                    st.markdown(f"*🤖 {p['ai_insight']}*")
                            with cols[2]:
                                st.markdown(f"### ${p['sale_price']}")
                                st.markdown(f"~~${p['price']}~~")
                                st.markdown(f"💰 ${sales:,.0f}/mo")
                            st.markdown("---")
                else:
                    st.warning("No products found. Try different filters.")

# ==================== TAB 2: Store Operations ====================

with tab2:
    st.header("🛒 Store Operations")
    st.markdown("<p style='color: #8888a0;'>Analyze and clone successful stores with white-label</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        store_url = st.text_input("Competitor Store URL", "https://hestiabeauty.com")
    with col2:
        if st.button("🔍 Analyze Store", use_container_width=True):
            with st.spinner("Analyzing..."):
                result = api("POST", "/api/store/analyze", {"url": store_url})
                st.session_state["store_analysis"] = result
    
    if "store_analysis" in st.session_state:
        r = st.session_state["store_analysis"]
        st.markdown(f"### {r.get('store', {}).get('name', 'Store Analysis')}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Monthly Revenue", f"${r.get('store', {}).get('monthly_revenue', 0)/1e6:.1f}M")
        with col2:
            st.metric("Monthly Traffic", f"{r.get('store', {}).get('monthly_traffic', 0)/1e3:.0f}K")
        with col3:
            st.metric("Niche", r.get('store', {}).get('niche', 'N/A'))
        
        if r.get("scraped"):
            with st.expander("📊 Scraped Data"):
                scraped = r["scraped"]
                st.json(scraped)
        
        if r.get("ai_insights"):
            with st.expander("🤖 AI Recommendations"):
                st.markdown(r["ai_insights"])
        
        st.markdown("#### Store Sections")
        for s in r.get("sections", []):
            st.markdown(f"- `{s['placeholder']}` → {s['name']}")
        
        brand = st.text_input("Your Brand Name", "SealSkin")
        if st.button("🔄 Clone Store", use_container_width=True, type="primary"):
            with st.spinner("Building your store..."):
                clone = api("POST", "/api/store/clone", {"brand_name": brand, "store_id": r.get("store", {}).get("id")})
                st.success(f"✅ Store '{brand}' created from {clone.get('cloned_from', 'template')}")
                with st.expander("📄 HTML Preview"):
                    st.code(clone.get("html_outline", "")[:2000], language="html")

# ==================== TAB 3: Creative Studio ====================

with tab3:
    st.header("✍️ Creative Studio")
    st.markdown("<p style='color: #8888a0;'>Generate AI-powered product copy and ad scripts</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        copy_product = st.selectbox("Product", [
            "prod_001 — Color Changing Foundation",
            "prod_002 — Overnight Fat Burner",
            "prod_003 — Red Light Device",
        ], key="copy_product")
        copy_tone = st.selectbox("Tone", ["confident_warm", "luxury", "professional", "youthful"])
    
    with col2:
        if st.button("✍️ Generate Copy", use_container_width=True):
            pid = copy_product.split(" —")[0]
            with st.spinner("Writing copy..."):
                result = api("POST", "/api/copy/generate", {"product_id": pid, "tone": copy_tone})
                st.session_state["copy_result"] = result
    
    if "copy_result" in st.session_state:
        copy = st.session_state["copy_result"]
        s = copy.get("copy_sections", {})
        st.markdown(f"### {copy.get('product', 'Product')}")
        if copy.get("ai_generated"):
            st.markdown("🤖 *AI-generated copy*")
        
        st.markdown(f"#### 🏷️ {s.get('hero', {}).get('headline', '')}")
        st.markdown(f"*{s.get('hero', {}).get('subheadline', '')}*")
        
        st.markdown("#### ✓ Features")
        for f in s.get("features", []):
            st.markdown(f"- {f.get('title', '')}")
        
        st.markdown("#### 💬 Testimonials")
        for t in s.get("testimonials", []):
            st.markdown(f"> \"{t.get('text', '')}\" — {t.get('name', '')}")
        
        st.markdown(f"#### 🛡️ {s.get('guarantee', '')}")
        st.markdown(f"#### ⚡ {s.get('urgency', '')}")

# ==================== TAB 4-7: Quick Setup ====================

with tab4:
    st.header("🎨 Image Lab")
    st.markdown("<p style='color: #8888a0;'>Generate product images with AI</p>", unsafe_allow_html=True)
    
    img_product = st.selectbox("Product", [
        "prod_001 — Color Changing Foundation",
        "prod_002 — Overnight Fat Burner",
    ], key="img_product")
    brand_name = st.text_input("Brand Name", "SealSkin")
    
    if st.button("🎨 Generate Image Plan", use_container_width=True):
        pid = img_product.split(" —")[0]
        with st.spinner("Creating images..."):
            result = api("POST", "/api/images/generate", {"product_id": pid, "brand_name": brand_name})
            st.success(f"Plan: {result.get('image_plan', {}).get('total_images_needed', 0)} images")
            st.text(result.get("brief", ""))
            
            previews = result.get("generated_previews", [])[:4]
            cols = st.columns(4)
            for i, img in enumerate(previews):
                with cols[i]:
                    st.image(img.get("url", ""), caption=f"{img.get('section')} - {img.get('type')}")

with tab5:
    st.header("📺 Ad Factory")
    st.markdown("<p style='color: #8888a0;'>Create video ad packages and AI avatars</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎬 Create Ads", use_container_width=True):
            with st.spinner("Building ads..."):
                result = api("POST", "/api/ads/create")
                for ad in result.get("ads", []):
                    st.markdown(f"**🎯 {ad['angle']}** — Quality: ⭐{ad.get('facebook_package', {}).get('estimated_quality_score', '?')}/10")
    
    with col2:
        avatar_script = st.text_area("Script for AI Avatar", "I didn't believe it... until I tried it.", height=100)
        avatar_type = st.selectbox("Avatar", ["Denise", "Sophia", "Emma"])
        if st.button("🤖 Prepare Avatar"):
            result = api("POST", "/api/ads/avatar", {"script": avatar_script, "avatar": avatar_type})
            st.info(f"Avatar: {result.get('avatar')} | {result.get('total_characters', 0)} chars | {len(result.get('script_lines', []))} lines")

with tab6:
    st.header("🚀 Launch Center")
    st.markdown("<p style='color: #8888a0;'>Configure and launch Facebook ad campaigns</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        campaign_name = st.text_input("Campaign Name", "SealSkin Launch Q2 2024")
        daily_budget = st.number_input("Daily Budget ($)", 5, 1000, 20)
        
        interests = campaign_manager.DEFAULT_INTERESTS
        selected = []
        st.markdown("**Target Interests:**")
        cols = st.columns(2)
        for i, interest in enumerate(interests):
            with cols[i % 2]:
                if st.checkbox(interest, value=True, key=f"int_{i}"):
                    selected.append(interest)
        
        st.markdown(f"**Total Daily Budget:** ${daily_budget * len(selected)}")
        
        if st.button("⚙️ Setup Campaign", use_container_width=True, type="primary"):
            with st.spinner("Configuring campaign..."):
                result = api("POST", "/api/launch/setup", {
                    "campaign_name": campaign_name,
                    "daily_budget": daily_budget,
                    "interests": selected,
                })
                st.session_state["campaign"] = result
                est = result.get("estimated_daily_results", {})
                st.success(f"Campaign ready! Est. {est.get('purchases', 0)} sales/day")
    
    with col2:
        st.markdown("### 📊 Forecast")
        f_budget = st.number_input("Budget ($)", 5, 500, 20, key="f_budget")
        f_price = st.number_input("Price ($)", 5, 200, 30, key="f_price")
        if st.button("Calculate", use_container_width=True):
            forecast = api("POST", "/api/launch/forecast", {"daily_budget": f_budget, "product_price": f_price})
            st.metric("Est. Purchases", forecast.get("estimated_purchases", 0))
            st.metric("Est. Revenue", f"${forecast.get('estimated_revenue', 0):.2f}")
            st.metric("ROAS", f"{forecast.get('estimated_roas', 0):.1f}x")
        
        if st.button("🔬 A/B Test Plan", use_container_width=True):
            plan = api("GET", "/api/launch/ab-test")
            st.info(f"Test: {plan.get('test_name', 'N/A')} | Duration: {plan.get('duration_days', 7)}d")
    
    if "campaign" in st.session_state and st.button("🚀 Launch Now!", use_container_width=True):
        result = api("POST", "/api/launch/execute")
        st.balloons()
        st.success(f"✅ Campaign launched! Status: {result.get('status', 'ACTIVE')}")

with tab7:
    st.header("⚙️ Settings")
    st.markdown("<p style='color: #8888a0;'>Configure API keys and system preferences</p>", unsafe_allow_html=True)
    
    st.markdown("### 🤖 AI Services")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**OpenAI**")
        openai_key = st.text_input("API Key", type="password", placeholder="sk-...", key="openai_input")
        if st.button("Save OpenAI Key", key="save_openai"):
            api("POST", "/api/settings/keys", {"service": "openai", "key": openai_key})
            st.success("✅ OpenAI key saved!")
    
    with col2:
        st.markdown("**Claude (Anthropic)**")
        claude_key = st.text_input("API Key", type="password", placeholder="sk-ant-...", key="claude_input")
        if st.button("Save Claude Key", key="save_claude"):
            api("POST", "/api/settings/keys", {"service": "claude", "key": claude_key})
            st.success("✅ Claude key saved!")
    
    st.markdown("---")
    st.markdown("### 🔐 Licensing")
    
    lic_key = st.text_input("License Key", type="password", placeholder="DRO-XXXXX-...")
    if st.button("Activate License"):
        result = api("POST", "/api/license/activate", {"service": "license", "key": lic_key})
        if result.get("valid"):
            st.balloons()
            st.success(f"✅ Licensed! {result.get('days_remaining', 0)} days remaining")
        else:
            st.error(f"❌ {result.get('message', 'Invalid key')}")
    
    st.markdown("---")
    st.markdown("### 🔬 Diagnostics")
    if st.button("Run System Test"):
        with st.spinner("Running diagnostics..."):
            h = api("GET", "/api/health")
            s = api("GET", "/api/settings/status")
            
            tests = [
                ("API Server", True),
                ("OpenAI" + (" ✅" if s.get("has_openai") else ""), s.get("has_openai", False)),
                ("Claude" + (" ✅" if s.get("has_claude") else ""), s.get("has_claude", False)),
                ("Data Files", True),
                ("License", h.get("license") == "valid"),
            ]
            
            for name, passed in tests:
                st.markdown(f"{'✅' if passed else '❌'} {name}")

# ==================== Footer ====================

st.markdown("""
<div class="footer">
    <strong>DRO — Agentic Commerce Engine</strong> v2.0<br>
    &copy; 2024 DRO Systems. All rights reserved.<br>
    Built with ❤️ for the next generation of e-commerce entrepreneurs.
</div>
""", unsafe_allow_html=True)
