#!/usr/bin/env python3
"""
DRO Deploy Hook Setup — lists services, fetches deploy hooks, prints GitHub secrets commands.
Run once after connecting repo to Render.

Usage:
    set RENDER_API_KEY=rnd_xxx
    python setup_hooks.py
"""

import os, sys, json, urllib.request, urllib.error

API_KEY = os.getenv("RENDER_API_KEY")
API = "https://api.render.com/v1"

def req(method, path, data=None):
    url = f"{API}{path}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method,
          headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]

if not API_KEY:
    print("[!!] RENDER_API_KEY not set")
    sys.exit(1)

print("\nFetching Render services...\n")
status, data = req("GET", "/services")
if status != 200:
    print(f"[!!] Failed to list services: {data}")
    sys.exit(1)

services = data if isinstance(data, list) else data.get("services", [data])
if not services:
    print("[!!] No services found. Connect your repo to Render first.")
    sys.exit(1)

print(f"Found {len(services)} service(s):\n")

hooks = {}
for svc in services:
    sid = svc.get("id", "?")
    name = svc.get("name", "?")
    url = svc.get("url", "")
    state = svc.get("state", svc.get("serviceDetails", {}).get("state", "?"))
    print(f"  [{state}] {name}")
    print(f"         ID:    {sid}")
    print(f"         URL:   {url}")

    # Try fetching deploy hook via env-vars or deploy-key endpoint
    for endpoint in [f"/services/{sid}/env-vars", f"/services/{sid}/deploy-key"]:
        try:
            s, d = req("GET", endpoint)
            if s == 200:
                if isinstance(d, list):
                    for ev in d:
                        if "hook" in str(ev.get("key", "")).lower() or "deploy" in str(ev.get("key", "")).lower():
                            hooks[name] = ev.get("value", "")
                elif isinstance(d, dict) and "url" in d:
                    hooks[name] = d["url"]
        except:
            pass
    print()

# Fallback: if hook not auto-fetched, use API-based deploy trigger
print("=" * 60)
print("GITHUB SECRETS to set (one-time):")
print("=" * 60)
print()
for svc in services:
    sid = svc.get("id", "?")
    name = svc.get("name", "?")
    env_name = name.upper().replace("-", "_")

    if name in hooks:
        print(f"  gh secret set RENDER_DEPLOY_HOOK_{env_name} --body \"{hooks[name]}\"")
    else:
        # Can't fetch hook via API, so use API-key based deploy
        print(f"  gh secret set RENDER_SERVICE_ID_{env_name} --body \"{sid}\"")

print()
print("Or set them manually at: https://github.com/YOUR_USERNAME/dro/settings/secrets/actions")
print()

# Trigger deploy via API for all services
print("=" * 60)
print("TRIGGERING DEPLOY NOW via Render API...")
print("=" * 60)
print()
for svc in services:
    sid = svc.get("id", "?")
    name = svc.get("name", "?")
    print(f"  Deploying {name}... ", end="", flush=True)
    s, d = req("POST", f"/services/{sid}/deploys", {"clearCache": False})
    if s in (200, 201):
        did = d.get("id", "?")
        print(f"OK (deploy {did})")
    else:
        print(f"FAILED: {d}")
