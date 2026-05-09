#!/usr/bin/env python3
"""
DRO Render CLI — create and manage Render services from the command line.
Uses Render's Public API to automate deployment without clicking buttons.

Prerequisites:
    1. Generate a Render API key: Dashboard → Account Settings → API Keys
    2. Set RENDER_API_KEY environment variable

Usage:
    python deploy_cli.py list                          # List all services
    python deploy_cli.py create                        # Create API + Dashboard from render.yaml
    python deploy_cli.py deploy <service-id>           # Trigger deploy for a service
    python deploy_cli.py logs <service-id>             # Fetch recent logs
    python deploy_cli.py status <service-id>           # Get service status
"""

import os
import sys
import json
import urllib.request
import urllib.error


API_BASE = "https://api.render.com/v1"
API_KEY = os.getenv("RENDER_API_KEY")


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def _request(method: str, path: str, data: dict = None) -> dict:
    url = f"{API_BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"status": resp.status, "body": json.loads(resp.read())}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": e.read().decode()[:500]}
    except urllib.error.URLError as e:
        return {"status": 0, "body": str(e.reason)}


def list_services():
    result = _request("GET", "/services")
    if result["status"] == 200:
        print(f"\n  Render Services ({len(result['body'])} found):\n")
        for s in result["body"]:
            sid = s.get("id", s.get("service", {}).get("id", "?"))
            name = s.get("name", s.get("service", {}).get("name", "?"))
            state = s.get("state", s.get("service", {}).get("state", "?"))
            url = s.get("url", s.get("service", {}).get("url", ""))
            print(f"  [{state}] {name}")
            print(f"         ID: {sid}")
            print(f"         URL: {url}")
            print()
    else:
        print(f"  [!!] {result}")


def create_service(name: str, repo_url: str, start_cmd: str, env_vals: dict = None):
    """Create a new web service from a GitHub repo."""
    data = {
        "type": "web",
        "name": name,
        "repo": repo_url,
        "autoDeploy": True,
        "serviceDetails": {
            "env": "python",
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": start_cmd,
            "healthCheckPath": "/api/health" if "api" in name else None,
        },
    }
    if env_vals:
        data["envVars"] = [{"key": k, "value": v} for k, v in env_vals.items()]

    result = _request("POST", "/services", data)
    if result["status"] in (200, 201):
        print(f"  [OK] Service '{name}' created")
        print(f"  ID: {result['body'].get('id', '?')}")
    else:
        print(f"  [!!] {result}")


def trigger_deploy(service_id: str):
    result = _request("POST", f"/services/{service_id}/deploys", {"clearCache": False})
    if result["status"] in (200, 201):
        deploy_id = result["body"].get("id", "?")
        print(f"  [OK] Deploy triggered — ID: {deploy_id}")
    else:
        print(f"  [!!] {result}")


def get_logs(service_id: str):
    result = _request("GET", f"/services/{service_id}/logs?limit=50")
    if result["status"] == 200:
        logs = result["body"]
        if isinstance(logs, list):
            for line in logs[-30:]:
                print(f"  {line.get('timestamp', '')} {line.get('text', '')}")
        else:
            print(json.dumps(logs, indent=2))
    else:
        print(f"  [!!] {result}")


def get_status(service_id: str):
    result = _request("GET", f"/services/{service_id}")
    if result["status"] == 200:
        s = result["body"]
        print(f"\n  Service: {s.get('name', '?')}")
        print(f"  State:   {s.get('state', '?')}")
        print(f"  URL:     {s.get('url', '?')}")
        print(f"  Updated: {s.get('updatedAt', '?')}")
    else:
        print(f"  [!!] {result}")


if __name__ == "__main__":
    if not API_KEY:
        print("  [!!] RENDER_API_KEY environment variable not set")
        print("  Get one: Render Dashboard -> Account Settings -> API Keys")
        sys.exit(1)

    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "list":
        list_services()
    elif cmd == "create" and len(sys.argv) >= 4:
        create_service(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "")
    elif cmd == "deploy" and len(sys.argv) >= 3:
        trigger_deploy(sys.argv[2])
    elif cmd == "logs" and len(sys.argv) >= 3:
        get_logs(sys.argv[2])
    elif cmd == "status" and len(sys.argv) >= 3:
        get_status(sys.argv[2])
    else:
        print(f"  Unknown command or missing arguments: {cmd}")
        print(__doc__)
