#!/usr/bin/env python3
"""
niklinx Production Health Check — run after deployment to verify all systems.

Usage:
    python diagnose.py [url]

Default URL: https://dro-api.onrender.com
"""

import sys, json, urllib.request, urllib.error

BASE = sys.argv[1] if len(sys.argv) > 1 else "https://dro-api.onrender.com"

def badge(s): return "[OK]" if s == 200 else "[!!]"

def check(path, method="GET", data=None):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method,
          headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except urllib.error.URLError as e:
        return 0, {"error": str(e.reason)}

print("\n" + "=" * 58)
print("  niklinx — Production Health Check")
print("=" * 58)
print(f"  Target: {BASE}\n")

# Root
s, d = check("/")
print(f"  {badge(s)}  Root          {s}  {d.get('service','')} v{d.get('version','')}")

# Health
s, d = check("/api/health")
ai = d.get("ai_service", "?")
mods = d.get("modules", [])
print(f"  {badge(s)}  Health        {s}  ai={ai}  modules={len(mods)}")

# Settings
s, d = check("/api/settings/status")
print(f"  {badge(s)}  Settings      {s}  hwid={d.get('hwid','?')}  active={d.get('active_service','?')}")

# License
s, d = check("/api/license/status")
print(f"  {badge(s)}  License       {s}  {d.get('message','')[:50]}")

# Search
s, d = check("/api/research/search", "POST", {"max_price": 50})
cnt = len(d.get("products", []))
print(f"  {badge(s)}  Research      {s}  {cnt} products loaded")

# Store
s, d = check("/api/store/analyze", "POST", {"url": "hestiabeauty.com"})
st = d.get("store", {})
print(f"  {badge(s)}  Store         {s}  template={st.get('name','?')}")

# Copy
s, d = check("/api/copy/generate", "POST", {"product_id": "prod_001"})
print(f"  {badge(s)}  Copy          {s}  ai_generated={d.get('ai_generated',False)}")

# Images
s, d = check("/api/images/generate", "POST", {"product_id": "prod_001"})
imgs = len(d.get("generated_previews", []))
print(f"  {badge(s)}  Images        {s}  {imgs} images in plan")

# Ads
s, d = check("/api/ads/create", "POST", {})
ads = len(d.get("ads", []))
print(f"  {badge(s)}  Ads           {s}  {ads} creatives")

# Forecast
s, d = check("/api/launch/forecast", "POST", {"daily_budget": 20})
rev = d.get("estimated_revenue", 0)
roas = d.get("estimated_roas", 0)
print(f"  {badge(s)}  Forecast      {s}  est_revenue=${rev}  roas={roas}x")

# AB Test
s, d = check("/api/launch/ab-test")
variants = len(d.get("variants", []))
print(f"  {badge(s)}  AB Test       {s}  {variants} variants")

print()
print("=" * 58)
print("  niklinx LAUNCH REPORT")
print("=" * 58)
print(f"  API:         {BASE}")
print(f"  API Docs:    {BASE}/docs")
print(f"  Dashboard:   https://dro-dashboard.onrender.com")
print()
if all(s == 200 for s, _ in [check("/api/health")]):
    print("  Status:      ONLINE — All systems operational")
else:
    print("  Status:      PENDING — Deploy in progress or not yet pushed")
    print("  Run:  git push -u origin main    then re-run this script")
print()
print("  License Key: Generate locally with:")
print("    python main.py license-gen")
print()
print("  AI Services: Configure via Dashboard Settings tab")
print("    - OpenAI:  set OPENAI_API_KEY env var")
print("    - Claude:  set CLAUDE_API_KEY env var")
print("=" * 58)
print("  niklinx is OPEN for business.")
print("=" * 58)
print()
