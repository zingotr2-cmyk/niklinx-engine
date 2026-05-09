#!/usr/bin/env python3
"""
DRO Deploy Trigger — uses Render Deploy Hook URL to trigger zero-downtime deployment.

Usage:
    # Set your deploy hook URL as env var, then run:
    python deploy_now.py

    # Or pass the hook URL directly:
    python deploy_now.py https://api.render.com/deploy/srv-xxx?key=yyy

How to get the deploy hook URL:
    1. Go to Render Dashboard → your service → Settings
    2. Scroll to "Deploy Hook" section
    3. Copy the URL (looks like: https://api.render.com/deploy/srv-xxx?key=yyy)
    4. Set it as RENDER_DEPLOY_HOOK_URL environment variable
"""

import os
import sys
import urllib.request
import urllib.error


def trigger_deploy(hook_url: str) -> dict:
    """Trigger a deploy via Render's Deploy Hook."""
    req = urllib.request.Request(hook_url, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return {"status": resp.status, "body": body}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": e.read().decode()}
    except urllib.error.URLError as e:
        return {"status": 0, "body": str(e.reason)}


def trigger_api_deploy(api_key: str, service_id: str, repo_url: str = "") -> dict:
    """Trigger a deploy via Render's Public API."""
    import json

    data = json.dumps({
        "serviceId": service_id,
        "repoUrl": repo_url,
        "clearCache": False,
    }).encode()

    req = urllib.request.Request(
        f"https://api.render.com/v1/services/{service_id}/deploys",
        data=data,
        method="POST",
    )
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return {"status": resp.status, "body": json.loads(body)}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": e.read().decode()}
    except urllib.error.URLError as e:
        return {"status": 0, "body": str(e.reason)}


if __name__ == "__main__":
    # Priority: CLI arg > env var
    hook_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("RENDER_DEPLOY_HOOK_URL")
    api_key = os.getenv("RENDER_API_KEY")
    service_id = os.getenv("RENDER_SERVICE_ID")

    if hook_url:
        print(f"  Triggering deploy via hook ...")
        result = trigger_deploy(hook_url)
        if result["status"] in (200, 201):
            print(f"  [OK] Deploy triggered (HTTP {result['status']})")
            print(f"  Body: {result['body']}")
        else:
            print(f"  [!!] Failed (HTTP {result['status']}): {result['body']}")
            sys.exit(1)

    elif api_key and service_id:
        print(f"  Triggering deploy via Render API ...")
        result = trigger_api_deploy(api_key, service_id)
        if result["status"] in (200, 201):
            print(f"  [OK] Deploy triggered (HTTP {result['status']})")
            print(f"  Deploy ID: {result['body'].get('id', 'unknown')}")
        else:
            print(f"  [!!] Failed (HTTP {result['status']}): {result['body']}")
            sys.exit(1)

    else:
        print("  [!!] No deploy hook URL or API credentials found.")
        print()
        print("  Provide one of:")
        print("    1. Hook URL: python deploy_now.py <hook_url>")
        print("    2. Env vars: RENDER_DEPLOY_HOOK_URL=<url>")
        print("    3. Env vars: RENDER_API_KEY + RENDER_SERVICE_ID")
        sys.exit(1)
